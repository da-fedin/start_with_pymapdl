from ansys.mapdl import core as pymapdl
from ansys.mapdl.core import examples
import os

result_path = r"tmp/vm1.py"

save_path = os.path.join(os.path.dirname(os.getcwd()), result_path)

py_code = pymapdl.convert_script(examples.vmfiles["vm1"], save_path)

# Print it
[print(_) for _ in py_code]
