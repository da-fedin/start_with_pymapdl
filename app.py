from flask import Flask, render_template, request
import shutil
import os
from typing import SupportsAbs, TypeVar

# import project specific files
from application import launch_mapdl_in_dir, solve_vm_35, roarks_vm_35
from application import (
    IMAGE_DIR_PATH,
    WORK_DIR_NAME,
    JOB_NAME,
    RUN_COMPLETE_MESSAGE,
    FINAL_IMAGE_PATH,
)

# Set some type hints
_T = TypeVar("_T", bound=SupportsAbs)

app = Flask(__name__)

# Get current working directory as a string
cwd = os.getcwd()

# Set path to dir with images for template
path_to_images = os.path.join(cwd, IMAGE_DIR_PATH)


def pyMAPDL_vm35(
    plate_length: float,
    plate_thickness: float,
    elastic_modulus1: float,
    elastic_modulus2: float,
    cte_mat1: float,
    cte_mat2: float,
    reference_temperature: float,
    ambient_temperature: float,
):
    """
    Solve model and get result image path and max displacement value
    """
    # Get MAPDL instance and working dir
    mapdl, dir_to_run = launch_mapdl_in_dir(work_dir=WORK_DIR_NAME, job_name=JOB_NAME)

    # Solve task and get result path to result image
    png_path, uz_max = solve_vm_35(
        path_to_images=path_to_images,
        mapdl=mapdl,
        plate_length=plate_length,
        plate_thickness=plate_thickness,
        elastic_modulus1=elastic_modulus1,
        elastic_modulus2=elastic_modulus2,
        cte_mat1=cte_mat1,
        cte_mat2=cte_mat2,
        reference_temperature=reference_temperature,
        ambient_temperature=ambient_temperature,
    )

    return [png_path, round(uz_max, 3)]


# Render template (displacement calculator)
@app.route(rule="/", methods=["POST", "GET"])
def calculator():
    # Set default values
    default_plate_length = 10.0
    default_plate_thickness = 0.1
    default_elastic_modulus1 = 3.0e7
    default_elastic_modulus2 = 3.0e7
    default_cte_mat1 = 1e-5
    default_cte_mat2 = 2e-5
    default_reference_temperature = 70
    default_ambient_temperature = 170

    usum = ""
    image = ""
    roarks_zmax = ""
    error1 = ""
    flag = ""

    # Get values from page form
    if request.method == "POST":
        # Get default values if the requested data doesn't exist
        default_plate_length = float(request.form.get("Length"))
        default_plate_thickness = float(request.form.get("Thickness"))
        default_elastic_modulus1 = float(request.form.get("mat1ex"))
        default_elastic_modulus2 = float(request.form.get("mat2ex"))
        default_cte_mat1 = float(request.form.get("mat1cte"))
        default_cte_mat2 = float(request.form.get("mat2cte"))
        default_reference_temperature = float(request.form.get("tref"))
        default_ambient_temperature = float(request.form.get("tamb"))

        # Run solution with entered values
        solution_results = pyMAPDL_vm35(
            default_plate_length,
            default_plate_thickness,
            default_elastic_modulus1,
            default_elastic_modulus2,
            default_cte_mat1,
            default_cte_mat2,
            default_reference_temperature,
            default_ambient_temperature,
        )

        print(RUN_COMPLETE_MESSAGE)

        # Move result image file or directory to final location
        shutil.move(solution_results[0], FINAL_IMAGE_PATH)
        image = FINAL_IMAGE_PATH
        usum = solution_results[1]
        flag = 1
        print(image)
        print(usum)
        roarks_zmax = roarks_vm_35(
            default_plate_length,
            default_plate_thickness,
            default_elastic_modulus1,
            default_elastic_modulus2,
            default_cte_mat1,
            default_cte_mat2,
            default_reference_temperature,
            default_ambient_temperature,
        )

        if not abs(usum) > 0.0:
            error1 = 0.000
            print("error1 " + str(error1))
        else:
            error1 = ((solution_results[1] - roarks_zmax) / solution_results[1]) * 100
            error1 = round(error1, 3)
            print("error is " + str(error1))
        print("roarks is " + str(roarks_zmax))

    return render_template(
        template_name_or_list="index.html",
        Flag=flag,
        TotalDeformation=usum,
        SolveStatus="Solved",
        RoarksZmax=roarks_zmax,
        error=error1,
        output_image_url=image,
        input_image_url=IMAGE_DIR_PATH,
        L2=default_plate_length,
        t2=default_plate_thickness,
        E21=default_elastic_modulus1,
        E22=default_elastic_modulus2,
        c21=default_cte_mat1,
        c22=default_cte_mat2,
        T1=default_reference_temperature,
        T2=default_ambient_temperature,
    )


if __name__ == "__main__":
    app.run(debug=True)
