import asyncio
import time
from datetime import datetime


class BuildQueue:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.current_user = None
        self.start_time = None
        self.queue_count = 0
    
    def is_building(self):
        return self.lock.locked()
    
    def get_current_user(self):
        return self.current_user
    
    def get_elapsed_time(self):
        if self.start_time:
            return int(time.time() - self.start_time)
        return 0
    
    def get_queue_position(self):
        self.queue_count += 1
        return self.queue_count
    
    async def acquire(self, user_id):
        position = None
        
        if self.is_building():
            position = self.get_queue_position()
        
        await self.lock.acquire()
        
        self.current_user = user_id
        self.start_time = time.time()
        self.queue_count = max(0, self.queue_count - 1)
        
        return position
    
    def release(self):
        self.current_user = None
        self.start_time = None
        if self.lock.locked():
            self.lock.release()


build_queue = BuildQueue()
