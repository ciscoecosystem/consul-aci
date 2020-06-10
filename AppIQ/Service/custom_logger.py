import os
import logging


class CustomLogger(object):
    __logger = None

    @classmethod
    def get_logger(cls, path):
        if cls.__logger == None:
            cls.__logger = CustomLogger.__get_logger(path)
        return cls.__logger


    @staticmethod
    def __get_logger(path):
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
