#!/bin/bash

# Function to start a port-forward in background
start_forward() {
    local service=$1
    local local_port=$2
    local service_port=$3
    local namespace=${4:-default}
    
    echo "Starting port-forward for $service..."
    kubectl port-forward -n $namespace svc/$service $local_port:$service_port &
    
    # Store the process ID for each port-forward
    echo $! >> /tmp/port-forward-pids.txt
}

# Clean up any existing port-forwards from previous runs
if [ -f /tmp/port-forward-pids.txt ]; then
    while read pid; do
        kill $pid 2>/dev/null
    done < /tmp/port-forward-pids.txt
    rm /tmp/port-forward-pids.txt
fi

# Create new pids file
touch /tmp/port-forward-pids.txt

# Start all port-forwards
start_forward robot-service 8080 80
start_forward prometheus 9090 9090
start_forward kibana 5601 5601
start_forward elasticsearch 9200 9200
start_forward grafana 3000 3000

echo ""
echo "All port-forwards started successfully!"
echo ""
echo "Available services:"
echo "- Robot Service: http://localhost:8080/robots"
echo "- Prometheus: http://localhost:9090"
echo "- Kibana: http://localhost:5601"
echo "- Elasticsearch: http://localhost:9200"
echo "- Grafana: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all port-forwards."
echo ""

# Function to clean up on exit
cleanup() {
    echo ""
    echo "Stopping all port-forwards..."
    while read pid; do
        kill $pid 2>/dev/null
    done < /tmp/port-forward-pids.txt
    rm /tmp/port-forward-pids.txt
    echo "All port-forwards stopped."
}

# Set up trap to clean up on exit
trap cleanup EXIT INT TERM

wait