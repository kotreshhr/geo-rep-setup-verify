import sys
import os
import re
import shutil
from errno import ENOENT
from subprocess import Popen, PIPE

def exit(str):
    print("FAILURE")
    if str == "gsec_create":
        print ("Consider doing 'gluster system:: gsec_create' again")
    if str == "create_push_pem":
        print ("Consider doing 'gluster geo-rep <mastervol> \
               <slavenode>::<slavevol> create push-pem force")
    sys.exit(-1)


def lstat(file):
    try:
        os.lstat(file)
        return 0
    except (IOError, OSError):
            ex = sys.exc_info()[1]
            if ex.errno == ENOENT:
                print("%s not found" % file)
                exit("gsec_create")
            else:
                raise


def str2bool(str):
  return str.lower() in ("yes", "true", "1")


def verify_gsec_create(init_node):
    """
    Verify gsec_create
    """

    orig_common_secret_path = "/var/lib/glusterd/geo-replication/common_secret.pem.pub"
    tmp_common_secret_path = "/var/lib/glusterd/common_secret.pem.pub.temp"

    secret_pem_path = "/var/lib/glusterd/geo-replication/secret.pem"
    secret_pem_pub_path = "/var/lib/glusterd/geo-replication/secret.pem.pub"
    tar_ssh_pem = "/var/lib/glusterd/geo-replication/tar_ssh.pem"
    tar_ssh_pem_pub = "/var/lib/glusterd/geo-replication/tar_ssh.pem.pub"


    print "Checking gsec_create:"
    lstat(secret_pem_path)
    lstat(secret_pem_pub_path)
    lstat(tar_ssh_pem)
    lstat(tar_ssh_pem_pub)

    if init_node:
        lstat(orig_common_secret_path)
        shutil.copyfile(orig_common_secret_path, tmp_common_secret_path)
        po = Popen(['gluster', 'system::', 'copy', 'file', 'common_secret.pem.pub.temp'], stderr=PIPE)
        (out, err) = po.communicate()
        if po.returncode != 0:
            print("gluster system:: copy file failed: %s" % err)
            exit("gsec_create")

    common_file = open(tmp_common_secret_path, 'r')
    common_data = common_file.read()
    common_file.close()

    secret_pub = open(secret_pem_pub_path, 'r')
    secret_pub_data = secret_pub.read()
    secret_pub.close()

    if not re.findall(re.escape(secret_pub_data), common_data):
        print("secret.pem.pub key missing in common_secret.pem.pub")
        exit("gsec_create")

    tar_pub = open(tar_ssh_pem_pub, 'r')
    tar_pub_data = tar_pub.read()
    tar_pub.close()

    if not re.findall(re.escape(tar_pub_data), common_data):
        print("tar_ssh.pem.pub key missing in common_secret.pem.pub")
        exit("gsec_create")

    print("PASS")


def verify_create_push_pem(master, slave):
    """
    Verify create push pem
    """
    print("Checking create push pem")
    slave_common_secret_file = master + '_' + slave + '_common_secret.pem.pub'
    if not os.path.isfile(os.path.join("/var/lib/glusterd/geo-replication", slave_common_secret_file)):
        print("slave_common_secret_pem.pub file not present")
        exit("create_push_pem")

    """
    TODO: Replace hardcoded paths
    """
    auth_file = open("/root/.ssh/authorized_keys", 'r')
    auth_data = auth_file.read()
    auth_file.close()

    common_file = open(os.path.join("/var/lib/glusterd/geo-replication", slave_common_secret_file), 'r')
    common_data = common_file.read()
    common_file.close()

    if not re.findall(re.escape(common_data), auth_data):
        print ("Keys not present in .ssh/authorized_keys")
        exit("create_push_pem")

    print("PASS")

def main():
    master = sys.argv[1]
    slave  = sys.argv[2]
    node   = sys.argv[3]
    init_node = str2bool(sys.argv[4])

    """
    Verify gsec_create step
    """
    if (node == master):
        verify_gsec_create(init_node)

    """
    Verify create push pem
    """
    if (node == slave):
        verify_create_push_pem(master, slave)

if __name__ == "__main__":
    main()
