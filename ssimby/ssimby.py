''' Guided command line program to extract ssim file data. '''

import sys
import click
import datetime
import copy
import ssimdata 

# used to tell Click that -h is shorthand for help
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# individual functions go here
def in_daterange(lower_date, upper_date, startdate, enddate):
  if enddate < lower_date:
    return False
  if startdate > upper_date:
    return False
  return True


@click.group()
def cli():
  click.echo('CLI launched.')

# START CLI COMMANDS
@cli.command('reduce', context_settings=CONTEXT_SETTINGS)
# required arguments
@click.argument('in-file', type=click.File('r'), required=True)
@click.argument('out-file', type=click.File('w+'), required=True)

# other required arguments
@click.version_option(version='1.0.0')

# main entry point function
def reduce(in_file, out_file):
  ''' Reduces a raw SSIM file to only FlightLegRecords. '''
  num_of_thousands = 0
  index = 0
  for line in in_file:
    if line.startswith('3'):
      out_file.write(line)
    if index >= 1000:
      index = 0
      num_of_thousands += 1
      click.echo('\rProcessed {} thousand lines.'.format(num_of_thousands), nl=False)
    index += 1
  out_file.close()
  exit()


@cli.command('filter', context_settings=CONTEXT_SETTINGS)
@click.argument('flights-file', type=click.File('r'), required=True)
@click.argument('airports-file', type=click.File('r', encoding='utf8'), required=True)
@click.argument('start-date', type=str, required=True)
@click.argument('end-date', type=str, required=True)
@click.argument('out-file', type=click.File('w+', encoding='utf8'), required=True)

@click.option('--airport', '-p', type=click.File('r', encoding='utf8'), default=None,
              help='Include detail columns from airport file in output.')
# options
@click.option('--both-airports', '-b', is_flag=True,
              help='Only save records with both Arrival and Departure airports in provided list.')
@click.option('--no-header', '-e', is_flag=True,
              help='Excludes the header from the output.')
@click.version_option(version='1.0.0')

def filter(flights_file, airports_file, out_file,
                  start_date, end_date, airport,
                  no_header, both_airports):
  ''' Reduces a flights file to flights to and from a list of IATA airport codes.
      Start and End date format: 20AUG18 or 01JAN19.
      Include airport to create dataset with airport details
  '''
  saved_lines = []

  # parse the header for column indexes
  header_line = flights_file.readline()

  airports_enabled = False
  if airport != None:
    click.echo('Airports enabled.')
    airports_enabled = True

  eol = '\n'
  # if --no-header, don't save the header
  # otherwise save it
  if not no_header:
    # use DOS line endings
    if '\r' in header_line:
      eol = '\r\n'
    saved_lines.append(ssimdata.FlightLegRecord.header(eol, airports_enabled) + eol)
  
  # upper and lower date limits for flight records
  start = ssimdata.datestring_to_date(start_date)
  end = ssimdata.datestring_to_date(end_date)


  # airport file for filtering (not airport data file)
  iata_airports = [x.strip() for x in airports_file.readlines()]

  # AIRPORT PROCESSING
  all_airports = []
  # because there are a lot of airports, we want to reduce the number of
  # list searches, so we check the cache before the full list
  airport_cache = []
  # parse airports
  if airports_enabled:
    all_airport_lines = [x.strip() for x in airport.readlines()]
    click.echo('Num of airports: {}'.format(len(all_airport_lines)))

    # find the columns we want in the airport dataset
    header_indices = ssimdata.Airport.get_header_indices(all_airport_lines[0])

    click.echo('Verifying header...')
    # verify that all required columns are found in the dataset
    missing_values = False
    for k,v in header_indices.items():
      if v == -1:
        # tell the user which columns are missing from the airports dat
        click.echo('MISSING COLUMN: {}'.format(k))
        missing_values = True
    # don't want to continue the program when the headers aren't there.
    if missing_values: exit()

    # parse and store all the airports
    click.echo('Processing airports...')
    for ap_line in all_airport_lines:
      airport = ssimdata.Airport(ap_line, header_indices)
      if airport.iata in iata_airports:
        # add this airport to the cache because it's a required airport
        airport_cache.append(airport)
      # add airport to list anyway
      all_airports.append(airport)


  line_count = 0
  lines_kept = 0
  click.echo('Processing flight lines...')
  for line in flights_file:
    # print progress
    line_count += 1
    if line_count % 1000:
      click.echo('\rKept {} of {} lines.'.format(lines_kept, line_count), nl=False)

    record = ssimdata.FlightLegRecord(line)
    # check for airport requirements
    has_airports = False
    if both_airports:
      if record.arr_station in iata_airports and record.dep_station in iata_airports:
        has_airports = True
    else:
      if record.arr_station in iata_airports or record.dep_station in iata_airports:
        has_airports = True
    # skip if fails airport requirements
    if not has_airports:
      continue

    # check for date requirements
    has_dates = False
    line_startdate = ssimdata.datestring_to_date(record.op_period[:7])
    line_enddate = ssimdata.datestring_to_date(record.op_period[7:])
    if in_daterange(start, end, line_startdate, line_enddate):
      has_dates = True
    # skip if fails date requirements
    if not has_dates:
      continue

    # get the operating days of the flight
    active_days = [int(x) for x in record.op_days if x != ' ']

    # time deltas
    dep_time = ssimdata.hour24_to_time(record.dep_sched_time)
    arr_time = ssimdata.hour24_to_time(record.arr_sched_time)

    # i hate python datetime libraries so much

    # create a blank airport here so we don't have to create one every time
    blank_indices = {
      'latitude': 0,
      'longitude': 0,
      'icao': 0,
      'iata': 0,
      'airport': 0,
      'country': 0,
    }
    blank_airport = ssimdata.Airport('NULL', blank_indices)

    # loop until past the end date
    current_date = start
    while current_date <= end:
      current_date = datetime.timedelta(days=1) + current_date
      # flight has not started yet at this date
      if current_date < line_startdate:
        continue
      # skip if not an operating date
      if current_date.isoweekday() not in active_days:
        continue

      # utc offset time deltas
      dep_utc = ssimdata.offset_utc(datetime.datetime.combine(current_date, dep_time), int(record.dep_utc_variation))
      arr_utc = ssimdata.offset_utc(datetime.datetime.combine(current_date, arr_time), int(record.arr_utc_variation))

      # duplicate and add the utc date
      active_record = copy.copy(record) # this may be redundant, because strings are being saved
      active_record.dep_local_date = datetime.datetime.combine(current_date, dep_time)
      active_record.arr_local_date = datetime.datetime.combine(current_date, arr_time)

      active_record.utc_dep_date = dep_utc
      active_record.utc_arr_date = arr_utc

      # correct for overnight flights (local arrival)
      if active_record.arr_local_date < active_record.dep_local_date:
        active_record.arr_local_date += datetime.timedelta(days=1)
      # correct for overnight flights (UTC arrival)
      if active_record.utc_arr_date < active_record.utc_dep_date:
        active_record.utc_arr_date += datetime.timedelta(days=1)

      # add airport columns, if applicable
      if airport:
        # search cache
        for ap in airport_cache:
          # find departure airport
          if ap.iata.lower() == active_record.dep_station.lower():
            active_record.dep_airport = ap
          # find arrival airport
          if ap.iata.lower() == active_record.arr_station.lower():
            active_record.arr_airport = ap

        if active_record.dep_airport == None or active_record.arr_airport == None:
          for ap in airport_cache:
            # find departure airport
            if active_record.dep_airport == None and ap.iata.lower() == active_record.dep_station.lower():
              active_record.dep_airport = ap
            # find arrival airport
            if active_record.arr_airport == None and ap.iata.lower() == active_record.arr_station.lower():
              active_record.arr_airport = ap

        # check if airport is still not found
        if active_record.dep_airport == None:
          active_record.dep_airport = blank_airport
        if active_record.arr_airport == None:
          active_record.arr_airport = blank_airport

      # save
      saved_lines.append(active_record.export(eol))
      lines_kept += 1

  click.echo('Saving...')
  # write the matched lines to the output file
  for line in saved_lines:
    out_file.write(line)
  out_file.close()
  click.echo('Saved.')
