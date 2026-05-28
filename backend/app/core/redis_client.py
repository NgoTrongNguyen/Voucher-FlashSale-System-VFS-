try:
    import redis  # type: ignore[import]
except ImportError as exc:
    raise ImportError(
        "Missing required dependency 'redis'. Install it with 'pip install redis'."
    ) from exc

import os
from typing import Any, List
from app.config import settings

class RedisClient:
    def __init__(self):
        # Init Redis connection pool with keep-alive options
        self.pool = redis.ConnectionPool.from_url(
            settings.Redis_URL,
            max_connections = settings.REDIS_POOL_SIZE,
            socket_timeout = settings.REDIS_SOCKET_TIMEOUT,
            socket_keepalive = True,
            socket_keepalive_options = {
                1: 1, # TCP_KEEPIDLE
                2: 2, # TCP_KEEPINTVL
                3: 3, # TCP_KEEPCNT
            } if os.name != 'nt' else {}
        )
        self.client = redis.Redis(connection_pool=self.pool)
        self.lua_scripts = {}

    # Operation to connect to Redis
    def ping(self) -> bool:
        try:
            return self.client.ping()
        except redis.RedisError as e:
            print(f"Redis ping failed: {e}")
            return False
    
    # Close Redis connection pool
    def close(self):
        self.pool.disconnect()

    #--------------------
    # Lua script management
    #--------------------

    def load_lua_script(self, script_name: str, script_path: str):
        # Load and register a Lua script from file
        try:
            with open(script_path, 'r') as f:
                script_content = f.read()
                self.lua_scripts[script_name] = self.client.register_script(script_content)
            print(f"Loaded Lua script: {script_name}")
        except FileNotFoundError:
            print(f"Script not found: {script_path}")
    
    def execute_lua_script(self, script_name: str, keys: List[str], args: List[Any]) -> Any:
        # Execute a registered Lua script 
        if script_name not in self.lua_scripts:
            raise ValueError(f"Script not loaded: {script_name}")
        script = self.lua_scripts[script_name]
        return script(keys=keys, args=args)

    #--------------------
    # Basic Redis operations
    #--------------------
    
    def set(self, key: str, value: Any, ex: int = None) ->bool:
        # Set a key-value pair with optional expiration
        return self.client.set(key, value, ex = ex)
    
    def get(self, key: str) -> Any:
        # Get the value of a key
        return self.client.get(key)
    
    def delete(self, key: str) -> int:
        # Delete a key
        return self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        # Check if a key exists
        return self.client.exists(key) > 0
    
    def incr(self, key: str, amount: int = 1) -> int:
        # Increment the integer value
        return self.client.incr(key, amount)
    
    def decr(self, key: str, amount: int = 1) -> int:
        # Decrement the integer value
        return self.client.decr(key, amount)
    
    def expire(self, key: str, time: int) -> bool:
        # Set a key's time to live
        return self.client.expire(key, time)
    
    def ttl(self, key: str) -> int:
        # Get the time to live of a key
        return self.client.ttl(key)
    
    #--------------------
    # Inventory operations (Voucher)
    #--------------------

    def get_inventory(self, voucher_id: int) -> int:
        # Get the inventory count for a voucher
        inventory_key = f"voucher:{voucher_id}:inventory"
        value = self.get(inventory_key)
        return int(value) if value else None
    
    def set_inventory(self, voucher_id: int, count: int, ex: int = None):
        # Set the inventory count for a voucher
        inventory_key = f"voucher:{voucher_id}:inventory"
        self.set(inventory_key, count, ex = ex)

    def decrement_inventory(self, voucher_id: int) -> int:
        # Decrement the inventory count
        inventory_key = f"voucher:{voucher_id}:inventory"
        return self.decr(inventory_key)  

    #--------------------
    # User lock operations (Voucher)
    #--------------------

    def set_lock_user(self, user_id: int, cooldown: int):
        key = f"user:{user_id}:lock"
        self.set(key, "1", ex = cooldown)

    def is_user_locked(self, user_id: int) -> bool:
        key = f"user:{user_id}:lock"
        return self.exists(key)

redis_client = RedisClient()