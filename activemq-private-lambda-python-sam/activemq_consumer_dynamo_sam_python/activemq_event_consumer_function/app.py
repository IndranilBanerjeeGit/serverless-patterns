import json
import base64
import boto3
import os
import time
from typing import Dict, Any

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event: Dict[str, Any], context) -> str:
    """
    Lambda function handler for processing ActiveMQ messages
    """
    logger = context.get_logger() if hasattr(context, 'get_logger') else print
    
    logger("Begin Event *************")
    logger(json.dumps(event))
    logger("End Event ***************")
    
    table_name = os.environ.get('DYNAMO_DB_TABLE')
    table = dynamodb.Table(table_name) if table_name else None
    
    try:
        for message in event.get('messages', []):
            process_message(message, event, table, logger)
        return "200"
    except Exception as e:
        logger(f"An exception happened - {str(e)}")
        return "500"

def process_message(message: Dict[str, Any], event: Dict[str, Any], table, logger) -> None:
    """
    Process individual ActiveMQ message
    """
    current_time = int(time.time() * 1000)  # Current time in milliseconds
    
    logger("Begin Message *************")
    logger(json.dumps(message))
    logger("End Message ***************")
    
    # Decode base64 message data
    logger("Begin Message Body *************")
    base64_data = message.get('data', '')
    decoded_data = ""
    if base64_data:
        decoded_bytes = base64.b64decode(base64_data)
        decoded_data = decoded_bytes.decode('utf-8')
    
    logger(decoded_data)
    logger("End Message Body ***************")
    
    # Log message details
    log_message_details(message, event, logger)
    
    # Parse person data from decoded message
    person = json.loads(decoded_data)
    logger(f"This person = {json.dumps(person)}")
    
    # Insert into DynamoDB if not running locally
    aws_sam_local = os.environ.get('AWS_SAM_LOCAL')
    if not aws_sam_local and table:
        insert_into_dynamodb(message, person, event, table, logger, current_time)

def log_message_details(message: Dict[str, Any], event: Dict[str, Any], logger) -> None:
    """
    Log ActiveMQ message details
    """
    logger(f"EventSource = {event.get('eventSource', '')}")
    logger(f"EventSourceARN = {event.get('eventSourceArn', '')}")
    logger(f"CorrelationID = {message.get('correlationID', '')}")
    logger(f"MessageID = {message.get('messageID', '')}")
    logger(f"MessageType = {message.get('messageType', '')}")
    logger(f"ReplyTo = {message.get('replyTo', '')}")
    logger(f"Type = {message.get('type', '')}")
    logger(f"BrokerInTime = {message.get('brokerInTime', '')}")
    logger(f"BrokerOutTime = {message.get('brokerOutTime', '')}")
    logger(f"DeliveryMode = {message.get('deliveryMode', '')}")
    logger(f"Expiration = {message.get('expiration', '')}")
    logger(f"Priority = {message.get('priority', '')}")
    logger(f"TimeStamp = {message.get('timestamp', '')}")
    
    destination = message.get('destination', {})
    logger(f"Queue = {destination.get('physicalName', '')}")
    logger(f"WhetherRedelivered = {message.get('redelivered', False)}")

def insert_into_dynamodb(message: Dict[str, Any], person: Dict[str, Any], 
                        event: Dict[str, Any], table, logger, receive_time: int) -> None:
    """
    Insert message and person data into DynamoDB
    """
    message_id = message.get('messageID', '')
    logger(f"Now inserting a row in DynamoDB for messageID = {message_id}")
    
    # Prepare DynamoDB item
    item = {
        'MessageID': message_id,
        'EventSource': event.get('eventSource', ''),
        'EventSourceARN': event.get('eventSourceArn', ''),
        'Firstname': person.get('firstname', ''),
        'Lastname': person.get('lastname', ''),
        'Company': person.get('company', ''),
        'Street': person.get('street', ''),
        'City': person.get('city', ''),
        'County': person.get('county', ''),
        'State': person.get('state', ''),
        'Zip': person.get('zip', ''),
        'Cellphone': person.get('cellPhone', ''),
        'Homephone': person.get('homePhone', ''),
        'Email': person.get('email', ''),
        'Website': person.get('website', ''),
        'CorrelationID': message.get('correlationID', ''),
        'MessageType': message.get('messageType', ''),
        'ReplyTo': message.get('replyTo'),
        'Type': message.get('type'),
        'BrokerInTime': message.get('brokerInTime', 0),
        'BrokerOutTime': message.get('brokerOutTime', 0),
        'DeliveryMode': message.get('deliveryMode', 0),
        'Expiration': message.get('expiration', 0),
        'Priority': message.get('priority', 0),
        'TimeStamp': message.get('timestamp', 0),
        'Queue': message.get('destination', {}).get('physicalName', ''),
        'WhetherRedelivered': message.get('redelivered', False),
        'ReceiveTime': receive_time
    }
    
    # Remove None values
    item = {k: v for k, v in item.items() if v is not None}
    
    try:
        table.put_item(Item=item)
        logger(f"Now done inserting a row in DynamoDB for messageID = {message_id}")
    except Exception as e:
        logger(f"Error inserting into DynamoDB: {str(e)}")
        raise
