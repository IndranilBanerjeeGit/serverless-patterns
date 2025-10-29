# activemq-private-lambda-python-sam
# Python AWS Lambda ActiveMQ (in private subnets) consumer, using AWS SAM

This is the Python version of the Java ActiveMQ Lambda consumer pattern. This pattern demonstrates a Lambda function written in Python that consumes messages from Amazon MQ (Apache ActiveMQ).

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders:

- `activemq_consumer_dynamo_sam_python/activemq_event_consumer_function/app.py` - Code for the application's Lambda function that will listen for Amazon MQ (Apache ActiveMQ) messages and write them to a DynamoDB table
- `activemq_message_sender_python/activemq_producer.py` - Code for publishing messages with JSON payload into an Amazon MQ (ActiveMQ cluster), that will in turn be consumed by the Lambda function
- `activemq_consumer_dynamo_sam_python/template.yaml` - A SAM template that defines the application's Lambda function
- `ActiveMQAndClientEC2_Python.yaml` - A CloudFormation template file that can be used to deploy an Amazon MQ (Apache ActiveMQ) cluster and also deploy an EC2 machine with all prerequisites already installed for Python development
- `activemq_queue_browser.sh` - A shell script that can be used to connect to the Amazon MQ (Apache ActiveMQ) brokers using the activemq command-line tool

## Requirements

* [Create an AWS account](https://portal.aws.amazon.com/gp/aws/developer/registration/index.html) if you do not already have one and log in. The IAM user that you use must have sufficient permissions to make necessary AWS service calls and manage AWS resources.
* Python 3.12 or later
* AWS SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)

## Deploy the CloudFormation template

Use the `ActiveMQAndClientEC2_Python.yaml` CloudFormation template to create the Amazon MQ (Apache ActiveMQ) cluster and client EC2 machine configured for Python development.

## Build and Deploy the Python Lambda function

Navigate to the Python SAM project directory:

```bash
cd activemq_consumer_dynamo_sam_python
```

Build your application with the `sam build` command:

```bash
sam build
```

## Test the build locally

Test a single function by invoking it directly with a test event:

```bash
sam local invoke --event events/event.json
```

## Deploy the sample application

To deploy your application for the first time, run the following:

```bash
sam deploy --capabilities CAPABILITY_IAM --no-confirm-changeset --no-disable-rollback --region $AWS_REGION --stack-name activemq-lambda-python-sam --guided
```

The sam deploy command will package and deploy your application to AWS, with a series of prompts. You can accept all the defaults by hitting Enter, or provide the same parameters as the Java version:

* **Stack Name**: activemq-lambda-python-sam
* **AWS Region**: The AWS region you want to deploy your app to
* **Parameter ActiveMQBrokerArn**: The ARN of the ActiveMQBroker that was created by the CloudFormation template
* **Parameter ActiveMQQueue**: The name of the ActiveMQ queue from which the lambda function will consume messages
* **Parameter SecretsManagerSecretForMQ**: The ARN of the secret that has username/password for Active MQ
* **Parameter Subnet1**: The first of the three private subnets where the ActiveMQ cluster is deployed
* **Parameter Subnet2**: The second of the three private subnets where the ActiveMQ cluster is deployed
* **Parameter Subnet3**: The third of the three private subnets where the ActiveMQ cluster is deployed
* **Parameter SecurityGroup**: The security group of the lambda function

## Test the application

Once the lambda function is deployed, send some messages to the Amazon MQ (Apache ActiveMQ) cluster using the Python message sender.

Navigate to the Python message sender directory:

```bash
cd activemq_message_sender_python
```

Install the required Python packages:

```bash
pip3 install -r requirements.txt
```

Run the message sender script:

```bash
sh ./commands.sh firstBatch 10
```

This will send 10 messages to the ActiveMQ queue. The Lambda function will process these messages and store them in the DynamoDB table named `ActiveMQDynamoDBTablePython`.

You can check CloudWatch logs for the Lambda function execution details and view the records in the DynamoDB console.

## Key Differences from Java Version

1. **Runtime**: Uses Python 3.12 instead of Java
2. **Dependencies**: Uses `boto3` for AWS SDK and `stomp.py` for ActiveMQ connectivity
3. **DynamoDB Table**: Creates `ActiveMQDynamoDBTablePython` instead of `ActiveMQDynamoDBTableJava`
4. **Function Name**: `python-activemq-consumer-dynamodb-sam` instead of `java-activemq-consumer-dynamodb-sam`
5. **Simpler Code**: Python version is more concise while maintaining the same functionality

## Cleanup

Clean up the Lambda function by running:

```bash
cd activemq_consumer_dynamo_sam_python
sam delete
```

Then delete the CloudFormation stack that created the Amazon MQ cluster and EC2 machine from the AWS console.

## Architecture

The Python version maintains the same architecture as the Java version:

1. ActiveMQ messages are sent to a queue in a private subnet
2. Lambda function is triggered by ActiveMQ events
3. Lambda processes messages and extracts person data
4. Data is stored in DynamoDB table
5. All operations are logged to CloudWatch

The Python implementation provides the same functionality with a more concise codebase and faster cold start times.
