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

import ansible.inventory
import ansible.playbook
import ansible.runner
import ansible.constants
from ansible import utils
from ansible import callbacks

import environments, gorms, nasons, units

def handler(event, context):
    log.debug("Received event {}".format(json.dumps(event)))
    return main()

  
def run_playbook(**kwargs):

    stats = callbacks.AggregateStats()
    playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
    runner_cb = callbacks.PlaybookRunnerCallbacks(
        stats, verbose=utils.VERBOSITY)
    
    # use /tmp instead of $HOME
    ansible.constants.DEFAULT_REMOTE_TMP = '/tmp/ansible'

    out = ansible.playbook.PlayBook(
        callbacks=playbook_cb,
        runner_callbacks=runner_cb,
        stats=stats,
        **kwargs
    ).run()

    return out


def main():
    out = run_playbook(
        playbook='playbook.yml',
        inventory=ansible.inventory.Inventory(['localhost'])
    )
    return(out)


if __name__ == '__main__':
    main()