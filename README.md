## geo-rep-setup-verify:
GlusterFS geo-replication:
This script verifies whether geo-replication is properly setup or not.

## Usage:
The script needs to be run on each node of both master and slave cluster
nodes with respective arguments as given below.

python geo-rep-setup-verify <mastervol> <slavevol> <init_node>

       <mastervol> : master volume name
       <slavevol>  : slave volume name
       <init_node> : Boolean
                     "1": For master node using which geo-rep session is created.
                     "0": For other master nodes and slave nodes.
