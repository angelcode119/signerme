import asyncio
import time


class BuildQueue:
    def __init__(self):
        self.user_locks = {}
        self.user_start_times = {}

    def is_user_building(self, user_id):
        return user_id in self.user_locks and self.user_locks[user_id].locked()

    def get_user_elapsed_time(self, user_id):
        if user_id in self.user_start_times:
            return int(time.time() - self.user_start_times[user_id])
        return 0

    async def acquire(self, user_id):
        if user_id not in self.user_locks:
            self.user_locks[user_id] = asyncio.Lock()

        await self.user_locks[user_id].acquire()
        self.user_start_times[user_id] = time.time()

    def release(self, user_id):
        if user_id in self.user_start_times:
            del self.user_start_times[user_id]

        if user_id in self.user_locks and self.user_locks[user_id].locked():
            self.user_locks[user_id].release()


build_queue = BuildQueue()
