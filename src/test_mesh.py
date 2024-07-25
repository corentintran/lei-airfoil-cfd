import LEIairfoilMesh
import subprocess
import os
import numpy as np

# Airfoil profile parameters
Corde_length = 1.0
Depth = 14
tube_size = 6
at = 22
Seam_angle = 35
Sail_angle = 13
nb_pts = 100

# Fluid domain parameters
Va = 90  # apparent wind speed
xmax = 40
ymax = 20

# Angle of attack
alpha = 10

# Mesh parameters
lc_init = 0.6               # initial size of volumes at boundaries
lc_prof = lc_init / 150     # size of volumes around the airfoil

# Boundary layer parameters
ep = 1.67e-2    # boundary layer thickness
yh = 1e-4       # size of the first element in the boundary layer

# Name of the directory where the mesh will be written
repertory = "Cas_de_base"

# Function to create the mesh geometry in the Cas_de_base directory and modify the boundary file
def update_mesh(U, Corde_length, Depth, tube_size, at, Seam_angle, Sail_angle, nb_pts, alpha, lc_prof, lc_init, xmax, ymax, ep, yh):
    # Mesh the kite and copy the mesh to the directory
    LEIairfoilMesh.mesh_LEI_airfoil(Corde_length, Depth, tube_size, at, Seam_angle, Sail_angle, nb_pts, lc_prof, lc_init, xmax, ymax, ep, yh)
    subprocess.run(["cp", "-r", "mesh.msh", repertory])
    subprocess.run(["rm", "mesh.msh"])

    # Check if the .msh file exists in the specified directory
    file_path = "Cas_de_base/mesh.msh"
    if os.path.exists(file_path):
        print("The file exists in the specified directory.")
    else:
        print("The file does not exist in the specified directory.")

    # Convert the mesh from gmsh to blockMesh format
    subprocess.run(['gmshToFoam mesh.msh'], shell=True, cwd=repertory)
    
    # Evaluate the quality of the mesh
    subprocess.run(['checkMesh'], shell=True, cwd=repertory)

    # Modify the boundary dictionary
    f = open(repertory + '/constant/polyMesh/boundary', 'r+')
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
    f = open(repertory + '/constant/polyMesh/boundary', 'w')
    f.writelines(new_lines)
    f.close()

    # Change the wind direction (equivalent to changing the AOA)
    v = U  # wind speed
    vx = v * np.cos(alpha * np.pi / 180)
    vy = v * np.sin(alpha * np.pi / 180)
    
    # Modify the 0/U dictionary
    f = open(repertory + '/0/U', 'r+')
    t = f.readlines()
    new_lines = []
    for line in t:
        if 'uniform' in line:
            new_lines = np.append(new_lines, 'internalField   uniform (' + str(vx) + ' ' + str(vy) + ' ' + '0);\n')
        else:
            new_lines = np.append(new_lines, line)
    f.close()
    f = open(repertory + '/0/U', 'w')
    f.writelines(new_lines)
    f.close()

    # Change the direction of liftDir/dragDir
    f = open(repertory + '/system/controlDict', 'r+')
    t = f.readlines()
    new_lines = []
    for line in t:
        if 'liftDir' in line:
            new_lines = np.append(new_lines, '        liftDir     (' + str(-np.sin(alpha * np.pi / 180)) + ' ' + str(np.cos(alpha * np.pi / 180)) + ' ' + '0);\n')
        elif 'dragDir' in line:
            new_lines = np.append(new_lines, '        dragDir     (' + str(np.cos(alpha * np.pi / 180)) + ' ' + str(np.sin(alpha * np.pi / 180)) + ' ' + '0);\n')
        else:
            new_lines = np.append(new_lines, line)
    f.close()
    f = open(repertory + '/system/controlDict', 'w')
    f.writelines(new_lines)
    f.close()

    # Run simpleFoam (commented out in the original code)
    # subprocess.run(['foamRun', '>', 'log'], shell=True, cwd=repertory)

    return ()

# Call the update_mesh function with the defined parameters
update_mesh(Va, Corde_length, Depth, tube_size, at, Seam_angle, Sail_angle, nb_pts, alpha, lc_prof, lc_init, xmax, ymax, ep, yh)
