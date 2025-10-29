#!/usr/bin/env python3

import sys
import json
import csv
import boto3
import stomp
import time
from datetime import datetime
from typing import List, Dict

class Person:
    def __init__(self, firstname="", lastname="", company="", street="", city="", 
                 county="", state="", zip_code="", home_phone="", cell_phone="", 
                 email="", website=""):
        self.firstname = firstname
        self.lastname = lastname
        self.company = company
        self.street = street
        self.city = city
        self.county = county
        self.state = state
        self.zip = zip_code
        self.homePhone = home_phone
        self.cellPhone = cell_phone
        self.email = email
        self.website = website
    
    def to_json(self) -> str:
        return json.dumps({
            "firstname": self.firstname,
            "lastname": self.lastname,
            "company": self.company,
            "street": self.street,
            "city": self.city,
            "county": self.county,
            "state": self.state,
            "zip": self.zip,
            "homePhone": self.homePhone,
            "cellPhone": self.cellPhone,
            "email": self.email,
            "website": self.website
        })

class SecretsManagerDecoder:
    @staticmethod
    def get_username_and_password():
        """
        Retrieve ActiveMQ credentials from AWS Secrets Manager
        This is a placeholder - in the actual implementation, you would
        retrieve the secret ARN from environment variables or parameters
        """
        # For demo purposes, return default credentials
        # In production, use boto3 to get secrets from Secrets Manager
        return {"username": "admin", "password": "admin"}

class JsonActiveMQProducer:
    def __init__(self):
        pass
    
    @staticmethod
    def read_data_file() -> List[str]:
        """Read the CSV data file and return list of lines"""
        people = []
        try:
            with open('us-500.csv', 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    people.append(','.join(row))
        except FileNotFoundError:
            print("Error: us-500.csv file not found")
            sys.exit(1)
        return people
    
    @staticmethod
    def get_person_from_line(line: str) -> Person:
        """Parse CSV line and create Person object"""
        # Handle CSV with quoted fields containing commas
        import csv
        from io import StringIO
        
        reader = csv.reader(StringIO(line))
        fields = next(reader)
        
        if len(fields) >= 12:
            return Person(
                firstname=fields[0],
                lastname=fields[1],
                company=fields[2],
                street=fields[3],
                city=fields[4],
                county=fields[5],
                state=fields[6],
                zip_code=fields[7],
                home_phone=fields[8],
                cell_phone=fields[9],
                email=fields[10],
                website=fields[11]
            )
        return Person()
    
    @staticmethod
    def get_today_date() -> str:
        """Get current date formatted string"""
        return datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
    
    @staticmethod
    def send_messages(activemq_endpoint: str, activemq_username: str, 
                     activemq_password: str, activemq_queue: str, 
                     seeder_key: str, number_of_messages: int):
        """Send messages to ActiveMQ"""
        
        people = JsonActiveMQProducer.read_data_file()
        messages_to_send = min(number_of_messages, len(people) - 1)  # -1 to skip header
        
        # Parse endpoint to get host and port
        # Format: ssl://b-xxx.mq.region.amazonaws.com:61617
        if "://" in activemq_endpoint:
            protocol_host = activemq_endpoint.split("://")[1]
            if ":" in protocol_host:
                host, port = protocol_host.split(":")
                port = int(port)
            else:
                host = protocol_host
                port = 61617
        else:
            host = activemq_endpoint
            port = 61617
        
        # Create STOMP connection
        conn = stomp.Connection([(host, port)])
        conn.set_listener('', stomp.PrintingListener())
        
        try:
            conn.connect(activemq_username, activemq_password, wait=True)
            
            for i in range(1, messages_to_send + 1):
                if i < len(people):
                    person = JsonActiveMQProducer.get_person_from_line(people[i])
                    person_json = person.to_json()
                    
                    # Send message
                    headers = {
                        'correlation-id': f"{seeder_key}-{i}",
                        'type': 'TextMessage',
                        'MessageBatchIdentifier': seeder_key,
                        'MessageNumberInBatch': str(i),
                        'persistent': 'true'
                    }
                    
                    conn.send(body=person_json, destination=f'/queue/{activemq_queue}', headers=headers)
                    current_time = int(time.time() * 1000)
                    print(f"Sent out one message - Number {i} at time = {current_time}")
            
        except Exception as e:
            print(f"Error sending messages: {e}")
            raise
        finally:
            conn.disconnect()

def main():
    if len(sys.argv) != 5:
        print("Usage: python activemq_producer.py <endpoint> <queue> <seeder_key> <num_messages>")
        sys.exit(1)
    
    activemq_endpoint = sys.argv[1]
    activemq_queue = sys.argv[2]
    seeder_key = sys.argv[3]
    num_messages = int(sys.argv[4])
    
    # Get credentials
    credentials = SecretsManagerDecoder.get_username_and_password()
    activemq_username = credentials["username"]
    activemq_password = credentials["password"]
    
    # Create message key with date
    activemq_message_key = f"{seeder_key}-{JsonActiveMQProducer.get_today_date()}"
    
    try:
        JsonActiveMQProducer.send_messages(
            activemq_endpoint, 
            activemq_username, 
            activemq_password, 
            activemq_queue, 
            activemq_message_key, 
            num_messages
        )
        print("Messages sent successfully")
    except Exception as e:
        print(f"Exception occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
