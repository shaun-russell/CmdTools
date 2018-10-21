''' Tool for extracting lines out of files. '''

# The functions of this could be done using awk or perl commands, but on
# Windows that relies on cygwin (which I have, but it's more convenient
# to have a python script I can edit and add more functions to (+ portable)

import os
import click
from functions import MatchTypes, remove_newline

# used to tell Click that -h is shorthand for help
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# the types of value matching to use for finding columns to keep
match_types = {'exact': MatchTypes.match_exact,
               'starts': MatchTypes.match_starts,
               'ends': MatchTypes.match_ends,
               'contains': MatchTypes.match_contains,
               'greater': MatchTypes.match_greater,
               'less': MatchTypes.match_less}

# individual functions go here
def get_values_to_match(values, file_flag, ignore_case):
  ''' Gets the values from file or text. '''
  match_values = []
  if file_flag == True:
    if not os.path.exists(values):
      click.echo('ERROR: Values file {} not found. Use of --file-values flag requires values argument to be a valid file path.'.format(values))
      exit()
    else:
      match_values = [x.strip() for x in open(values).readlines()]
  else:
    match_values = values.split(',')
  if ignore_case:
    return [x.lower() for x in match_values]
  else:
    return match_values

def get_column_index(col_idx, col_name, header, ignore_case, delim, verbose):
  ''' Gets the index number of the column based on flags and provided arguments. ''' 
  # if no column name, use the index (default if also not given)
  if col_name == '':
    if verbose: click.echo('Using numeric index.')
    return col_idx
  if ignore_case:
    if verbose: click.echo('Ignoring case.')
    col_name = col_name.lower()
    delim = delim.lower()
  # get the header index
  if verbose: click.echo('Using string column name.')
  try:
    header = header.lower().split(delim) if ignore_case else header.split(delim)
    if verbose: click.echo('Header: {}'.format(header))
    return header.index(col_name)
  except:
    click.echo('ERROR: Column not found in header.')
    exit()

# START CLI COMMANDS
@click.command(context_settings=CONTEXT_SETTINGS)
# required arguments
@click.argument('in-file', type=click.File('r'), required=True)
@click.argument('values', type=str, required=True)
@click.argument('out-file', type=click.File('w+'), required=True)

# optional arguments
@click.option('--delimiter', '-d', default='\t',
              help='Delimiter to use in the files. Default is TAB.')
@click.option('--column-index', '-x', default=0, type=int,
              help='Column index to use. Index is zero-based and default is 0.')
@click.option('--column-name', '-n', default='',
              help='Find column by name. Takes precedence over --column-index.')
@click.option('--match', '-m', default='exact',
              type=click.Choice(match_types.keys()),
              help='The method used to match values. Default is "exact".')

# flags
@click.option('--file-values', '-f', is_flag=True,
              help='Read values as a file path.')
@click.option('--ignore-case', '-i', is_flag=True,
              help='Ignores letter case when searching and matching.')
@click.option('--no-header', '-e', is_flag=True,
              help='Excludes the header from the output.')
@click.option('--verbose', is_flag=True,
              help='Enables information-dense terminal output.')

# other required arguments
@click.version_option(version='1.0.0')


# main entry point function
def cli(in_file, values, out_file,
        column_index, column_name, match, delimiter,
        verbose, ignore_case, file_values, no_header):
  ''' Filter lines in a file based on the values of a single column.\n
  Supports a variety of string matching functions.\n
  VALUES must be a file path (each value on a new line) or as a comma-separated
  sequence of words.'''
  # first validate whether values are correct
  match_values = get_values_to_match(values, file_values, ignore_case)

  # parse the header for column indexes
  header_line = in_file.readline()
  header = header_line.strip()

  saved_lines = []

  # if --no-header, don't save the header
  # otherwise save it
  if not no_header:
    # use DOS line endings
    if '\r' in header_line:
      saved_lines.append(header + '\r\n')
    # standard unix endings
    else:
      saved_lines.append(header + '\n')

  # if header is default, but tab delimiter not found in header,
  # if the header has columns, assume it's a CSV
  if delimiter == '\t' and '\t' not in header and ',' in header:
    delimiter = ','
    if verbose:
      click.echo('Default delimiter TAB not found in header, using COMMA.')
  # if delimiter is made of letters, needs to work when case-insensitive
  if ignore_case:
    delimiter = delimiter.lower()

  # get the column index depending on which argument options are provided
  idx = get_column_index(column_index, column_name, header, ignore_case, delimiter, verbose)
  if verbose:
    click.echo('Header: {}'.format(header.split(delimiter)))
    click.echo('Column index: {}'.format(idx))
    click.echo('Match values: {}'.format(match_values))

  # because first line read as header, the file pointer is at the first data line
  for line in in_file:
    # split line into columns (with lowercase if --ignore-case)
    columns = remove_newline(line).lower().split(delimiter) if ignore_case else remove_newline(line).split(delimiter)
    # try find a match with every value
    if verbose: click.echo(columns)
    for value in match_values:
      # use the specified function to find matches
      if match_types[match](columns[idx], value):
        saved_lines.append(line)
        break
  if verbose: click.echo('Saving...')

  # write the matched lines to the output file
  for line in saved_lines:
    out_file.write(line)
  out_file.close()

  # finished
  if verbose: click.echo('Saved')
