import setuptools

import os

thelibFolder = os.path.dirname(os.path.realpath(__file__))

requirementPath = thelibFolder + '/requirements.txt'
install_requires = [] # Examples: ["gunicorn", "docutils>=0.3", "lxml==0.5a7"]
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

setuptools.setup(
    name="MA_Backtester",
    version="0.0.1",
    author="Alexandre MARTINS",
    author_email="alexandre.martins-f@outlook.com",
    url="https://github.com/MartinsAlex/MA_Backtester",
    packages=['MA_Backtester'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
    install_requires=install_requires,
    package_data={'MA_Backtester': ['tickerLists/*.csv']}
)
