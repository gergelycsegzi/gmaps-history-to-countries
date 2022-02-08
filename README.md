# gmaps-history-to-countries
Transform Google location history json into a list of timestamped travel destinations potentially flattening for source country

The tool may be useful for answering the following question: *Where and when have I gone from country X?*
In my case, it helped me get an overview of my trips outside of the UK that is required for UK citizenship application.

The included script will parse the extracted JSON data from Google Maps' Location History, and output a list of country to country travel objects into a JSON file. If a country filter is provided (e.g. `-c "United Kingdom"`) then this will be further flattened to only consider leaving the source country and returning to it.

To export your location data visit [Google Takeout](https://takeout.google.com/settings/takeout).

## Parse your export data

1. Download `index.py` and place the script in the same directory as your `Records.json` export.
2. Run the script from your chosen command line (`python index.py`). Use `-h` flag to see options.
3. This will generate `travels.json` unless overridden.

## Known issues

With some versions of python the reverse geocoding library may throw an encoding error:
```
  File "c:\utils\Python\Python37\lib\encodings\cp1252.py", line 23, in decode
    return codecs.charmap_decode(input,self.errors,decoding_table)[0]
UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 in position 464: character maps to <undefined>
```
This can be solved by [manually overriding the underlying library, as explained here](https://github.com/richardpenman/reverse_geocode/pull/10).