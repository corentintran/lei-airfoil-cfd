import LEIairfoilMesh
import runOpenFoam
import numpy as np
import os
import csv
import matplotlib.pyplot as plt

######  Study case inputs #########
case_name = 'default-kite'
Va = 20         # apparent wind 
L = 1           # true chord of the kite for Re number
Depth = 9       # max depth (in % of the chord)
tube_size = 9   # tube diameter (in % of the chord)
at = 25         # x-position of the max camber (in % of the chord)
TE_angle = 7   
remesh = True   #boolean for recompute mesh

# Range of angle of attack
min_AOA = 0
max_AOA = 17
delta_AOA = 2
range_AOA = np.arange(min_AOA, max_AOA, delta_AOA)
#####################################

# Default parameters of LEI airfoil geometry for meshing
Corde_length = 1
Seam_angle = 35
nb_pts = 100    # Number of points to define the profile

# Fluid domain
xmax = 40   # size of the domain downstream of the profile
ymax = 30   # half-thickness of the domain

# Mesh parameters
lc_init = 0.6           # size of the volumes at the boundaries
lc_prof = lc_init / 150 # size of the volumes around the profile

# Air characteristics
rho = 1.225
mu = 1.8e-5
nu = mu/rho

# Boundary layer parameters
Re = Va * L / nu    # Reynolds number
U = Re * nu         # Equivalent speed for the Re with a chord of 1 (used in the simulation)
# Size of the first cell in the boundary layer
# yh = bl_parameter.compute_deltay(Re, U, rho, nu)
yh = 1e-4
# Theoretical thickness of the boundary layer at the trailing edge
ep = LEIairfoilMesh.compute_delta_te(Re)

#Mesh of the kite
if remesh :
    LEIairfoilMesh.mesh_LEI_airfoil(Corde_length, Depth, tube_size, at, Seam_angle, TE_angle, nb_pts, lc_prof, lc_init, xmax, ymax, ep, yh)

# Create or reset the polar.csv file
csv_file = 'results/' + case_name + '.csv'
header = ["Alpha", "Time", "Cm", "Cd", "Cl", "Cl(f)", "Cl(r)"]
# Check if file exists
if os.path.exists(csv_file):
    # If file exists, clear its content but keep the header
    with open(csv_file, 'r') as file:
        lines = file.readlines()
    if len(lines) == 0 or lines[0].strip() != ','.join(header):
        # File is empty or header is incorrect, rewrite the correct header
        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
    else:
        # File has the correct header, clear its content but keep the header
        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
else:
    # If file does not exist, create it and write the header
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)

# Create or append the profiles caracteristics of the polar to 'polars_list.txt'
polars_list_file = 'data/polars_list.txt'
if not os.path.exists(polars_list_file):
    with open(polars_list_file, 'w') as file:
        file.write("##################\n")
        file.write(csv_file + "\n")
        file.write("##################\n")
        file.write(f"Tube size = {tube_size:.2f} %\nDepth = {Depth:.2f} %\nat {at:.2f} % \nTE angle = {TE_angle:.2f} °\nChord = {L:.2f} m\n\n")

else:
    with open(polars_list_file, 'r') as file:
        content = file.read()
    if csv_file not in content:
        with open(polars_list_file, 'a') as file:
            file.write("##################\n")
            file.write(csv_file + "\n")
            file.write("##################\n")
            file.write(f"Tube size = {tube_size:.2f} %\nDepth = {Depth:.2f} %\nat {at:.2f} % \nTE angle = {TE_angle:.2f} °\nChord = {L:.2f} m\n\n")
       

# Computation of the different angles of attack
for q in range(len(range_AOA)):
    runOpenFoam.compute_alpha(U, range_AOA[q], csv_file)

# Plotting the polars from polar.csv
alpha_values = []
Cl_values = []
Cd_values = []
Cm_values = []

with open(csv_file, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        alpha_values.append(float(row['Alpha']))  # Assuming 'Alpha' column is correctly labeled
        Cl_values.append(float(row['Cl']))
        Cd_values.append(float(row['Cd']))
        Cm_values.append(float(row['Cm']))

plt.figure(figsize=(12, 10))

# Plot Cl vs Alpha
plt.subplot(2, 2, 1)
plt.plot(alpha_values, Cl_values, 'b-o')
plt.xlabel('Alpha (degrees)')
plt.ylabel('Cl')
plt.title('Cl vs Alpha')
plt.grid(True)

# Plot Cd vs Alpha
plt.subplot(2, 2, 2)
plt.plot(alpha_values, Cd_values, 'r-o')
plt.xlabel('Alpha (degrees)')
plt.ylabel('Cd')
plt.title('Cd vs Alpha')
plt.grid(True)

# Plot Cm vs Alpha
plt.subplot(2, 2, 3)
plt.plot(alpha_values, Cm_values, 'g-o')
plt.xlabel('Alpha (degrees)')
plt.ylabel('Cm')
plt.title('Cm vs Alpha')
plt.grid(True)

# Plot Cl vs Cd
plt.subplot(2, 2, 4)
plt.plot(Cl_values, Cd_values, 'g-o')
plt.xlabel('Cd')
plt.ylabel('Cl')
plt.title('Cl vs Cd')
plt.grid(True)

plt.tight_layout()
plt.show()
