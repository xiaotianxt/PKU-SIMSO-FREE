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

# s.save_request(exen_type='一事一议的必要事项（就业、科研、学业等）', track='自行车',
#                description='两点一线前往学校科研', start='万柳园区', end='燕园', zdxm='南门', delta=1)


print(prettify(s.get_latest()))
