#!/bin/bash

# This script uses an date-stamped suffix for the snapshot rather than depend on the array generated suffix.

# Set up source and target array names and users

runtime=scripted-`date "+%Y-%m-%d-%H-%M-%S"`
sourcearray="10.21.39.107"
targetarray="10.21.39.107"

# Using username auth, this should use public keys instead if you want it to run without asking for a password.
# Using password auth can be a failsafe that prevents accidental use of the script, however. 

sourceuser="pureuser"
targetuser="pureuser"

sourcevolume="p66hanadatavolume"
targetvolume="p66hanasecdatavolume"

echo "Running command ssh $sourceuser@$sourcearray purevol snap $sourcevolume --suffix=$runtime"
          response=$(ssh $sourceuser@$sourcearray "purevol snap $sourcevolume --suffix=$runtime" 2>&1)
finalsource=$sourcevolume"."$runtime
echo "Running command ssh $sourceuser@$sourcearray purevol copy --overwrite  $finalsource $targetvolume"
	  response=$(ssh $sourceuser@$sourcearray "purevol copy --overwrite  $finalsource $targetvolume" 2>&1) 
echo "======"
echo "Save the output below if you wish to restore from this snapshot."
echo "======"
echo $response


