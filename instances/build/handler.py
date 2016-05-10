from __future__ import print_function

import json
import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)

import sys, os

here = os.path.dirname(os.path.realpath(__file__))
log.debug( 'here: %s' % here)

# Add function-specific binaries and libs in path
sys.path.append(os.path.join(here, "../binaries"))
sys.path.append(os.path.join(here, "../shared"))
sys.path.append(os.path.join(here, "../vendored"))

# Add top level binaries and libs in path
sys.path.append(os.path.join(here, "../../binaries"))
sys.path.append(os.path.join(here, "../../shared"))
sys.path.append(os.path.join(here, "../../vendored"))
log.debug( 'sys.path: %s' % sys.path)

import environments, gorms, nasons, units
#import ansible, packer

def handler(event, context):
    log.debug("Received event {}".format(json.dumps(event)))
    os.system("%s/instances/binaries/packer build ami.json" % os.environ["LAMBDA_TASK_ROOT"])
    return {}
