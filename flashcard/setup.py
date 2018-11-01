from setuptools import setup

setup(
  name='flashcard',
  version='1.0.0',
  py_modules=['flashcard'],
  install_requires=['Click'],
  entry_points='''
    [console_scripts]
    flashcard=flashcard:cli
  '''
)