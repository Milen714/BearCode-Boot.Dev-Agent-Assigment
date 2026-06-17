import os
from functions.utils import resolve_and_validate_path
from config import MAX_CHARS 
from google.genai import types

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the contents of a specified file relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to read, relative to the working directory",
            ),
        },
        required=["file_path"],
    ),
)

def _outside_dir_error(path: str) -> str:
    return f'Error: Cannot read "{path}" as it is outside the permitted working directory'


def read_file(file_path:str)-> str:
    file_content_string: str = ""
    with open(file_path, "r") as f:
        file_content_string = f.read(MAX_CHARS)
        if f.read(10):
            file_content_string += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
    return file_content_string

def get_file_content(working_directory: str, file_path: str) -> str:
    try:
        abs_path, err = resolve_and_validate_path(working_directory, file_path, _outside_dir_error)
        if err:
            return err

        if not os.path.isfile(abs_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        else:
            return read_file(abs_path)

        
    except Exception as e:
        return f"Error getting file contents: {e}"


