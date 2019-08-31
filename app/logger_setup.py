'''
logger_setup.py customizes the app's logging module. Each time an event is
logged the logger checks the level of the event (eg. debug, warning, info...).
If the event is above the approved threshold then it goes through. The handlers
do the same thing; they output to a file/shell if the event level is above their
threshold.
:Example:
        >>> from website import logger
        >>> logger.info('event', foo='bar')
**Levels**:
        - logger.debug('For debugging purposes')
        - logger.info('An event occured, for example a database update')
        - logger.warning('Rare situation')
        - logger.error('Something went wrong')
        - logger.critical('Very very bad')
You can build a log incrementally as so:
        >>> log = logger.new(date='now')
        >>> log = log.bind(weather='rainy')
        >>> log.info('user logged in', user='John')
'''

import datetime as dt
import logging
from logging.handlers import RotatingFileHandler
import pytz

from flask import request, session
from structlog import wrap_logger
from structlog.processors import JSONRenderer, KeyValueRenderer
from flask_login import current_user
from app import app
import sys

# Set the logging level
app.logger.setLevel(app.config['LOG_LEVEL'])

# the stdout handler is by default
app.logger.addHandler(logging.StreamHandler())

TZ = pytz.timezone(app.config['TIMEZONE'])


def add_fields(_, level, event_dict):
    ''' Add custom fields to each record. '''
    now = dt.datetime.now()
    event_dict['timestamp'] = TZ.localize(now, True).astimezone(pytz.utc).isoformat()
    event_dict['level'] = level

    if session:
        event_dict['session_id'] = session.get('_id')
        if current_user.is_authenticated:
            event_dict['logged_in'] = current_user.email
        else:
            event_dict['logged_in'] = 'none'

    if request:
        try:
            event_dict['ip_address'] = request.headers['Host'].split(':')[0].strip()
        except:
            event_dict['ip_address'] = 'unknown'

    return event_dict


# Add a handler to write log messages to a file
if app.config.get('LOG_FILENAME'):
    file_handler = RotatingFileHandler(filename=app.config['LOG_FILENAME'],
                                       maxBytes=app.config['LOG_MAXBYTES'],
                                       backupCount=app.config['LOG_BACKUPS'],
                                       mode='a',
                                       encoding='utf-8')
    #file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)

# Wrap the application logger with structlog to format the output
logger = wrap_logger(
    app.logger,
    processors=[
        add_fields,
        #KeyValueRenderer(sort_keys=True, key_order=None, drop_missing=False, repr_native_str=True)
        JSONRenderer(sort_keys=False)
    ]
)
