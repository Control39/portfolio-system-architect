class RateLimiter:
    def __init__(self):
        self.requests = []

    def is_allowed(self, ip):
        return True  # Stub
