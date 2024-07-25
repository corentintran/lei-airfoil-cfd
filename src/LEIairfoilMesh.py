import numpy as np
import gmsh

# Interpolation function for creating smooth transitions between points
# Input: 
#   P1, P2 - Coordinates of the two ends [x, y]
#   t1, t2 - Tangent slopes at the two ends
#   n - Total number of points (default 20)
# Output:
#   points - List of interpolated points [[x1, y1], [x2, y2], ...]
def interpolation(P1, P2, t1, t2, n=20):
    x1 = P1[0]
    x2 = P2[0]
    y1 = P1[1]
    y2 = P2[1]
    b = np.array([y1, y2, np.tan(t1), np.tan(t2)])
    A = np.array([[x1 ** 3, x1 ** 2, x1, 1],
                  [x2 ** 3, x2 ** 2, x2, 1],
                  [3 * x1 ** 2, 2 * x1, 1, 0],
                  [3 * x2 ** 2, 2 * x2, 1, 0]])
    C = np.linalg.solve(A, b)
    x1 = np.linspace(x1, x2, n)
    y1 = C[0] * x1 ** 3 + C[1] * x1 ** 2 + C[2] * x1 + C[3]
    points = np.transpose(np.vstack((x1, y1)))
    return points   


# Function to create and mesh an LEI airfoil with given parameters
def mesh_LEI_airfoil(Corde_length, Depth, tube_size, at, Seam_angle, TE_angle, nb_pts, lc_prof, lc_edge, xmax, ymax, ep, yh):

    output = True  # mesh.msh output
    gmsh_GUI = False  # gmsh GUI

    # Calculate number of points for each segment based on the given parameters
    n1 = np.int_(nb_pts * (6 * tube_size) / (6 * tube_size + 200))
    n2 = np.int_(nb_pts * (2 * at) / (6 * tube_size + 200))
    n3 = np.int_(nb_pts * (2 * (100 - at)) / (6 * tube_size + 200))

    # Convert angles from degrees to radians
    Seam_angle = np.pi * Seam_angle / 180
    TE_angle = np.pi * TE_angle / 180
    radius = tube_size * Corde_length / 100 / 2  # Radius of the tube
    Origin_Circle = [radius, 0]

    e = 0.5  # Thickness, default to 0.5% of the chord length
    e = Corde_length * e / 100
    delta_Seam_angle = np.pi  

    # Generate points for the circular arc at the leading edge
    theta = np.linspace(3 * np.pi - Seam_angle - delta_Seam_angle, np.pi - Seam_angle, n1)
    x_cr = Origin_Circle[0] + radius * np.cos(theta)
    y_cr = Origin_Circle[1] + radius * np.sin(theta)
    points0 = np.transpose(np.array([x_cr, y_cr]))

    # Define key points on the airfoil
    P1 = [radius * (1 - np.cos(Seam_angle)), radius * np.sin(Seam_angle)]
    P2 = [at / 100 * Corde_length, Depth / 100 * Corde_length]
    P22 = [at / 100 * Corde_length, Depth / 100 * Corde_length - e]
    P3 = [Corde_length, 0]
    r1 = e * 0.2
    P31 = [P3[0] + r1 * np.sin(TE_angle), P3[1] + r1 * np.cos(TE_angle)]
    P32 = [P3[0] - r1 * np.sin(TE_angle), P3[1] - r1 * np.cos(TE_angle)]
    P33 = [P3[0] + r1 * np.sin(TE_angle + np.pi / 180 * 5), P3[1] + r1 * np.cos(TE_angle + np.pi / 180 * 5)]
    P34 = [P3[0] + r1 * np.sin(TE_angle + np.pi / 180 * 175), P3[1] + r1 * np.cos(TE_angle + np.pi / 180 * 175)]

    # Smooth the profile with additional points
    r = 0.06
    beta = Seam_angle
    P4 = [radius + (radius + r) * (-np.cos(Seam_angle + delta_Seam_angle)), (radius + r) * np.sin(Seam_angle + delta_Seam_angle)]
    P5 = [P4[0] - r * np.cos(beta), P4[1] + r * np.sin(beta)]
    ls_beta = np.linspace(np.pi - beta, 2 * np.pi - Seam_angle - delta_Seam_angle, 20)  # 20 points for the circle
    x_cr_1 = P4[0] + r * np.cos(ls_beta)
    y_cr_1 = P4[1] + r * np.sin(ls_beta)
    points5 = np.transpose(np.array([x_cr_1, y_cr_1]))

    # Create points for each segment using interpolation
    points1 = interpolation(P1, P2, (np.pi / 2) - Seam_angle, 0, n2)
    points2 = interpolation(P2, P31, 0, -TE_angle, n3)
    points3 = interpolation(P32, P22, -TE_angle, 0, n3)
    points4 = interpolation(P22, P5, 0, (np.pi / 2) - Seam_angle, n2)

    # Combine all points into a single array
    points = np.vstack((points0, points1[1:], points2[1:], points3[:], points4[1:], points5[1:-1]))

    if output:
        # Write mesh to file using gmsh
        gmsh.initialize()
        gmsh.option.setNumber("General.ExpertMode", 1)  # Enable expert mode (to disable all the messages meant for inexperienced users)
        gmsh.model.add("mesh")

        # Add points to the gmsh model
        for i in range(1, len(points0) + 1):
            gmsh.model.geo.addPoint(points[i][0], points[i][1], 0, lc_prof)  # leading edge
        for i in range(len(points0) + 1, len(points)):
            gmsh.model.geo.addPoint(points[i][0], points[i][1], 0, lc_prof)
        gmsh.model.geo.addPoint(P33[0], P33[1], 0, lc_prof / 10, 10000)  # P33
        gmsh.model.geo.addPoint(P34[0], P34[1], 0, lc_prof / 10, 10002)  # P34
        gmsh.model.geo.addPoint(P3[0], P3[1], 0, lc_prof, 10001)  # P3

        # Create splines and arcs to form the airfoil shape
        gmsh.model.geo.addSpline(np.arange(1, len(points0) + len(points1) + len(points2) - 2))
        gmsh.model.geo.addCircleArc(len(points0) + len(points1) + len(points2) - 3, 10001, 10000)
        gmsh.model.geo.addCircleArc(10000, 10001, 10002)
        gmsh.model.geo.addCircleArc(10002, 10001, len(points0) + len(points1) + len(points2) - 2)
        gmsh.model.geo.addSpline(np.hstack((np.arange(len(points0) + len(points1) + len(points2) - 2, len(points)), [1])))
        gmsh.model.geo.addCurveLoop([1, 2, 3, 4, 5])

        # creation of the fluid domain
        gmsh.model.geo.addPoint(-0.5, ymax, 0, lc_edge, 11001)
        gmsh.model.geo.addPoint(-0.5, -ymax, 0, lc_edge, 11002)
        gmsh.model.geo.addPoint(xmax, -ymax, 0, lc_edge, 11003)
        gmsh.model.geo.addPoint(xmax, ymax, 0, lc_edge, 11004)
        gmsh.model.geo.addPoint(0, 0, 0, lc_prof, 11005)
        gmsh.model.geo.addCircleArc(11001, 11005, 11002)
        gmsh.model.geo.addLine(11002, 11003)
        gmsh.model.geo.addLine(11003, 11004)
        gmsh.model.geo.addLine(11004, 11001)
        gmsh.model.geo.addCurveLoop([6, 7, 8, 9])
        gmsh.model.geo.addPlaneSurface([1, 2])

        # creation of the boundary layer
        f = gmsh.model.mesh.field.add("BoundaryLayer")
        gmsh.model.mesh.field.setNumbers(f, "CurvesList", [1, 2, 3, 4, 5])
        gmsh.model.mesh.field.setNumber(f, "Size", yh)
        gmsh.model.mesh.field.setNumber(f, "Ratio", 1.05)
        gmsh.model.mesh.field.setNumber(f, "Thickness", ep)
        gmsh.model.mesh.field.setNumber(f, "Quads", 1)
        gmsh.model.mesh.field.setAsBoundaryLayer(f)

        # Extrusion of the mesh and creation of physical groups
        gmsh.model.geo.extrude([(2, 1)], 0, 0, 1, [1], [1], 1)  # 3D modeling
        gmsh.model.addPhysicalGroup(2, [43, 55, 51], name="inlet")
        gmsh.model.addPhysicalGroup(2, [47], name="outlet")
        gmsh.model.addPhysicalGroup(2, [1, 56], name="side")
        gmsh.model.addPhysicalGroup(2, [23, 27, 31, 35, 39], name="airfoil")
        gmsh.model.addPhysicalGroup(3, [1], name="FLUID")

        # Finalization and file output
        gmsh.model.geo.synchronize()
        gmsh.model.mesh.generate()
        gmsh.option.setNumber("Mesh.MshFileVersion",2.2)   
        gmsh.write("data/mesh.msh")
        if gmsh_GUI:
            gmsh.fltk.run()
        gmsh.finalize()

    return()


## Boundary Layer functions ##

# Function to compute Reynolds number
def computeRe(Va, L, nu):
    return Va*L/nu  

# Function to compute equivalent speed for the Reynolds number with a chord of 1 (used in 2D simulations)
def computeU_eq(Re, nu):
    return Re*nu         

# Function to compute boundary layer thickness
def compute_deltay(Re, U, rho, nu, yplus=1) :
    Cf = 0.0576*(Re)**(-1/5)  # Empirical relation for skin friction coefficient Cf
    print(Cf)
    tau = 0.5*rho*Cf*U**2
    utau = np.sqrt(tau/rho)
    print(utau)
    return yplus * nu / utau

# Empirical relation for the turbulent boundary layer thickness at the trailing edge
def compute_delta_te(Re):
    return 0.38*Re**(-1/5)*1 

