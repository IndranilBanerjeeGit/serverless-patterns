#!/bin/bash

# Setup script for Python ActiveMQ message sender
echo "Setting up Python ActiveMQ message sender..."

# Install required Python packages
echo "Installing required Python packages..."
pip3 install -r requirements.txt

# Make the commands script executable
chmod +x commands.sh

echo "Setup complete!"
echo ""
echo "Usage:"
echo "  sh commands.sh <batch_name> <number_of_messages>"
echo "  Example: sh commands.sh firstbatch 10"
