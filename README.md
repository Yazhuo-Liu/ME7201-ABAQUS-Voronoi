# ME7201-ABAQUS-Voronoi

This is the ABAQUS python script for generating Voronoi Polycrystal geometry.

Preprocessor:
    ~ Geometry parameters: width, height, number of seed points, depth, etc.
    ~ Required package: numpy, scipy

ele_Vor:
    generate the mesh first and assign material properties to the mesh element based on the Voronoi structure. It means that the grain boundaries are non-smooth or in other words, "stepped".
    ~ Material constants
    ~ Required env: ABAQUS 6.13+ (with Python2.7 numpy1.4.1+)

cell_Vor:
    Devide the part into several cells based on the Voronoi structure. And then generate mesh for each cell. In this case, the grain boundaries are smooth, or at least represents the real geometry structure.
    ~ Material constants
    ~ Required env: ABAQUS 6.13+ (with Python2.7 numpy1.4.1+)

Difference between ele_Vor and cell_Vor:
![alt text](https://github.com/Yazhuo-Liu/ME7201-ABAQUS-Voronoi/blob/main/cell%20and%20ele%20difference.png)

Idea for preprocessor:
![alt text](https://github.com/Yazhuo-Liu/ME7201-ABAQUS-Voronoi/blob/main/idea%20for%20preprocessor.png)

