#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Webotron: Deploy websites with AWS.

Webotron automates the process of deploying static websites to AWS
- Configure AWS buckets
  - Create them
  - Set them up for static website hosting
  - Deploy local files to them
- Configure DNS with AWS Route53
- Configure a content delivery network and SSL with AWS CDN
"""

from pathlib import Path
import mimetypes
import boto3
from botocore.exceptions import ClientError
import click

SESSION = boto3.Session(profile_name='pythonAutomation')
S3 = SESSION.resource('s3')


@click.group()
def cli():
    """Webotron deploys websites to AWS."""
    pass


@cli.command('list-buckets')
def list_buckets():
    """List all s3 buckets."""
    for bucket in S3.buckets.all():
        print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List objects in a S3 bucket."""
    for obj in S3.Bucket(bucket).objects.all():
        print(obj)


@cli.command('setup-bucket')
@click.argument('bucketname')
def setup_bucket(bucketname):
    """Create and configure S3 bucket."""
    s3_bucket = None

    try:
        s3_bucket = createS3Bucket(bucketname)
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            s3_bucket = S3.Bucket(bucketname)
        else:
            raise e

    if s3_bucket:
        configurePublicReadAccessForS3Bucket(s3_bucket)
        configureS3BucketAsStaticWebsite(s3_bucket)

    return


def createS3Bucket(s3BucketName):
    """Create S3 Bucket."""
    return S3.create_bucket(
        Bucket=s3BucketName,
        CreateBucketConfiguration={
            'LocationConstraint': SESSION.region_name
        }
    )


def configurePublicReadAccessForS3Bucket(s3Bucket):
    """Configure Public Read Access for S3 Bucket."""
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
    """Configure S3 bucket to host static website."""
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


def upload_file(s3_bucket, path, key):
    """Upload file from path to s3 bucket."""
    content_type = mimetypes.guess_type(key)[0] or 'text/plain'
    s3_bucket.upload_file(
        path,
        key,
        ExtraArgs={
            'ContentType': content_type
        })


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucketname')
def sync(pathname, bucketname):
    """Sync contents of PATHNAME to BUCKET."""
    s3_bucket = S3.Bucket(bucketname)

    root = Path(pathname).expanduser().resolve()

    def handle_directory(target):
        for p in target.iterdir():
            if p.is_dir():
                handle_directory(p)
            if p.is_file():
                upload_file(s3_bucket, str(p), str(p.relative_to(root)))

    handle_directory(root)


if __name__ == '__main__':
    cli()
