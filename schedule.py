import asyncio

from osm_validator.validators.processor import init_validators, process_changes

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_validators())
    loop.run_until_complete(process_changes())
