import os

from ansys.mapdl import core as pymapdl
from ansys.mapdl.core import launch_mapdl

mapdl = launch_mapdl()

search_dir = os.path.join(os.path.dirname(__file__), "sources")
search_path = os.path.join(search_dir, "beam.inp")

pymapdl.convert_script(search_path)  # , pyscript)

mapdl.exit()
