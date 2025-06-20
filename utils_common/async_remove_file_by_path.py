from aiofiles import os as aios


async def async_remove_file(full_file_path: str) -> None:
    if await aios.path.exists(full_file_path):
        await aios.remove(full_file_path)
