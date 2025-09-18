#!/usr/bin/env python3
"""
S3 Operations
Basic S3 operations with error handling and best practices
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import os
import json
from datetime import datetime
from pathlib import Path

class S3Operations:
    """Handle basic S3 operations with proper error handling"""
    
    def __init__(self, region='us-east-1'):
        """Initialize S3 client"""
        self.region = region
        try:
            self.s3_client = boto3.client('s3', region_name=region)
        except NoCredentialsError:
            print("ERROR: AWS credentials not found. Please configure AWS CLI.")
            raise
    
    def create_bucket(self, bucket_name, region=None):
        """Create S3 bucket"""
        if region is None:
            region = self.region
            
        try:
            if region == 'us-east-1':
                self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            print(f"SUCCESS: Bucket {bucket_name} created successfully")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BucketAlreadyExists':
                print(f"ERROR: Bucket {bucket_name} already exists (owned by someone else)")
            elif error_code == 'BucketAlreadyOwnedByYou':
                print(f"INFO: Bucket {bucket_name} already exists and is owned by you")
                return True
            else:
                print(f"ERROR: Failed to create bucket: {e}")
            return False

    def list_buckets(self):
        """List all S3 buckets"""
        try:
            response = self.s3_client.list_buckets()
            buckets = response['Buckets']
            print(f"Found {len(buckets)} bucket(s):")
            for bucket in buckets:
                print(f"  - {bucket['Name']} (created: {bucket['CreationDate']})")
            return buckets
        except ClientError as e:
            print(f"ERROR: Failed to list buckets: {e}")
            return []

    def upload_file(self, file_path, bucket_name, object_name=None):
        """Upload file to S3"""
        if object_name is None:
            object_name = Path(file_path).name
        
        if not os.path.exists(file_path):
            print(f"ERROR: File {file_path} not found")
            return False
        
        try:
            # Upload with metadata
            extra_args = {
                'Metadata': {
                    'uploaded_by': 'S3Operations',
                    'upload_date': datetime.now().isoformat()
                }
            }
            
            self.s3_client.upload_file(file_path, bucket_name, object_name, ExtraArgs=extra_args)
            print(f"SUCCESS: File {file_path} uploaded to {bucket_name}/{object_name}")
            return True
        except ClientError as e:
            print(f"ERROR: Failed to upload file: {e}")
            return False

    def download_file(self, bucket_name, object_name, file_path):
        """Download file from S3"""
        try:
            self.s3_client.download_file(bucket_name, object_name, file_path)
            print(f"SUCCESS: File downloaded to {file_path}")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"ERROR: Object {object_name} not found in {bucket_name}")
            else:
                print(f"ERROR: Failed to download file: {e}")
            return False

    def list_objects(self, bucket_name, prefix=''):
        """List objects in S3 bucket"""
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
            
            objects = []
            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        objects.append({
                            'Key': obj['Key'],
                            'Size': obj['Size'],
                            'LastModified': obj['LastModified'],
                            'ETag': obj['ETag']
                        })
            
            print(f"Found {len(objects)} object(s) in {bucket_name}:")
            for obj in objects:
                size_mb = obj['Size'] / (1024 * 1024)
                print(f"  - {obj['Key']} ({size_mb:.2f} MB, modified: {obj['LastModified']})")
            
            return objects
        except ClientError as e:
            print(f"ERROR: Failed to list objects: {e}")
            return []

    def delete_object(self, bucket_name, object_name):
        """Delete object from S3"""
        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=object_name)
            print(f"SUCCESS: Object {object_name} deleted from {bucket_name}")
            return True
        except ClientError as e:
            print(f"ERROR: Failed to delete object: {e}")
            return False

    def get_object_metadata(self, bucket_name, object_name):
        """Get object metadata using HEAD operation"""
        try:
            response = self.s3_client.head_object(Bucket=bucket_name, Key=object_name)
            metadata = {
                'ContentType': response.get('ContentType'),
                'ContentLength': response.get('ContentLength'),
                'LastModified': response.get('LastModified'),
                'ETag': response.get('ETag'),
                'Metadata': response.get('Metadata', {})
            }
            
            print(f"Metadata for {bucket_name}/{object_name}:")
            for key, value in metadata.items():
                if key == 'ContentLength':
                    size_mb = value / (1024 * 1024) if value else 0
                    print(f"  - {key}: {value} bytes ({size_mb:.2f} MB)")
                else:
                    print(f"  - {key}: {value}")
            
            return metadata
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"ERROR: Object {object_name} not found")
            else:
                print(f"ERROR: Failed to get metadata: {e}")
            return None

    def copy_object(self, source_bucket, source_key, dest_bucket, dest_key=None):
        """Copy object from one location to another"""
        if dest_key is None:
            dest_key = source_key
            
        try:
            copy_source = {'Bucket': source_bucket, 'Key': source_key}
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=dest_bucket,
                Key=dest_key
            )
            print(f"SUCCESS: Copied {source_bucket}/{source_key} to {dest_bucket}/{dest_key}")
            return True
        except ClientError as e:
            print(f"ERROR: Failed to copy object: {e}")
            return False

    def delete_bucket(self, bucket_name, force=False):
        """Delete S3 bucket (optionally force delete with all objects)"""
        if force:
            # Delete all objects first
            try:
                paginator = self.s3_client.get_paginator('list_objects_v2')
                page_iterator = paginator.paginate(Bucket=bucket_name)
                
                objects_deleted = 0
                for page in page_iterator:
                    if 'Contents' in page:
                        objects = [{'Key': obj['Key']} for obj in page['Contents']]
                        self.s3_client.delete_objects(
                            Bucket=bucket_name,
                            Delete={'Objects': objects}
                        )
                        objects_deleted += len(objects)
                
                if objects_deleted > 0:
                    print(f"INFO: Deleted {objects_deleted} object(s) from bucket")
            except ClientError as e:
                print(f"ERROR: Failed to delete objects: {e}")
                return False
        
        # Delete the bucket
        try:
            self.s3_client.delete_bucket(Bucket=bucket_name)
            print(f"SUCCESS: Bucket {bucket_name} deleted")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BucketNotEmpty':
                print(f"ERROR: Bucket {bucket_name} is not empty. Use force=True to delete all objects first.")
            else:
                print(f"ERROR: Failed to delete bucket: {e}")
            return False

    def generate_presigned_url(self, bucket_name, object_name, expiration=3600, method='get_object'):
        """Generate presigned URL for S3 object"""
        try:
            response = self.s3_client.generate_presigned_url(
                method,
                Params={'Bucket': bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            print(f"Generated presigned URL (expires in {expiration} seconds):")
            print(response)
            return response
        except ClientError as e:
            print(f"ERROR: Failed to generate presigned URL: {e}")
            return None

def main():
    """Main function to demonstrate S3 operations"""
    print("S3 Operations Demo")
    print("="*50)
    
    # Initialize S3Operations
    try:
        s3_ops = S3Operations()
    except NoCredentialsError:
        return
    
    # Example bucket name (you should change this)
    bucket_name = f"test-s3-operations-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Demo operations
    print("\n1. Listing existing buckets:")
    s3_ops.list_buckets()
    
    print(f"\n2. Creating test bucket: {bucket_name}")
    if s3_ops.create_bucket(bucket_name):
        
        print("\n3. Creating test file for upload:")
        test_file = "test_upload.txt"
        with open(test_file, "w") as f:
            f.write(f"Test file created at {datetime.now().isoformat()}\n")
            f.write("This is a test file for S3 operations demo.\n")
            f.write("It contains sample content for testing upload/download operations.\n")
        
        print(f"\n4. Uploading file: {test_file}")
        if s3_ops.upload_file(test_file, bucket_name):
            
            print(f"\n5. Listing objects in bucket:")
            s3_ops.list_objects(bucket_name)
            
            print(f"\n6. Getting object metadata:")
            s3_ops.get_object_metadata(bucket_name, test_file)
            
            print(f"\n7. Generating presigned URL:")
            s3_ops.generate_presigned_url(bucket_name, test_file, expiration=3600)
            
            print(f"\n8. Downloading file:")
            downloaded_file = "downloaded_test.txt"
            s3_ops.download_file(bucket_name, test_file, downloaded_file)
            
            print(f"\n9. Copying object:")
            s3_ops.copy_object(bucket_name, test_file, bucket_name, "copy_of_" + test_file)
        
        print(f"\n10. Final object listing:")
        s3_ops.list_objects(bucket_name)
        
        print(f"\n11. Cleaning up (deleting bucket and all objects):")
        s3_ops.delete_bucket(bucket_name, force=True)
        
        # Clean up local files
        for file in [test_file, downloaded_file]:
            if os.path.exists(file):
                os.remove(file)
                print(f"Removed local file: {file}")
    
    print("\nDemo completed!")

if __name__ == "__main__":
    main()