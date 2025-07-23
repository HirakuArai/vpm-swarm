#!/usr/bin/env python3
"""
Synthesizer Cell - Hyper-Swarm Phase-0
Data synthesis and output generation role for the swarm system.
"""

import os
import asyncio
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="Synthesizer Cell", version="0.1.0")

# Global state for the synthesizer
synthesizer_state = {
    "status": "active",
    "synthesis_results": [],
    "input_sources": ["planner", "curator", "archivist", "watcher"],
    "synthesis_count": 0,
    "current_synthesis": None
}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Synthesizer Cell is running", "role": "synthesizer"}

@app.get("/health")
async def health():
    """Health check for Kubernetes probes"""
    return {"status": "healthy", "role": "synthesizer"}

@app.get("/status")
async def get_status():
    """Get current synthesizer status"""
    return {
        "status": synthesizer_state["status"],
        "synthesis_count": synthesizer_state["synthesis_count"],
        "results_count": len(synthesizer_state["synthesis_results"]),
        "input_sources": synthesizer_state["input_sources"],
        "current_synthesis": synthesizer_state["current_synthesis"]
    }

@app.post("/synthesize")
async def create_synthesis(request: Dict[str, Any]):
    """Create synthesis from multiple input sources"""
    inputs = request.get("inputs", [])
    synthesis_type = request.get("type", "standard")
    
    # Simulate synthesis process
    synthesis_result = {
        "id": f"synthesis_{synthesizer_state['synthesis_count']}",
        "timestamp": asyncio.get_event_loop().time(),
        "type": synthesis_type,
        "input_count": len(inputs),
        "inputs": inputs,
        "output": {
            "summary": f"Synthesized from {len(inputs)} sources",
            "key_points": [f"Point {i+1}" for i in range(min(3, len(inputs)))],
            "confidence": min(0.9, len(inputs) * 0.2),
            "recommendations": ["Action A", "Action B", "Action C"]
        },
        "metadata": {
            "processing_time": 0.5,
            "quality_score": hash(str(inputs)) % 100,
            "source_diversity": len(set(inp.get("source", "") for inp in inputs))
        }
    }
    
    synthesizer_state["synthesis_results"].append(synthesis_result)
    synthesizer_state["synthesis_count"] += 1
    synthesizer_state["current_synthesis"] = synthesis_result["id"]
    
    return JSONResponse({
        "status": "synthesis_complete",
        "synthesis_id": synthesis_result["id"],
        "output": synthesis_result["output"],
        "metadata": synthesis_result["metadata"]
    })

@app.get("/results")
async def get_synthesis_results(limit: int = 20):
    """Get recent synthesis results"""
    results = synthesizer_state["synthesis_results"]
    recent_results = results[-limit:] if len(results) > limit else results
    
    return {
        "results": recent_results,
        "total_count": len(synthesizer_state["synthesis_results"])
    }

@app.get("/result/{synthesis_id}")
async def get_synthesis_result(synthesis_id: str):
    """Get specific synthesis result by ID"""
    for result in synthesizer_state["synthesis_results"]:
        if result["id"] == synthesis_id:
            return result
    
    raise HTTPException(status_code=404, detail="Synthesis result not found")

@app.post("/aggregate")
async def aggregate_data(request: Dict[str, Any]):
    """Aggregate data from multiple cells for synthesis"""
    cell_data = request.get("cell_data", {})
    
    # Simulate aggregation logic
    aggregated_inputs = []
    for cell_name, data in cell_data.items():
        aggregated_inputs.append({
            "source": cell_name,
            "data": data,
            "weight": 1.0,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    # Auto-trigger synthesis with aggregated data
    synthesis_request = {
        "inputs": aggregated_inputs,
        "type": "aggregated"
    }
    
    return await create_synthesis(synthesis_request)

async def synthesizer_loop():
    """Main async loop for synthesizer operations"""
    while True:
        print(f"[Synthesizer] Active... {synthesizer_state['synthesis_count']} syntheses completed")
        
        # Simulate periodic cleanup
        if len(synthesizer_state["synthesis_results"]) > 100:
            synthesizer_state["synthesis_results"] = synthesizer_state["synthesis_results"][-50:]
            print("[Synthesizer] Cleaned up old synthesis results")
        
        await asyncio.sleep(8)

@app.on_event("startup")
async def startup_event():
    """Initialize synthesizer on startup"""
    print("[Synthesizer] Starting synthesizer cell...")
    asyncio.create_task(synthesizer_loop())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)