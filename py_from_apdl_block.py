from ansys.mapdl.core.convert import convert_apdl_block

apdl_string = """/com, This is a block of APDL commands.
/PREP7
N,,0,0,0
N,,0,0,1
FINISH"""

apdl_string_list = [
    "/com, This is a block of APDL commands.",
    "/PREP7",
    "N,,0,0,0",
    "N,,0,0,1",
    "FINISH",
]

pycode_block = convert_apdl_block(apdl_string)

print(pycode_block)

pycode_list = convert_apdl_block(apdl_string_list)

[print(_) for _ in pycode_list]
