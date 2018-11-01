''' Proggy to do basic learning of thingies in the terminal. '''

import click
import random

# used to tell Click that -h is shorthand for help
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

class QAItem():
  def __init__(self, string, ignore_case):
    stringsplit = string.split(',')

    self.question = stringsplit[0]

    if ignore_case:
      self.answers = stringsplit[1].lower().split(';')
    else:
      self.answers = stringsplit[1].split(';')

    if len(stringsplit) > 2:
      self.details = stringsplit[2]
    else:
      self.details = ''

def display_question(question):
  click.clear()
  click.echo('QUESTION:')
  click.echo('  ' + question)

def display_answer(answers, user_answer, details):
  if user_answer not in answers:
    click.echo(click.style('  Incorrect. Correct answers: {}'.format(', '.join(answers)), fg='white', bg='red'))
  else:
    click.echo(click.style('  Correct!', bg='green', fg='white'))
  click.echo(details)

# START CLI COMMANDS
@click.command(context_settings=CONTEXT_SETTINGS)
# required arguments
@click.argument('in-file', type=click.File('r'), required=True)

# optional arguments
@click.option('--ignore-case', '-i', is_flag=True,
              help='Ignores letter case when searching and matching.')
# other required arguments
@click.version_option(version='1.0.0')

# main entry point function
def cli(in_file, ignore_case):
  qas = []
  for line in in_file:
    if len(line) < 4 or line.startswith('%'):
      continue
    qas.append(QAItem(line.strip(), ignore_case))
  while True:
    random.shuffle(qas)

    for item in qas:
      display_question(item.question)
      user_answer = input('  > ')

      if ignore_case:
        user_answer = user_answer.lower()

      display_answer(item.answers, user_answer, item.details)
      input('\nContinue...')
    keep_going = input('No more questions. Replay? (y/n) ')
    if keep_going.lower().startswith('y'):
      continue
    else:
      break
  click.echo('Finished now.')

  