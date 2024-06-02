from ansys.mapdl.core import launch_mapdl
import os

mapdl = launch_mapdl()

print(mapdl)

project_path = os.getcwd()
job_name = "user_job_name"

print(job_name)

mapdl.exit()
