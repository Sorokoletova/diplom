import logging


class HealthCheckFilter(logging.Filter):
    def filter(self, record):
        return record.getMessage().find('/ping/') == -1
