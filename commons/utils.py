import os
import ansys.mapdl.core


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

    return search_path


def get_mapdl_version(mapdl_instance, method="Category") -> float:
    """
    Get mapdl version
    """
    if method == "Category":
        version = mapdl_instance.version
    else:
        version = mapdl_instance.get_value("Active", 0, "Rev")

    return version
