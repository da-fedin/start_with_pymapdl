""" Get .py file from .inp file automatically"""
import os

from ansys.mapdl import core as pymapdl

mapdl = pymapdl.launch_mapdl()

search_dir = os.path.join(os.path.dirname(__file__), "sources")

search_path = os.path.join(search_dir, "beam.inp")

save_path = os.path.join(os.path.dirname(__file__), "tmp")

print(save_path)

pymapdl.convert_script(filename_in=search_path, filename_out=save_path)  # , pyscript)

mapdl.exit()
