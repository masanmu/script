#!/bin/bash

ZABBIX_SENDER="/usr/bin/zabbix_sender"
ZABBIX_SERVER="172.16.142.190"

usage(){
cat << EOF
Usage:This program is extract data from  iostats to zabbix.
Options:
  --help|-h)
    Print help info.
  --zabbix-server|-z)
    Hostname or IP address of Zabbix server(default=172.16.142.190).
  --disk|-d)
   Device Name..
Example:
  ./$0 -z 172.16.142.190 -d /dev/sda1
EOF
}

while test -n "$1" ;do
	case "$1" in
	-z|--zabbix_server)
		zabbix_server=$2
		shift 2
		;;
	-h|--help)
		usage
		exit
		;;
	-d|--disk)
		device=$2
		shift 2
		;;
	*)
		echo "Unknown argument: $1"
		exit
		usage
		;;
	esac
done

iostat_info="/dev/shm/iostat_info"

key_name=("Device" "iostat.rrqm" "iostat.wrqm" "iostat.r" "iostat.w" "iostat.rkB" "iostat.wkB" "iostat.avgrq-sz" "iostat.avgqu-sz" "iostat.await" "iostat.svctm" "iostat.util")
IP=$(ifconfig | grep -E "(eth|bond)" -A 1 | grep addr: | grep -E "10\.|172\.16" | awk -F\: '{print $2}' | cut -d' ' -f 1)
num=0
for i in `/usr/bin/iostat -x -k $device | egrep "$device"`
do
	echo "$IP ${key_name[$num]} $i" >> $iostat_info
	num=`echo $num +1 | bc`
done
$ZABBIX_SENDER -z $ZABBIX_SERVER -i $iostat_info
rm -rf $iostat_info
