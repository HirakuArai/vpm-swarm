#!/usr/bin/env python3
"""
Smoke test for Hyper-Swarm Phase-0
Tests basic connectivity and health of all cells.
"""

import pytest
import requests
import time
from typing import Dict, Any

# Default cell endpoints (can be overridden with environment variables)
CELL_ENDPOINTS = {
    "planner": "http://localhost:8001",
    "curator": "http://localhost:8002", 
    "archivist": "http://localhost:8003",
    "watcher": "http://localhost:8004",
    "synthesizer": "http://localhost:8005"
}

def test_planner_health():
    """Test planner cell health endpoint"""
    response = requests.get(f"{CELL_ENDPOINTS['planner']}/health", timeout=5)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["role"] == "planner"

def test_planner_root():
    """Test planner cell root endpoint"""
    response = requests.get(CELL_ENDPOINTS["planner"], timeout=5)
    assert response.status_code == 200
    
    data = response.json()
    assert "Planner Cell is running" in data["message"]
    assert data["role"] == "planner"

def test_curator_health():
    """Test curator cell health endpoint"""
    response = requests.get(f"{CELL_ENDPOINTS['curator']}/health", timeout=5)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["role"] == "curator"

def test_archivist_health():
    """Test archivist cell health endpoint"""
    response = requests.get(f"{CELL_ENDPOINTS['archivist']}/health", timeout=5)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["role"] == "archivist"

def test_watcher_health():
    """Test watcher cell health endpoint"""
    response = requests.get(f"{CELL_ENDPOINTS['watcher']}/health", timeout=5)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["role"] == "watcher"

def test_synthesizer_health():
    """Test synthesizer cell health endpoint"""
    response = requests.get(f"{CELL_ENDPOINTS['synthesizer']}/health", timeout=5)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["role"] == "synthesizer"

def test_all_cells_basic_functionality():
    """Test basic functionality of all cells"""
    
    # Test planner plan creation
    plan_response = requests.post(
        f"{CELL_ENDPOINTS['planner']}/plan",
        json={"tasks": ["test_task"], "priority": "high"},
        timeout=5
    )
    assert plan_response.status_code == 200
    assert plan_response.json()["status"] == "plan_created"
    
    # Test curator content curation
    curator_response = requests.post(
        f"{CELL_ENDPOINTS['curator']}/curate",
        json={"items": [{"content": "test content", "source": "test"}]},
        timeout=5
    )
    assert curator_response.status_code == 200
    assert curator_response.json()["status"] == "curation_complete"
    
    # Test archivist data archival
    archive_response = requests.post(
        f"{CELL_ENDPOINTS['archivist']}/archive",
        json={
            "id": "test_data",
            "content": {"test": "data"},
            "metadata": {"source": "smoke_test"}
        },
        timeout=5
    )
    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == "archived"
    
    # Test watcher observation recording
    observe_response = requests.post(
        f"{CELL_ENDPOINTS['watcher']}/observe",
        json={
            "source": "smoke_test",
            "event_type": "test_event",
            "data": {"test": True},
            "severity": "info"
        },
        timeout=5
    )
    assert observe_response.status_code == 200
    assert observe_response.json()["status"] == "observation_recorded"
    
    # Test synthesizer synthesis
    synthesis_response = requests.post(
        f"{CELL_ENDPOINTS['synthesizer']}/synthesize",
        json={
            "inputs": [
                {"source": "test", "data": {"key": "value"}},
                {"source": "test2", "data": {"key2": "value2"}}
            ],
            "type": "test_synthesis"
        },
        timeout=5
    )
    assert synthesis_response.status_code == 200
    assert synthesis_response.json()["status"] == "synthesis_complete"

def test_cell_status_endpoints():
    """Test that all cells return proper status information"""
    for cell_name, endpoint in CELL_ENDPOINTS.items():
        response = requests.get(f"{endpoint}/status", timeout=5)
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        print(f"[{cell_name}] Status: {data}")

if __name__ == "__main__":
    # Run basic smoke test
    print("Running Hyper-Swarm Phase-0 Smoke Test...")
    
    try:
        test_planner_health()
        test_planner_root()
        print("✓ Planner cell tests passed")
        
        test_curator_health()
        print("✓ Curator cell tests passed")
        
        test_archivist_health()
        print("✓ Archivist cell tests passed")
        
        test_watcher_health()
        print("✓ Watcher cell tests passed")
        
        test_synthesizer_health()
        print("✓ Synthesizer cell tests passed")
        
        test_all_cells_basic_functionality()
        print("✓ All cells basic functionality tests passed")
        
        test_cell_status_endpoints()
        print("✓ All cell status endpoints working")
        
        print("\n🎉 All smoke tests passed! Hyper-Swarm Phase-0 is functional.")
        
    except Exception as e:
        print(f"\n❌ Smoke test failed: {e}")
        exit(1)