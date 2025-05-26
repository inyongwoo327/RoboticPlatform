from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import time
import re
from datetime import datetime, timedelta
import pytz
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import uvicorn
import os
import json
from kubernetes import client, config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

request_duration = Histogram(
    "log_api_request_duration_seconds", "Request duration in seconds", ["endpoint"]
)
search_count = Counter("log_api_search_total", "Total number of log searches")

try:
    config.load_incluster_config()
    logger.info("Loaded in-cluster Kubernetes configuration")
    k8s_available = True
except Exception as e:
    logger.warning(f"Failed to load in-cluster config, will try local config: {e}")
    try:
        config.load_kube_config()
        logger.info("Loaded local Kubernetes configuration")
        k8s_available = True
    except Exception as e:
        logger.error(f"Failed to load Kubernetes configuration: {e}")
        k8s_available = False

v1 = client.CoreV1Api() if k8s_available else None

# Fallback mock logs for when Kubernetes API is unavailable
mock_logs = [
    {
        "timestamp": datetime.now().isoformat(),
        "level": "info",
        "message": "Robot service started",
        "kubernetes": {"pod_name": "robot-service", "container_name": "robot-service"},
    },
    {
        "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
        "level": "info",
        "message": "Robot added: test-robot-efk",
        "kubernetes": {"pod_name": "robot-service", "container_name": "robot-service"},
    },
    {
        "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat(),
        "level": "warning",
        "message": "High CPU usage detected",
        "kubernetes": {"pod_name": "prometheus", "container_name": "prometheus"},
    },
    {
        "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
        "level": "error",
        "message": "Failed to connect to database",
        "kubernetes": {"pod_name": "robot-service", "container_name": "robot-service"},
    },
    {
        "timestamp": (datetime.now() - timedelta(minutes=20)).isoformat(),
        "level": "info",
        "message": "Dashboard service started",
        "kubernetes": {"pod_name": "dashboard", "container_name": "dashboard"},
    },
]


class LogSearchResult(BaseModel):
    total: int
    logs: List[Dict[Any, Any]]


def parse_log_line(line):
    """Parse a log line to extract timestamp, level, and message.
    This is a simplified example and would need to be adapted to your log format.
    """
    try:
        # Pattern 1: ISO timestamp [LEVEL] Message
        iso_pattern = r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.?\d*Z?) \[(INFO|WARNING|ERROR|DEBUG)\] (.*)"
        # Pattern 2: YYYY-MM-DD HH:MM:SS LEVEL Message
        std_pattern = (
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (INFO|WARNING|ERROR|DEBUG) (.*)"
        )
        # Pattern 3: LEVEL: Message (timestamp is missing)
        simple_pattern = r"(INFO|WARNING|ERROR|DEBUG): (.*)"

        iso_match = re.match(iso_pattern, line, re.IGNORECASE)
        std_match = re.match(std_pattern, line, re.IGNORECASE)
        simple_match = re.match(simple_pattern, line, re.IGNORECASE)

        if iso_match:
            timestamp = iso_match.group(1)
            level = iso_match.group(2).lower()
            message = iso_match.group(3)
        elif std_match:
            timestamp = std_match.group(1)
            level = std_match.group(2).lower()
            message = std_match.group(3)
        elif simple_match:
            timestamp = datetime.now(pytz.UTC).isoformat()
            level = simple_match.group(1).lower()
            message = simple_match.group(2)
        else:
            timestamp = datetime.now(pytz.UTC).isoformat()

            # Try to extract log level by keywords
            level = "info"
            lower_line = line.lower()
            if (
                "error" in lower_line
                or "exception" in lower_line
                or "fail" in lower_line
            ):
                level = "error"
            elif "warn" in lower_line:
                level = "warning"
            elif "debug" in lower_line:
                level = "debug"

            message = line

        return {"timestamp": timestamp, "level": level, "message": message}
    except Exception as e:
        # Fallback for unparseable lines
        logger.warning(f"Failed to parse log line: {e}")
        return {
            "timestamp": datetime.now(pytz.UTC).isoformat(),
            "level": "info",
            "message": line,
        }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/logs", response_model=LogSearchResult)
async def get_logs(
    query: Optional[str] = None,
    level: Optional[str] = None,
    pod: Optional[str] = None,
    container: Optional[str] = None,
    from_time: Optional[str] = None,
    to_time: Optional[str] = None,
    limit: int = Query(100, gt=0, le=1000),
    offset: int = Query(0, ge=0),
):
    with request_duration.labels(endpoint="/logs").time():
        search_count.inc()
        logger.info(f"Searching logs with query: {query}, level: {level}, pod: {pod}")

        all_logs = []

        if k8s_available and v1:
            try:
                # Get all pods in all namespaces
                pods = v1.list_pod_for_all_namespaces(watch=False)

                # Collect logs from each pod
                for pod_item in pods.items:
                    pod_name = pod_item.metadata.name
                    namespace = pod_item.metadata.namespace

                    # Skip if pod filter is specified and doesn't match
                    if pod and pod != pod_name:
                        continue

                    # Get containers for this pod
                    if pod_item.spec and pod_item.spec.containers:
                        for container_item in pod_item.spec.containers:
                            container_name = container_item.name

                            # Skip if container filter is specified and doesn't match
                            if container and container != container_name:
                                continue

                            try:
                                # Get logs for this container
                                pod_logs = v1.read_namespaced_pod_log(
                                    name=pod_name,
                                    namespace=namespace,
                                    container=container_name,
                                    tail_lines=100,  # Limit for performance
                                )

                                # Parse log lines
                                for line in pod_logs.split("\n"):
                                    if not line:
                                        continue

                                    # Parse log line to extract timestamp and level
                                    log_entry = parse_log_line(line)
                                    log_entry["kubernetes"] = {
                                        "pod_name": pod_name,
                                        "container_name": container_name,
                                        "namespace": namespace,
                                    }

                                    # Apply filters
                                    if level and log_entry.get("level") != level:
                                        continue
                                    if query and query.lower() not in line.lower():
                                        continue

                                    all_logs.append(log_entry)
                            except Exception as e:
                                logger.error(
                                    f"Error getting logs for pod {pod_name}, container {container_name}: {e}"
                                )
                                # Continue with next container
            except Exception as e:
                logger.error(f"Error accessing Kubernetes API: {e}")

        if not all_logs:
            logger.info("Using mock logs as fallback")
            all_logs = mock_logs.copy()

            # Apply filters to mock logs
            if query:
                all_logs = [
                    log
                    for log in all_logs
                    if query.lower() in log.get("message", "").lower()
                ]

            if level:
                all_logs = [log for log in all_logs if log.get("level") == level]

            if pod:
                all_logs = [
                    log
                    for log in all_logs
                    if log.get("kubernetes", {}).get("pod_name") == pod
                ]

            if container:
                all_logs = [
                    log
                    for log in all_logs
                    if log.get("kubernetes", {}).get("container_name") == container
                ]

        # Sort logs by timestamp (descending)
        all_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        # Apply pagination
        paginated_logs = all_logs[offset : offset + limit]

        return {"total": len(all_logs), "logs": paginated_logs}


@app.get("/pods")
async def get_pods():
    with request_duration.labels(endpoint="/pods").time():
        if k8s_available and v1:
            try:
                # Get pods from Kubernetes API
                pods = v1.list_pod_for_all_namespaces(watch=False)
                pod_names = [pod.metadata.name for pod in pods.items]
                return {"pods": pod_names}
            except Exception as e:
                logger.error(f"Error getting pods from Kubernetes API: {e}")

        # Use mock pods if K8s not available or error occurred
        pods = list(
            set(
                log.get("kubernetes", {}).get("pod_name")
                for log in mock_logs
                if log.get("kubernetes", {}).get("pod_name")
            )
        )
        return {"pods": pods}


@app.get("/containers")
async def get_containers():
    with request_duration.labels(endpoint="/containers").time():
        if k8s_available and v1:
            try:
                # Get containers from Kubernetes API
                pods = v1.list_pod_for_all_namespaces(watch=False)
                containers = []
                for pod in pods.items:
                    if pod.spec and pod.spec.containers:
                        for container in pod.spec.containers:
                            containers.append(container.name)
                return {"containers": list(set(containers))}
            except Exception as e:
                logger.error(f"Error getting containers from Kubernetes API: {e}")

        # Use mock containers if K8s not available or error occurred
        containers = list(
            set(
                log.get("kubernetes", {}).get("container_name")
                for log in mock_logs
                if log.get("kubernetes", {}).get("container_name")
            )
        )
        return {"containers": containers}


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
