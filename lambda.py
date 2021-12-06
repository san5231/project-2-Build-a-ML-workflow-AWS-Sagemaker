#Serialize image data lambda function
import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    key = event['s3_key']
    bucket = event['s3_bucket']

    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    s3.download_file(bucket, key, "/tmp/image.png")
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }
#Invoke endpoint classify image_data
import json
import boto3
import base64

#from sagemaker.serializers import IdentitySerializer

# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2021-12-04-11-38"
runtime= boto3.client('runtime.sagemaker')

def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event["image_data"])

    response = runtime.invoke_endpoint(EndpointName=ENDPOINT,
                                        ContentType='image/png',
                                        Body=image)

    inferences = json.loads(response['Body'].read().decode())

    event["inferences"] = inferences

    return {
        'statusCode': 200,
        'body': json.dumps(event)
        }

#Filter inferences confidence

import json


THRESHOLD = .8
meets_threshold = False

def lambda_handler(event, context):

    # Grab the inferences from the event
    inferences = event['inferences']
    meets_threshold = False
    # Check if any values in our inferences are above THRESHOLD
    if inferences[0] > inferences[1]:
        if inferences[0] > THRESHOLD:
            meets_threshold = True
    elif inferences[0] < inferences[1]:
        if inferences[1] > THRESHOLD:
            meets_threshold = True
    else:
        meets_threshold = False


    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
