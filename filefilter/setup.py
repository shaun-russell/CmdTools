from setuptools import setup

setup(
  name='FileFilter',
  version='1.0',
  py_modules=['filefilter'],
  install_requires=['Click'],
  entry_points='''
    [console_scripts]
    filefilter=filefilter:cli
  '''
)