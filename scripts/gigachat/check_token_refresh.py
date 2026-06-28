import asyncio
from src.ai.config.token_refresh_service import TokenRefreshService


async def test():
    s = TokenRefreshService()
    t = await s.get_token()
    print("Token:", t[:30] if t else "None")
    print("Starts with:", t[:10] if t else "None")
    print("Is JWT:", t.startswith("eyJ") if t else "No")


asyncio.run(test())
