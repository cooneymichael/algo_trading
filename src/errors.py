################################################################################
#
# File:    errors.py
# Author:  Michael Cooney
# Purpose: Define errors here that will be used to signal problems without
#          crashing the program by raising an exception.
#
################################################################################

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
