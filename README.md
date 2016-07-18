# costit

This repository contains a set of scripts designed to help answer questions of the form:

How much would it cost me to run an EC2 cluster of N spot worker nodes and one master for H hours?

It uses historical spot pricing data (averages) to establish such an estimate.

For example:

	python costit.py --slave_type=r3.4xlarge --num_slaves=100 --days=1

Will compute the total dollars spent running a cluster of 100 r3.4xlarge nodes for 1 day based on the last 7 days of pricing. ($445.63 at time of writing)

## Requirements
Requires boto3, [properly configured](http://boto3.readthedocs.io/en/latest/guide/quickstart.html).

## Usage

	usage: costit.py [-h] [--hours HOURS] [--days DAYS] [--weeks WEEKS]
	                 [--instance_type INSTANCE_TYPE] [--slave_type SLAVE_TYPE]
	                 [--master_type MASTER_TYPE] [--num_slaves NUM_SLAVES]
	                 [--availability_zone AVAILABILITY_ZONE]
	                 [--spot_method {average,max,last}] [--days_back DAYS_BACK]

	Estimates AWS EC2 spot cluster costs.

	optional arguments:
	  -h, --help            show this help message and exit
	  --hours HOURS         Number of hours. (default: 0)
	  --days DAYS           Number of days. (default: 0)
	  --weeks WEEKS         Number of weeks. (default: 0)
	  --instance_type INSTANCE_TYPE
	                        Instance type for master *and* slaves overrides slave
	                        and master type if set. (default: None)
	  --slave_type SLAVE_TYPE
	                        Slave instance type. (default: r3.4xlarge)
	  --master_type MASTER_TYPE
	                        Master instance type. (default: r3.4xlarge)
	  --num_slaves NUM_SLAVES
	                        Number of slaves. (default: 1)
	  --availability_zone AVAILABILITY_ZONE
	                        Availability zone. (default: us-west-2b)
	  --spot_method {average,max,last}
	                        Method to use when calculating prevailing spot price.
	                        (default: average)
	  --days_back DAYS_BACK
	                        Number of days to use when calculating average spot
	                        price. (default: 1)

## License

This project is released under the Apache2 License.
