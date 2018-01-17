import logging

from django.core.exceptions import SuspiciousOperation

class StopSuspiciousOperation(logging.Filter):
    def filter(self, record):
        if record.exc_info:
            exc_value = record.exc_info[1]
            return isinstance(exc_value, SuspiciousOperation)
        return True

