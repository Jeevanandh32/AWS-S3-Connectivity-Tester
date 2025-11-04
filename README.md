##S3 Connectivity Tester

A simple Python utility to validate AWS S3 access and basic operations.
Useful for troubleshooting IAM permissions, testing new S3 endpoints, or verifying network routes to AWS.

What it does

This tool performs a sequence of S3 checks, including:

Credential validation

Listing buckets

Creating and deleting a test bucket

Upload, download, and delete of a test object

Object metadata lookup (HEAD request)

Multipart upload flow

Bucket versioning check

Cleanup of all test data

JSON test report output

It’s meant to give you a quick “yes or no” answer on whether your environment can talk to S3 and perform standard operations.

Note: This script creates temporary buckets and objects. They are removed at the end of the run.

Requirements

Python 3.7 or newer

AWS account with S3 permissions

AWS credentials configured (env vars, AWS CLI, or shared credentials file)

Setup
git clone https://github.com/jeevanandh32/s3-connectivity_tester.git
cd s3-connectivity-tester


Create a virtual environment:

python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate


Install dependencies:

pip install -r requirements.txt

Usage

Run all tests (default region: us-east-1):

python3 s3_connectivity_tester.py


Specify a region:

python3 s3_connectivity_tester.py us-west-2


Use custom credentials:

export AWS_ACCESS_KEY_ID=YOUR_KEY
export AWS_SECRET_ACCESS_KEY=YOUR_SECRET
python3 s3_connectivity_tester.py

Example Output
Starting S3 Connectivity Tests
--------------------------------------------

Credential Check .................... OK
List Buckets ....................... OK
Create Bucket ...................... OK
Upload Object ...................... OK
Read Object ........................ OK
Head Object ........................ OK
Delete Object ...................... OK
Multipart Upload ................... OK
Bucket Versioning .................. OK
Cleanup Resources .................. OK

All tests passed successfully.
Report saved: s3_test_report_20250110_120545.json

JSON Report Example
{
  "timestamp": "2025-01-10T12:05:45",
  "region": "us-east-1",
  "account": "123456789012",
  "results": {
    "credentials": true,
    "list_buckets": true,
    "create_bucket": true,
    "upload_object": true,
    "read_object": true,
    "head_object": true,
    "delete_object": true,
    "multipart_upload": true,
    "bucket_versioning": true,
    "cleanup": true
  },
  "summary": {
    "total": 10,
    "passed": 10,
    "failed": 0,
    "success_rate": "100%"
  },
  "errors": []
}

Why this exists

When debugging S3 access issues, it’s helpful to have a small script that walks through real operations end-to-end. This avoids guessing whether a failure is because of IAM, networking, or your client configuration.
