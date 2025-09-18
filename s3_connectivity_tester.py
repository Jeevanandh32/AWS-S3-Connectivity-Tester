#!/usr/bin/env python3
"""
S3 Connectivity Tester
A comprehensive tool to test AWS S3 connectivity and operations
"""

import boto3
import json
import time
import hashlib
import os
import sys
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError, ParamValidationError
from typing import Dict, List, Optional, Tuple

class S3ConnectivityTester:
    """Test S3 connectivity and perform basic operations"""
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize S3 client with error handling"""
        self.region = region
        self.s3_client = None
        self.test_results = []
        self.test_bucket_name = None
        
        try:
            self.s3_client = boto3.client('s3', region_name=region)
            self.sts_client = boto3.client('sts', region_name=region)
        except NoCredentialsError:
            print("Error: AWS credentials not found. Please configure AWS CLI or set environment variables.")
            sys.exit(1)
    
    def test_credentials(self) -> Tuple[bool, str]:
        """Test if AWS credentials are valid"""
        print("\nTesting AWS Credentials...")
        try:
            caller_identity = self.sts_client.get_caller_identity()
            account_id = caller_identity['Account']
            user_arn = caller_identity['Arn']
            print(f"SUCCESS: Credentials valid for account: {account_id}")
            print(f"   User/Role: {user_arn}")
            return True, account_id
        except ClientError as e:
            print(f"FAILED: Invalid credentials: {e}")
            return False, ""
    
    def test_list_buckets(self) -> bool:
        """Test listing S3 buckets"""
        print("\nTesting List Buckets...")
        try:
            response = self.s3_client.list_buckets()
            bucket_count = len(response['Buckets'])
            print(f"SUCCESS: Successfully listed {bucket_count} bucket(s)")
            
            if bucket_count > 0:
                print("   First 5 buckets:")
                for bucket in response['Buckets'][:5]:
                    print(f"   - {bucket['Name']}")
            return True
        except ClientError as e:
            print(f"FAILED: Failed to list buckets: {e}")
            return False
    
    def test_create_bucket(self, bucket_name: str) -> bool:
        """Test creating an S3 bucket"""
        print(f"\nTesting Create Bucket: {bucket_name}...")
        try:
            if self.region == 'us-east-1':
                self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            self.test_bucket_name = bucket_name
            print(f"SUCCESS: Successfully created bucket: {bucket_name}")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BucketAlreadyOwnedByYou':
                print(f"WARNING: Bucket already exists and owned by you: {bucket_name}")
                self.test_bucket_name = bucket_name
                return True
            else:
                print(f"FAILED: Failed to create bucket: {e}")
                return False
    
    def test_upload_object(self, bucket_name: str) -> bool:
        """Test uploading an object to S3"""
        print("\nTesting Upload Object...")
        
        test_content = f"Test upload at {datetime.now().isoformat()}"
        test_key = "test-connectivity/test-file.txt"
        
        try:
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=test_content.encode('utf-8'),
                ContentType='text/plain',
                Metadata={'test': 'connectivity', 'timestamp': str(time.time())}
            )
            print(f"SUCCESS: Successfully uploaded object: {test_key}")
            return True
        except ClientError as e:
            print(f"FAILED: Failed to upload object: {e}")
            return False
    
    def test_read_object(self, bucket_name: str) -> bool:
        """Test reading an object from S3"""
        print("\nTesting Read Object...")
        test_key = "test-connectivity/test-file.txt"
        
        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=test_key)
            content = response['Body'].read().decode('utf-8')
            print(f"SUCCESS: Successfully read object: {test_key}")
            print(f"   Content preview: {content[:50]}...")
            return True
        except ClientError as e:
            print(f"FAILED: Failed to read object: {e}")
            return False
    
    def test_head_object(self, bucket_name: str) -> bool:
        """Test HEAD operation on object"""
        print("\nTesting HEAD Object...")
        test_key = "test-connectivity/test-file.txt"
        
        try:
            response = self.s3_client.head_object(Bucket=bucket_name, Key=test_key)
            print(f"SUCCESS: Successfully retrieved object metadata:")
            print(f"   Size: {response['ContentLength']} bytes")
            print(f"   Type: {response['ContentType']}")
            print(f"   ETag: {response['ETag']}")
            return True
        except ClientError as e:
            print(f"FAILED: Failed to get object metadata: {e}")
            return False
    
    def test_delete_object(self, bucket_name: str) -> bool:
        """Test deleting an object from S3"""
        print("\nTesting Delete Object...")
        test_key = "test-connectivity/test-file.txt"
        
        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=test_key)
            print(f"SUCCESS: Successfully deleted object: {test_key}")
            return True
        except ClientError as e:
            print(f"FAILED: Failed to delete object: {e}")
            return False
    
    def test_multipart_upload(self, bucket_name: str) -> bool:
        """Test multipart upload functionality"""
        print("\nTesting Multipart Upload...")
        test_key = "test-connectivity/multipart-test.txt"
        
        try:
            # Initiate multipart upload
            response = self.s3_client.create_multipart_upload(
                Bucket=bucket_name,
                Key=test_key
            )
            upload_id = response['UploadId']
            
            # Upload one part (minimum 5MB in production, but this is just a test)
            part_data = b"Test multipart upload content" * 1000
            part_response = self.s3_client.upload_part(
                Bucket=bucket_name,
                Key=test_key,
                PartNumber=1,
                UploadId=upload_id,
                Body=part_data
            )
            
            # Complete multipart upload
            self.s3_client.complete_multipart_upload(
                Bucket=bucket_name,
                Key=test_key,
                UploadId=upload_id,
                MultipartUpload={
                    'Parts': [{
                        'PartNumber': 1,
                        'ETag': part_response['ETag']
                    }]
                }
            )
            
            print(f"SUCCESS: Successfully completed multipart upload")
            
            # Clean up
            self.s3_client.delete_object(Bucket=bucket_name, Key=test_key)
            return True
            
        except ClientError as e:
            print(f"FAILED: Failed multipart upload test: {e}")
            return False
    
    def test_bucket_versioning(self, bucket_name: str) -> bool:
        """Test bucket versioning configuration"""
        print("\nTesting Bucket Versioning...")
        
        try:
            # Check current versioning status
            response = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
            status = response.get('Status', 'Not Enabled')
            print(f"   Current versioning status: {status}")
            
            # Enable versioning
            self.s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            print(f"SUCCESS: Successfully configured bucket versioning")
            return True
            
        except ClientError as e:
            print(f"FAILED: Failed to configure versioning: {e}")
            return False
    
    def cleanup(self, bucket_name: str) -> bool:
        """Clean up test bucket and objects"""
        print("\nCleaning up test resources...")
        
        try:
            # Delete all objects in the bucket
            response = self.s3_client.list_objects_v2(Bucket=bucket_name)
            
            if 'Contents' in response:
                objects = [{'Key': obj['Key']} for obj in response['Contents']]
                self.s3_client.delete_objects(
                    Bucket=bucket_name,
                    Delete={'Objects': objects}
                )
                print(f"   Deleted {len(objects)} object(s)")
            
            # Delete the bucket
            self.s3_client.delete_bucket(Bucket=bucket_name)
            print(f"SUCCESS: Successfully cleaned up bucket: {bucket_name}")
            return True
            
        except ClientError as e:
            print(f"WARNING: Cleanup partial or failed: {e}")
            return False
    
    def generate_report(self, results: Dict[str, bool]) -> None:
        """Generate a test report"""
        print("\n" + "="*50)
        print("S3 CONNECTIVITY TEST REPORT")
        print("="*50)
        
        total_tests = len(results)
        passed_tests = sum(1 for v in results.values() if v)
        
        print(f"\nTest Summary:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {total_tests - passed_tests}")
        print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            print(f"  {test_name}: {status}")
        
        print("\n" + "="*50)
        
        # Save report to file
        report_file = f"s3_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'region': self.region,
                'results': results,
                'summary': {
                    'total': total_tests,
                    'passed': passed_tests,
                    'failed': total_tests - passed_tests,
                    'success_rate': f"{(passed_tests/total_tests)*100:.1f}%"
                }
            }, f, indent=2)
        print(f"\nReport saved to: {report_file}")
    
    def run_all_tests(self) -> None:
        """Run all connectivity tests"""
        print("\nStarting S3 Connectivity Tests...")
        print("="*50)
        
        results = {}
        
        # Test credentials
        creds_valid, account_id = self.test_credentials()
        results['credentials'] = creds_valid
        
        if not creds_valid:
            print("\nCannot proceed without valid credentials")
            return
        
        # Test list buckets
        results['list_buckets'] = self.test_list_buckets()
        
        # Generate unique bucket name for testing
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        test_bucket = f"s3-connectivity-test-{account_id[-6:]}-{timestamp}"
        
        # Test bucket creation
        results['create_bucket'] = self.test_create_bucket(test_bucket)
        
        if results['create_bucket']:
            # Test object operations
            results['upload_object'] = self.test_upload_object(test_bucket)
            
            if results['upload_object']:
                results['read_object'] = self.test_read_object(test_bucket)
                results['head_object'] = self.test_head_object(test_bucket)
                results['delete_object'] = self.test_delete_object(test_bucket)
            
            # Test advanced features
            results['multipart_upload'] = self.test_multipart_upload(test_bucket)
            results['bucket_versioning'] = self.test_bucket_versioning(test_bucket)
            
            # Cleanup
            time.sleep(2)  # Brief pause before cleanup
            results['cleanup'] = self.cleanup(test_bucket)
        
        # Generate report
        self.generate_report(results)


def main():
    """Main function"""
    print("""
AWS S3 Connectivity Tester
Version 1.0.0
    """)
    
    # Check for region override
    region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    
    if len(sys.argv) > 1:
        region = sys.argv[1]
    
    print(f"Using AWS Region: {region}")
    
    # Run tests
    tester = S3ConnectivityTester(region=region)
    tester.run_all_tests()


if __name__ == "__main__":
    main()