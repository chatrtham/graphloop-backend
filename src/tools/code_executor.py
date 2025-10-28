"""Code execution tool for running Python code in sandbox."""

from src.core.sandbox import run_python_code


# Tool function for agent
async def python_code_executor(code: str) -> str:
    """
    Execute Python code in a secure sandbox environment.

    Args:
        code (str): Python code to execute

    Returns:
        str: Execution output or error message
    """
    try:
        result = await run_python_code(code)
        return result
    except Exception as e:
        return f"Error executing code: {str(e)}"


# Export the tool function
__all__ = ["python_code_executor"]