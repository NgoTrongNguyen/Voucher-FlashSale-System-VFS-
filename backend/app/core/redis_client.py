import redis
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

redis_client = RedisClient()