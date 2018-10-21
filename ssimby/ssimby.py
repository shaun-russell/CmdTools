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

  saved_records = []
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
    if in_daterange(start, end, line_startdate, line_enddate):
      has_dates = True
    # skip if fails date requirements
    if not has_dates:
      continue

    # get the operating days of the flight
    active_days = [int(x) for x in record.op_days if x != ' ']

    # time deltas
    dep_timedelta = ssimdata.hour24_to_timedelta(record.dep_sched_time)
    arr_timedelta = ssimdata.hour24_to_timedelta(record.arr_sched_time)

    # utc offset time deltas
    dep_utc = ssimdata.offset_utc(dep_timedelta, int(record.dep_utc_variation))
    arr_utc = ssimdata.offset_utc(arr_timedelta, int(record.arr_utc_variation))

    record.utc_dep_date = dep_utc
    record.utc_arr_date = arr_utc


    # loop until past the end date
    current_date = start
    while current_date.date <= end:
      current_date = datetime.timedelta(days=1) + current_date
      # flight has not started yet at this date
      if current_date < line_startdate:
        continue
      # skip if not an operating date
      if current_date.isoweekday() not in active_days:
        continue

      active_record = copy.copy(record)
      active_record.local_date = current_date
      active_record.utc = current_date


    # save
    saved_records.append(record)
    lines_kept += 1


    


  # # parse the header for column indexes
  # header_line = in_file.readline()
  # header = header_line.strip()

  # saved_lines = []

  # # if --no-header, don't save the header
  # # otherwise save it
  # if not no_header:
  #   # use DOS line endings
  #   if '\r' in header_line:
  #     saved_lines.append(header + '\r\n')
  #   # standard unix endings
  #   else:
  #     saved_lines.append(header + '\n')


  # # write the matched lines to the output file
  # if verbose: click.echo('Saving...')
  # for line in saved_lines:
  #   out_file.write(line)
  # out_file.close()

  # # finished
  # if verbose: click.echo('Saved')
