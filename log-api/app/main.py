from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import uvicorn
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, in production specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
request_duration = Histogram("log_api_request_duration_seconds", "Request duration in seconds", ["endpoint"])
search_count = Counter("log_api_search_total", "Total number of log searches")

# Elasticsearch client
es_host = os.getenv("ELASTICSEARCH_HOST", "elasticsearch")
es_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
es = Elasticsearch([f"http://{es_host}:{es_port}"])

class LogSearchResult(BaseModel):
    total: int
    logs: List[Dict[Any, Any]]

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
    offset: int = Query(0, ge=0)
):
    with request_duration.labels(endpoint="/logs").time():
        search_count.inc()
        logger.info(f"Searching logs with query: {query}, level: {level}, pod: {pod}")
        
        # Build Elasticsearch query
        must_conditions = []
        
        if query:
            must_conditions.append({"query_string": {"query": query}})
        
        if level:
            must_conditions.append({"match": {"kubernetes.labels.level": level}})
        
        if pod:
            must_conditions.append({"match": {"kubernetes.pod_name": pod}})
        
        if container:
            must_conditions.append({"match": {"kubernetes.container_name": container}})
        
        date_range = {}
        if from_time:
            date_range["gte"] = from_time
        if to_time:
            date_range["lte"] = to_time
        
        if date_range:
            must_conditions.append({"range": {"@timestamp": date_range}})
        
        search_query = {
            "query": {
                "bool": {
                    "must": must_conditions if must_conditions else [{"match_all": {}}]
                }
            },
            "sort": [{"@timestamp": {"order": "desc"}}],
            "from": offset,
            "size": limit
        }
        
        try:
            result = es.search(index="k8s-*", body=search_query)
            logs = [hit["_source"] for hit in result["hits"]["hits"]]
            total = result["hits"]["total"]["value"]
            return {"total": total, "logs": logs}
        except Exception as e:
            logger.error(f"Error searching logs: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error searching logs: {str(e)}")

@app.get("/pods")
async def get_pods():
    with request_duration.labels(endpoint="/pods").time():
        try:
            # Get unique pod names from Elasticsearch
            agg_query = {
                "size": 0,
                "aggs": {
                    "pods": {
                        "terms": {
                            "field": "kubernetes.pod_name.keyword",
                            "size": 100
                        }
                    }
                }
            }
            
            result = es.search(index="k8s-*", body=agg_query)
            pods = [bucket["key"] for bucket in result["aggregations"]["pods"]["buckets"]]
            return {"pods": pods}
        except Exception as e:
            logger.error(f"Error fetching pods: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching pods: {str(e)}")

@app.get("/containers")
async def get_containers():
    with request_duration.labels(endpoint="/containers").time():
        try:
            # Get unique container names from Elasticsearch
            agg_query = {
                "size": 0,
                "aggs": {
                    "containers": {
                        "terms": {
                            "field": "kubernetes.container_name.keyword",
                            "size": 100
                        }
                    }
                }
            }
            
            result = es.search(index="k8s-*", body=agg_query)
            containers = [bucket["key"] for bucket in result["aggregations"]["containers"]["buckets"]]
            return {"containers": containers}
        except Exception as e:
            logger.error(f"Error fetching containers: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching containers: {str(e)}")

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)