import time
from rich import print
import asyncio

async def endpoint(route: str) -> str:
    print(f"[yellow]<<< handling {route}[/yellow]")
    
    # ✅ await is required here
    await asyncio.sleep(1)
    
    print(f"[green]<<< response {route}[/green]")
    return route


async def server():
    tests = (
        "GET /shipment?id=1",
        "PATCH /shipment?id=4",
        "GET /shipment?id=3"
    )
    
    start = time.perf_counter()
    
    # ✅ Python 3.10 way (instead of TaskGroup)
    tasks = [endpoint(route) for route in tests]
    results = await asyncio.gather(*tasks)
    
    print(f"[blue]Results: {results}[/blue]")
    
    end = time.perf_counter()
    print(f"[bold]Time taken: {end - start:.2f}s[/bold]")


# ✅ run server
if __name__ == "__main__":
    asyncio.run(server())