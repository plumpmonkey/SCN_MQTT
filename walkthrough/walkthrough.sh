#!/bin/bash

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
	echo "Docker could not be found. Please install Docker."
	exit 1
fi

# Remove any existing mosquitto container
if sudo docker ps -a --format '{{.Names}}' | grep -q '^mosquitto$'; then
	echo "Removing existing mosquitto container..."
	sudo docker rm -f mosquitto
fi

echo "Starting MQTT broker in Docker..."
sudo docker run -d --name mosquitto -p 1883:1883 -v $(pwd)/mosquitto_config:/mosquitto/config eclipse-mosquitto

# Wait for the broker to start
sleep 5

echo "Starting the hvac controller script..."
python hvac.py

# Stop the broker when done
echo "Stopping MQTT broker..."
sudo docker stop mosquitto
sudo docker rm mosquitto

echo "All processes finished."
