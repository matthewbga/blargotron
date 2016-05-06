import json
import os
import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)

here = os.path.dirname(os.path.realpath(__file__))
log.info( 'You have successfully included %s: %s' % (__file__, here))
