from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import statistics
import numpy as np
import os

app = FastAPI()

# Proper CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# Handle OPTIONS explicitly (important for Vercel)
@app.options("/api/latency")
async def options_handler():
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )

# Load telemetry
file_path = os.path.join(os.path.dirname(__file__), "..", "q-vercel-latency.json")

with open(file_path) as f:
    data = json.load(f)

@app.post("/api/latency")
async def calculate_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 0)

    response = {}

    for region in regions:
        region_data = [d for d in data if d["region"] == region]

        if not region_data:
            continue

        latencies = [d["latency_ms"] for d in region_data]
        uptimes = [d["uptime_pct"] for d in region_data]

        response[region] = {
            "avg_latency": statistics.mean(latencies),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": statistics.mean(uptimes),
            "breaches": sum(1 for l in latencies if l > threshold),
        }

    return JSONResponse(
        content=response,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )
