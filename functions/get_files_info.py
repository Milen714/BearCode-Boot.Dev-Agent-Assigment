import os
from functions.utils import resolve_and_validate_path
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)

def _outside_dir_error(path: str) -> str:
    return f'Error: Cannot list "{path}" as it is outside the permitted working directory'

def list_files_in_directory(directory: str) -> str:
        
        dir_list = os.listdir(directory)
        result: str = ""
        for item in dir_list:
            item_path = os.path.join(directory, item)
            is_dir = os.path.isdir(item_path)
            file_size = os.path.getsize(item_path)
            result += f"- {item}: file_size={file_size} bytes, is_dir={is_dir}\n"
        return result

def get_files_info(working_directory: str, directory: str = ".") -> str:
    try:
    
        abs_path, err = resolve_and_validate_path(working_directory, directory, _outside_dir_error)
        if err:
            return err

        is_directory = os.path.isdir(abs_path)
        if not is_directory:
            raise ValueError(f'Error: "{directory}" is not a directory')
        else:
            return f'Result for current directory:\n{list_files_in_directory(abs_path)}'
    except Exception as e:
        return f'Result for current directory:\n{str(e)}'
    

    