import logging


class CustomLogger(object):
    """ Class for custom logger"""
    __logger = None

    @classmethod
    def get_logger(cls, path):
        """ Method returns logger for specified path """
        if cls.__logger is None:
            cls.__logger = CustomLogger.__get_logger(path)
        return cls.__logger

    @staticmethod
    def __get_logger(path):
        """ Method returns logger with custom configurations """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # create a file handler
        handler = logging.FileHandler(path)
        handler.setLevel(logging.DEBUG)

        # create a logging format
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s:%(lineno)d - %(message)s')
        handler.setFormatter(formatter)

        # add the handlers to the logger
        logger.addHandler(handler)

        return logger
