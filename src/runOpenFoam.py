import subprocess
import numpy as np
import csv

def compute_alpha(U, alpha, csv_polar):
    # Create the working directory
    subprocess.run(["mkdir", "-p", "openFoam/AOA_" + str(alpha)])
    subprocess.run(["cp", "-r", "openFoam/Cas_de_base/0", "openFoam/Cas_de_base/constant", "openFoam/Cas_de_base/system", "openFoam/AOA_" + str(alpha)])
    subprocess.run(["cp", "-r", "data/mesh.msh", "openFoam/AOA_" + str(alpha)])

    # Convert the mesh from gmsh to blockMesh format
    subprocess.run(['gmshToFoam mesh.msh'], shell=True, cwd="openFoam/AOA_" + str(alpha))

    # Modify the boundary dictionary
    f = open("openFoam/AOA_" + str(alpha) + '/constant/polyMesh/boundary', 'r+')
    t = f.readlines()
    new_lines = []
    replace = [
        '        type            empty;\n', 
        '        physicalType    empty;\n', 
        '        type            wall;\n',
        '        physicalType    wall;\n',
        '        type            patch;\n',
        '        physicalType    inlet;\n',
        '        type            patch;\n',
        '        physicalType    outlet;\n'
    ]
    k = 0
    for line in t:
        if 'patch' in line:
            new_lines = np.append(new_lines, replace[k])
            k = k + 1
        else:
            new_lines = np.append(new_lines, line)
    f.close()
    f = open("openFoam/AOA_" + str(alpha) + '/constant/polyMesh/boundary', 'w')
    f.writelines(new_lines)
    f.close()

    # Change the wind direction (equivalent to changing the AOA)
    v = U  # wind speed
    vx = v * np.cos(alpha * np.pi / 180)
    vy = v * np.sin(alpha * np.pi / 180)
    # Modify the 0/U dictionary
    f = open("openFoam/AOA_" + str(alpha) + '/0/U', 'r+')
    t = f.readlines()
    new_lines = []
    for line in t:
        if 'uniform' in line:
            new_lines = np.append(new_lines, 'internalField   uniform (' + str(vx) + ' ' + str(vy) + ' ' + '0);\n')
        else:
            new_lines = np.append(new_lines, line)
    f.close()
    f = open("openFoam/AOA_" + str(alpha) + '/0/U', 'w')
    f.writelines(new_lines)
    f.close()

    # Change the direction of liftDir/dragDir
    f = open("openFoam/AOA_" + str(alpha) + '/system/controlDict', 'r+')
    t = f.readlines()
    new_lines = []
    for line in t:
        if 'liftDir' in line:
            new_lines = np.append(new_lines, '        liftDir     (' + str(-np.sin(alpha * np.pi / 180)) + ' ' + str(np.cos(alpha * np.pi / 180)) + ' ' + '0);\n')
        elif 'dragDir' in line:
            new_lines = np.append(new_lines, '        dragDir     (' + str(np.cos(alpha * np.pi / 180)) + ' ' + str(np.sin(alpha * np.pi / 180)) + ' ' + '0);\n')
        elif 'magUInf' in line:
            new_lines = np.append(new_lines, '        magUInf     ' + str(U) + ';\n')
        else:
            new_lines = np.append(new_lines, line)
    f.close()
    f = open("openFoam/AOA_" + str(alpha) + '/system/controlDict', 'w')
    f.writelines(new_lines)
    f.close()

    # Run simpleFoam
    subprocess.run(['foamRun > log'], shell=True, cwd="openFoam/AOA_" + str(alpha))

    # Read the last lines of the file forceCoeffs.dat
    force_coeffs_path = "openFoam/AOA_" + str(alpha) + "/postProcessing/forces/0/forceCoeffs.dat"
    with open(force_coeffs_path, 'r') as f:
        lines = f.readlines()
        last_line = lines[-1].strip()

    # Convert last_line to a list of values
    last_line_values = last_line.split()

    # Convert string values to float
    last_line_values = list(map(float, last_line_values))

    # Insert alpha at the beginning of the list
    last_line_values.insert(0, alpha)

    # Write it in polar.csv
    with open(csv_polar, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(last_line_values)

    return ()
