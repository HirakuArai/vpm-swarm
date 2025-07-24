#!/usr/bin/env python3
"""
Planner Cell - Hyper-Swarm Phase-0
Planning and coordination role for the swarm system.
"""

import os
import sys
import asyncio
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Add parent directory to path to import common modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.memory import Memory

app = FastAPI(title="Planner Cell", version="0.1.0")

# Global state for the planner
planner_state = {
    "status": "active",
    "cycle_count": 0,
    "last_plan": None,
    "connected_cells": []
}

# Initialize memory instance
memory = Memory()

# Pydantic models for memory API
class MemoryRequest(BaseModel):
    id: str
    data: Any

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Planner Cell is running", "role": "planner"}

@app.get("/health")
async def health():
    """Health check for Kubernetes probes"""
    return {"status": "healthy", "role": "planner"}

@app.get("/status")
async def get_status():
    """Get current planner status"""
    return planner_state

@app.post("/plan")
async def create_plan(request: Dict[str, Any]):
    """Create a new plan for the swarm cycle"""
    plan_data = {
        "plan_id": f"plan_{planner_state['cycle_count'] + 1}",
        "timestamp": asyncio.get_event_loop().time(),
        "tasks": request.get("tasks", []),
        "priority": request.get("priority", "normal")
    }
    
    planner_state["last_plan"] = plan_data
    planner_state["cycle_count"] += 1
    
    return JSONResponse({"status": "plan_created", "plan": plan_data})

@app.get("/current-plan")
async def get_current_plan():
    """Get the current active plan"""
    if planner_state["last_plan"] is None:
        raise HTTPException(status_code=404, detail="No active plan")
    
    return planner_state["last_plan"]

# Memory API endpoints
@app.post("/memory")
async def store_memory(request: MemoryRequest):
    """Store data in memory with given ID"""
    success = memory.put(request.id, request.data)
    if success:
        return JSONResponse({"status": "stored", "id": request.id})
    else:
        raise HTTPException(status_code=500, detail="Failed to store data")

@app.get("/memory/{id}")
async def get_memory(id: str):
    """Retrieve data from memory by ID"""
    data = memory.get(id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"No data found for ID: {id}")
    
    return {"id": id, "data": data}

@app.get("/memory")
async def list_memory_ids():
    """List all memory IDs"""
    ids = memory.list_ids()
    return {"ids": ids}

async def planner_loop():
    """Main async loop for planner operations"""
    while True:
        print(f"[Planner] Cycle {planner_state['cycle_count']} - Planning...")
        
        # Simulate planning work
        await asyncio.sleep(5)
        
        # Update cycle count periodically
        planner_state["cycle_count"] += 1

@app.on_event("startup")
async def startup_event():
    """Initialize planner on startup"""
    print("[Planner] Starting planner cell...")
    asyncio.create_task(planner_loop())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)