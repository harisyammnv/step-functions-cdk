import boto3

sm = boto3.client('sagemaker')

def lambda_handler(event, context):

    job_name = event['ProcessingJobName']

    response = sm.describe_processing_job(
        ProcessingJobName=job_name
    )
    job_status = response["ProcessingJobStatus"]
    print(response)
    
    if response["ProcessingJobStatus"] == "Completed":
            return {"status": "SUCCEEDED", 'ProcessingJobName': job_name,
        'ProcessingJobStatus': job_status, "event": event}
    if response["ProcessingJobStatus"] == "Failed":
        return {"status": "FAILED", "event": event}
    else:
        return {"status":"WAIT", 'ProcessingJobName': job_name,
        'ProcessingJobStatus': job_status}