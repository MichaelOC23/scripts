import asyncio
import json
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrTimeout

async def main():
    nc = NATS()

    
    await nc.connect("nats://localhost:4222")

    # Request payload
    request_payload = {"PrimaryExchange":"NASDAQ"}

    # Headers
    headers = {
        "Project": "CMS",
        "Token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiJhM2E1ZWJjYi00NGYyLTQ5ZjMtYjIyNS0yNDQzYzYzZGNhZGMiLCJ1bmlxdWVfbmFtZSI6Im1pY2hhZWxAanVzdGJ1aWxkaXQuY29tIiwiZW1haWwiOiJtaWNoYWVsQGp1c3RidWlsZGl0LmNvbSIsImdpdmVuX25hbWUiOiJNaWNoYWVsIFNtaXRoIiwidGVuYW50X2lkIjoiODMyZTM1MjAtYzM0OS00ZWQ2LWJmMjktNTNhNTUxOTc4MmM2IiwidGVuYW50IjoiY29tbXVuaWZ5IiwibmJmIjoxNzE5NTQxMTI4LCJleHAiOjE3MTk5MDExMjgsImlhdCI6MTcxOTU0MTEyOCwiaXNzIjoiQUJEM1pXUVg0RFpPNzJGTVlPUjNSUVJJSFhKSEVMQ1ZSVUlSR0xKQlhHRzdGU1NDS0FMQ0JJMk0iLCJhdWQiOiJjb21tdW5pZnkubG9jYWxob3N0In0.-VEJ-7k_6j-WFYVkds-BRZGhQmpXMCfdcjybvisjCI0"
    }

    try:
        response = await nc.request("account.query", json.dumps(request_payload).encode(), headers=headers, timeout=5)
        response_data = json.loads(response.data.decode())
        print("Received response:", response_data)
    except ErrTimeout:
        print("Request timed out")

    await nc.close()

if __name__ == '__main__':
    asyncio.run(main())