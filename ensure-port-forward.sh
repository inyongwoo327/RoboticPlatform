#!/bin/bash

# Kill any existing port-forwards
pkill -f "kubectl port-forward"

# Wait a moment
sleep 2

# Start all port-forwards
echo "Starting port-forwards..."

kubectl port-forward svc/robot-service 8080:80 > /dev/null 2>&1 &
sleep 1

kubectl port-forward svc/prometheus 9090:9090 > /dev/null 2>&1 &
sleep 1

kubectl port-forward svc/kibana 5601:5601 > /dev/null 2>&1 &
sleep 1

kubectl port-forward svc/elasticsearch 9200:9200 > /dev/null 2>&1 &
sleep 1

kubectl port-forward svc/grafana 3000:3000 > /dev/null 2>&1 &
sleep 1

echo "Port-forwards started. Testing connections..."

# Test each service
echo "Testing robot-service..."
curl -s http://localhost:8080/robots > /dev/null && echo "✅ Robot service is accessible" || echo "❌ Robot service failed"

echo "Testing prometheus..."
curl -s http://localhost:9090 > /dev/null && echo "✅ Prometheus is accessible" || echo "❌ Prometheus failed"

echo "Testing elasticsearch..."
# Try with authentication first
if curl -s -u elastic:changeme http://localhost:9200 > /dev/null; then
  echo "✅ Elasticsearch is accessible (with authentication)"
else
  # Try without authentication as fallback
  curl -s http://localhost:9200 > /dev/null && echo "✅ Elasticsearch is accessible (no auth)" || echo "❌ Elasticsearch failed"
fi

echo "Testing kibana..."
KIBANA_RESPONSE=$(curl -s -v http://localhost:5601 2>&1)
HTTP_CODE=$(echo "$KIBANA_RESPONSE" | grep -o "< HTTP/[0-9.]* [0-9]*" | grep -o "[0-9]*$")
if [[ "$HTTP_CODE" =~ ^(200|302)$ ]]; then
  echo "✅ Kibana is accessible (HTTP code: $HTTP_CODE)"
else
  echo "❌ Kibana failed (HTTP code: $HTTP_CODE)"
  echo "Response details: $(echo "$KIBANA_RESPONSE" | grep -A 2 -B 2 "< HTTP")"
fi

echo -e "\nAll port-forwards are running. Services are accessible on:"
echo "- Robot Service: http://localhost:8080"
echo "- Prometheus: http://localhost:9090"
echo "- Kibana: http://localhost:5601"
echo "- Elasticsearch: http://localhost:9200"
echo "- Grafana: http://localhost:3000"