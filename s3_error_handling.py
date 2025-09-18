#!/usr/bin/env python3
"""
S3 Error Handling Examples
Demonstrates common S3 errors and their handling patterns
"""

import boto3
from botocore.exceptions import ClientError, ParamValidationError, NoCredentialsError

s3_client = boto3.client('s3')

def demonstrate_common_errors():
    """Demonstrate common S3 errors and their handling"""
    
    print("Demonstrating common S3 errors and handling:\n")
    
    # 1. AccessDenied (403)
    print("1. Testing AccessDenied (403) error:")
    try:
        s3_client.get_object(Bucket='private-bucket-you-dont-own', Key='file.txt')
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            print("   CAUGHT: Access Denied (403) - You don't have permission")
            print(f"   Details: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"   Other error: {e}")
    
    # 2. NoSuchBucket (404)
    print("\n2. Testing NoSuchBucket (404) error:")
    try:
        s3_client.list_objects_v2(Bucket='non-existent-bucket-xyz123')
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            print("   CAUGHT: NoSuchBucket (404) - Bucket doesn't exist")
            print(f"   Details: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"   Other error: {e}")
    
    # 3. NoSuchKey (404)
    print("\n3. Testing NoSuchKey (404) error:")
    try:
        # This will likely fail unless you have a bucket named 'your-bucket'
        s3_client.get_object(Bucket='first-bucket-2403', Key='non-existent-file.txt')
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            print("   CAUGHT: NoSuchKey (404) - Object doesn't exist")
            print(f"   Details: {e.response['Error']['Message']}")
        elif e.response['Error']['Code'] == 'AccessDenied':
            print("   CAUGHT: Access denied to bucket")
        elif e.response['Error']['Code'] == 'NoSuchBucket':
            print("   CAUGHT: Bucket doesn't exist")
    except Exception as e:
        print(f"   Other error: {e}")
    
    # 4. BucketAlreadyExists (409)
    print("\n4. Testing BucketAlreadyExists (409) error:")
    try:
        s3_client.create_bucket(Bucket='amazon')  # Common name, likely exists
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyExists':
            print("   CAUGHT: BucketAlreadyExists (409) - Choose unique bucket name")
            print(f"   Details: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"   Other error: {e}")
    
    # 5. InvalidBucketName (400)
    print("\n5. Testing InvalidBucketName (400) error:")
    try:
        s3_client.create_bucket(Bucket='Invalid_Bucket_Name')  # Underscores not allowed
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidBucketName':
            print("   CAUGHT: InvalidBucketName (400) - Follow S3 naming rules")
            print(f"   Details: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"   Other error: {e}")

def robust_s3_operation_example():
    """Example of robust S3 operations with comprehensive error handling"""
    
    print("\n" + "="*60)
    print("ROBUST S3 OPERATION EXAMPLE")
    print("="*60)
    
    bucket_name = "test-bucket-example"
    key_name = "test-file.txt"
    
    def safe_create_bucket(bucket_name, region='us-east-1'):
        """Safely create S3 bucket with error handling"""
        try:
            if region == 'us-east-1':
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            print(f"SUCCESS: Created bucket {bucket_name}")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BucketAlreadyExists':
                print(f"WARNING: Bucket {bucket_name} already exists (owned by someone else)")
            elif error_code == 'BucketAlreadyOwnedByYou':
                print(f"INFO: Bucket {bucket_name} already exists and is owned by you")
                return True
            elif error_code == 'InvalidBucketName':
                print(f"ERROR: Invalid bucket name: {bucket_name}")
            else:
                print(f"ERROR: Failed to create bucket: {e}")
            return False
    
    def safe_upload_object(bucket_name, key, content):
        """Safely upload object with error handling"""
        try:
            s3_client.put_object(Bucket=bucket_name, Key=key, Body=content)
            print(f"SUCCESS: Uploaded {key} to {bucket_name}")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                print(f"ERROR: Bucket {bucket_name} doesn't exist")
            elif error_code == 'AccessDenied':
                print(f"ERROR: Access denied to bucket {bucket_name}")
            else:
                print(f"ERROR: Failed to upload object: {e}")
            return False
    
    def safe_download_object(bucket_name, key):
        """Safely download object with error handling"""
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=key)
            content = response['Body'].read()
            print(f"SUCCESS: Downloaded {key} from {bucket_name}")
            return content
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                print(f"ERROR: Bucket {bucket_name} doesn't exist")
            elif error_code == 'NoSuchKey':
                print(f"ERROR: Object {key} doesn't exist in {bucket_name}")
            elif error_code == 'AccessDenied':
                print(f"ERROR: Access denied to {bucket_name}/{key}")
            else:
                print(f"ERROR: Failed to download object: {e}")
            return None
    
    # Demonstrate robust operations
    print("\n1. Attempting to create bucket...")
    safe_create_bucket(bucket_name)
    
    print("\n2. Attempting to upload object...")
    safe_upload_object(bucket_name, key_name, "This is test content")
    
    print("\n3. Attempting to download object...")
    content = safe_download_object(bucket_name, key_name)
    if content:
        print(f"   Downloaded content: {content.decode('utf-8')}")

def print_error_codes_reference():
    """Print comprehensive S3 error codes reference"""
    
    print("\n" + "="*60)
    print("S3 ERROR CODES REFERENCE")
    print("="*60)
    
    error_codes = {
        "400 Bad Request": [
            "InvalidBucketName - Bucket name doesn't follow naming rules",
            "InvalidArgument - Invalid argument provided",
            "InvalidRequest - Invalid request format",
            "MalformedXML - XML in request is malformed"
        ],
        "403 Forbidden": [
            "AccessDenied - Insufficient permissions",
            "AccountProblem - Problem with AWS account",
            "InvalidPayer - Invalid payer for request",
            "RequestTimeTooSkewed - Request time too different from server time"
        ],
        "404 Not Found": [
            "NoSuchBucket - Bucket doesn't exist",
            "NoSuchKey - Object doesn't exist",
            "NoSuchVersion - Object version doesn't exist"
        ],
        "409 Conflict": [
            "BucketAlreadyExists - Bucket name taken by another account",
            "BucketAlreadyOwnedByYou - Bucket already exists in your account",
            "BucketNotEmpty - Bucket contains objects, can't delete"
        ],
        "500 Internal Server Error": [
            "InternalError - AWS internal server error"
        ],
        "503 Service Unavailable": [
            "ServiceUnavailable - Service temporarily unavailable",
            "SlowDown - Reduce request rate"
        ]
    }
    
    for category, codes in error_codes.items():
        print(f"\n{category}:")
        for code in codes:
            print(f"  - {code}")

if __name__ == "__main__":
    try:
        demonstrate_common_errors()
        robust_s3_operation_example()
        print_error_codes_reference()
        
    except NoCredentialsError:
        print("ERROR: AWS credentials not found.")
        print("Please configure AWS CLI: aws configure")
        print("Or set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
    except Exception as e:
        print(f"Unexpected error: {e}")