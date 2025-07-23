#!/usr/bin/env python3
"""
Curator Cell - Hyper-Swarm Phase-0
Content curation and filtering role for the swarm system.
"""

import os
import asyncio
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="Curator Cell", version="0.1.0")

# Global state for the curator
curator_state = {
    "status": "active",
    "curated_items": [],
    "filter_rules": ["quality", "relevance", "safety"],
    "processed_count": 0
}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Curator Cell is running", "role": "curator"}

@app.get("/health")
async def health():
    """Health check for Kubernetes probes"""
    return {"status": "healthy", "role": "curator"}

@app.get("/status")
async def get_status():
    """Get current curator status"""
    return curator_state

@app.post("/curate")
async def curate_content(request: Dict[str, Any]):
    """Process and curate incoming content"""
    content_items = request.get("items", [])
    
    curated_results = []
    for item in content_items:
        # Simulate curation logic
        score = hash(str(item)) % 100  # Simple scoring
        
        if score > 30:  # Basic quality threshold
            curated_item = {
                "original": item,
                "score": score,
                "tags": ["curated", "approved"],
                "curator_id": "curator-cell",
                "timestamp": asyncio.get_event_loop().time()
            }
            curated_results.append(curated_item)
            curator_state["curated_items"].append(curated_item)
    
    curator_state["processed_count"] += len(content_items)
    
    return JSONResponse({
        "status": "curation_complete",
        "processed": len(content_items),
        "curated": len(curated_results),
        "results": curated_results
    })

@app.get("/curated")
async def get_curated_items():
    """Get all curated items"""
    return {
        "items": curator_state["curated_items"],
        "total_count": len(curator_state["curated_items"])
    }

@app.put("/filters")
async def update_filters(filters: List[str]):
    """Update curation filter rules"""
    curator_state["filter_rules"] = filters
    return {"status": "filters_updated", "filters": filters}

async def curator_loop():
    """Main async loop for curator operations"""
    while True:
        print(f"[Curator] Processing... {curator_state['processed_count']} items processed")
        
        # Simulate periodic cleanup of old curated items
        if len(curator_state["curated_items"]) > 1000:
            curator_state["curated_items"] = curator_state["curated_items"][-500:]
            print("[Curator] Cleaned up old curated items")
        
        await asyncio.sleep(7)

@app.on_event("startup")
async def startup_event():
    """Initialize curator on startup"""
    print("[Curator] Starting curator cell...")
    asyncio.create_task(curator_loop())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)