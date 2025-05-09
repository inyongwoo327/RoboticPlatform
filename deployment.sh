#!/bin/bash

set -e

echo "Ensure minikube is running."
minikube status || minikube start

echo "Enable ingress addon."
minikube addons enable ingress

echo "Set up docker environment for minikube."
eval $(minikube docker-env)

echo "Build docker images."
echo "Build robot-service."
docker build -t robot-service:latest ./robot-service

echo "Build log-api."
docker build -t log-api:latest ./log-api

echo "Build dashboard."
docker build -t dashboard:latest ./dashboard

echo "Create RBAC resources."
echo "Creat Prometheus RBAC."
kubectl apply -f manifests/prometheus-rbac.yaml

echo "Create Log API RBAC."
kubectl apply -f manifests/log-api-rbac.yaml

echo "Deploy observability stack."
echo "Deploy Prometheus."
kubectl apply -f manifests/prometheus-configmap.yaml
kubectl apply -f manifests/prometheus-deployment.yaml
kubectl apply -f manifests/prometheus-service.yaml
kubectl apply -f manifests/prometheus-ingress.yaml

echo "Deploy application services."
echo "Deploy robot-service."
kubectl apply -f manifests/robot-service-deployment.yaml
kubectl apply -f manifests/robot-service-service.yaml
kubectl apply -f manifests/robot-service-ingress.yaml

echo "Deploy log-api."
kubectl apply -f manifests/log-api-deployment.yaml
kubectl apply -f manifests/log-api-service.yaml
kubectl apply -f manifests/log-api-ingress.yaml

echo "Deploy dashboard."
kubectl apply -f manifests/dashboard-deployment.yaml
kubectl apply -f manifests/dashboard-service.yaml
kubectl apply -f manifests/dashboard-ingress.yaml

echo "Wait for pods to be ready."
kubectl wait --for=condition=ready pod --all --timeout=300s || true

echo "You can do this with the following command:"
echo "echo \"127.0.0.1 dashboard.local robot.local prometheus.local log-api.local\" | sudo tee -a /etc/hosts"

echo "Deployment complete!"
echo "Access the services at:"
echo "- Dashboard: http://dashboard.local"
echo "- Robot Service: http://robot.local"
echo "- Log API: http://log-api.local"
echo "- Prometheus: http://prometheus.local"

echo "Check pod status:"
kubectl get pods