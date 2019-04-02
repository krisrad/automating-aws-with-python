import boto3
import click
from botocore.exceptions import ClientError

session = boto3.Session(profile_name='pythonAutomation')
s3 = session.resource('s3')

@click.group()
def cli():
    "Webotron deploys websites to AWS"
    pass

@cli.command('list-buckets')
def list_buckets():
    "List all s3 buckets"
    for bucket in s3.buckets.all():
        print (bucket)

@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    "List objects in a S3 bucket"
    for obj in s3.Bucket(bucket).objects.all():
        print (obj)

@cli.command('setup-bucket')
@click.argument('bucketname')
def setup_bucket(bucketname):
    "Create and configure S3 bucket"

    s3_bucket = None

    try:
        s3_bucket = createS3Bucket(bucketname)
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            s3_bucket = s3.Bucket(bucketname)
        else:
            raise e

    if s3_bucket:
        configurePublicReadAccessForS3Bucket(s3_bucket)
        configureS3BucketAsStaticWebsite(s3_bucket)

    return

def createS3Bucket(s3BucketName):
    return s3.create_bucket(
        Bucket=s3BucketName,
        CreateBucketConfiguration={
            'LocationConstraint': session.region_name
        }
    )

def configurePublicReadAccessForS3Bucket(s3Bucket):
    policy = """
    {
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::%s/*"
            ]
        }]
    }
    """ % s3Bucket.name
    policy = policy.strip()
    pol = s3Bucket.Policy()
    pol.put(Policy=policy)
    return

def configureS3BucketAsStaticWebsite(s3Bucket):
    ws = s3Bucket.Website()
    ws.put(WebsiteConfiguration={
        'ErrorDocument': {
            'Key': 'error.html'
        },
        'IndexDocument': {
            'Suffix': 'index.html'
        }
    })
    return

if __name__=='__main__':
    cli()
