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

from webotron.bucket import BucketManager
from webotron.domain import DomainManager
from webotron.certificate import CertificateManager
from webotron.cdn import DistributionManager

from pprint import pprint
from webotron import util

session = None
bucket_manager = None
domain_manager = None
cert_manager = None
dist_manager = None

@click.group()
@click.option('--profile', default=None,
    help="Use a given AWS profile.")
def cli(profile):
    """Webotron deploys websites to AWS."""
    global session, bucket_manager, domain_manager, cert_manager, dist_manager
    session_cfg = {}
    if profile:
        session_cfg['profile_name'] = profile

    session = boto3.Session(**session_cfg)
    bucket_manager = BucketManager(session)
    domain_manager = DomainManager(session)
    cert_manager = CertificateManager(session)
    dist_manager = DistributionManager(session)

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


@cli.command('setup-domain')
@click.argument('domain_name')
def setup_domain(domain_name):
    """Configure domain to point to bucket."""
    zone = domain_manager.find_hosted_zone(domain_name) \
            or domain_manager.create_hosted_zone(domain_name)
    # pprint(zone)

    # domain_name is same as bucket_name
    bucket = bucket_manager.get_bucket(domain_name)
    endpoint = util.get_endpoint(bucket_manager.get_region_name_for_bucket(bucket))
    a_record = domain_manager.create_s3_domain_record(zone, domain_name, endpoint)
    print("Domain Configured: http://{}".format(domain_name))
    # pprint(a_record)

@cli.command('find-cert')
@click.argument('domain_name')
def find_cert(domain_name):
    """Find certificate for the domain_name."""
    pprint(cert_manager.find_matching_cert(domain_name))

@cli.command('setup-cdn')
@click.argument('domain_name')
@click.argument('bucket_name')
def setup_cdn(domain_name, bucket_name):
    dist = dist_manager.find_matching_dist(domain_name)
    if not dist:
        cert = cert_manager.find_matching_cert(domain_name)
        if not cert:
            print("Error: No matching cert found")
            return
        dist = dist_manager.create_dist(domain_name, cert)
        print ('waiting for distribution deployment...')
        dist_manager.await_deploy(dist)

    zone = domain_manager.find_hosted_zone(domain_name) \
        or domain_manager.create_hosted_zone(domain_name)

    domain_manager.create_cf_domain_record(zone, domain_name, dist['DomainName'])
    print("Domain Configured: https://{}".format(domain_name))
    return


if __name__ == '__main__':
    cli()
