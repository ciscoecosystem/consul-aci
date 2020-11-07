"""A utility for all the decorators"""

import datetime
from custom_logger import CustomLogger

logger = CustomLogger.get_logger("/home/app/log/app.log")


def time_it(method):
    """Decorator function to log time taken by function

    Arguments:
        method function -- function for which we want to measure time
    """

    def timed(*args, **kw):
        start_time = datetime.datetime.now()
        result = method(*args, **kw)
        end_time = datetime.datetime.now()
        logger.info("Time for ACI {} is {}: ".format(method.__name__, str(end_time - start_time)))
        return result
    return timed


def exception_handler(method):
    """Handle exception

    Args:
        method {func}: function on which wrapper added
    """
    def wrapper(*args):
        """Wrapper method
        """
        try:
            method(*args)
        except Exception as e:
            logger.exception('Exception in {} : {}'.format(method.__name__, str(e)))
    return wrapper


# Decorators used in alchemy
def alchemy_commit_session(method):
    """Commmit alchemy data into db

    Args:
        method (func): function on which wrapper added
    """
    def wrapper(*args):
        """Wrapper method
        """
        try:
            method(*args)
        except Exception as e:
            logger.exception('error in {} : {}'.format(method.__name__, str(e)))
        finally:
            args[0].commit_session()  # here 0th argument is self so args[0].commit_session()
    return wrapper


def alchemy_read(method):
    """Read alchemy from db

    Args:
        method (func): function on which wrapper added
    """
    def wrapper(*args):
        """Wrapper method

        Returns:
            {func/list}: if no exception then method else empty list
        """
        try:
            return method(*args)
        except Exception as e:
            logger.exception('error in {} : {}'.format(method.__name__, str(e)))
            return []
    return wrapper
