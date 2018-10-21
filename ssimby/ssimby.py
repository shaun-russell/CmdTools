''' Guided command line program to extract ssim file data. '''

import sys
import click

# used to tell Click that -h is shorthand for help
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group()
def cli():
  click.echo('CLI launched.')

# individual functions go here



# START CLI COMMANDS
@cli.command(context_settings=CONTEXT_SETTINGS)
# required arguments
@click.argument('in-file', type=click.File('r'), required=True)
@click.argument('out-file', type=click.File('w+'), required=True)

# other required arguments
@click.version_option(version='1.0.0')


# main entry point function
def reduce(in_file, out_file):
  ''' Reduce a raw SSIM file to only FlightLegRecords. '''

  exit()
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
