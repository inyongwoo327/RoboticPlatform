# Robotic Platform

A cloud-native application that simulates part of a robotics platform deployed on a local Kubernetes cluster using Minikube.

## Project Objective: 
Build and deploy a small application that simulates part of a robotics cloud platform. It should include:
● A backend service that tracks robots.
● A frontend dashboard that visualizes and interacts with data.
● Local Kubernetes deployment via Minikube.
● Observability (metrics and logs) for all services in the cluster.

## Project Overview
This project implements a robotics platform with the following components:

- **Backend Service**: A REST API for tracking robots (FastAPI)
- **Dashboard**: A web UI for robot management, metrics visualization, and log viewing (Vue.js)
- **Log API**: A service for aggregating and exposing logs from all pods
- **Prometheus**: Metrics collection and monitoring for all services
- **Kubernetes Infrastructure**: Deployments, services, and ingress resources

## Architecture

The Architecture diagram is in 'Architecture diagram.jpeg' file.
The platform follows a microservices architecture running in a Minikube Kubernetes cluster:

- **User Interface**: Accessible via domain names configured in /etc/hosts
- **Ingress Controller**: Routes traffic to appropriate services based on host names
- **Service Layer**: Manages communication between pods and external access
- **Pod Layer**: Contains the actual application containers
- **Observability**: Prometheus collects metrics from all services

### Port Configuration

| Service | Service Port | Target Port | Node Port |
|---------|-------------|-------------|-----------|
| Dashboard | 80 | 80 | 30880 |
| Robot Service | 80 | 8080 | 30080 |
| Log API | 80 | 8080 | 30180 |
| Prometheus | 9090 | 9090 | 30090 |

## Local Setup Instructions

### Prerequisites

- Docker
- Minikube
- kubectl
- Git

### 1. Clone the Repository

git clone https://github.com/inyongwoo327/RoboticPlatform.git
cd robotics-platform

### 2. Start Minikube

minikube start
minikube addons enable ingress

### 3. Setup Local Domain Names

$(minikube ip) dashboard.local robot.local prometheus.local log-api.local

### 4. Build Docker Images

Configure Docker to use Minikube's Docker daemon:
eval $(minikube docker-env)

Build the services:

docker build -t robot-service:1.0 ./robot-service
docker build -t dashboard:1.0 ./dashboard
docker build -t log-api:1.0 ./log-api

### 5. Create RBAC Resources

Apply the RBAC configurations for Prometheus and Log API:

kubectl apply -f manifests/prometheus-rbac.yaml
kubectl apply -f manifests/log-api-rbac.yaml

### 6. Deploy Services

Apply all Kubernetes manifests:
kubectl apply -f manifests/

### 7. Verify Deployment

Check whether all the pods are running properly:
kubectl get pods

### 8. Access the Application
Open your browser and navigate to:
Dashboard: http://dashboard.local

## Design Decisions and Tradeoffs

### Microservices Architecture

Pro: Clean separation of concerns, independent scaling, technology flexibility
Con: Increased complexity, network overhead
Decision: Microservices architecture chosen to demonstrate cloud-native design patterns

### Mock Logs in Log API

Pro: Demonstrates functionality without complex log aggregation
Con: Not showing real-time logs from actual services
Decision: Mock logs provide a consistent demo experience; code is in place to extend to real logs
Further suggestions: To simplify the implementations of displaying searchable logs, using EFK Stacks would be recommended.

### Frontend Framework (Vue.js)

Pro: Lightweight, component-based architecture, TypeScript support
Con: Smaller ecosystem compared to React
Decision: Vue.js chosen for its simplicity and performance for this project scale

### Prometheus for Monitoring

Pro: Industry standard, well-integrated with Kubernetes
Con: Requires additional RBAC configuration
Decision: The standard choice for Kubernetes monitoring, providing solid metrics foundation

### Future Improvements

Persistence Layer: Add a database (PostgreSQL or MongoDB) for storing robot data
Real Log Aggregation: Implement ELK or similar stack for real log collection
Authentication: Add user authentication and authorization
CI/CD Pipeline: Automate testing and deployment
Helm Charts: Package the application for easier deployment
Resource Limits: Fine-tune resource requests and limits for all pods
Enhanced Metrics: Add business metrics beyond basic technical monitoring
High Availability: Configure services for resilience and redundancy