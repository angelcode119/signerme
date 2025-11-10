import asyncio
import time


class BuildQueue:
    def __init__(self, max_concurrent=5):
        self.user_locks = {}
        self.user_start_times = {}
        self.global_semaphore = asyncio.Semaphore(max_concurrent)
        self.active_count = 0
        self.waiting_count = 0
        self.count_lock = asyncio.Lock()

    def is_user_building(self, user_id):
        return user_id in self.user_locks and self.user_locks[user_id].locked()

    def get_user_elapsed_time(self, user_id):
        if user_id in self.user_start_times:
            return int(time.time() - self.user_start_times[user_id])
        return 0

    async def get_queue_status(self):
        async with self.count_lock:
            return self.active_count, self.waiting_count

    async def acquire(self, user_id):
        if user_id not in self.user_locks:
            self.user_locks[user_id] = asyncio.Lock()

        await self.user_locks[user_id].acquire()
        
        async with self.count_lock:
            self.waiting_count += 1
        
        await self.global_semaphore.acquire()
        
        async with self.count_lock:
            self.waiting_count -= 1
            self.active_count += 1
        
        self.user_start_times[user_id] = time.time()

    def release(self, user_id):
        if user_id in self.user_start_times:
            del self.user_start_times[user_id]

        if user_id in self.user_locks and self.user_locks[user_id].locked():
            self.user_locks[user_id].release()
        
        try:
            self.global_semaphore.release()
            asyncio.create_task(self._decrease_active_count())
        except:
            pass
    
    async def _decrease_active_count(self):
        async with self.count_lock:
            if self.active_count > 0:
                self.active_count -= 1


build_queue = BuildQueue()
