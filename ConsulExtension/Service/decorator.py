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
    def wrapper(*args):
        try:
            method(*args)
        except Exception as e:
            logger.exception('Exception in {} : {}'.format(method.__name__, str(e)))
    return wrapper


# Decorators used in alchemy
def alchemy_commit_session(method):
    def wrapper(*args):
        try:
            method(*args)
        except Exception as e:
            logger.exception('error in {} : {}'.format(method.__name__, str(e)))
        finally:
            args[0].commit_session()  # here 0th argument is self so args[0].commit_session()
    return wrapper


def alchemy_read(method):
    def wrapper(*args):
        try:
            return method(*args)
        except Exception as e:
            logger.exception('error in {} : {}'.format(method.__name__, str(e)))
            return []
    return wrapper
