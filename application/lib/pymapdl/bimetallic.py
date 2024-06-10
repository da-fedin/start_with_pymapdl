import os
from ansys.mapdl.core import launch_mapdl
from ansys.mapdl.core.mapdl_grpc import MapdlGrpc
from typing import SupportsAbs, TypeVar

# Set some type hints
_T = TypeVar("_T", bound=SupportsAbs)


def clean_work_dir(current_dir: str) -> None:
    # Get list of names of the files in the directory
    file_list = [_ for _ in os.listdir(current_dir)]

    # Loop over list
    for _ in file_list:
        # Remove files in the directory
        os.remove(os.path.join(current_dir, _))


def launch_mapdl_in_dir(work_dir: str, job_name: str) -> tuple[MapdlGrpc, str]:
    """Get MAPDL instance in predefined dir"""
    # Get root folder path
    path = os.getcwd()

    # Set dir path
    dir_path = os.path.join(path, work_dir)

    # Create dir
    try:
        os.mkdir(dir_path)

    except OSError as e:
        clean_work_dir(dir_path)

    # Run MAPDL
    mapdl = launch_mapdl(
        run_location=dir_path,
        jobname=job_name,
        nproc=1,
        override=True,
        additional_switches="-smp",
    )

    return mapdl, dir_path


def solve_vm_35(
    path_to_images: str,
    mapdl: MapdlGrpc,
    length: float,
    thickness: float,
    ex_mat1: float,
    ex_mat2: float,
    cte_mat1: float,
    cte_mat2: float,
    my_t_ref: float,
    my_t_amb: float,
) -> tuple[str, _T]:
    """Solve the MAPDL model and get path to image file and max displacement"""
    # Clear the database
    mapdl.clear("NOSTART")

    # Enter the model creation preprocessor
    mapdl.prep7()

    # Annotate the database with the system of units used
    mapdl.units(label="BIN")

    # Enter the model creation preprocessor
    mapdl.prep7()

    # Define a main title
    mapdl.title(title="VM35 BIMETALLIC LAYERED CANTILEVER PLATE WITH THERMAL LOADING")

    # Run single APDL commands to place a comments in the output
    mapdl.run(
        command="C***     ROARK AND YOUNG, FORMULAS FOR STRESS AND STRAIN, PP. 113-114."
    )
    mapdl.run(command="C*** USING SHELL281")

    # Specify the analysis type and restart status
    mapdl.antype(antype="STATIC")

    # ------------------------- Elements --------------------------------------
    # Define a local element type from the element library
    mapdl.et(itype=1, ename="SHELL281")

    # Associates section type information with a section ID number
    mapdl.sectype(secid=1, type_="SHELL")

    # Describes the geometry of a section for layers
    mapdl.secdata(
        val1=thickness / 2, val2=1, val3=0
    )  # LAYER 1: 0.05 THICK, MAT'L 1, THETA 0
    mapdl.secdata(
        val1=thickness / 2, val2=2, val3=0
    )  # LAYER 2: 0.05 THICK, MAT'L 2, THETA 0,

    # ------------------------- Materials --------------------------------------
    mapdl.mp("EX", 1, ex_mat1)  # MATERIAL PROPERTIES
    mapdl.mp("EX", 2, ex_mat2)
    mapdl.mp("ALPX", 1, cte_mat1)
    mapdl.mp("ALPX", 2, cte_mat2)
    mapdl.mp("NUXY", 1, 0)
    mapdl.mp("NUXY", 2, 0)
    mapdl.n(1)  # DEFINE GEOMETRY
    mapdl.n(12, "", 1)
    mapdl.n(22, length, 1)
    mapdl.n(11, length)
    mapdl.fill(1, 11, 9, 2, 1)
    mapdl.fill(12, 22, 9, 13, 1)

    for _ in range(0, 6):
        mapdl.fill(_ * 2 + 1, (_ + 1) * 2 + 10, 1, _ + 23)

    for _ in range(0, 5):
        mapdl.e(
            _ * 2 + 1,
            (_ + 1) * 2 + 10,
            (_ + 1) * 2 + 12,
            _ * 2 + 3,
            _ + 23,
            _ * 2 + 13,
            _ + 24,
            _ * 2 + 2,
        )

    mapdl.nsel("S", "LOC", "X")
    mapdl.nsel("R", "LOC", "Y", 0.5)
    mapdl.d("ALL", "ALL")  # FIX ONE END OF CANTILEVER
    mapdl.nsel("S", "LOC", "Y", 0.5)
    mapdl.dsym("SYMM", "Y")  # SYMMETRY PLANE DOWN CENTERLINE
    mapdl.nsel("ALL")
    mapdl.tref(my_t_ref)
    mapdl.bfunif("TEMP", my_t_amb)  # DEFINE UNIFORM TEMPERATURE
    mapdl.finish()
    mapdl.run("/SOLU")
    mapdl.outpr("NSOL", 1)
    mapdl.outpr("RSOL", 1)
    mapdl.solve()
    mapdl.upcoord(1)
    mapdl.finish()
    mapdl.post1()
    mapdl.set("last")
    png_path = os.path.join(path_to_images, "cylinder.png")
    sbar_kwargs = {
        "color": "black",
        "title": "Z Displacement (inch)",
        "vertical": False,
        "n_labels": 9,
    }
    mapdl.post_processing.plot_nodal_displacement(
        "Z",
        "",
        cpos="iso",
        background="white",
        edge_color="black",
        show_edges=True,
        scalar_bar_args=sbar_kwargs,
        n_colors=9,
        savefig=png_path,
    )

    disp = mapdl.post_processing.nodal_displacement("Z")
    uz_max = max(disp.max(), disp.min(), key=abs)
    mapdl.exit()

    return png_path, uz_max


def roarks_vm_35(
    length: float,
    thickness: float,
    ex_mat1: float,
    ex_mat2: float,
    cte_mat1: float,
    cte_mat2: float,
    my_t_ref: float,
    my_t_amb: float,
) -> float:
    """
    Get k_1.
    Notes:
    We are constraining the layer thicknesses to be the same, so ta/tb term is 1
    which simplifies the equation. I'm dropping the (ta/tb)^n terms as they are all 1
    k_1 = ex_mat1 / ex_mat2
    """

    k_1 = 4.0 + 6.0 + 4.0 + (ex_mat1 / ex_mat2) + (ex_mat2 / ex_mat1)

    ymax = (6.0 * (cte_mat2 - cte_mat1) * (my_t_amb - my_t_ref) * thickness) / (
        k_1 * ((thickness / 2) ** 2)
    )

    ymax = (ymax * (length**2)) / 2.0

    return round(ymax, 3)
