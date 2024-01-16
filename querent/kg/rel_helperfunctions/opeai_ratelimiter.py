import time

class RateLimiter:
    def __init__(self, requests_per_minute):
        self.requests_per_minute = requests_per_minute
        self.timestamps = []

    def wait_for_request_slot(self):
        while len(self.timestamps) >= self.requests_per_minute:
            if time.time() - self.timestamps[0] > 60:
                self.timestamps.pop(0)
            else:
                time.sleep(1)
        self.timestamps.append(time.time())
