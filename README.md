# Automating AWS with Python
Repository for automating aws with python

## 01-webotron

Webotron is a script that will sync a local directory to an s3 bucket and optionally configure Route53 and cloudfront as well

### Features
Webotron currently has the following features:

- List bucket
- List content of a bucket
- Create and Setup Bucket
- Sync directory tree to bucket
- Set AWS profile with --profile=<profileName>
- Configure Route53 domain for the s3 bucket

## 02-notifon
Notifon is a project to notify Slack users of changes to your AWS account using cloudwatch events.

### features

Notifon currently has the following features:

- Send notifications to slack when cloudwatch events happen.