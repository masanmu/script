#!/bin/bash

Open_Falcon=/usr/local/open-falcon
NAME=Open-Falcom
SERVER="127.0.0.1"
module="all"
declare -A port

port=(
["agent"]="1988"
["alarm"]="9912"
["dashboard"]="8081"
["fe"]="1234"
["graph"]="6071"
["hbs"]="6031"
["judge"]="6081"
["links"]="5090"
["portal"]="5050"
["task"]="8002"
["transfer"]="6060"
["query"]="9966"
)

usage(){
cat << EOF
Usage:
This program is init open-falcon
Options:
	-h|--help)
		print "help info"
	-m|--module)
		module name default(all)
		agent:1988
		alarm:9912
		dashboard:8081
		fe:1234
		graph:6071
		hbs:6031
		judge:6081
		links:5090
		portal:5050
		task:8002
		transfer:6060
		query:9966
	-s|--signal)
		send signal to a master process: stop, quit, reopen, reload
	$NAME {build|pack|start|stop|restart|status|tail}"
EOF
}


if [ $# -eq "0" ];then
        usage
        exit -1
fi

while test -n "$1";
do
	case $1 in
		-h|--help)
			usage
			exit 
			;;
		-m|--module)
			module=$2
			shift 2
			;;
		-s|--signal)
			signal=$2
			shift 2
			;;
		*)
			echo "unknowe argument :$1"
			usage
			exit -1
			;;
	esac
done

open_falcon(){
	if [ $1 == "all" ];then
		for module in $(echo ${!port[*]})
		do
			echo -e "\033[32m===========================================\033[0m"
			a=`cd "$Open_Falcon/$module/" && ./control $2`
	       	 	echo -e "\033[33m$module\t:\033[0m\033[32m$a\033[0m"
		done
	else
		echo -e "\033[32m===========================================\033[0m"
		a=`cd "$Open_Falcon/$1/" && ./control $2`
		echo -e "\033[33m$module\t:\033[0m\033[32m$a\033[0m"
	fi
}

open_falcon_health(){
	if [ $1 == "all" ];then
		for module in $(echo ${!port[*]})
		do
			a=`/usr/bin/curl -s http://$SERVER:${port[$module]}/health`
			if [ "$a" == "ok" ]; then
				echo -e "\033[33m$module\033[0m:\t[\033[32m$a\033[0m]"
			else
				echo -e "\033[33m$module\033[0m:\t[\033[31mNo medical examination or alive\033[0m]"
			fi
		done
	else
		a=`/usr/bin/curl -s http://$SERVER:${port[$1]}/health`
		if [ "$a" == "ok" ]; then
			echo -e "\033[33m$module\033[0m:\t[\033[32m$a\033[0m]"
		else
			echo -e "\033[33m$module\033[0m:\t[\033[31mNo medical examination or alive\033[0m]"
		fi

	fi
}

case $signal in
	build|pack|start|stop|restart|status|tail)
		open_falcon $module $signal
		;;
	health)
		open_falcon_health $module $signal
		;;
esac
