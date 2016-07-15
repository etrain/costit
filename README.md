# COSTIT

This repository contains a set of scripts designed to help answer questions of the form:

How much would it cost me to run a spark cluster of N spot worker nodes and one master for H hours?

It uses historical spot pricing data (averages) to establish such an estimate.

For example:

	costit.sh --slave_type=r3.4xlarge --num_slaves=100 --days=1

Will compute the total dollars spent running a cluster of 100 r3.4xlarge nodes for 1 day based on the last 7 days of pricing. ($2026.82 at time of writing)

## Requirements
You will need to have the `aws` [command line tools](https://aws.amazon.com/cli/) installed.

## Usage

	costit.sh INSTANCE_TYPE DAYS_BACK_PRICING NUM_NODES NUM_HOURS [NUM_DAYS [NUM_WEEKS [...]]]

## Limitations

Currently this code assumes that you're using `r3.4xlarge` as your master instance type.

## Future Work

1. Port my terrible shell to python. Boto [supports](http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.describe_spot_price_history) the main call we use.
1. Error handling.
1. Determine if we can answer the question: "how much is my current spot cluster costing me right now." with these APIs.

## License

This project is released under the Apache2 License.
