import json, sys
from operator import mul

print json.loads(sys.stdin.read())["ReservedInstancesOfferings"][0]["RecurringCharges"][0]["Amount"]*reduce(mul, map(int, sys.argv[2:]))
