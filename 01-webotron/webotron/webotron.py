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

import boto3
import click

from bucket import BucketManager

session = None
bucket_manager = None

@click.group()
@click.option('--profile', default=None,
    help="Use a given AWS profile.")
def cli(profile):
    """Webotron deploys websites to AWS."""
    global session, bucket_manager
    session_cfg = {}
    if profile:
        session_cfg['profile_name'] = profile

    session = boto3.Session(**session_cfg)
    bucket_manager = BucketManager(session)


@cli.command('list-buckets')
def list_buckets():
    """List all s3 buckets."""
    for bucket in bucket_manager.all_buckets():
        print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List objects in a S3 bucket."""
    for obj in bucket_manager.all_objects(bucket):
        print(obj)


@cli.command('setup-bucket')
@click.argument('bucketname')
def setup_bucket(bucketname):
    """Create and configure S3 bucket."""
    s3_bucket = bucket_manager.create_or_find(bucketname)
    if s3_bucket:
        bucket_manager.configure_public_read_access_for_bucket(s3_bucket)
        bucket_manager.configure_bucket_as_static_website(s3_bucket)


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucketname')
def sync(pathname, bucketname):
    """Sync contents of PATHNAME to BUCKET."""
    bucket_manager.sync(pathname, bucketname)
    print(bucket_manager.get_bucket_url(bucket_manager.S3.Bucket(bucketname)))


if __name__ == '__main__':
    cli()
