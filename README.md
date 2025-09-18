# S3 Connectivity Tester

A comprehensive Python tool for testing AWS S3 connectivity and operations.

## Features

- ✅ Credential validation
- ✅ Bucket operations (create, list, delete)
- ✅ Object operations (upload, download, delete)
- ✅ Metadata retrieval (HEAD operations)
- ✅ Multipart upload testing
- ✅ Versioning configuration
- ✅ Comprehensive error handling
- ✅ Detailed test reporting

## Prerequisites

- Python 3.7+
- AWS Account with S3 access
- Configured AWS credentials

## Installation
```bash
# Clone repository
git clone https://github.com/jeevanandh32/s3-connectivity_tester.git
cd s3-connectivity-tester
```
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

Basic Test
# Run all tests with default settings
python3 s3_connectivity_tester.py
Specify Region

# Test S3 in specific region
python3 s3_connectivity_tester.py us-west-2
Use Different Credentials

# Set credentials via environment variables
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
python3 s3_connectivity_tester.py

What Gets Tested
The tool performs these tests in order:
TestWhat It ChecksCommon IssuesCredentialsAre AWS keys valid?Wrong keys, expired keysList BucketsCan you see S3 buckets?No S3 permissionsCreate BucketCan you create new buckets?Region issues, naming conflictsUpload ObjectCan you write files?Write permissions missingRead ObjectCan you download files?Read permissions missingObject MetadataCan you get file info?HEAD operation blockedDelete ObjectCan you delete files?Delete permissions missingMultipart UploadCan you upload large files?Complex upload issuesVersioningCan you enable versioning?Bucket feature permissionsCleanupRemoves all test resourcesPrevents AWS charges

Example Output
🚀 Starting S3 Connectivity Tests...
==================================================

🔐 Testing AWS Credentials...
✅ Credentials valid for account: 123456789012
   User/Role: arn:aws:iam::123456789012:user/john

📋 Testing List Buckets...
✅ Successfully listed 3 bucket(s)

🪣 Testing Create Bucket: s3-test-789012-20250110120530...
✅ Successfully created bucket

📤 Testing Upload Object...
✅ Successfully uploaded object: test-connectivity/test-file.txt

📥 Testing Read Object...
✅ Successfully read object
   Content preview: Test upload at 2025-01-10T12:05:30...

🔍 Testing HEAD Object...
✅ Successfully retrieved object metadata:
   Size: 42 bytes
   Type: text/plain
   ETag: "d41d8cd98f00b204e9800998ecf8427e"

🗑️ Testing Delete Object...
✅ Successfully deleted object

📦 Testing Multipart Upload...
✅ Successfully completed multipart upload

📚 Testing Bucket Versioning...
✅ Successfully configured bucket versioning

🧹 Cleaning up test resources...
✅ Successfully cleaned up bucket

==================================================
📊 S3 CONNECTIVITY TEST REPORT
==================================================

Test Summary:
  Total Tests: 10
  Passed: 10
  Failed: 0
  Success Rate: 100.0%

📄 Report saved to: s3_test_report_20250110_120545.json
Report Format
The tool generates a JSON report with detailed results:
json{
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
    "success_rate": "100.0%"
  },
  "errors": []
}
