import os
import json
import boto3
import time

from typing import Optional


sm = boto3.client('sagemaker')


def get_unique_job_name(base_name: str):
    """ Returns a unique job name based on a given base_name
        and the current timestamp """
    timestamp = time.strftime('%Y%m%d-%H%M%S')
    return f'{base_name}-{timestamp}'


def get_file_input(name: str, input_s3_uri: str, output_path: str):
    """ Returns the input file configuration
        Modify if you need different input method """
    return {
        'InputName': name,
        'S3Input': {
            'S3Uri': input_s3_uri,
            'LocalPath': output_path,
            'S3DataType': 'S3Prefix',
            'S3InputMode': 'File'
        }
    }

def get_file_output(name: str, local_path: str, ouput_s3_uri: str):
    """ Returns output file configuration
        Modify for different output method """
    return {
        'OutputName': name,
        'S3Output': {
            'S3Uri': ouput_s3_uri,
            'LocalPath': local_path,
            'S3UploadMode': 'EndOfJob'
        }
    }


def get_app_spec(image_uri: str, container_arguments: Optional[str], entrypoint: Optional[str]):
    app_spec = {
        'ImageUri': image_uri
    }
    
    if container_arguments is not None:
        app_spec['ContainerArguments'] = container_arguments

    if entrypoint is not None:
        # Similar to ScriptProcessor in sagemaker SDK:
        # Run a custome script within the container
        app_spec['ContainerEntrypoint'] = ['python3', entrypoint]

    return app_spec


def lambda_handler(event, context):

    # (1) Get inputs
    #input_uri = event['S3Input']
    #ouput_uri = event['S3Output']
    image_uri = event['ImageUri']
    #script_uri = event.get('S3Script', None)  # Optional: S3 path to custom script

    # Get execution environment
    role = event['RoleArn']
    instance_type = event['InstanceType']
    volume_size = event['VolumeSizeInGB']
    max_runtime = event.get('MaxRuntimeInSeconds', 3600)  # Default: 1h
    container_arguments = event.get('ContainerArguments', None) # Optional: Arguments to pass to the container
    entrypoint = "src/main.py"  # Entrypoint to the container, will be set automatically later

    job_name = get_unique_job_name('sm-processing-job')  # (2)

    #
    # (3) Specify inputs / Outputs
    #

    #inputs = [
    #    get_file_input('data', input_uri, '/opt/ml/processing/input')
    #]

    #if script_uri is not None:
    #    # Add custome script to the container (similar to ScriptProcessor)
    #    inputs.append(get_file_input('script', script_uri, '/opt/ml/processing/code'))

        # Make script new entrypoint for the container
    #    filename = os.path.basename(script_uri)
    #    entrypoint = f'/opt/ml/processing/code/{filename}'

    #outputs = [
    #    get_file_output('output_data', '/opt/ml/processing/output', ouput_uri)
    #]

    #
    # Define execution environment
    #

    app_spec = get_app_spec(image_uri, container_arguments, entrypoint)

    cluster_config = {
        'InstanceCount': 1,
        'InstanceType': instance_type,
        'VolumeSizeInGB': volume_size
    }

    #
    # (4) Create processing job and return job ARN
    #
    sm.create_processing_job(
        ProcessingJobName=job_name,
        ProcessingResources={
            'ClusterConfig': cluster_config
        },
        StoppingCondition={
            'MaxRuntimeInSeconds': max_runtime
        },
        AppSpecification=app_spec,
        RoleArn=role
    )

    return {
        'ProcessingJobName': job_name
    }