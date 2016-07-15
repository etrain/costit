import json, sys
from operator import mul

def average_price(history):
	return sum([float(h["SpotPrice"]) for h in history])/len(history)

def main():
	data = json.loads(sys.stdin.read())
	print average_price(data["SpotPriceHistory"])*reduce(mul, map(int, sys.argv[1:]))

if __name__ == "__main__":
	main()
