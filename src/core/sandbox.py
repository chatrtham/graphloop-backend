"""Sandbox management for code execution."""

from contextlib import asynccontextmanager
from e2b_code_interpreter import AsyncSandbox


@asynccontextmanager
async def get_sandbox():
    """Context manager for sandbox lifecycle."""
    sandbox = None
    try:
        sandbox = await AsyncSandbox.create()
        yield sandbox
    finally:
        if sandbox:
            await sandbox.kill()


async def run_python_code(code: str) -> str:
    """Run python code in a sandbox and return the output."""
    async with get_sandbox() as sandbox:
        result = await sandbox.run_code(code)
        return result