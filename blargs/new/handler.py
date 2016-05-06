from __future__ import print_function

import json
import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)

import sys, os

here = os.path.dirname(os.path.realpath(__file__))
log.debug( 'here: %s' % here)

sys.path.append(os.path.join(here, "../binaries"))
sys.path.append(os.path.join(here, "../shared"))
sys.path.append(os.path.join(here, "../vendored"))
sys.path.append(os.path.join(here, "../../binaries"))
sys.path.append(os.path.join(here, "../../shared"))
sys.path.append(os.path.join(here, "../../vendored"))
log.debug( 'sys.path: %s' % sys.path)

import environments, gorms, nasons, units

def handler(event, context):
    log.debug("Received event {}".format(json.dumps(event)))
    return {}
