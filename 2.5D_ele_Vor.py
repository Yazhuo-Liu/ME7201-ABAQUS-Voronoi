# -*- coding: utf-8 -*-

from abaqus import *
from abaqusConstants import *
import numpy as np
import random

parameters = np.load('parameters.npy',mmap_mode='r')
points = np.load('points.npy',mmap_mode='r')
vertices = np.load('vertices.npy',mmap_mode='r')
vor_points = np.load('vor_points.npy',mmap_mode='r')
edges = np.load('edges.npy',mmap_mode='r')

point_number = parameters[0]
length = parameters[1]
width = parameters[2]
depth = parameters[3]
mass = 1

# create base
myModel = mdb.models["Model-1"]
mySketch1 = myModel.ConstrainedSketch(name='sketch1', sheetSize=200.0)
mySketch1.rectangle(point1=(0.0, 0.0), point2=(length, width))
myPart = myModel.Part(name='Part-voronoi', dimensionality=THREE_D,type=DEFORMABLE_BODY)
myPart2 = myModel.Part(name="Part-analys", dimensionality=THREE_D, type=DEFORMABLE_BODY)
myPart = myPart.BaseSolidExtrude(depth=depth, sketch=mySketch1)
myPart2 = myPart2.BaseSolidExtrude(depth=depth, sketch=mySketch1)
myPart = mdb.models['Model-1'].parts['Part-voronoi']
myPart2 = mdb.models['Model-1'].parts['Part-analys']

#create voronoi
mySketch2 = myModel.ConstrainedSketch(name='__profile__',sheetSize=200, gridSpacing=10)

# create limited edge
for edge in np.array(edges):
    if np.all(edge >= 0):
        mySketch2.Line(point1=tuple(vertices[edge[0]]), point2=tuple(vertices[edge[1]]))
        
# # create infinite edge
center = points.mean(axis=0)
for pointidx, simplex in zip(vor_points,edges):
    simplex = np.asarray(simplex)
    if np.any(simplex < 0):
        i = simplex[simplex >= 0]
        t = points[pointidx[1]] - points[pointidx[0]]
        t = t/np.linalg.norm(t)
        n = np.array([-t[1],t[0]])
        midpoint = points[pointidx].mean(axis=0)
        far_point = vertices[i] + np.sign(np.dot(midpoint - center, n))*n*100
        mySketch2.Line(point1=tuple(vertices[i[0]]), point2=tuple(far_point[0]))

# partition face
face1center = (length/2, width/2,0)
myPart.PartitionFaceBySketch(faces=myPart.faces.findAt(face1center), sketch=mySketch2)

myPart = mdb.models['Model-1'].parts['Part-voronoi']
e = myPart.edges
c = myPart.cells
v = myPart.vertices
myPart.Set(edges=e, name='Edges')
myPart.Set(vertices=v, name='Vertices')
myEdges_obj = mdb.models['Model-1'].parts['Part-voronoi'].allSets['Edges'].edges
myVertices_obj = mdb.models['Model-1'].parts['Part-voronoi'].allSets['Vertices'].vertices

myVertices = []
for i in range(0,len(myVertices_obj)):
    VerCood = myVertices_obj[i].pointOn[0]
    myVertices.append([VerCood[0],VerCood[1],VerCood[2]])
    
myEdges = []
for i in range(0,len(myEdges_obj)):
    indexs = myEdges_obj[i].getVertices()
    myEdges.append([indexs[0],indexs[1]])
    

def is_inner_point(point,xlim,ylim):
    isInner = False
    x, y = point[0], point[1]
    if x>0 and x<xlim and y>0 and y<ylim:
        isInner = True
    return isInner

myPart = mdb.models['Model-1'].parts['Part-voronoi']

for i in range(0,len(myEdges)):
    boundindex = myEdges[i] 
    boundary1 = np.array(myVertices[boundindex[0]])
    boundary2 = np.array(myVertices[boundindex[1]])
    midpoint = (boundary1 + boundary2)/2
    if midpoint[2] == 0.0 and is_inner_point(midpoint, length, width):
        sweepEdge = mdb.models['Model-1'].parts['Part-voronoi'].edges.findAt((length,width,0.4*depth))
        pickcells = mdb.models['Model-1'].parts['Part-voronoi'].cells
        cutEdge = mdb.models['Model-1'].parts['Part-voronoi'].edges.findAt((midpoint[0],midpoint[1],0))
        myPart.PartitionCellByExtrudeEdge(line=sweepEdge, cells=pickcells, edges=cutEdge, sense=FORWARD)


# Assign Materials
for i in range(len(myPart.cells)):
    psi = np.random.uniform(0,90)
    myMaterial = myModel.Material(name='Material-{}'.format(i))
    myMaterial.Density(table=((mass, ), ))
    myMaterial.Depvar(n=81)
    myMaterial.UserMaterial(mechanicalConstants=(279000,119000,80000,psi,0,0,0.001,0.02,100,3000,500,4,1,1.4,0,0,0,0)) 
    # create section
    myModel.HomogeneousSolidSection(name='Section-{}'.format(i), material='Material-{}'.format(i), thickness=None)
    # asign material
    region = myPart.Set(cells = myPart.cells[i:i+1],name = "Set-{}".format(i))
    myPart.SectionAssignment(region = region, sectionName='Section-{}'.format(i), offset=0.0,
                        offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)


# mesh analysis Part
myPart2.seedPart(size=min(length,width)/50.0, deviationFactor=0.1, minSizeFactor=0.1)
myPart2.generateMesh()
myCells = myPart.cells
myNodes = myPart2.nodes
myElement = myPart2.elements

# create void list
element_number = []
for i in range(len(myCells)):
    element_number.append([])

for element in myElement:
    points = []
    for index in element.connectivity:
        points.append(list(myNodes[index].coordinates))
    center = np.array(points).mean(axis=0)
    index = myCells.findAt(center, ).index
    for i in range(len(myCells)):
        if index == i:
            element_number[i].append(element.label-1)

# create element set and assign materials
for set_element in element_number:
    if set_element == []:
        continue
    else:
        element = myElement[set_element[0]:set_element[0]+1]
        for i in range(1, len(set_element)):
            element += myElement[set_element[i]:set_element[i]+1]
        region = myPart2.Set(elements=element, name="Set-{}".format(element_number.index(set_element)))
        p = mdb.models['Model-1'].parts['Part-analys']
        p.SectionAssignment(region=region, sectionName='Section-{}'.format(element_number.index(set_element)) 
                            , offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)

