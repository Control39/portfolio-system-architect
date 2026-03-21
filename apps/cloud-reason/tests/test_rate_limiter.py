import unittest
from src.utils.rate_limiter import RateLimiter

class TestRateLimiter(unittest.TestCase):
    def test_is_allowed(self):
        limiter = RateLimiter()
        self.assertTrue(limiter.is_allowed('127.0.0.1'))

