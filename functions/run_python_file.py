import subprocess
import os
from functions.utils import resolve_and_validate_path
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file relative to the working directory, with optional command-line arguments",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Python file path to execute, relative to the working directory",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Optional command-line arguments to pass to the Python file",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
        required=["file_path"],
    ),
)

def _outside_dir_error(path: str) -> str:
    return f'Error: Cannot execute "{path}" as it is outside the permitted working directory'

def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    try:
        abs_working_dir = os.path.abspath(working_directory)
        abs_path, err = resolve_and_validate_path(working_directory, file_path, _outside_dir_error)
        if err:
            return err
        
        if not os.path.isfile(abs_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not abs_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'
        
        command = ["python", abs_path]
        if args:
            command.extend(args)

        result = subprocess.run(
                        command,
                        cwd=abs_working_dir,
                        capture_output=True,
                        text=True,
                        timeout=30,)

        output = []

        if result.returncode != 0:
            output.append(f"Process exited with code {result.returncode}")

        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")

        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")

        if not output:
            output.append("No output produced")

        return "\n".join(output)

    except Exception as e:
        return f"Error: executing Python file: {e}"
