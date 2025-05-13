#!/bin/bash

echo "Checking if metrics endpoint is accessible..."
curl -s http://localhost:8080/metrics > /dev/null
if [ $? -ne 0 ]; then
  echo "Metrics endpoint not accessible!"
  exit 1
fi

echo "Checking for robots_total metric..."
curl -s http://localhost:8080/metrics | grep -E "robots_total"
if [ $? -ne 0 ]; then
  echo "robots_total metric not found!"
  echo "Current available metrics:"
  curl -s http://localhost:8080/metrics | grep -E "^# HELP|^# TYPE" | sort
  exit 1
else
  echo "✅ robots_total metric found!"
fi