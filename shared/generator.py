import logging
from troposphere import Ref, Template, Tags, Join, Output
from troposphere.ec2 import SecurityGroup
from troposphere.sns import Topic
from troposphere.s3 import Bucket, Private
from troposphere.elasticbeanstalk import (
    Application, ApplicationVersion, ConfigurationTemplate, Environment,
    SourceBundle, OptionSettings
)

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel(logging.INFO)

def name_tag(suffix):
    return Tags(Name=Join('-', [Ref('AWS::StackName'), suffix]))

def generate_application_template(app_dict):
    app_name = app_dict['app_name']

    t = Template()
    t.add_version()
    t.add_description('app template for %s' % app_name)

    app = Application(app_name, Description=app_name)
    t.add_resource(app)

    bucket_name = 'ehi-pcf-%s' % app_name
    bucket = Bucket('AppBucket', BucketName=bucket_name, AccessControl=Private)
    t.add_resource(bucket)

    return t.to_json()

def generate_env_template(app_env, env_dict):
    sg_name = env_dict['sg_name']
    vpc_id = 'vpc-a1d187c4'  # query for this!
    logger.debug('generating template for %s' % vpc_id)
    
    t = Template()
    t.add_version('2010-09-09')
    t.add_description('env template for %s' % app_env)
    app_sg = SecurityGroup('TestAppSecurityGroup')
    app_sg.VpcId = vpc_id
    app_sg.GroupDescription = 'testing'
    app_sg.Tags = name_tag(sg_name)
    t.add_resource(app_sg)
    return t.to_json()

