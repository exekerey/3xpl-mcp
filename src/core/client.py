import json

from httpx import AsyncClient

from src.core.config import config


class CustomClient(AsyncClient):
    async def request(self, method, url, *args, **kwargs):
        params = kwargs.get('params')
        if params is None:
            params = dict()
        params['token'] = config.threexpl_api_key
        kwargs['params'] = params
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
