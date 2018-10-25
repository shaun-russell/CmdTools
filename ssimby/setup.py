from setuptools import setup

setup(
  name='ssimby',
  version='1.0.1',
  py_modules=['ssimby', 'ssimdata'],
  install_requires=['Click'],
  entry_points='''
    [console_scripts]
    ssimby=ssimby:cli
  '''
)