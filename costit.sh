#!/bin/bash

INSTANCE_TYPE=$1
shift
DAYSBACK=$1d
shift 

#Usage: costit.sh INSTANCE_TYPE DAYS_BACK_PRICING NUM_NODES NUM_HOURS [NUM_DAYS [NUM_WEEKS [...]]]

START=`date -j -v-$DAYSBACK +"%Y-%m-%d"`


CLUSTER=`aws ec2 describe-spot-price-history --start-time $START --instance-types $INSTANCE_TYPE | python costit.py $@`
MASTER=`aws ec2 describe-reserved-instances-offerings --instance-type=r3.4xlarge --product-description="Linux/UNIX" --instance-tenancy=default --offering-type="No Upfront" | python master_cost.py $@`

out=`echo "$CLUSTER + $MASTER" | bc`

printf '$%.2f\n' $out
