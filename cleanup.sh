#!/bin/bash
# Exit on any error
set -e

echo "Start cleanup of robotics platform."

echo "Remove application services."
echo "Delete dashboard resources."
kubectl delete -f manifests/dashboard-ingress.yaml --ignore-not-found
kubectl delete -f manifests/dashboard-service.yaml --ignore-not-found
kubectl delete -f manifests/dashboard-deployment.yaml --ignore-not-found

echo "Delete robot-service resources."
kubectl delete -f manifests/robot-service-ingress.yaml --ignore-not-found
kubectl delete -f manifests/robot-service-service.yaml --ignore-not-found
kubectl delete -f manifests/robot-service-deployment.yaml --ignore-not-found

echo "Delete log-api resources."
kubectl delete -f manifests/log-api-ingress.yaml --ignore-not-found
kubectl delete -f manifests/log-api-service.yaml --ignore-not-found
kubectl delete -f manifests/log-api-deployment.yaml --ignore-not-found

echo "Remove observability stack."
echo "Delete Prometheus resources."
kubectl delete -f manifests/prometheus-ingress.yaml --ignore-not-found
kubectl delete -f manifests/prometheus-service.yaml --ignore-not-found
kubectl delete -f manifests/prometheus-deployment.yaml --ignore-not-found
kubectl delete -f manifests/prometheus-configmap.yaml --ignore-not-found

echo "Remove RBAC resources."
echo "Delete Log API RBAC."
kubectl delete -f manifests/log-api-rbac.yaml --ignore-not-found

echo "Delete Prometheus RBAC."
kubectl delete -f manifests/prometheus-rbac.yaml --ignore-not-found

echo "Clean up Docker images."
echo "The following images would be manually removed if needed:"
eval $(minikube docker-env)
docker images | grep -E 'robot-service|log-api|dashboard'
docker rmi dashboard:latest
docker rmi log-api:latest
docker rmi robot-service:latest