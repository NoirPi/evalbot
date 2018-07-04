import asyncio
from dataclasses import dataclass

import aiohttp

from config import jdoodle_id, jdoodle_secret

EXECUTE_ENDPOINT = "https://api.jdoodle.com/v1/execute"


def get_parameters(**kwargs):
    return dict(
        clientId=jdoodle_id,
        clientSecret=jdoodle_secret,
        **kwargs,
    )


def post(url, data=None, json=None, **kwargs):
    return asyncio.get_event_loop().run_in_executor(None, lambda *_: requests.post(url, data, json, **kwargs))


@dataclass
class ExecuteResponse(object):
    output: str
    cpu_time: float
    memory: int
    status_code: int


def parse_execute_response(response: dict) -> ExecuteResponse:
    memory = response['memory']
    output = response['output']
    cpu_time = response['cpuTime']
    status_code = response['statusCode']
    return ExecuteResponse(output, cpu_time, memory, status_code)


async def execute(code: str, language: str, version: str) -> ExecuteResponse:
    async with aiohttp.ClientSession() as session:
        response = await session.post(EXECUTE_ENDPOINT, json=get_parameters(
            script=code,
            language=language,
            versionIndex=version))
        return parse_execute_response(await response.json())
