''' Tool for extracting lines out of files. '''

# The functions of this could be done using awk or perl commands, but on
# Windows that relies on cygwin (which I have, but it's more convenient
# to have a python script I can edit and add more functions to (+ portable)

import click

@click.group()
def cli():
  pass

@cli.command()
@click.option('--mungo', default='',
              help='Provide a mungo rank.')
@click.option('--repeat', default=0, type=int,
              help='How many mungo messages to show.')
@click.argument('out', type=click.File('w'), default='-', required=False)
def rat(mungo, repeat, out):
  ''' This script is mungo-enabled. '''
  click.echo('This is filefilter')
  if mungo != '':
    click.echo('Mungo was empowered to reach {} status.'.format(mungo))
  if repeat > 0:
    for x in range(0,repeat):
      click.echo('Levelling...')
    else:
      click.echo('Empowered!')
