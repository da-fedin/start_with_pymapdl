from flask import Flask, render_template, request
import shutil
import os


# import project specific files
from application import launch_mapdl_in_dir, solve_vm_35, roarks_vm_35
from application import IMAGE_PATH, NEW_WDIR_NAME, JNAME, RUN_COMPLETE, FINAL_IMAGE_PATH

app = Flask(__name__)

# Get current working directory as a string
cwd = os.getcwd()

# Set path to dir with images for template
path_to_images = os.path.join(cwd, IMAGE_PATH)


def pyMapdl_vm35(L, t, e1, e2, c1, c2, T1, T2):
    # Launch MAPDL in predefined dir
    mapdl, dir_to_run = launch_mapdl_in_dir(work_dir=NEW_WDIR_NAME, job_name=JNAME)

    # Solve task and get result path to result image
    png_path, uz_max = solve_vm_35(path_to_images, mapdl, L, t, e1, e2, c1, c2, T1, T2)

    return [png_path, round(uz_max, 3)]


@app.route("/", methods=["POST", "GET"])
def calculator():
    # Set default values
    my_length = 10.0
    my_thickness = 0.1
    my_mat1ex = 3.0e7
    my_mat2ex = 3.0e7
    my_mat1cte = 1e-5
    my_mat2cte = 2e-5
    my_tref = 70
    my_tamb = 170

    usum = ""
    image = ""
    roarks_zmax = ""
    error1 = ""
    flag = ""

    if request.method == "POST":
        my_length = float(request.form.get("Length"))
        my_thickness = float(request.form.get("Thickness"))
        my_mat1ex = float(request.form.get("mat1ex"))
        my_mat2ex = float(request.form.get("mat2ex"))
        my_mat1cte = float(request.form.get("mat1cte"))
        my_mat2cte = float(request.form.get("mat2cte"))
        my_tref = float(request.form.get("tref"))
        my_tamb = float(request.form.get("tamb"))

        p_run = pyMapdl_vm35(
            my_length,
            my_thickness,
            my_mat1ex,
            my_mat2ex,
            my_mat1cte,
            my_mat2cte,
            my_tref,
            my_tamb,
        )

        print(RUN_COMPLETE)

        shutil.move(p_run[0], FINAL_IMAGE_PATH)
        image = FINAL_IMAGE_PATH
        usum = p_run[1]
        flag = 1
        print(image)
        print(usum)
        roarks_zmax = roarks_vm_35(
            my_length,
            my_thickness,
            my_mat1ex,
            my_mat2ex,
            my_mat1cte,
            my_mat2cte,
            my_tref,
            my_tamb,
        )

        if not abs(usum) > 0.0:
            error1 = 0.000
            print("error1 " + str(error1))
        else:
            error1 = ((p_run[1] - roarks_zmax) / p_run[1]) * 100
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
        input_image_url=IMAGE_PATH,
        L2=my_length,
        t2=my_thickness,
        E21=my_mat1ex,
        E22=my_mat2ex,
        c21=my_mat1cte,
        c22=my_mat2cte,
        T1=my_tref,
        T2=my_tamb,
    )


if __name__ == "__main__":
    app.run(debug=True)
