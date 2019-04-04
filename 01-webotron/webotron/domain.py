# -*- coding: utf-8 -*-

"""Classes for Route53 Domains."""

import uuid

class DomainManager:
    """Manage a Route53 domain."""

    def __init__(self, session):
        """Create domain manager object."""
        self.session = session
        self.client = session.client('route53')

    def find_hosted_zone(self, domain_name):
        """find the hosted zone for the domain name"""
        paginator = self.client.get_paginator('list_hosted_zones')
        for page in paginator.paginate():
            for zone in page['HostedZones']:
                if domain_name.endswith(zone['Name'][:-1]):
                    return zone
        return None

    # domain_name = "subdomain.kitttenweb.conwayrk.net"
    # zone_name = "conwayrk.net."
    def create_hosted_zone(self, domain_name):
        """Create a hosted zone for the domain name"""
        zone_name = '.'.join(domain_name.split('.')[-2:]) + '.'
        return self.client.create_hosted_zone(
            Name=zone_name,
            CallerReference=str(uuid.uuid4())
        )

    def create_s3_domain_record(self, zone, domain_name, endpoint):
        """create domain record in hosted zone, to point to s3 bucket."""
        return self.client.change_resource_record_sets(
            HostedZoneId=zone['Id'],
            ChangeBatch={
                'Comment': 'Created by Webotron',
                'Changes': [{
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': domain_name,
                        'Type': 'A',
                        'AliasTarget': {
                            'HostedZoneId': endpoint.zone,
                            'DNSName': endpoint.host,
                            'EvaluateTargetHealth': False
                        }
                    }
                }]
            }
        )
