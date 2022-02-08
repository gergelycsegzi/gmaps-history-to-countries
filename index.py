import json
import reverse_geocode
import datetime
from dateutil.parser import parse
import argparse

event_filter_window_in_seconds = 60 * 10

parser = argparse.ArgumentParser(description='Convert Google Maps location history to country transfers json.')
parser.add_argument(
    '-i', '--input', help='Filepath to location history .json file.', default='Records.json'
)
parser.add_argument(
    '-o', '--output', help='Filepath to write resulting .json file to.', default='travels.json'
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
    seconds_from_last_point = (timestamp - previous_timestamp).total_seconds()
    is_accurate = int(location['accuracy']) < 200
    if (seconds_from_last_point > event_filter_window_in_seconds) and is_accurate:
        lat = location['latitudeE7']/1e7
        long = location['longitudeE7']/1e7
        coordinates.append((lat, long))
        filtered_locations.append(location)
        previous_timestamp = timestamp

if verbose:
    print("Progress: Loaded " + str(len(coordinates)) + " location points")

location_metadata = reverse_geocode.search(coordinates)
timestamp_to_country = []
for index, location in enumerate(filtered_locations):

    timestamp = parse(location['timestamp']).strftime("%Y-%m-%d")
    timestamp_to_country.append(
        {
            "timestamp": timestamp,
            "country": location_metadata[index]['country'],
            "latlong": str(location['latitudeE7']/1e7) + "," + str(location['longitudeE7']/1e7)
        }
    )

if verbose:
    print("Progress: created lookup table for countries")

index = 0
international_movements = []
current_country = timestamp_to_country[0]['country']
previous_country = timestamp_to_country[0]['country']
while index < len(timestamp_to_country):
    current_country = timestamp_to_country[index]['country']

    if current_country != previous_country:
        if (not args.country) or (args.country == current_country) or (args.country == previous_country):
            international_movements.append(
                {
                    "timestamp": timestamp_to_country[index]['timestamp'],
                    "origin": previous_country,
                    "destination": current_country,
                    "latlong": timestamp_to_country[index]['latlong']
                }
            )
    previous_country = current_country
    index += 1

    if verbose and (index % 1000 == 0):
        print("Progress: processed " + str(index) + " / " + str(len(timestamp_to_country)))

if args.country:
    if verbose:
        print("Flattening into trips originating from origin country")
    trips_from_country = []
    for index, travel in enumerate(international_movements):
        if travel['origin'] == args.country:
            departure = travel['timestamp']
            destination = travel['destination']

        if (travel['destination'] == args.country) and departure:
            trips_from_country.append({
                "departure": departure,
                "return": travel['timestamp'],
                "destination": destination
            })         
    to_write = trips_from_country
else:
    to_write = international_movements

with open(args.output, 'w', encoding='utf-8') as f:
    json.dump(to_write, f, ensure_ascii=False, indent=4)