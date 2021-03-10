"""
Raising exceptions
"""
class Error(Exception):
    pass

class UnsupportedFormat(Error):
    """Input is not .json or .csv"""
    pass

class TweepyApiError(Error):
    """Cannot connect to Twitter API. Please enter credentials"""
    pass
class NoCredentialsFound(Error):
    """Cannot load Twitter API Credentials. Check .env file"""
    pass
class StreamError(Error):
    """Something went wrong during stream processing. To skip this error, set skip_error=True"""
    pass