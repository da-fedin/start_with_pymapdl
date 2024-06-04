import os


class StopExecution(Exception):
    def _render_traceback_(self):
        return []


def get_file_path(folder_name: str, file_name: str) -> str:
    """Return the relative path to the file by folder and file name"""
    # Define the directory to search in relative to the current working directory
    # search_dir = os.path.join(os.getcwd(), folder_name)
    search_dir = os.path.join(os.path.dirname(os.getcwd()), folder_name)

    # Combine the directory and file name to form the search path
    search_path = os.path.join(search_dir, file_name)

    print(search_dir)
    print(search_path)

    return search_path
