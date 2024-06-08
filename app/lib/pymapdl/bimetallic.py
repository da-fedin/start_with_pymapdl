import os
from ansys.mapdl.core import launch_mapdl
import numpy as np

# path = os.getcwd()


def clean_wdir(mydir):
    filelist = [f for f in os.listdir(mydir)]
    for f in filelist:
        os.remove(os.path.join(mydir, f))


def my_mapdl_launch_in_cwd(my_wdirnew, my_job_name):
    """create a new working directory beside the py file"""
    path = os.getcwd()
    new_wdir_path = os.path.join(path, my_wdirnew)
    try:
        os.mkdir(new_wdir_path)
    except:
        clean_wdir(new_wdir_path)
    mapdl = launch_mapdl(
        run_location=new_wdir_path,
        jobname=my_job_name,
        nproc=1,
        override=True,
        additional_switches="-smp",
    )
    return mapdl, new_wdir_path


def solve_vm_35(
    images,
    mapdl,
    length,
    thickness,
    ex_mat1,
    ex_mat2,
    cte_mat1,
    cte_mat2,
    my_t_ref,
    my_t_amb,
):
    mapdl.clear("NOSTART")
    mapdl.prep7()
    mapdl.units("BIN")
    mapdl.prep7()
    mapdl.title("VM35 BIMETALLIC LAYERED CANTILEVER PLATE WITH THERMAL LOADING")
    mapdl.run("C***     ROARK AND YOUNG, FORMULAS FOR STRESS AND STRAIN, PP. 113-114.")
    mapdl.run("C*** USING SHELL281")
    mapdl.antype("STATIC")
    mapdl.et(1, "SHELL281")
    mapdl.sectype(1, "SHELL")
    mapdl.secdata(thickness / 2, 1, 0)  # LAYER 1: 0.05 THICK, MAT'L 1, THETA 0
    mapdl.secdata(thickness / 2, 2, 0)  # LAYER 2: 0.05 THICK, MAT'L 2, THETA 0,
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
    for ii in range(0, 6):
        mapdl.fill(ii * 2 + 1, (ii + 1) * 2 + 10, 1, ii + 23)
    for jj in range(0, 5):
        mapdl.e(
            jj * 2 + 1,
            (jj + 1) * 2 + 10,
            (jj + 1) * 2 + 12,
            jj * 2 + 3,
            jj + 23,
            jj * 2 + 13,
            jj + 24,
            jj * 2 + 2,
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
    png_path = os.path.join(images, "cylinder.png")
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
    # mapdl.exit()
    return png_path, uz_max


def roarks_vm_35(
    length, thickness, ex_mat1, ex_mat2, cte_mat1, cte_mat2, my_t_ref, my_t_amb
):
    # we are constraining the layer thicknesses to be the same, so ta/tb term is 1
    # which simplifies the equation and I'm dropping the (ta/tb)^n terms as they are all 1
    # K1 = ex_mat1 / ex_mat2

    K1 = 4.0 + 6.0 + 4.0 + (ex_mat1 / ex_mat2) + (ex_mat2 / ex_mat1)
    ymax = (6.0 * (cte_mat2 - cte_mat1) * (my_t_amb - my_t_ref) * thickness) / (
        K1 * ((thickness / 2) ** 2)
    )
    ymax = (ymax * (length**2)) / 2.0
    return round(ymax, 3)
