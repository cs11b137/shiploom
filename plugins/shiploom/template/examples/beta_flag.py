"""Example only: default off; identifiers must be non-sensitive."""
import hashlib

def enabled(user_id: str, *, beta_enabled: bool = False, percent: int = 0, allowlist=()) -> bool:
    if not beta_enabled or not 0 <= percent <= 100:
        return False
    if user_id in allowlist:
        return True
    bucket = int.from_bytes(hashlib.sha256(('feature-v1:' + user_id).encode()).digest()[:8], 'big') % 100
    return bucket < percent
