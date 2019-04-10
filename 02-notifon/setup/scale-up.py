import boto3
session = boto3.Session(profile_name='pythonAutomation')
as_client = session.client('autoscaling')
as_client.execute_policy(AutoScalingGroupName='notifon-example-group',PolicyName='Scale Up')
