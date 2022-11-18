from os import getenv
import logging

from session import *

LOGLEVEL = getenv('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)

s = Session()
s.login(getenv('STUDENTID'), getenv('PASSWORD'))

places = list(map(str.strip, getenv('PLACES').split(',')))
logging.debug(f'places: {places}')

description = getenv('DESCRIPTION')
logging.debug(f'description: {description}')
