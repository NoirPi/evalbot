import base64
from io import BytesIO
from typing import Optional, List, Union

import aiohttp
from discord import File

EXECUTE_ENDPOINT = "http://rextester.com/rundotnet/api"


def get_parameters(**kwargs):
    return kwargs


class ExecuteResponse(object):

    def __init__(self, warnings: Optional[str], errors: Optional[str], output: str, stats, files):
        self.output: Optional[str] = output
        self.warnings: Optional[str] = warnings
        self.errors: Optional[str] = errors
        self.stats: str = stats
        self.files: Optional[List[str]] = files

    @property
    def discord_files(self) -> List[File]:
        if not self.files:
            return []

        def convert_file(b64, i):
            bytesio = BytesIO()
            bytesio.write(base64.b64decode(b64))
            bytesio.seek(0)
            return File(bytesio, filename=f'output{i}.png')

        return [convert_file(b64, i) for i, b64 in enumerate(self.files)]


def parse_execute_response(response: dict) -> ExecuteResponse:
    warnings = response['Warnings']
    errors = response['Errors']
    output = response['Result']
    stats = response['Stats']
    files = response['Files']
    return ExecuteResponse(warnings, errors, output, stats, files)


async def execute(code: str, language: Union[str, int]) -> ExecuteResponse:
    async with aiohttp.ClientSession() as session:
        print(code)
        print(language)
        response = await session.post(EXECUTE_ENDPOINT, data=get_parameters(
            Program=code,
            LanguageChoice=language,
            Input="",
            CompilerArgs="",
        ))
        return parse_execute_response(await response.json())
