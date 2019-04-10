# coding: utf-8
import boto3
session = boto3.Session(profile_name='pythonAutomation')
ec2 = session.resource('ec2')
key_name = 'notifon_python_automation_key'
img = ec2.Image('ami-02bcbb802e03574ba')
instances = ec2.create_instances(ImageId=img.id, MinCount=1, MaxCount=1, InstanceType='t2.micro', KeyName=key_name)
inst = instances[0]
sg = ec2.SecurityGroup(inst.security_groups[0]['GroupId'])
# sg.authorize_ingress(IpPermissions=[{'FromPort':22, 'ToPort':22, 'IpProtocol':'TCP', 'IpRanges':[{'CidrIp':'115.249.63.129/32'}]}])
# sg.authorize_ingress(IpPermissions=[{'FromPort':80, 'ToPort':80, 'IpProtocol':'TCP', 'IpRanges':[{'CidrIp':'115.249.63.129/32'}]}])
inst.wait_until_running()
inst.reload()
inst.public_dns_name
inst.public_ip_address
inst.private_ip_address
