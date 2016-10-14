#!/bin/bash

#Variable definition
mysql_status="/dev/shm/mysql_status"
mysqladmin="/usr/bin/mysqladmin"
zabbix_server="127.0.0.1"
zabbix_sender="/usr/bin/zabbix_sender"

usage() {
cat << EOF
Usage:
This program is used to obtain MySQL information sent to ZABBI
Options:
    --help|-h)
        print help info.
    --zabbix-server|-z)
        Hostname or IP address of Zabbix server(default=172.16.35.92).
    --sql_server|-s)
        MySQL host.
    --user|-u)
        Access MySQL user name
    --passwd|-p)
        Access MySQL user name
    --hostname|-H)
	server name(default=127.0.0.1)
Example:
    ./$0 -z 10.13.0.92 -H 127.0.0.1 -s 127.0.0.1 -u root -p 123
EOF
}

while test -n "$1";do
    case "$1" in
    -z|--zabbix-server)
        zabbix_server=$2
        shift 2
        ;;
    -h|--help)
        usage
        exit
        ;;
    -s|--sql_server)
        mysql_server=$2
        shift 2
        ;;
    -u|--user)
        user=$2
        shift 2
        ;;
    -p|--passwd)
        passwd=$2
        shift 2
        ;;
    -P|--prot)
	port=$2
	shift 2
	;;
    -H|--host)
	hostname=$2
	shift 2
	;;
    *)
        echo "Unknown argument: $1"
        usage
        exit
        ;;
    esac
done

#Get Host ip
if [ ! -n "$hostname" ];then
	hostname=$(ifconfig | grep 'inet addr:' | egrep '10\.|172\.16\.' | awk '{print $2}' | awk -F':' '{print $2}')
fi

#Get [Uptime Slow_queries Questions] infomation
for i in `echo "Uptime Slow_queries Questions"`
do
    key=$(echo $i | sed 's/_/ /g')
    value=$($mysqladmin -h$mysql_server -P$port -u$user -p$passwd status | sed 's/  /\n/g' | grep "$key" | awk -F':' '{print $2}')
    echo  "$hostname mysql.status[$i] $value" >> $mysql_status
done

#Get [Com_update Com_select Com_rollback Com_insert Com_delete Com_commit Bytes_sent Bytes_received Com_begin] information
for i in `echo "Com_update Com_select Com_rollback Com_insert Com_delete Com_commit Bytes_sent Bytes_received Com_begin"`
do
    value=$($mysqladmin -h$mysql_server -P$port -u$user -p$passwd extended-status | grep "$i " | awk -F'|' '{print $3}')
    echo  "$hostname mysql.status[$i] $value" >> $mysql_status
done

#MySQL version information
mysql_version=$(mysql -V)
echo "$hostname mysql.version \"$mysql_version\"" >> $mysql_status
#MySQL service state
mysql_ping=$($mysqladmin -h$mysql_server -P$port -u$user -p$passwd ping  | grep -c alive)
echo "$hostname mysql.ping $mysql_ping" >> $mysql_status

$zabbix_sender -z $zabbix_server -i $mysql_status
rm -rf $mysql_status
