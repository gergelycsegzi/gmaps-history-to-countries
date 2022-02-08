import json
import reverse_geocode
import datetime
from dateutil.parser import parse
import argparse
import pytz

utc=pytz.UTC 

event_filter_window_in_seconds = 60 * 10

parser = argparse.ArgumentParser(description='Convert Google Maps location history to country transfers json.')
parser.add_argument(
    '-i', '--input', help='Filepath to location history .json file.', default='Records.json'
)
parser.add_argument(
    '-o', '--output', help='Filepath to write resulting .json file to.', default='travelszz.json'
)
parser.add_argument('-s', '--silent', help='Silence disables logs', default=False)
parser.add_argument('-c', '--country', help='Only include logs originating from or ending at provided country', required=False)

args = parser.parse_args()
verbose = not args.silent

if verbose:
    print('Verbosely executing with input file: ' + args.input + ' and output file: ' + args.output)
    if args.country:
        print('Will also filter to country: ' + args.country)
    print('Loading input JSON')

records = json.load(open(args.input))
locations = records["locations"]

coordinates = []

timestamp = parse(locations[0]['timestamp'])
previous_timestamp = timestamp - datetime.timedelta(seconds=event_filter_window_in_seconds + 1)
filtered_locations = []
for location in locations:
    timestamp = parse(location['timestamp'])
    if (timestamp > utc.localize(datetime.datetime(2014, 4, 24))) and (timestamp < utc.localize(datetime.datetime(2014, 4, 27))):
        filtered_locations.append(location)

with open(args.output, 'w', encoding='utf-8') as f:
    json.dump(filtered_locations, f, ensure_ascii=False, indent=4)
