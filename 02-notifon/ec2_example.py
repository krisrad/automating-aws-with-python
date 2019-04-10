# coding: utf-8
import boto3
session = boto3.Session(profile_name='pythonAutomation')
ec2 = session.resource('ec2')
key_name = 'python_automation_key'
key_path = key_name + '.pem'
key_name = 'notifon_python_automation_key'
key_path = key_name + '.pem'
key = ec2.create_key_pair(KeyName=key_name)
key.key_material
with open(key_path, 'w') as key_file:
    key_file.write(key.key_material)

get_ipython().run_line_magic('save', 'ipysession.py 1-100')
get_ipython().run_line_magic('history', '')
get_ipython().run_line_magic('save', 'ipysession.py 1-100')
ec2.images.filter(Owners=['amazon'])
list(ec2.images.filter(Owners=['amazon']))
len(list(ec2.images.filter(Owners=['amazon'])))
img = ec2.Image('ami-02bcbb802e03574ba')
img
img.Name
img.name
img.name
ec2_apse2 = session.resource('ec2', region_name='ap-southeast-2')
img_apse2 = ec2_apse2.Image('ami-02bcbb802e03574ba')
img_apse2.name
img.name
ami_name = 'amzn2-ami-hvm-2.0.20190313-x86_64-gp2'
filters = [{'Name':'name', 'Values':[ami_name]}]
list(ec2.images.filter(Owners=['amazon'], Filters=filters))
list(ec2_apsec2.images.filter(Owners=['amazon'], Filters=filters))
list(ec2_apse2.images.filter(Owners=['amazon'], Filters=filters))
get_ipython().run_line_magic('save', 'ipysession.py 1-500')
instances = ec2.create_instances(ImageId=img.id, MinCount=1, MaxCount=1, InstanceType='t2.micro', KeyName=key.key_name)
instances
inst = instances[0]
inst
inst.terminate()
instances = ec2.create_instances(ImageId=img.id, MinCount=1, MaxCount=1, InstanceType='t2.micro', KeyName=key.key_name)
inst = instances[0]
inst
inst.public_dns_name
inst.public_dns_name
inst.public_dns_name
inst.wait_until_running()
inst.reload()
inst.public_dns_name
inst.security_groups
sec_group = inst.security_groups[0]
sec_group
sec_group.group_name
sec_group['group_name']
sec_grp_id = sec_group['GroupId']
sec_grp_id
sec_grp = ec2.SecurityGroup(sec_grp_id)
sec_grp
sec_grp.group_name
sec_grp.ip_permissions
sec_grp.ip_permissions_egress
sg = ec2.SecurityGroup(inst.security_groups[0]['GroupId'])
sg
sg.authorize_ingress(IpPermissions=[{'FromPort':22, 'ToPort':22, 'IpProtocol':'TCP', 'IpRanges':[{'CidrIp':'115.249.63.129/32'}]}])
inst
inst.public_ip_address
inst.private_ip_address
sg.authorize_ingress(IpPermissions=[{'FromPort':80, 'ToPort':80, 'IpProtocol':'TCP', 'IpRanges':[{'CidrIp':'115.249.63.129/32'}]}])
get_ipython().run_line_magic('save', 'ipysession.py 1-500')
get_ipython().run_line_magic('save', 'ec2_example.py 1-66')
