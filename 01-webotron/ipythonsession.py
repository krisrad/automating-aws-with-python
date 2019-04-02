# coding: utf-8
import boto3
session = boto3.Session(profile_name='pythonAutomation')
s3 = session.resource('s3')
for bucket in s3.buckets.all():
    print (bucket)
    
'test'
ec2_client = session.client('ec2')
get_ipython().run_line_magic('history', '')
get_ipython().run_line_magic('save', 'ipythonsession.py')
get_ipython().run_line_magic('save', 'ipythonsession.py 1-10')
