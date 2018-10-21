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
@click.argument('airports-file', type=click.File('r'), required=True)
@click.argument('start-date', type=str, required=True)
@click.argument('end-date', type=str, required=True)
@click.argument('out-file', type=click.File('w+'), required=True)

# options
@click.option('--both-airports', '-b', is_flag=True,
              help='Only save records with both Arrival and Departure airports in provided list.')
@click.option('--no-header', '-e', is_flag=True,
              help='Excludes the header from the output.')

def filter(flights_file, airports_file, out_file,
                  start_date, end_date,
                  no_header, both_airports):
  ''' Reduces a flights file to flights to and from a list of IATA airport codes.
      Start and End date format: 20AUG18 or 01JAN19.

  '''

  saved_lines = []

  # parse the header for column indexes
  header_line = flights_file.readline()

  eol = '\n'
  # if --no-header, don't save the header
  # otherwise save it
  if not no_header:
    # use DOS line endings
    if '\r' in header_line:
      eol = '\r\n'
    saved_lines.append(ssimdata.FlightLegRecord.header(eol))

  iata_airports = [x.strip() for x in airports_file.readlines()]
  
  start = ssimdata.datestring_to_date(start_date)
  end = ssimdata.datestring_to_date(end_date)

  line_count = 0
  lines_kept = 0

  for line in flights_file:
    # print progress
    line_count += 1
    if line_count > 1000:
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
    print(record.op_period[:7], record.op_period[7:])
    if in_daterange(start, end, line_startdate, line_enddate):
      has_dates = True
    # skip if fails date requirements
    if not has_dates:
      continue

    # get the operating days of the flight
    active_days = [int(x) for x in record.op_days if x != ' ']
    print(active_days)

    # time deltas
    dep_time = ssimdata.hour24_to_time(record.dep_sched_time)
    arr_time = ssimdata.hour24_to_time(record.arr_sched_time)

    # i hate python datetime libraries so much

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
      active_record = copy.copy(record)
      active_record.dep_local_date = datetime.datetime.combine(current_date, dep_time)
      active_record.arr_local_date = datetime.datetime.combine(current_date, arr_time)
      # correct for overnight flights
      if active_record.arr_local_date < active_record.dep_local_date:
        active_record.arr_local_date += datetime.timedelta(days=1)
      active_record.utc_dep_date = dep_utc
      active_record.utc_arr_date = arr_utc

      # save
      saved_lines.append(active_record.export(eol))
      lines_kept += 1

  # write the matched lines to the output file
  for line in saved_lines:
    out_file.write(line)
  out_file.close()
