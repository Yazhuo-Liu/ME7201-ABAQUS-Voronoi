from abaqus import *
from abaqusConstants import *
import numpy as np
import random

parameters = np.load('parameters.npy',mmap_mode='r')
points = np.load('points.npy',mmap_mode='r')
vertices = np.load('vertices.npy',mmap_mode='r')
vor_points = np.load('vor_points.npy',mmap_mode='r')
edges_np = np.load('edges.npy',mmap_mode='r')

point_number = parameters[0]
length = parameters[1]
width = parameters[2]
depth = parameters[3]
ex = parameters[4]

size = (length + width + depth)/3
mx = 10000

edges = []
for edge in edges_np:
    edge_np = edge[~np.isnan(edge)].astype(int)
    edge = list(edge_np)
    edges.append(edge)
    
for edge in edges:
    for number in edge:
        if number !=-1 :
            for coord in vertices[number]:
                if coord > 0.5*mx*size or coord < -0.5*mx*size:
                    edges[edges.index(edge)].append(-1)
                    break



face_points = []
for edge in np.array(edges):
    edge = np.array(edge)
    temp = []
    if np.all(edge >= 0):
        for i in edge:
            temp.append(tuple(vertices[i]))
        temp.append(vertices[edge[0]])
    if (len(temp)>0):
        face_points.append(temp)

#
myModel = mdb.models['Model-1']
myPart = myModel.Part(name='Part-vor3', dimensionality=THREE_D, type=DEFORMABLE_BODY)

for i in range(len(face_points)):
    wire = myPart.WirePolyLine(mergeType=SEPARATE, meshable=ON, points=(face_points[i]))
    face_edge = myPart.getFeatureEdges(name=wire.name)
    myPart.CoverEdges(edgeList = face_edge, tryAnalytical=True)

faces = myPart.faces[:]
myPart.AddCells(faceList = faces)


# cut Voronoi
#create core to left
myPart2 = myModel.Part(name='Part-core', dimensionality=THREE_D, type=DEFORMABLE_BODY)
mySketch2 = myModel.ConstrainedSketch(name="mysketch-2",sheetSize = 200)
mySketch2.rectangle(point1=(0,0), point2=(length,width))
myPart2.BaseSolidExtrude(sketch=mySketch2, depth=depth)

#create base

myPart3 = myModel.Part(name='Part-base', dimensionality=THREE_D, type=DEFORMABLE_BODY)
mySketch3 = myModel.ConstrainedSketch(name='__profile__', sheetSize=200.0)
mySketch3.ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0))
curve = mySketch3.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(size*mx,0.0))
mySketch3.Line(point1=(0.0, mx*size), point2=(0.0, -mx*size))
mySketch3.autoTrimCurve(curve1=curve, point1=(-size*mx,0.0))
myPart3.BaseSolidRevolve(sketch=mySketch3, angle=360.0, flipRevolveDirection=OFF)

# instance
myAssembly = myModel.rootAssembly
myAssembly.Instance(name='Part-base-1', part=myModel.parts["Part-base"], dependent=ON)
myAssembly.Instance(name='Part-core-1', part=myModel.parts["Part-core"], dependent=ON)
# myAssembly.translate(instanceList=('Part-core-1', ), vector=(size*(ex-1)/2,size*(ex-1)/2,size*(ex-1)/2))
myAssembly.InstanceFromBooleanCut(name='Part-base-cut',instanceToBeCut=myAssembly.instances['Part-base-1'],
                                  cuttingInstances=(myAssembly.instances['Part-core-1'], ), originalInstances=DELETE)

# cut voronoi
myAssembly.Instance(name='Part-cut-1', part=myModel.parts["Part-base-cut"], dependent=ON)
myAssembly.Instance(name='Part-vor3-1', part=myModel.parts["Part-vor3"], dependent=ON)
myAssembly.InstanceFromBooleanCut(name='Part-vor3-cut',instanceToBeCut=myAssembly.instances['Part-vor3-1'],
                                  cuttingInstances=(myAssembly.instances['Part-cut-1'], ), originalInstances=DELETE)

for key in myAssembly.instances.keys():
    del myAssembly.instances[key]

for key in myModel.parts.keys():
    if key != "Part-vor3-cut":
        del myModel.parts[key]

myPart = mdb.models['Model-1'].parts['Part-vor3-cut']

for i in range(len(myPart.cells)):
    # create material
    a,b,c = random.uniform(0,1),random.uniform(0,1),random.uniform(0,1) 
    myMaterial = myModel.Material(name='Material-{}'.format(i))
    myMaterial.UserMaterial(mechanicalConstants=(a,b,c ))
    # create section
    myModel.HomogeneousSolidSection(name='Section-{}'.format(i), material='Material-{}'.format(i), thickness=None)
    # asign material
    region = myPart.Set(cells = myPart.cells[i:i+1],name = "Set-{}".format(i))
    myPart.SectionAssignment(region = region, sectionName='Section-{}'.format(i), offset=0.0,
                        offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)




