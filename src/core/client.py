import json
import logging
from httpx import AsyncClient

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CustomClient(AsyncClient):
    async def request(self, method, url, *args, **kwargs):
        logger.debug(f"Request URL: {url}")
        response = await super().request(method, url, *args, **kwargs)
        saved_content = response.content
        try:
            response_json = response.json()
            del response_json['context']
            response._content = json.dumps(response_json)
        except (json.JSONDecodeError, KeyError):  # rollback
            response._content = saved_content
        return response


client = CustomClient(timeout=5)  # reusable client
