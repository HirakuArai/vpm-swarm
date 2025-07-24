#!/usr/bin/env python3
"""
E2E tests for Memory API
Tests the memory API endpoints via docker compose planner-cell
"""

import json
import requests
import pytest
import time
from typing import Dict, Any


class TestMemoryAPI:
    """E2E tests for the Memory API via planner-cell"""
    
    BASE_URL = "http://localhost:8001"  # planner-cell port from docker-compose
    
    @classmethod
    def setup_class(cls):
        """Wait for services to be ready"""
        max_retries = 30
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = requests.get(f"{cls.BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    print(f"[Test] Planner service is ready")
                    break
            except requests.exceptions.RequestException:
                pass
            
            retry_count += 1
            time.sleep(2)
        
        if retry_count >= max_retries:
            pytest.fail("Planner service did not become ready in time")
    
    def test_memory_store_and_retrieve(self):
        """Test storing and retrieving data via memory API"""
        # Test data
        test_id = "test_charter_001"
        test_data = {
            "type": "charter",
            "content": "Implement advanced swarm coordination",
            "priority": "high",
            "timestamp": "2024-01-01T10:00:00Z"
        }
        
        # Store data via POST /memory
        store_response = requests.post(
            f"{self.BASE_URL}/memory",
            json={"id": test_id, "data": test_data},
            headers={"Content-Type": "application/json"}
        )
        
        assert store_response.status_code == 200
        store_result = store_response.json()
        assert store_result["status"] == "stored"
        assert store_result["id"] == test_id
        
        # Retrieve data via GET /memory/{id}
        get_response = requests.get(f"{self.BASE_URL}/memory/{test_id}")
        
        assert get_response.status_code == 200
        get_result = get_response.json()
        assert get_result["id"] == test_id
        assert get_result["data"] == test_data
    
    def test_memory_conversation_log(self):
        """Test storing and retrieving conversation log data"""
        # Test conversation log data
        log_id = "conversation_log_001"
        log_data = {
            "type": "conversation_log",
            "messages": [
                {"role": "user", "content": "What should we focus on?"},
                {"role": "assistant", "content": "We should prioritize swarm coordination."},
                {"role": "user", "content": "How do we implement that?"}
            ],
            "session_id": "sess_123",
            "timestamp": "2024-01-01T10:05:00Z"
        }
        
        # Store conversation log
        store_response = requests.post(
            f"{self.BASE_URL}/memory",
            json={"id": log_id, "data": log_data}
        )
        
        assert store_response.status_code == 200
        
        # Retrieve conversation log
        get_response = requests.get(f"{self.BASE_URL}/memory/{log_id}")
        
        assert get_response.status_code == 200
        retrieved_data = get_response.json()
        assert retrieved_data["data"] == log_data
    
    def test_memory_list_ids(self):
        """Test listing all memory IDs"""
        # Store multiple test entries
        test_entries = [
            {"id": "list_test_1", "data": {"value": "first"}},
            {"id": "list_test_2", "data": {"value": "second"}},
            {"id": "list_test_3", "data": {"value": "third"}}
        ]
        
        # Store all entries
        for entry in test_entries:
            response = requests.post(f"{self.BASE_URL}/memory", json=entry)
            assert response.status_code == 200
        
        # List all IDs
        list_response = requests.get(f"{self.BASE_URL}/memory")
        assert list_response.status_code == 200
        
        result = list_response.json()
        assert "ids" in result
        
        # Check that our test IDs are in the list
        stored_ids = result["ids"]
        for entry in test_entries:
            assert entry["id"] in stored_ids
    
    def test_memory_not_found(self):
        """Test retrieving non-existent memory ID"""
        non_existent_id = "non_existent_id_12345"
        
        response = requests.get(f"{self.BASE_URL}/memory/{non_existent_id}")
        assert response.status_code == 404
        
        error_result = response.json()
        assert "detail" in error_result
        assert non_existent_id in error_result["detail"]
    
    def test_memory_complex_data_structures(self):
        """Test storing complex nested data structures"""
        complex_id = "complex_data_test"
        complex_data = {
            "metadata": {
                "version": "1.0",
                "created_by": "planner-cell",
                "tags": ["important", "phase-1", "memory-api"]
            },
            "content": {
                "tasks": [
                    {
                        "id": "task_001",
                        "description": "Initialize memory system",
                        "status": "completed",
                        "assignee": "archivist-cell"
                    },
                    {
                        "id": "task_002", 
                        "description": "Test memory persistence",
                        "status": "in_progress",
                        "assignee": "curator-cell"
                    }
                ],
                "dependencies": {
                    "task_002": ["task_001"]
                }
            },
            "statistics": {
                "total_tasks": 2,
                "completed_tasks": 1,
                "success_rate": 0.5
            }
        }
        
        # Store complex data
        store_response = requests.post(
            f"{self.BASE_URL}/memory",
            json={"id": complex_id, "data": complex_data}
        )
        assert store_response.status_code == 200
        
        # Retrieve and verify complex data
        get_response = requests.get(f"{self.BASE_URL}/memory/{complex_id}")
        assert get_response.status_code == 200
        
        retrieved = get_response.json()
        assert retrieved["data"] == complex_data
        
        # Verify nested structure integrity
        assert retrieved["data"]["metadata"]["version"] == "1.0"
        assert len(retrieved["data"]["content"]["tasks"]) == 2
        assert retrieved["data"]["statistics"]["success_rate"] == 0.5
    
    def test_memory_persistence_across_requests(self):
        """Test that memory persists across multiple API calls"""
        persistence_id = "persistence_test"
        initial_data = {"step": 1, "message": "Initial data"}
        
        # Store initial data
        requests.post(f"{self.BASE_URL}/memory", json={"id": persistence_id, "data": initial_data})
        
        # Make multiple GET requests to ensure data persists
        for i in range(5):
            response = requests.get(f"{self.BASE_URL}/memory/{persistence_id}")
            assert response.status_code == 200
            data = response.json()["data"]
            assert data == initial_data
            time.sleep(0.1)  # Small delay between requests