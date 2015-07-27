r"""simple regular expression based validator for the strings

This script provides simple validation.

"""

import re

__author__ = "Eugene L. Zyatev"
__copyright__ = "Copyright 2015, The Userman Project"
__license__ = "GPL"
__version__ = "1.0.1"
__email__ = "eu@f1dev.com"


class Validator(object):
    @staticmethod
    def validate(string):
        return NotImplementedError('You should to implement the validate() method.')


class User(Validator):
    @staticmethod
    def validate(string):
        match = re.match('[a-z_]+', string)
        if match:
            return True
        raise Exception('Incorrect username.')


class DBName(Validator):
    @staticmethod
    def validate(string):
        match = re.match('[a-z_]+', string)
        if match:
            return True
        raise Exception('Incorrect database name.')


class DomainName(Validator):
    @staticmethod
    def validate(string):
        match = re.match('^([a-z0-9-]+\.)*[a-z0-9-]+\.[a-z]+$', string)
        if match:
            return True
        raise Exception('Incorrect domain name.')
