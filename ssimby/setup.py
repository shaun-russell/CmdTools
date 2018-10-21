from setuptools import setup

setup(
  name='ssimby',
  version='1.0',
  py_modules=['ssimby'],
  install_requires=['Click'],
  entry_points='''
    [console_scripts]
    ssimby=ssimby:cli
  '''
)