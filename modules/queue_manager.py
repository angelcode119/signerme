import asyncio
import time
import logging

logger = logging.getLogger(__name__)


class BuildQueue:
    def __init__(self, max_concurrent=1):  # Only 1 user at a time!
        self.user_locks = {}
        self.user_start_times = {}
        self.building_users = {}  # Add this for admin panel tracking
        self.global_semaphore = asyncio.Semaphore(max_concurrent)
        self.active_count = 0
        self.waiting_count = 0
        self.count_lock = asyncio.Lock()
        self.max_concurrent = max_concurrent
        logger.info(f"BuildQueue initialized (max_concurrent={max_concurrent})")

    def is_user_building(self, user_id):
        """Check if user is currently building"""
        try:
            return user_id in self.user_locks and self.user_locks[user_id].locked()
        except Exception as e:
            logger.error(f"Error checking if user {user_id} is building: {str(e)}")
            return False

    def get_user_elapsed_time(self, user_id):
        """Get elapsed time for user's current build"""
        try:
            if user_id in self.user_start_times:
                return int(time.time() - self.user_start_times[user_id])
            return 0
        except Exception as e:
            logger.error(f"Error getting elapsed time for user {user_id}: {str(e)}")
            return 0

    async def get_queue_status(self):
        """Get current queue status (active, waiting)"""
        try:
            async with self.count_lock:
                return self.active_count, self.waiting_count
        except Exception as e:
            logger.error(f"Error getting queue status: {str(e)}")
            return 0, 0

    async def acquire(self, user_id):
        """Acquire build slot for user"""
        try:
            if user_id not in self.user_locks:
                self.user_locks[user_id] = asyncio.Lock()

            await self.user_locks[user_id].acquire()
            
            async with self.count_lock:
                self.waiting_count += 1
            
            logger.debug(f"User {user_id} waiting for build slot...")
            await self.global_semaphore.acquire()
            
            async with self.count_lock:
                self.waiting_count -= 1
                self.active_count += 1
            
            self.user_start_times[user_id] = time.time()
            self.building_users[user_id] = time.time()
            
            logger.info(f"User {user_id} acquired build slot (active={self.active_count}/{self.max_concurrent})")
            
        except Exception as e:
            logger.error(f"Error acquiring build slot for user {user_id}: {str(e)}", exc_info=True)
            # Try to clean up on error
            try:
                async with self.count_lock:
                    if self.waiting_count > 0:
                        self.waiting_count -= 1
            except:
                pass

    def release(self, user_id):
        """Release build slot for user"""
        try:
            if user_id in self.user_start_times:
                elapsed = int(time.time() - self.user_start_times[user_id])
                logger.info(f"User {user_id} build completed in {elapsed}s")
                del self.user_start_times[user_id]
            
            if user_id in self.building_users:
                del self.building_users[user_id]

            if user_id in self.user_locks and self.user_locks[user_id].locked():
                self.user_locks[user_id].release()
            
            try:
                self.global_semaphore.release()
                # Use asyncio.create_task safely
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(self._decrease_active_count())
                    else:
                        # If no event loop, decrease synchronously
                        pass
                except RuntimeError:
                    # No event loop, skip async decrease
                    pass
            except Exception as e:
                logger.error(f"Error releasing semaphore for user {user_id}: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error releasing build slot for user {user_id}: {str(e)}", exc_info=True)
    
    async def _decrease_active_count(self):
        """Decrease active count safely"""
        try:
            async with self.count_lock:
                if self.active_count > 0:
                    self.active_count -= 1
                    logger.debug(f"Active count decreased to {self.active_count}")
        except Exception as e:
            logger.error(f"Error decreasing active count: {str(e)}")


build_queue = BuildQueue()
