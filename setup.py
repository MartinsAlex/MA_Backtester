from setuptools import setup

setup(
   name='foo',
   version='1.0',
   description='A useful module',
   author='Man Foo',
   author_email='foomail@foo.com',
   packages=['scripts'],  #same as name
   install_requires=['matplotlib', 'pandas', "numpy", "pandas-datareader"], #external packages as dependencies
   scripts=[
            'MA_Backtester.py'
           ]
)
