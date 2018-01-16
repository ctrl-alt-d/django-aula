import logging

from django.core.exceptions import SuspiciousOperation

class StopSuspiciousOperation(logging.Filter):
    def filter(self, record):
        es_SuspiciousOperation = False
        try:
            es_SuspiciousOperation = ( record.exc_info[0] == SuspiciousOperation )
        except:
            pass
        return not es_SuspiciousOperation