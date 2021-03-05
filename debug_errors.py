"""
Raising exceptions
"""
class Error(Exception):
    pass

class UnsupportedFormat(Error):
    """Input is not .json or .csv"""
    pass