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
    plate_length: float,
    plate_thickness: float,
    elastic_modulus1: float,
    elastic_modulus2: float,
    cte_mat1: float,
    cte_mat2: float,
    reference_temperature: float,
    ambient_temperature: float,
) -> tuple[str, _T]:
    """Solve the MAPDL model and get path to image file and max displacement"""
    # Clear the database
    mapdl.clear("NOSTART")

    # Enter the model creation preprocessor
    mapdl.prep7()

    # Annotate the database with the system of units used
    mapdl.units(label="BIN")

    # ------------------------- PREP7 --------------------------------------
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
        val1=plate_thickness / 2, val2=1, val3=0
    )  # LAYER 1: 0.05 THICK, MAT'L 1, THETA 0
    mapdl.secdata(
        val1=plate_thickness / 2, val2=2, val3=0
    )  # LAYER 2: 0.05 THICK, MAT'L 2, THETA 0,

    # ------------------------- Materials --------------------------------------
    # Define a linear material property
    # Elastic modulus
    mapdl.mp(lab="EX", mat=1, c0=elastic_modulus1)
    mapdl.mp(lab="EX", mat=2, c0=elastic_modulus2)
    # Thermal expansion coefficient
    mapdl.mp(lab="ALPX", mat=1, c0=cte_mat1)
    mapdl.mp(lab="ALPX", mat=2, c0=cte_mat2)
    # Poisson's ratio
    mapdl.mp(lab="NUXY", mat=1, c0=0)
    mapdl.mp(lab="NUXY", mat=2, c0=0)

    # ------------------------- Geometry --------------------------------------
    # Define nodes
    mapdl.n(node=1)
    mapdl.n(node=12, x="", y=1)
    mapdl.n(node=22, x=plate_length, y=1)
    mapdl.n(node=11, x=plate_length)

    # Generate lines of nodes between two existing nodes
    mapdl.fill(node1=1, node2=11, nfill=9, nstrt=2, ninc=1)
    mapdl.fill(node1=12, node2=22, nfill=9, nstrt=13, ninc=1)

    for _ in range(0, 6):
        mapdl.fill(_ * 2 + 1, (_ + 1) * 2 + 10, 1, _ + 23)

    # Define elements by node connectivity
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

    # ------------------------- BC/Loads --------------------------------------
    # Select nodes with x=0
    mapdl.nsel("S", "LOC", "X")
    # Reselect nodes with x=0 and y=.5
    mapdl.nsel("R", "LOC", "Y", 0.5)
    # Fix all DOF of selected nodes
    mapdl.d(node="ALL", lab="ALL")

    # Select nodes with y=.5
    mapdl.nsel("S", "LOC", "Y", 0.5)
    # Specify symmetry degree-of-freedom constraints on selected nodes
    mapdl.dsym(lab="SYMM", normal="Y")

    # Select all nodes
    mapdl.nsel("ALL")
    # Define the reference temperature for selected nodes
    mapdl.tref(tref=reference_temperature)
    # Assign a uniform body force load to all nodes
    mapdl.bfunif(lab="TEMP", value=ambient_temperature)

    # Exit preprocessor normally
    mapdl.finish()

    # ------------------------- SOLUTION --------------------------------------
    # Run /SOLU command
    mapdl.run("/SOLU")

    # Control the solution printout for Nodal DOF solution
    mapdl.outpr(item="NSOL", freq=1)
    # and for Nodal reaction loads
    mapdl.outpr("RSOL", 1)

    # Solve problem
    mapdl.solve()

    # Modify the coordinates of the active set of nodes
    mapdl.upcoord(factor=1)

    # Exit preprocessor normally
    mapdl.finish()

    # ------------------------- POST1 --------------------------------------
    mapdl.post1()

    # Select las t result set for post-processing
    mapdl.set(lstep="last")

    # Set path to result image
    png_path = os.path.join(path_to_images, "cylinder.png")

    # Set plot settings as a tuple
    sbar_kwargs = {
        "color": "black",
        "title": "Z Displacement (inch)",
        "vertical": False,
        "n_labels": 9,
    }

    # Plot nodal displacement for selected nodes to file
    mapdl.post_processing.plot_nodal_displacement(
        component="Z",
        show_node_numbering="",
        cpos="iso",
        background="white",
        edge_color="black",
        show_edges=True,
        scalar_bar_args=sbar_kwargs,
        n_colors=9,
        savefig=png_path,
    )

    # Get nodal displacement for selected nodes
    disp = mapdl.post_processing.nodal_displacement("Z")

    # Get max value of displacements
    uz_max = max(disp.max(), disp.min(), key=abs)

    # Exit MAPDL
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
    Get round to 3 digits the value of k_1.
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
