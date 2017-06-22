clear
# Set reverse video mode
tput rev
echo "M A I N - M E N U"
tput sgr0

tput cup 7 15
echo "1. SAP HANA SYSTEM SNAPSHOT"

tput cup 8 15
echo "2. SAP HANA BACKUP"

tput cup 9 15
echo "3. SAP HANA SYSTEM COPY"

# Set bold mode
tput bold
tput cup 12 15
read -p "Enter your choice [1-3] " choice

if [ `ps -ef | grep hdb | wc -l` -gt 3 ]; then
   echo "Shutdown Target HANA Database"
   exit 1
fi

echo "Unmounting the Target SAP HANA system data volume"
umount /hana/data/P66

echo "Prepare the source SAP HANA for Storage Snapshot..."
ssh p66adm@10.21.39.145 "
/usr/sap/P66/home/.profile
/usr/sap/P66/home/.bashrc
/usr/sap/P66/home/.sapsrc.sh
/usr/sap/P66/home/.sapenv.sh
pwd
cd /usr/sap/P66/HDB00
export PATH=/usr/sap/P66/HDB00/saphana:/usr/sap/P66/HDB00:/usr/sap/P66/HDB00/exe:/usr/sap/P66/HDB00/exe/mdc:/usr/sap/P66/HDB00/exe/Python/bin:/usr/sap/P66/HDB00/exe/dat_bin_dir:.:/usr/sap/P66/home:/usr/sap/P66/home/bin:/usr/local/bin:/usr/bin:/bin:/usr/bin/X11:/usr/X11R6/bin:/usr/games:/usr/lib/mit/bin:/usr/lib/mit/sbin

pwd
hdbsql -S P66 -n 10.21.39.145:30015 -u system -p Osmium76 <<EOF
BACKUP DATA CREATE SNAPSHOT;
select * from M_BACKUP_CATALOG WHERE "ENTRY_TYPE_NAME" = 'data snapshot' and "STATE_NAME" = 'prepared'
exit
EOF
" > backup_id.txt

varbackupid=`sed '12!d' backup_id.txt | cut -d',' -f1`
echo "Backup id $varbackupid"

echo "Freezing the Data volumes File system"
ssh root@10.21.39.145 "
xfs_freeze -f /hana/data/P66
"

echo "Take the Storage Snapshot and copy it to target"

echo "Take snapshot of Data volume..."
./snapcopydatavolume.sh


echo "Unfreezing the Data volumes File system"
ssh root@10.21.39.145 "
xfs_freeze -u /hana/data/P66
"

echo "Close SAP HANA for Storage Snapshot..."
ssh p66adm@10.21.39.145 "
/usr/sap/P66/home/.profile
/usr/sap/P66/home/.bashrc
/usr/sap/P66/home/.sapsrc.sh
/usr/sap/P66/home/.sapenv.sh
pwd
cd /usr/sap/P66/HDB00
export PATH=/usr/sap/P66/HDB00/saphana:/usr/sap/P66/HDB00:/usr/sap/P66/HDB00/exe:/usr/sap/P66/HDB00/exe/mdc:/usr/sap/P66/HDB00/exe/Python/bin:/usr/sap/P66/HDB00/exe/dat_bin_dir:.:/usr/sap/P66/home:/usr/sap/P66/home/bin:/usr/local/bin:/usr/bin:/bin:/usr/bin/X11:/usr/X11R6/bin:/usr/games:/usr/lib/mit/bin:/usr/lib/mit/sbin
pwd
hdbsql -S P66 -n 10.21.39.145:30015 -u system -p Osmium76 <<EOF
BACKUP DATA CLOSE SNAPSHOT BACKUP_ID $varbackupid UNSUCCESSFUL;
exit
EOF
"
echo "Mounting the Target SAP HANA system data volume"
mount /dev/mapper/3624a9370122281ffa371414400011077 /hana/data/P66

echo "Restart SAP HANA...."

ssh p66adm@10.21.39.146 "
cd /usr/sap/P66/HDB00/
./HDBSettings.sh recoverSys.py --silent --command=RECOVER\ DATA\ \ USING\ SNAPSHOT\ \ CLEAR\ LOG --masterOnly
"



