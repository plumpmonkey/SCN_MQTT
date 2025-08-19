#!/bin/bash

# Challenge Runner Script for Light Controller Ransomware Challenge
# This script manages the complete challenge environment for students

echo "Light Controller Ransomware Challenge Runner"
echo "============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker could not be found. Please install Docker."
    exit 1
fi

# Function to start the challenge
start_challenge() {
    echo "Starting challenge environment..."
    
    # Remove any existing mosquitto container
    if sudo docker ps -a --format '{{.Names}}' | grep -q '^mosquitto$'; then
        echo "Removing existing mosquitto container..."
        sudo docker rm -f mosquitto
    fi

    echo "Starting MQTT broker in Docker..."
    # Use our updated config from the challenge directory
    sudo docker run -d --name mosquitto -p 1883:1883 -v $(pwd)/mosquitto_config:/mosquitto/config eclipse-mosquitto

    # Wait for the broker to start
    sleep 5

    echo "Testing MQTT connectivity..."
    if mosquitto_pub -h localhost -t "test/connection" -m "test" 2>/dev/null; then
        echo "✓ MQTT broker is ready"
    else
        echo "✗ MQTT broker connection failed"
        echo "Please check Docker logs: sudo docker logs mosquitto"
        return 1
    fi

    echo ""
    echo "Challenge environment is ready!"
    echo ""
    echo "Mosquitto commands:"
    echo "  mosquitto_pub -h localhost -t '<topic>' -m '<message>'"
    echo "  mosquitto_sub -h localhost -t '#' -v  # Monitor all traffic"
    echo "  mosquitto_sub -h localhost -t '<topic>' -v"  # Monitor a specific topic
    echo ""
    echo ""
    echo "Running infected application: python lights_controller.py"
    python lights_controller.py
}


# Function to stop the challenge
stop_challenge() {
    echo "Stopping challenge environment..."
    if sudo docker ps --format '{{.Names}}' | grep -q '^mosquitto$'; then
        sudo docker stop mosquitto
        sudo docker rm mosquitto-cllenge
        echo "✓ Challenge environment stopped"
    else
        echo "No running challenge environment found"
    fi
}


# Function to show status
show_status() {
    echo "Challenge Environment Status:"
    echo "============================="
    
    if sudo docker ps --format '{{.Names}}' | grep -q '^mosquitto$'; then
        echo "✓ MQTT broker: Running"
        if mosquitto_pub -h localhost -t "test/connection" -m "test" 2>/dev/null; then
            echo "✓ MQTT connectivity: OK"
        else
            echo "✗ MQTT connectivity: Failed"
        fi
    else
        echo "✗ MQTT broker: Not running"
    fi
    
    echo ""
    echo "Container details:"
    sudo docker ps --filter "name=mosquitto" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}


# Main script logic - Default to start if no arguments provided
case "${1:-start}" in
    start)
        start_challenge
        ;;
    stop)
        stop_challenge
        ;;
    status)
        show_status
        ;;
    restart)
        stop_challenge
        sleep 2
        start_challenge
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the challenge environment (default)"
        echo "  stop    - Stop the challenge environment"
        echo "  status  - Show current status"
        echo "  restart - Restart the challenge environment"
        echo ""
        echo "If no command is specified, 'start' will be executed by default."
        exit 1
        ;;
esac
