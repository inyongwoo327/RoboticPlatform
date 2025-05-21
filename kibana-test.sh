#!/bin/bash

# Wait a moment to ensure port-forward is ready
sleep 3

echo "Testing connection to robot service..."
curl -s http://localhost:8080/robots

echo -e "\n\nAdding robots..."

for i in {12..13}; do
  # Make the request and save both response body and status code
  response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" \
    http://localhost:8080/robots \
    -d '{"id": "demo-'$i'", "name": "Demo Robot '$i'", "status": "online"}')
  
  # Extract status code from last line
  status_code=$(echo "$response" | tail -n1)
  
  # Extract response body (everything except the last line)
  body=$(echo "$response" | sed '$d')
  
  if [[ $status_code == "200" ]]; then
    echo "Added robot demo-$i"
  elif [[ $status_code == "400" && $body == *"already exists"* ]]; then
    echo "Robot demo-$i already exists, skipping..."
  else
    echo "Failed to add robot demo-$i (HTTP $status_code): $body"
  fi
  
  sleep 1
done

# Check if robots were added
echo -e "\n\nGetting list of robots..."
curl -s http://localhost:8080/robots | jq '.'

echo -e "\n\nChecking metrics for robots_total..."
curl -s http://localhost:8080/metrics | grep robots_total

echo -e "\n\nOpening Kibana..."
open http://localhost:5601