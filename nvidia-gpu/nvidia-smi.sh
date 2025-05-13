#!/usr/bin/bash

# 查看可查询的字段
# nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu,temperature.gpu --format=csv
# nvidia-smi --help-query-gpu

if [ "$1"x = x ] || [ "$1"x = "usage"x ];then
	nvidia-smi -l 1 -q -d UTILIZATION

elif [ "$1"x = "pids"x ];then
	nvidia-smi -l 1 -q -d PIDS

fi
