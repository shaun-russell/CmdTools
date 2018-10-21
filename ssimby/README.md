# SSIMby
SSIMby is a tool to parse IATA ssim files to extract flight information. It also has functions to integrate departure and arrival airport information from a file (joined using the IATA code).

## Installation
Download the files and install locally with pip. Requires Python 3 (may work with Python 2, but haven't checked) and the `click` package (this should be installed automatically because it's a required package).

`pip install .`

You can also just copy and paste the files around, but that's not a very good approach.
Once installed, run just `ssimby` or `ssimby --help` in the terminal for usage instructions.

## Usage
SSIMby is a multi-command program.

```
Usage: ssimby [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  filter  Reduces a flights file to flights to and from...
  reduce  Reduces a raw SSIM file to only...
```

## reduce
Reduce breaks the full IATA ssim file into only FlightLegRecords. SSIMby only uses these records, so this will need to be run first.

```
Usage: ssimby reduce [OPTIONS] IN_FILE OUT_FILE

  Reduces a raw SSIM file to only FlightLegRecords.

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.
```

## filter
Filter reduces flight records based on Date Ranges and specific airports. Date ranges are in the format **20FEB18** for 20th of February, 2018. Both a start date and an end date must be provided, and the program will create a flight record for every day within that range that a flight operates.

A list of airport IATA codes must be provided in a file to focus the flights to a specific area. By default, a flight will be kept if the arrival _or_ departure airport is in the file, but the `--both-airports` flag will make the program only keep lines where both arrival and departure airports are in the file.

The `--no-header` flag will exclude the header in cases where a output files will be concatenated later.

Airport information (latitude, longitude, airport name, icao, and country) can be added as columns for arrival and departure airports by using the `--airport` or `-p` option followed by a path to a file containing airports. The header will be searched for the following column names (search is a case-insensitive 'contains' search): 
- latitude
- longitude
- airport (the name of the airport)
- icao
- iata
- country

DateTime columns are added for local departure, local arrival, UTC depature, UTC arrival.

```
Usage: ssimby filter [OPTIONS] FLIGHTS_FILE AIRPORTS_FILE START_DATE END_DATE
                     OUT_FILE

  Reduces a flights file to flights to and from a list of IATA airport
  codes. Start and End date format: 20AUG18 or 01JAN19. Include airport to
  create dataset with airport details

Options:
  -p, --airport FILENAME  Include detail columns from airport file in output.
  -b, --both-airports     Only save records with both Arrival and Departure
                          airports in provided list.
  -e, --no-header         Excludes the header from the output.
  -h, --help              Show this message and exit.
  --version   Show the version and exit.
```

Here is an example of the filter command with an airport information file:

`ssimby filter -p files/airports.txt files/flights.txt files/iatas.txt 11NOV18 18NOV18 files\ssim-export.txt`

Here is an example of the filter command _without_ an airport information file, with the `--both-airports` and `--no-header` flags:

`ssimby filter -eb files/flights.txt files/iatas.txt 11NOV18 18NOV18 files\ssim-export.txt`

## Notes
Sample data files are not included because the license does not allow it.

DateTime formats are strings in `YYYY-mm-dd HH:MM` 24-hour format.