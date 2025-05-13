# Get the Elasticsearch pod name
ES_POD=$(kubectl get pods -l app=elasticsearch -o name | sed 's/pod\///')

# Set the password for kibana_system user
kubectl exec $ES_POD -- bash -c "
echo 'Setting kibana_system user password...'
curl -s -X POST http://localhost:9200/_security/user/kibana_system/_password -H 'Content-Type: application/json' -u elastic:changeme -d '{
  \"password\": \"changeme\"
}'
echo ''
"