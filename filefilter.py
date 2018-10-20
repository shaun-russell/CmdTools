''' Tool for extracting lines out of files. '''

# The functions of this could be done using awk or perl commands, but on
# Windows that relies on cygwin (which I have, but it's more convenient
# to have a python script I can edit and add more functions to (+ portable)

import click

@click.command()
# required arguments
@click.argument('output-file', type=click.File('w'), default='-', required=False)

# optional arguments
@click.option('--column-index', default=0, type=int,
              help='Column index to use, default is 0.')
@click.option('--column-name', default='',
              help='Find index of column name in header.')

# flags
@click.option('--verbose', is_flag=True,
              help='Enables information-dense terminal output.')
@click.option('--ignore-case', is_flag=True,
              help='Ignores letter case when searching and matching.')
def cli(verbose, ignore_case):
  ''' Documentation for process. '''
  pass

