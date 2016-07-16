import argparse
import boto3
from datetime import datetime, timedelta

def total_hours(opts):
  return opts.hours + 24*(opts.days + 7*opts.weeks)

def costs(hours, cost_per_hour, machines=1):
  return hours*cost_per_hour*machines
  
def get_spot_price(availability_zone, instance_type, days_back):
  client = boto3.client('ec2', region_name=availability_zone[:-1])
  resp = client.describe_spot_price_history(
      StartTime=datetime.utcnow()-timedelta(days=days_back),
      EndTime=datetime.utcnow(),
      InstanceTypes=[instance_type],
      ProductDescriptions=['Linux/UNIX'],
      AvailabilityZone=availability_zone
  )
  
  #TODO: Currently we only make one call and thus only get the last 1000 price
  #points. This api supports a paging syntax for more accurate pricing.
  
  price_list = [float(p["SpotPrice"]) for p in resp["SpotPriceHistory"]]
  
  return sum(price_list)/len(price_list)
  
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
  parser.add_argument("--days_back", type=int, default=7, help="Number of days to use when calculating average spot price.")
  parser.add_argument("--slave_type", default="r3.4xlarge", help="Slave instance type.")
  parser.add_argument("--master_type", default="r3.4xlarge", help="Master instance type.")
  parser.add_argument("--num_slaves", type=int, default=1, help="Number of slaves.")
  parser.add_argument("--availability_zone", default="us-west-2b", help="Availability zone.")
    
  options = parser.parse_args()
  
  return options
  
def main():
  opts = parse_options()
  
  hours = total_hours(opts)
  
  slave_hourly_price = get_spot_price(opts.availability_zone, opts.slave_type, opts.days_back)
  master_hourly_price = get_reserved_price(opts.availability_zone, opts.master_type)
  
  total_cost = costs(hours, master_hourly_price) + costs(hours, slave_hourly_price, opts.num_slaves)
  
  print "$%4.2f" % total_cost
  
if __name__ == "__main__":
  main()

