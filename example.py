import asyncio
from rezka.client import Client


async def main():
    client = Client()

    series = await client.info("https://rezka.ag/series/thriller/646-vo-vse-tyazhkie-2008.html")
    print(series)

    await client.close()


asyncio.run(main())
