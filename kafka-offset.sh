#!/bin/bash

zookeeper="localhost:2181"
open_falcon="http://127.0.0.1:1988/v1/push"
kafka_home="/usr/local/kafka/"

usage() {
cat << EOF
Usage:
This progrom is used to obtain kafka offset info send to open-falcon
Options:
	-h|--help)
		print "helo info"
	-o|--open-falcon)
		open-falcon server ip (default:127.0.0.1)
	-k|--kafka)
		kafka installation directory (default:/usr/local/kafka/)
	-t|--topic)
		consumer topic (REQUIRED)
	-g|--consumer-group)
		consumer group (REQUIRED)
	-z|--zookeeper)
		zookeeper server ip and port (default:localhost:2181)
Example:
	./$0 -t topic -g consumer-group
EOF
}

if [ $# -lt 4 ];then
	usage
	exit -1
fi

while test -n "$1";
do
	case $1 in
		-o|--open-falcon)
			open_falcon="http://"$2":1988/v1/push"
			shift 2
			;;
		-k|--kafka)
			kafka_home=$2
			shift 2
			;;
		-t|--topic)
			topic=$2
			shift 2
			;;
		-g|--consumer-group)
			consumer_group=$2
			shift 2
			;;
		-z|--zookeeper)
			zookeeper=$2
			shift 2
			;;
		-h|--help)
			usage
			exit
			;;
		*)
			echo "unknowe argument argument:$1"
			usage
			exit
			;;
	esac
done

kafka_consumer_offset="$kafka_home/bin/kafka-consumer-offset-checker.sh"
if [ ! -f "$kafka_consumer_offset" ];then
	echo "This $kafka_home or $kafka_consumer_offset does not exist"
	exit -1
fi

info=`$kafka_consumer_offset --zookeeper $zookeeper --topic $topic --group $consumer_group | /bin/awk 'BEGIN{OFS=":"}/[0-9]/{Lag+=$6;logSize+=$5;Offset+=$4}END{print Lag,logSize,Offset}'`
Lag=`echo $info | cut -d":" -f1`
logSize=`echo $info | cut -d":" -f2`
Offset=`echo $info | cut -d":" -f3`
ts=`date +%s`
endpoint=$HOSTNAME

for metric in Lag logSize Offset
do
	counter="kafka_"$topic"_"$metric
	/usr/bin/curl -X POST -d "[{\"metric\": \"$counter\", \"endpoint\": \"$endpoint\", \"timestamp\": $ts,\"step\": 60,\"value\": $[$metric],\"counterType\": \"GAUGE\",\"tags\": \"role=kafka\"}]" $open_falcon
done
