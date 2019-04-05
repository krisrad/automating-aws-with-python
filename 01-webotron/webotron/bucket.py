# -*- coding: utf-8 -*-

"""Classes for S3 Buckets."""

import boto3
import mimetypes
from pathlib import Path, PurePosixPath
from botocore.exceptions import ClientError
from webotron import util
from hashlib import md5
from pprint import pprint
from functools import reduce

class BucketManager:
    """Manage an S3 Bucket."""

    CHUNK_SIZE = 8388608

    def __init__(self, session):
        """Create a BucketManager Object."""
        self.S3 = session.resource('s3')
        self.REGION_NAME = session.region_name
        self.transfer_config = boto3.s3.transfer.TransferConfig(
            multipart_chunksize = self.CHUNK_SIZE,
            multipart_threshold = self.CHUNK_SIZE
        )
        self.manifest = {}
        self.uploaded_files = []
        pass

    def get_bucket(self, bucket_name):
        """Get a bucket by name."""
        return self.S3.Bucket(bucket_name)

    def get_region_name_for_bucket(self, bucket):
        """Get the bucket's region name"""
        bucket_location = self.S3.meta.client.get_bucket_location(Bucket=bucket.name)
        return bucket_location["LocationConstraint"] or 'us-east-1'

    def get_bucket_url(self, bucket):
        """Get the website URL  for this bucket"""
        reg_name = self.get_region_name_for_bucket(bucket)
        return "http://{}.{}".format(bucket.name, util.get_endpoint(reg_name).host)

    def all_buckets(self):
        """Get an iterator for all buckets."""
        return self.S3.buckets.all()

    def all_objects(self, bucketname):
        """Get an iterator for all objects in a bucket"""
        return self.S3.Bucket(bucketname).objects.all()

    def create_or_find(self, bucketname):
        """Creates a new or gets an existing bucket."""
        s3_bucket = None
        try:
            s3_bucket = self.S3.create_bucket(
                Bucket=bucketname,
                CreateBucketConfiguration={
                    'LocationConstraint': self.REGION_NAME
                }
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                s3_bucket = self.S3.Bucket(bucketname)
            else:
                raise e
        return s3_bucket

    def configure_public_read_access_for_bucket(self, bucket):
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
        """ % bucket.name
        bucket.Policy().put(Policy=policy.strip())

    def configure_bucket_as_static_website(self, bucket):
        """Configure S3 bucket to host static website."""
        wsc = {
            'ErrorDocument': {
                'Key': 'error.html'
            },
            'IndexDocument': {
                'Suffix': 'index.html'
            }
        }
        bucket.Website().put(WebsiteConfiguration=wsc)

    def load_manifest(self, bucket):
        """Load manifest for caching purposes"""
        pagninator = self.S3.meta.client.get_paginator('list_objects_v2')
        for page in pagninator.paginate(Bucket=bucket.name):
            for obj in page.get('Contents', []):
                self.manifest[obj['Key']] = obj['ETag']
                # pprint(obj)

    @staticmethod
    def hash_data(data):
        """Generate md5 hash for data."""
        hash = md5()
        hash.update(data)
        return hash

    def gen_etag(self, path):
        """Generate etag for file."""
        hashes = []

        with open(path, 'rb') as f:
            while True:
                data = f.read(self.CHUNK_SIZE)
                if not data:
                    break
                hashes.append(self.hash_data(data))

        if not hashes:
            return
        elif len(hashes) == 1:
            return '"{}"'.format(hashes[0].hexdigest())
        else:
            hash = self.hash_data(reduce(lambda x,y: x+y, (h.digest() for h in hashes)))
            return '"{}-{}"'.format(hash.hexdigest(), len(hashes))

    def upload_file(self, bucket, path, key):
        """Upload file from path to s3 bucket."""
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'

        self.uploaded_files.append(key)

        etag = self.gen_etag(path)
        if self.manifest.get(key, '') == etag:
            print("Skippin {}, etags match".format(key))
            return

        return bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType': content_type
            },
            Config = self.transfer_config)

    def delete_files(self, bucket):
        """Remove files in S3, that were deleted locally."""
        for k in self.manifest:
            if k not in self.uploaded_files:
                print("deleting object {}".format(k))
                bucket.delete_objects(Delete={
                    'Objects': [{'Key':k}]
                })

    def sync(self, pathname, bucketname):
        """sync pathname to bucket."""
        bucket = self.S3.Bucket(bucketname)
        self.load_manifest(bucket)
        # pprint(self.manifest)

        root = Path(pathname).expanduser().resolve()

        def handle_directory(target):
            for p in target.iterdir():
                if p.is_dir():
                    handle_directory(p)
                if p.is_file():
                    self.upload_file(
                        bucket,
                        str(p),
                        str(PurePosixPath(p.relative_to(root)))
                    )
                    # print(str(p), str(PurePosixPath(p.relative_to(root))))
        handle_directory(root)
        self.delete_files(bucket)
