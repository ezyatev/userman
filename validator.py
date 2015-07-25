import re
import sys

sys.tracebacklimit = 0


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


class DomainName(Validator):
    @staticmethod
    def validate(string):
        match = re.match('^([a-z0-9-]+\.)*[a-z0-9-]+\.[a-z]+$', string)
        if match:
            return True
        raise Exception('Incorrect domain name.')
