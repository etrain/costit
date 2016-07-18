import argparse
import boto3
from datetime import datetime, timedelta

def total_hours(opts):
  return opts.hours + 24*(opts.days + 7*opts.weeks)

def costs(hours, cost_per_hour, machines=1):
  return hours*cost_per_hour*machines

def get_spot_price(availability_zone, instance_type, days_back, method):
  client = boto3.client('ec2', region_name=availability_zone[:-1])
  paginator = client.get_paginator("describe_spot_price_history")
  pages = paginator.paginate (
      StartTime=datetime.utcnow()-timedelta(days=days_back),
      EndTime=datetime.utcnow(),
      InstanceTypes=[instance_type],
      ProductDescriptions=['Linux/UNIX'],
      AvailabilityZone=availability_zone
  )
  
  price_list = [float(p["SpotPrice"]) for resp in pages for p in resp["SpotPriceHistory"]]
  
  return {
    "average": lambda x: sum(x)/len(x),
    "max": lambda x: max(x),
    "last": lambda x: x[0]
  }[method](price_list)

def get_reserved_price(availability_zone, instance_type):
  client = boto3.client('ec2', region_name=availability_zone[:-1])
  resp = client.describe_reserved_instances_offerings(
    InstanceType=instance_type,
    AvailabilityZone=availability_zone,
    OfferingType="No Upfront",
    ProductDescription="Linux/UNIX",
  )
  return float(resp["ReservedInstancesOfferings"][0]["RecurringCharges"][0]["Amount"])

def parse_options():
  parser = argparse.ArgumentParser(
    description="Estimates AWS EC2 spot cluster costs.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--hours", type=int, default=0, help="Number of hours.")
  parser.add_argument("--days", type=int, default=0, help="Number of days.")
  parser.add_argument("--weeks", type=int, default=0, help="Number of weeks.")
  parser.add_argument("--instance_type", default=None, 
      help="Instance type for master *and* slaves overrides slave and master type if set.")
  parser.add_argument("--slave_type", default="r3.4xlarge", help="Slave instance type.")
  parser.add_argument("--master_type", default="r3.4xlarge", help="Master instance type.")
  parser.add_argument("--num_slaves", type=int, default=1, help="Number of slaves.")
  parser.add_argument("--availability_zone", default="us-west-2b", help="Availability zone.")
  parser.add_argument("--spot_method", choices=["average","max","last"], default="average", 
      help="Method to use when calculating prevailing spot price.")
  parser.add_argument("--days_back", type=int, default=1, 
      help="Number of days to use when calculating average spot price.")
    
  options = parser.parse_args()
  
  if options.instance_type:
    options.slave_type = options.instance_type
    options.master_type = options.instance_type
    
  if options.spot_method == "last":
    options.days_back = 1
  
  return options
  
def main():
  opts = parse_options()
  
  hours = total_hours(opts)
  
  slave_hourly_price = get_spot_price(opts.availability_zone, opts.slave_type, opts.days_back, opts.spot_method)
  master_hourly_price = get_reserved_price(opts.availability_zone, opts.master_type)
  
  total_cost = costs(hours, master_hourly_price) + costs(hours, slave_hourly_price, opts.num_slaves)
  
  print "$%4.2f" % total_cost
  
if __name__ == "__main__":
  main()

