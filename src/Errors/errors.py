################################################################################
#
# File:    errors.py
# Author:  Michael Cooney
# Purpose: Define errors here that will be used to signal problems without
#          crashing the program by raising an exception.
#
################################################################################

from dataclasses import dataclass


class Error():
    def __init__(self, message):
        self.message = message

    def __str__(self):
        # print(f'{self.error_type}: {self.message}')
        raise NotImplementedError('Child error class needs to implement this method')


class NoNewDataError(Error):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        print(f'NoNewDataError: f{self.message}')

        
class InvalidDateFormatError(Error):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        print(f'InvalidDateFormatError: f{self.message}')


class FailedConnectionException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        print(f'FailedConnectionException: f{self.message}')


class FailedDisconnectException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        print(f'FailedDisconnectException: f{self.message}')


class FailedCursorOpenException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        print(f'FailedCursorOpenException: f{self.message}')


class FailedCursorCloseException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        print(f'FailedCursorCloseException: f{self.message}')
