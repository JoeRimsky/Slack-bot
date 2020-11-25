#!/usr/bin/python3
import logging, time

levels_dict = {
    "INFO": logging.INFO,
    "WARNGING": logging.WARNING,
    "ERROR": logging.ERROR
}

class Logger:
    def __init__(self, log, file_name):
        self.logger = logging.getLogger(log)
        self.handler = logging.FileHandler(file_name)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)

    def log_data(self, username, message, data, level):
        now = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        self.logger.log(levels_dict[level], f"{now} : {username} : {message} : {data}")