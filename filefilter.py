''' Tool for extracting lines out of files. '''

# The functions of this could be done using awk or perl commands, but on
# Windows that relies on cygwin (which I have, but it's more convenient
# to have a python script I can edit and add more functions to (+ portable)

import os
import click

# used to tell Click that -h is shorthand for help
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# the types of value matching to use for finding columns to keep
match_types = ['exact',
               'starts',
               'ends',
               'contains',
               'greater',
               'less',
               ]


# individual functions go here
def get_values_to_match(values, file_flag):
  ''' Gets the values from file or text. '''
  match_values = []
  if file_flag == True:
    if not os.path.exists(values):
      click.echo('VALUES file {} not found. Use of --file-values flag requires values argument to be a valid file path.'.format(values))
      exit()
    else:
      match_values = [x.strip() for x in open(values).readlines()]
  else:
    match_values = values.split(',')
  return match_values

def get_column_index(col_idx, col_name, header, ignore_case, delim):
  ''' info ''' 
  if col_name == '':
    return col_idx
  else:
    try:
      header = header.lower().split(delim) if ignore_case else header.split(delim)
      return header.index(col_name)
    except:
      click.echo('ERROR: Column not found in header.')
      exit()

@click.command(context_settings=CONTEXT_SETTINGS)
# required arguments
@click.argument('in-file', type=click.File('r'), required=True)
@click.argument('values', type=str, required=True)
@click.argument('out-file', type=click.File('w'), required=True)

# optional arguments
@click.option('--delimiter', '-d', default='\t',
              help='Delimiter to use in the files. Default is TAB.')
@click.option('--column-index', '-x', default=0, type=int,
              help='Column index to use. Default is 0.')
@click.option('--column-name', '-n', default='',
              help='Find column by name. Takes precedence over --column-index.')
@click.option('--match', '-m', default='exact',
              type=click.Choice(match_types),
              help='The method used to match values. Default is "exact".')

# flags
@click.option('--file-values', '-f', is_flag=True,
              help='Read values as a file path.')
@click.option('--ignore-case', '-i', is_flag=True,
              help='Ignores letter case when searching and matching.')
@click.option('--verbose', is_flag=True,
              help='Enables information-dense terminal output.')

# other required arguments
@click.version_option(version='1.0.0')


# main entry point function
def cli(in_file, values, out_file,
        column_index, column_name, match, delimiter,
        verbose, ignore_case, file_values):
  ''' <Insert description of main process> 
  VALUES must be a file path (each value on a new line) or comma-separated values
  '''
  # first validate whether values are correct
  match_values = get_values_to_match(values, file_values)

  header = in_file.readline().strip()
  idx = get_column_index(column_index, column_name, header, ignore_case, delimiter)
  if verbose:
    click.echo('HEADER:')
    click.echo(header.split(delimiter))
    click.echo('COLUMN INDEX: {}'.format(idx))

  if verbose:
    click.echo('Matching rows containing: {}'.format(match_values))

  all_lines = []
  for line in in_file:

  


  

