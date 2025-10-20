import httpx


class DeFiLlamaClient:
    BASE_URL = "https://api.llama.fi"

    async def fetch_protocols(self) -> list:
        url = f"{self.BASE_URL}/protocols"
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()



