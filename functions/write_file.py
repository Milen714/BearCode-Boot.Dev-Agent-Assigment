import os
from functions.utils import resolve_and_validate_path
from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes or overwrites a file relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to write to, relative to the working directory",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content to write to the file",
            ),
        },
        required=["file_path", "content"],
    ),
)

def _outside_dir_error(path: str) -> str:
    return f'Error: Cannot write to "{path}" as it is outside the permitted working directory'

def write_file(working_directory: str, file_path: str, content: str) -> str:
    try:
        abs_path, err = resolve_and_validate_path(working_directory, file_path, _outside_dir_error)
        if err:
            return err

        if os.path.isdir(abs_path):
            return f'Error: Cannot write to "{file_path}" as it is a directory'
        
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w") as f:
            f.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except Exception as e:
        return f"Error: {e}"
