from __future__ import print_function

import boto3
import hashlib
import json
import logging
import math
import os
import sys
import time

ENV_CONFIG_FILENAME = 'environment.json'
PWD = os.environ['LAMBDA_TASK_ROOT']
REGION = os.environ['AWS_REGION']
CFN_STACK_NOTIFICATION_TOPIC_ARNS = ['arn:aws:sns:us-east-1:368307275692:BlargotronMain']

log = logging.getLogger()
log.setLevel(logging.DEBUG)

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
from generator import generate_env_template
from generator import generate_application_template
from util import get_uuid

dynamodb = boto3.resource('dynamodb')

def equal_dicts(d1, d2):
    return dict_hash(d1) == dict_hash(d2)

def dict_hash(dictionary):
    dict = json.dumps(dictionary, sort_keys=True, indent=None)
    return hashlib.md5(dict.encode()).hexdigest()

def apply_template(stack_name, template_body, notify=False, wait=False):
    ''' create or update the stack '''

    client = boto3.client('cloudformation', REGION)
    
    # TODO: handle multiple "pages" of stacks via NextToken parameter
    log.debug('searching for existing stack')
    stack_filter = ['CREATE_COMPLETE', 'ROLLBACK_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE']
    stacks = client.list_stacks(StackStatusFilter=stack_filter)['StackSummaries']
    stacks = filter(lambda s: s['StackName'] == stack_name, stacks)
    
    if stacks:
        # find out if the current stack is already updated
        response = client.get_template(StackName=stack_name)
        current_json = response['TemplateBody']

        if equal_dicts(current_json, json.loads(template_body)):
            log.info('stack up to date: %s' % stack_name)
        else:
            log.info('updating stack: %s' % stack_name)
            client.update_stack(StackName=stack_name, TemplateBody=template_body,
                                NotificationARNs=CFN_STACK_NOTIFICATION_TOPIC_ARNS)
            if wait:
                log.info('waiting for update to complete...')
                waiter = client.get_waiter('stack_update_complete')
                waiter.wait(StackName=stack_name)
    else:
        log.info('creating stack: %s' % stack_name)
        client.create_stack(StackName=stack_name, TemplateBody=template_body,
                            NotificationARNs=CFN_STACK_NOTIFICATION_TOPIC_ARNS)
        if wait:
            log.info('waiting for create to complete...')
            waiter = client.get_waiter('stack_create_complete')
            waiter.wait(StackName=stack_name)


def handler(event, context):
    log.debug("Received event {}".format(json.dumps(event)))
    
    if "Records" in event:
        # from SNS/CFN
        snsData = json.loads(event["Records"][0]["Sns"]["Message"]["message"])
        log.debug("From SNS: %s" % snsData)
        message = snsData["message"]
    else:
        # from APIG or CLI call
        if "httpMethod" in event:
            log.debug("Context: %s" % event['httpMethod'])
            if event["httpMethod"] == "POST":
                # create
                #env_name = event['params']['path']['envname']
                env_name = "dev"
                
                config_path = os.path.join(here, ENV_CONFIG_FILENAME)
                with open(config_path) as json_file:
                    config_dict = json.load(json_file)
                env_dict = config_dict[env_name]
                app_name = config_dict['app_name']
                app_env = '%s-%s' % (app_name, env_name)

                table = dynamodb.Table('BlargotronJobs')
                jobId = get_uuid()
                timestamp = int(time.time())
                log.debug("timestamp: %s" % timestamp)
                table.put_item(
                    Item={
                        'jobId': jobId,
                        'timestamp': timestamp,
                        'env_name': env_name,
                        'steps': [
                            {
                                'name': 'createEnvironment',
                                'template': ENV_CONFIG_FILENAME,
                                'status': 'WAITING'
                            },
                            {
                                'name': 'deployBeanstalkApp',
                                'template': 'ebapp.json',
                                'status': 'WAITING'
                            }
                        ]
                    }
                )

                # now, actually do work
                template_body = generate_application_template(config_dict)
                apply_template(app_name, template_body, wait=True)
#
#                template_body = generate_env_template(app_env, env_dict)
#                apply_template(app_env, template_body, notify=True)


                
            elif event["httpMethod"] == "PUT":
                # update
                log.debug("APIG call: PUT")
        else:
            # CLI call
            log.debug("CLI call")

    return {}
