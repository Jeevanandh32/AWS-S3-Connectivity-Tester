# S3 Connectivity Tester

A lightweight Python script to validate AWS S3 access and core operations.
Handy for checking IAM permissions, testing S3 endpoints, or confirming network paths to AWS.

## What it does

The script runs a set of S3 operations end-to-end:

- Validate AWS credentials
- List existing buckets
- Create a temporary test bucket
- Upload, download, and delete a test file
- Retrieve object metadata (HEAD request)
- Multipart upload test
- Enable and verify bucket versioning
- Cleanup all test resources
- Generate a JSON test report

The goal is to quickly verify that your environment can connect to S3 and perform standard actions without guessing.

## Requirements

- Python 3.7+
- AWS credentials with S3 access (via env vars or AWS CLI)

## Setup

```bash
git clone https://github.com/jeevanandh32/s3-connectivity_tester.git
cd s3-connectivity-tester
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
## Run
```bash
python3 s3_connectivity_tester.py
```

Specify a region:
```
python3 s3_connectivity_tester.py us-west-2

```
Use custom credentials:
```
export AWS_ACCESS_KEY_ID=xxxxx
export AWS_SECRET_ACCESS_KEY=xxxxx
python3 s3_connectivity_tester.py
```
Example output: 

S3 Connectivity Test
-----------------------------

Credentials .............. OK
List Buckets ............ OK
Create Bucket ........... OK
Upload Object ........... OK
Download Object ......... OK
HEAD Object ............. OK
Multipart Upload ........ OK
Versioning .............. OK
Cleanup ................. OK

All tests passed.
Report saved to: s3_test_report_YYYYMMDD_HHMMSS.json
