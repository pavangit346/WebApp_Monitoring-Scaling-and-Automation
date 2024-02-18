# import boto3,json,time
import boto3
import json
import time


# defining variable for region of choice
#REGION='us-east-1'

# --> Step 1: Web Application Deployment 

# Create an S3 client
s3_client = boto3.client('s3')

# defining function to create an s3 bucket with handling errors gracefully
def create_s3_bucket(bucket_name):

    # try block to attempt creating a bucket
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        # return bucket created text if the create_bucket was successful
        return f"S3 bucket '{bucket_name}' created successfully."
    
    # If any exception, like bucket name already exists or if bucket is already owned by us
    except Exception as e:
        return f"An error occurred: {str(e)}"

# defning bucket name in a vatiable
bucket_name = 'webapppn346'

# calling the create bucket function
result_message = create_s3_bucket(bucket_name)

# printing the return value for the create bucket function
print(result_message)

# defining function to upload to s3 bucket with handling errors gracefully
def upload_to_s3_bucket(bucket_name):
    # try block to attempt upload file a bucket
    try:
        s3_client.upload_file('index.html',bucket_name, 'index.html')
        return f"File index.html has been uploaded successfully."
    # if eny exception, return the exception as a string
    except Exception as e:
        return f"An error occurred: {str(e)}"

# sotring the response from upload to s3 function
result_message_upload_to_s3 = upload_to_s3_bucket(bucket_name)

# printing the response from upload to s3 function
print(result_message_upload_to_s3)

time.sleep (120)


# Create an ec2 client

import boto3

# AWS credentials
aws_access_key_id = 'AKIASNJVEGLGO4KUT6VH'
aws_secret_access_key = 'g6TQwD1yksnlmWuH7m2Szrb/CYorn3nDDpavSi2n'
region_name = 'us-east-1'  # e.g., 'us-east-1'

# Create EC2 client
ec2 = boto3.client('ec2', 
                   aws_access_key_id=aws_access_key_id,
                   aws_secret_access_key=aws_secret_access_key,
                   region_name=region_name)

# Define instance parameters
image_id = 'ami-0c7217cdde317cfec'  # Ubuntu Server 20.04 LTS - Free Tier Eligible
instance_type = 't2.micro'  # Free Tier eligible instance type
key_name = 'PavanAWSbotousr'  # Name of the key pair
security_group_ids = ['sg-0d8b3e13d2f44bca8']  # List of security group IDs
subnet_id = 'subnet-0ab482c5c7ee20ade'  # Subnet ID
ROLE_PROFILE = 'EC2S3Access'
user_data ='''#!/bin/bash
sudo apt update
sudo apt install awscli nginx -y
aws s3 cp s3://webapppn346/index.html /tmp/index.html
sudo systemctl start nginx
sudo systemctl enable nginx
sudo rm -rf /var/www/html/*
sudo cp /tmp/index.html /var/www/html/index.html
sudo systemctl restart nginx
'''

# Launch EC2 instance
response = ec2.run_instances(
    ImageId=image_id,
    InstanceType=instance_type,
    KeyName=key_name,
    SecurityGroupIds=security_group_ids,
    SubnetId=subnet_id,
    UserData=user_data,
    MinCount=1,
    MaxCount=2,
    IamInstanceProfile={
                'Name':ROLE_PROFILE
            }
)

# Print instance ID
instance_id = response['Instances'][0]['InstanceId']
instance_id = response['Instances'][1]['InstanceId']
print(f'Instance ID: {instance_id} Successfully')

