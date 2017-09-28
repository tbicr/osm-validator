#!/usr/bin/env python3
import io
import random
from aiohttp import web, ClientSession
from aiohttp.web import HTTPFound
from PIL import Image


# NASA_API_KEY = 'DEMO_KEY'
NASA_API_KEY = 'xQQH1uQBL5D3dsZV0UCd1NTOmznChTkUpcelOtO9'
ROVER_URL = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos'


async def validate_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    return image.width >= 1024 and image.height >= 1024 and image.mode != 'L'


async def get_mars_image_url_from_nasa():
    while True:
        sol = random.randint(0, 1722)
        params = {'sol': sol, 'api_key': NASA_API_KEY}
        async with ClientSession() as session:
            async with session.get(ROVER_URL, params=params) as resp:
                resp_dict = await resp.json()
        if 'photos' not in resp_dict:
            raise Exception
        photos = resp_dict['photos']
        if not photos:
            continue
        return random.choice(photos)['img_src']


async def get_mars_photo_bytes():
    while True:
        image_url = await get_mars_image_url_from_nasa()
        async with ClientSession() as session:
            async with session.get(image_url) as resp:
                image_bytes = await resp.read()
        if await validate_image(image_bytes):
            break
    return image_bytes


async def get_mars_photo(request):
    image = await get_mars_photo_bytes()
    return web.Response(body=image, content_type='image/jpeg')


app = web.Application()
app.router.add_get('/', get_mars_photo, name='mars_photo')
web.run_app(app, host='127.0.0.1', port=8080)

