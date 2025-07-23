#!/usr/bin/env python3
"""
Watcher Cell - Hyper-Swarm Phase-0
Monitoring and observation role for the swarm system.
"""

import os
import asyncio
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="Watcher Cell", version="0.1.0")

# Global state for the watcher
watcher_state = {
    "status": "active",
    "observations": [],
    "monitoring_targets": ["planner", "curator", "archivist", "synthesizer"],
    "alert_count": 0,
    "last_scan": None
}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Watcher Cell is running", "role": "watcher"}

@app.get("/health")
async def health():
    """Health check for Kubernetes probes"""
    return {"status": "healthy", "role": "watcher"}

@app.get("/status")
async def get_status():
    """Get current watcher status"""
    return {
        "status": watcher_state["status"],
        "observations_count": len(watcher_state["observations"]),
        "monitoring_targets": watcher_state["monitoring_targets"],
        "alert_count": watcher_state["alert_count"],
        "last_scan": watcher_state["last_scan"]
    }

@app.post("/observe")
async def record_observation(request: Dict[str, Any]):
    """Record a new observation"""
    observation = {
        "id": f"obs_{len(watcher_state['observations'])}",
        "timestamp": asyncio.get_event_loop().time(),
        "source": request.get("source", "unknown"),
        "event_type": request.get("event_type", "info"),
        "data": request.get("data", {}),
        "severity": request.get("severity", "low")
    }
    
    watcher_state["observations"].append(observation)
    
    # Check for alert conditions
    if observation["severity"] in ["high", "critical"]:
        watcher_state["alert_count"] += 1
    
    return JSONResponse({
        "status": "observation_recorded",
        "observation_id": observation["id"],
        "severity": observation["severity"]
    })

@app.get("/observations")
async def get_observations(limit: int = 50, severity: str = None):
    """Get recent observations"""
    observations = watcher_state["observations"]
    
    if severity:
        observations = [obs for obs in observations if obs["severity"] == severity]
    
    # Return most recent observations
    recent_observations = observations[-limit:] if len(observations) > limit else observations
    
    return {
        "observations": recent_observations,
        "total_count": len(watcher_state["observations"]),
        "filtered_count": len(observations)
    }

@app.get("/alerts")
async def get_alerts():
    """Get current alert summary"""
    high_severity_obs = [
        obs for obs in watcher_state["observations"] 
        if obs["severity"] in ["high", "critical"]
    ]
    
    return {
        "alert_count": watcher_state["alert_count"],
        "recent_alerts": high_severity_obs[-10:],
        "alert_summary": {
            "critical": len([obs for obs in high_severity_obs if obs["severity"] == "critical"]),
            "high": len([obs for obs in high_severity_obs if obs["severity"] == "high"])
        }
    }

async def watcher_loop():
    """Main async loop for watcher operations"""
    while True:
        current_time = asyncio.get_event_loop().time()
        watcher_state["last_scan"] = current_time
        
        print(f"[Watcher] Scanning... {len(watcher_state['observations'])} observations recorded")
        
        # Simulate periodic health checks of other cells
        for target in watcher_state["monitoring_targets"]:
            # Record simulated health check
            health_obs = {
                "source": f"{target}-cell",
                "event_type": "health_check",
                "data": {"status": "healthy", "response_time": 0.1},
                "severity": "info"
            }
            # This would normally be an HTTP call to other cells
        
        # Clean up old observations (keep last 1000)
        if len(watcher_state["observations"]) > 1000:
            watcher_state["observations"] = watcher_state["observations"][-500:]
        
        await asyncio.sleep(4)

@app.on_event("startup")
async def startup_event():
    """Initialize watcher on startup"""
    print("[Watcher] Starting watcher cell...")
    asyncio.create_task(watcher_loop())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)