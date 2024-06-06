""" Get .py file from .inp file automatically"""
import os

from ansys.mapdl import core as pymapdl

# Set source and destination
source_folder = "sources"

source_file_name = "beam.inp"

result_path = r"tmp\beam.py"

# Set paths
search_dir = os.path.join(os.path.dirname(os.getcwd()), source_folder)

search_path = os.path.join(search_dir, source_file_name)

save_path = os.path.join(os.path.dirname(os.getcwd()), result_path)

# Run server
mapdl = pymapdl.launch_mapdl()

# Convert file
if not os.path.exists(save_path):
    pymapdl.convert_script(filename_in=search_path, filename_out=save_path)

else:
    print("Mapdl file already exists")

mapdl.exit()
