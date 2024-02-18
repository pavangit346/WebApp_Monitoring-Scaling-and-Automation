import boto3
import time
import json

# --> Step 1: Load Balancing with ELB
InstanceIds = ["i-02ebae7470ab6fcec","i-0cccb8beb341ab632"]

# Create an elb client
elb_client = boto3.client('elbv2')

# defining ALB attributes

alb_name = "webapp-alb"
subnets = ['subnet-0ab482c5c7ee20ade','subnet-07e40be476d688dee','subnet-0564d17c714b6a55a']
security_group_ids = ['sg-0d8b3e13d2f44bca8']
# defining empty list to store the target arn's
target_group_arns = []

# defining function which will create load balancer, target group, register targets and add a listener to the ALB

def create_alb_and_attach_ec2():

    # defining target_group attributes

    target_group_name = 'webapp-target-group'
    target_port = 80
    health_check_path = '/'
    protocol = 'HTTP'

    # create_target_group to create the target group
    response_target_grp = elb_client.create_target_group(
        Name=target_group_name,
        Protocol=protocol,
        Port=target_port,
        VpcId='vpc-0f7f2c0401b568528',
        HealthCheckProtocol=protocol,
        HealthCheckPath=health_check_path,
        HealthCheckPort=str(target_port),
        HealthCheckIntervalSeconds=30,
        HealthCheckTimeoutSeconds=5,
        HealthyThresholdCount=2,
        UnhealthyThresholdCount=2,
        Matcher={'HttpCode': '200'}
    )

    # extracting the target group ARN's 
    target_group_arn = response_target_grp['TargetGroups'][0]['TargetGroupArn']

    # append the target group arn to an empty list to use it in future
    target_group_arns.append(target_group_arn)

    print("Target groups created are: ", target_group_arns)

    # create alb

    # using create_load_balancer to create ALB with some tags
    response_alb = elb_client.create_load_balancer(
        Name = alb_name,
        Subnets = subnets,
        SecurityGroups=security_group_ids,
        Scheme='internet-facing',
        Tags=[{'Key':'Name','Value':alb_name}]
    )

    # Extracting the ARN of the created ALB

    # extracting the load balancer ARN

    alb_arn = response_alb['LoadBalancers'][0]['LoadBalancerArn']

    # Register ec2 instance with the target
    
    elb_client.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=[{'Id': instance} for instance in InstanceIds]
    )

    # Create a listener for the ALB

    listener_port = 80

    elb_client.create_listener(
        DefaultActions=[{
            'Type': 'forward',
            'TargetGroupArn': target_group_arn
        }],
        LoadBalancerArn=alb_arn,
        Port=listener_port,
        Protocol=protocol
    )

    return f"ALB {alb_name} and Target Group {target_group_name} created successfully."

print(create_alb_and_attach_ec2())

#Auto Scaling Group (ASG) Configuration

autoscaling_grp_arns = []

# Create an autoscaling client

REGION = 'us-east-1'
autoscaling_client = boto3.client('autoscaling',region_name=REGION)

cloudwatch_client = boto3.client('cloudwatch', region_name=REGION)

def create_autoscaling():
    autoscaling_client = boto3.client('autoscaling',region_name=REGION)

    autoscaling_client.create_auto_scaling_group(
        AutoScalingGroupName='assigment_autoscaling_grp',
        # LaunchConfigurationName='assignment_lauch_config',
        MinSize=1,
        MaxSize=2,
        DesiredCapacity=1,
        InstanceId=InstanceIds[0],
        TargetGroupARNs=target_group_arns
    )

    time.sleep(120)

    response_describe_auto_scaling = autoscaling_client.describe_auto_scaling_groups(
        AutoScalingGroupNames=[
            'assigment_autoscaling_grp',
        ]
    )

    asg_arn = response_describe_auto_scaling['AutoScalingGroups'][0]['AutoScalingGroupARN']

    autoscaling_grp_arns.append(asg_arn)

    print(autoscaling_grp_arns)

    # Scale out policy

    autoscaling_client.put_scaling_policy(
        AutoScalingGroupName='assigment_autoscaling_grp',
        PolicyName='ScaleOutPolicy',
        PolicyType='SimpleScaling',
        AdjustmentType='ChangeInCapacity',
        ScalingAdjustment=1,
        Cooldown=300,  # 5 minutes
    )

    # Scale in policy

    autoscaling_client.put_scaling_policy(
        AutoScalingGroupName='assigment_autoscaling_grp',
        PolicyName='ScaleInPolicy',
        PolicyType='SimpleScaling',
        AdjustmentType='ChangeInCapacity',
        ScalingAdjustment=-1,
        Cooldown=300,  # 5 minutes
    )

    print("Auto Scaling Group and Scaling Policies created successfully.")

    return "autoscaling is created"

result = create_autoscaling
print(result)
