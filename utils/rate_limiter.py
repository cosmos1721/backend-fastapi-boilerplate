import os
import asyncio
from fastapi import Request
from utils.invalid_response_class import RequestTimeoutError
from utils.helpers import add_time, current_datetime
from asyncio import Lock
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_limit: int = 30, time_window: int = 60, wait_request_limit: int = 10):
        self.is_development = os.getenv('ENVIRONMENT') == 'DEVELOPMENT'
        self.requests_limit = requests_limit
        self.time_window = time_window
        self.wait_request_limit = wait_request_limit
        self.request_counters = defaultdict(lambda: defaultdict(int))
        self.wait_request_counters = defaultdict(lambda: defaultdict(int))
        self.cooldown_times = defaultdict(lambda: defaultdict(lambda: None))
        self.lock = Lock()

    async def time_sleep(self, seconds: int):
        print(f"\nSleeping for {seconds} seconds")
        await asyncio.sleep(seconds)

    async def __call__(self, request: Request):
        if self.is_development or request.headers.get('user-agent')== 'AI': # add specific term for it
            # Bypass rate limiter in development mode
            print("\nRate limiter bypassed in development mode.")
            return
        
        user = request.headers.get('x-forwarded-for', request.client.host)
        endpoint = request.url.path

        async with self.lock:
            if self.cooldown_times[user][endpoint] and self.cooldown_times[user][endpoint] > current_datetime():
                print(f"\nCooldown time active for {user} on {endpoint}, raising RequestTimeoutError")
                raise RequestTimeoutError()

            if self.request_counters[user][endpoint] >= self.requests_limit:
                print(f"\nRequest limit reached for {user} on {endpoint}")

                if self.wait_request_counters[user][endpoint] >= self.wait_request_limit:
                    print(f"\nWait request limit reached for {user} on {endpoint}, raising RequestTimeoutError")
                    asyncio.create_task(self.cooldown(user, endpoint, 1))
                    raise RequestTimeoutError('TESTTTTTTTTTTTTTTTTTT')

                self.wait_request_counters[user][endpoint] += 1
                print(f"\nIncremented wait counter for {user} on {endpoint}, wait: {self.wait_request_counters[user][endpoint]}")

                await self.time_sleep(self.time_window)

            else:
                self.request_counters[user][endpoint] += 1
                print(f"\nIncremented request counter for {user} on {endpoint}, request: {self.request_counters[user][endpoint]}")

    async def cooldown(self, user, endpoint, minutes: int):
        self.cooldown_times[user][endpoint] = add_time(minutes=minutes)
        await self.time_sleep(minutes * 60)
        self.cooldown_times[user][endpoint] = None
        self.request_counters[user][endpoint] = 0
        self.wait_request_counters[user][endpoint] = 0
        print(f"\nCooldown for {minutes} minutes for {user} on {endpoint}")
        print(f"\nCooldown over, reset counters for {user} on {endpoint}, request: {self.request_counters[user][endpoint]}, wait: {self.wait_request_counters[user][endpoint]}")
