from typing import List

import httpx, asyncio
import json

from database import schemas, models
from pydantic import ValidationError
from pydantic import parse_obj_as


async def ass():
    async with httpx.AsyncClient() as client:
        data = {"brand": "ASS2"}
        headers = {'content-type': 'application/json'}
        r = await client.post(url='http://127.0.0.1:8000/brand', headers=headers, json=data)
    print(r)

    async with httpx.AsyncClient() as client:
        r = await client.get('http://127.0.0.1:8000/brand')
    jason = r.json()[0]
    brandik = schemas.Brand.parse_raw(str(jason).replace("'",'"'))
    print(brandik)

    async with httpx.AsyncClient() as client:
        r = await client.get(f'http://127.0.0.1:8000/brand/{brandik.id}')
    jason = r.content
    brandik = schemas.Brand.parse_raw(jason)
    print(brandik)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ass())
