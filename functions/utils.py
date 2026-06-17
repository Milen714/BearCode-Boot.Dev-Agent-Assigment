import os
from typing import Callable

def resolve_and_validate_path(
    working_directory: str,
    path: str,
    make_error: Callable[[str], str],
) -> tuple[str, str | None]:
    abs_working_dir = os.path.abspath(working_directory)
    abs_path = os.path.normpath(os.path.join(abs_working_dir, path))
    if os.path.commonpath([abs_working_dir, abs_path]) != abs_working_dir:
        return abs_path, make_error(path)
    return abs_path, None