"""This module estimates the cost of running a cluster of EC2 spot instances."""

import argparse
from datetime import datetime, timedelta
import statistics
import boto3



def total_hours(hours, days, weeks):
    """Total hours in w weeks + d days + h hours."""
    return hours + 24 * (days + 7 * weeks)


def costs(hours, cost_per_hour, machines=1):
    """cost = hours * $/hour * machines"""
    return hours * cost_per_hour * machines


def get_spot_price(
        client,
        availability_zone,
        instance_type,
        days_back,
        method):
    """Gets the hourly price of a given spot instance type in a given availability zone.

       This method uses the average, max, or most recent of the last `days_back` days of spot prices
       as returned by the EC2 API.
    """
    paginator = client.get_paginator("describe_spot_price_history")
    pages = paginator.paginate(
        StartTime=datetime.utcnow() - timedelta(days=days_back),
        EndTime=datetime.utcnow(),
        InstanceTypes=[instance_type],
        ProductDescriptions=['Linux/UNIX'],
        AvailabilityZone=availability_zone
    )

    price_list = [float(p["SpotPrice"])
                  for resp in pages for p in resp["SpotPriceHistory"]]

    return {
        "average": lambda x: sum(x) / len(x),
        "last": lambda x: x[0],
        "max": max,
        "median": statistics.median
    }[method](price_list)


def get_reserved_price(client, availability_zone, instance_type):
    """Gets price of a given reserved Linux instance type in a given availability zone."""
    resp = client.describe_reserved_instances_offerings(
        InstanceType=instance_type,
        AvailabilityZone=availability_zone,
        OfferingType="No Upfront",
        ProductDescription="Linux/UNIX",
    )
    return float(resp["ReservedInstancesOfferings"][
        0]["RecurringCharges"][0]["Amount"])


def parse_options():
    """Parse command line options."""
    parser = argparse.ArgumentParser(
        description="Estimates AWS EC2 spot cluster costs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--hours",
        type=int,
        default=0,
        help="Number of hours.")
    parser.add_argument("--days", type=int, default=0, help="Number of days.")
    parser.add_argument(
        "--weeks",
        type=int,
        default=0,
        help="Number of weeks.")
    parser.add_argument(
        "--instance_type",
        default=None,
        help="Instance type for master *and* slaves overrides slave and master type if set.")
    parser.add_argument(
        "--slave_type",
        default="r3.4xlarge",
        help="Slave instance type.")
    parser.add_argument(
        "--master_type",
        default="r3.4xlarge",
        help="Master instance type.")
    parser.add_argument(
        "--num_masters",
        type=int,
        default=1,
        help="Number of masters (priced at reserve rate).")
    parser.add_argument(
        "--num_slaves",
        type=int,
        default=1,
        help="Number of slaves (priced at spot rate).")
    parser.add_argument(
        "--availability_zone",
        default="us-west-2b",
        help="Availability zone.")
    parser.add_argument(
        "--spot_method",
        choices=[
            "average",
            "max",
            "last",
            "median"],
        default="average",
        help="Method to use when calculating prevailing spot price.")
    parser.add_argument(
        "--days_back",
        type=int,
        default=1,
        help="Number of days to use when calculating average spot price.")

    options = parser.parse_args()

    if options.instance_type:
        options.slave_type = options.instance_type
        options.master_type = options.instance_type

    if options.spot_method == "last":
        options.days_back = 1

    return options


def get_cost_estimate(
        ec2_client,
        hours=0,
        availability_zone="us-west-2b",
        master_type="r3.4xlarge",
        slave_type="r3.4xlarge",
        days_back=1,
        spot_method="average",
        num_masters=1,
        num_slaves=1):
    """Deliver a cost estimate for running a given cluster in an availability zone with
       the given instance type for a certain length of time.

    Args:
      hours (int): How many hours will the cluster run for?
      days (int): How many days?
      weeks (int): How many weeks?
      availability_zone (string): In what availability zone?
      master_type (string): What will the instance type of the master be?
      slave_type (string): What will the instance type of the slaves be?
      days_back (int): How many days of pricing history should be used?
      spot_method (string): What price calculation method should be used?
          (one of "average", "max", "median", or "last")

    Returns:
      An estimate (in USD) of the cost to run such a cluster for this length of time.
    """

    if num_slaves > 0:
        slave_hourly_price = get_spot_price(
            ec2_client,
            availability_zone,
            slave_type,
            days_back,
            spot_method)
    else:
        slave_hourly_price = 0.0

    if num_masters > 0:
        master_hourly_price = get_reserved_price(
            ec2_client, availability_zone, master_type)
    else:
        master_hourly_price = 0.0

    total_cost = costs(hours, master_hourly_price, num_masters) + \
        costs(hours, slave_hourly_price, num_slaves)

    return total_cost


def main():
    """Entry point for the command line interface."""
    opts = parse_options()

    ec2_client = boto3.client('ec2', region_name=opts.availability_zone[:-1])

    hours = total_hours(opts.hours, opts.days, opts.weeks)

    total_cost = get_cost_estimate(
        ec2_client,
        hours,
        opts.availability_zone,
        opts.master_type,
        opts.slave_type,
        opts.days_back,
        opts.spot_method,
        opts.num_masters,
        opts.num_slaves)

    print "$%4.2f" % total_cost

if __name__ == "__main__":
    main()
