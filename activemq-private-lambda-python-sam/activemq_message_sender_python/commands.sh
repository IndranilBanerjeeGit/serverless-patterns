#!/bin/bash

# Pass a random string as the first command-line argument to this shell script. It will be used to uniquely identify a batch of messages
# Pass an integer as the second command-line argument to this shell script < 500. For example if you want to send 100 messages, pass 100
# Example: sh commands.sh firstbatch 100

python3 activemq_producer.py ACTIVEMQ_BROKER_ENDPOINT ACTIVEMQ_QUEUE_NAME $1 $2
