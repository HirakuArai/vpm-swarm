#!/usr/bin/env python3
"""
Memory API - Phase-1
Provides persistent storage with Redis fallback to JSON file.
"""

import json
import os
from typing import Any, Dict, List, Optional
from pathlib import Path


class Memory:
    """
    Memory storage class with Redis/JSON fallback.
    Uses Redis (host redis:6379) if available, otherwise ./data/memory.json
    """
    
    def __init__(self, redis_host: str = "redis", redis_port: int = 6379, 
                 json_path: str = "./data/memory.json"):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.json_path = Path(json_path)
        self.redis_client = None
        self.use_redis = False
        
        # Try to connect to Redis first
        self._init_redis()
        
        # If Redis is not available, ensure JSON file directory exists
        if not self.use_redis:
            self._init_json_storage()
    
    def _init_redis(self):
        """Initialize Redis connection if available"""
        try:
            import redis
            self.redis_client = redis.Redis(
                host=self.redis_host, 
                port=self.redis_port, 
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            self.use_redis = True
            print(f"[Memory] Connected to Redis at {self.redis_host}:{self.redis_port}")
        except (ImportError, Exception) as e:
            print(f"[Memory] Redis not available, falling back to JSON: {e}")
            self.use_redis = False
    
    def _init_json_storage(self):
        """Initialize JSON file storage"""
        # Create data directory if it doesn't exist
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create empty JSON file if it doesn't exist
        if not self.json_path.exists():
            with open(self.json_path, 'w') as f:
                json.dump({}, f)
        
        print(f"[Memory] Using JSON storage at {self.json_path}")
    
    def _load_json_data(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        try:
            with open(self.json_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json_data(self, data: Dict[str, Any]):
        """Save data to JSON file"""
        with open(self.json_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def put(self, id: str, data: Any) -> bool:
        """
        Store data with given ID
        
        Args:
            id: Unique identifier for the data
            data: Data to store (must be JSON serializable)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.use_redis:
                # Store as JSON string in Redis
                self.redis_client.set(id, json.dumps(data))
            else:
                # Store in JSON file
                json_data = self._load_json_data()
                json_data[id] = data
                self._save_json_data(json_data)
            
            return True
        except Exception as e:
            print(f"[Memory] Error storing data for ID {id}: {e}")
            return False
    
    def get(self, id: str) -> Optional[Any]:
        """
        Retrieve data by ID
        
        Args:
            id: Unique identifier for the data
            
        Returns:
            Data if found, None otherwise
        """
        try:
            if self.use_redis:
                # Get JSON string from Redis and parse
                data_str = self.redis_client.get(id)
                if data_str is None:
                    return None
                return json.loads(data_str)
            else:
                # Get from JSON file
                json_data = self._load_json_data()
                return json_data.get(id)
        
        except Exception as e:
            print(f"[Memory] Error retrieving data for ID {id}: {e}")
            return None
    
    def list_ids(self) -> List[str]:
        """
        List all stored IDs
        
        Returns:
            List of all stored IDs
        """
        try:
            if self.use_redis:
                # Get all keys from Redis
                return self.redis_client.keys("*")
            else:
                # Get all keys from JSON file
                json_data = self._load_json_data()
                return list(json_data.keys())
        
        except Exception as e:
            print(f"[Memory] Error listing IDs: {e}")
            return []
    
    def delete(self, id: str) -> bool:
        """
        Delete data by ID
        
        Args:
            id: Unique identifier for the data to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.use_redis:
                result = self.redis_client.delete(id)
                return result > 0
            else:
                json_data = self._load_json_data()
                if id in json_data:
                    del json_data[id]
                    self._save_json_data(json_data)
                    return True
                return False
        
        except Exception as e:
            print(f"[Memory] Error deleting data for ID {id}: {e}")
            return False
    
    def clear_all(self) -> bool:
        """
        Clear all stored data
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.use_redis:
                self.redis_client.flushdb()
            else:
                self._save_json_data({})
            
            return True
        except Exception as e:
            print(f"[Memory] Error clearing all data: {e}")
            return False