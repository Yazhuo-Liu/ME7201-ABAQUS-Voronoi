# -*- coding: utf-8 -*-

from scipy.spatial import *
import numpy as np
import matplotlib.pyplot as plt
from random import *

#initial variables
point_number = 100
length = 50
width = 50
depth = 1
seed = 500

parameters = np.array([point_number,length,width,depth])
np.random.seed(seed)

## Random points
# randPoints = np.random.rand(point_number,2)
# sizes = np.array([length,width])
# points = randPoints*sizes

## Equal space points
# x = np.linspace(1, length-1, 10)
# y = np.linspace(1, width-1, 10)
# xv, yv = np.meshgrid(x, y)
# x = xv.flatten()
# y = yv.flatten()
# points = np.vstack((x,y)).T

## Hexagon Grain
# points = []
# x = np.sqrt(2*np.sqrt(3)*length*width/point_number)
# print(x,int(length/(x/2))+2)
# for i in range(int(length/(x/2))+2):
#     for j in range(int(width/(x/np.sqrt(3)))+2):
#         if i%2 == 0:
#             points.append([i*x/2, j*x/np.sqrt(3)])
#         else:
#             points.append([i*x/2, (j+0.5)*x/np.sqrt(3)])
# points = np.array(points)

## Uniform grain size
points = []
x = np.sqrt(length*width/point_number)
for i in range(int(length/x)+2):
    for j in range(int(width/x)+2):
        px = np.random.uniform(i*x, (i+1)*x)
        py = np.random.uniform(j*x, (j+1)*x)
        points.append([px, py])       
points = np.array(points)


vor = Voronoi(points)#create instance

vertices = vor.vertices
edges = np.array(vor.ridge_vertices)
vor_points = vor.ridge_points

np.save('parameters.npy', parameters)
np.save('points.npy', points)
np.save('vor_points.npy' , vor_points)
np.save('vertices.npy' , vertices)
np.save('edges.npy' , edges)

plt.figure()
plt.plot(points[:,0],points[:,1],'.')

# Limited edges
for simplex in np.array(edges):
    if np.all(simplex >= 0):
        plt.plot(vertices[simplex,0],vor.vertices[simplex,1],'black')

# Infinite edges
center = points.mean(axis=0)
# print(center)
for pointidx, simplex in zip(vor_points,edges):
    simplex = np.asarray(simplex)

    if np.any(simplex < 0):
        # print(pointidx, simplex)
        i = simplex[simplex >= 0]
        t = points[pointidx[1]] - points[pointidx[0]]
        t = t/np.linalg.norm(t)
        n = np.array([-t[1],t[0]])
        midpoint = points[pointidx].mean(axis=0)
        far_point = vor.vertices[i] + np.sign(np.dot(midpoint - center, n))*n*100
        plt.plot([vor.vertices[i,0], far_point[0][0]], [vor.vertices[i,1], far_point[0][1]], 'k--')
        
plt.xlim((0,length+10))
plt.ylim((0,width+10))
plt.show()

