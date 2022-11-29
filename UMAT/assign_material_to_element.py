from abaqus import *
from abaqusConstants import *
import numpy as np

myModel = mdb.models['Model-1']
myPart = mdb.models['Model-1'].parts['mesh']
C11 = 259000.
C12 = 179000.
C44 = 109000.
Depvar = 130
n = 10.
adot = 0.001
h_0 = 110
tau_s = 580.5
tau_0 = 95.5
q0 = 1
q1 = 1

for element in myPart.elements:
    i = element.label
    psi = np.round(np.random.uniform(0,45),2) * np.pi / 180
    Q = np.array([[np.cos(psi), -np.sin(psi),0], [np.sin(psi), np.cos(psi), 0],[0, 0, 1]])
    myMaterial = myModel.Material(name='MATERIAL-Ele-{}'.format(i))
    myMaterial.Depvar(n=130)
    mat = np.zeros(160)
    
    # cubic constants
    mat[0] = C11
    mat[1] = C12
    mat[2] = C44

    # number of slip systems
    mat[24] = 1

    # slip plane
    mat[32] = 1.
    mat[33] = 1.
    mat[34] = 1.

    #slip direction
    mat[35] = 1.
    mat[36] = 1.
    mat[37] = 0.

    # Grain Orientation
    # The directions in global system and directions in local cubic crystal system of 
    # two non parallel vectors are needed to determine the crystal orientation.
    mat[56] = 1.
    mat[57] = 0.
    mat[58] = 0.

    mat[59] = Q[0,0]
    mat[60] = Q[1,0]
    mat[61] = Q[2,0]

    mat[64] = 0.
    mat[65] = 1.
    mat[66] = 0.

    mat[67] = Q[0,1]
    mat[68] = Q[1,1]
    mat[69] = Q[2,1]

    # Constitutive law
    mat[72] = n
    mat[73] = adot

    # parameters characterizing the self and latent-hardening laws of slip systems
    mat[96] = h_0
    mat[97] = tau_s
    mat[98] = tau_0

    mat[104] = q0
    mat[105] = q1
    mat[106] = 0.

    # PROPS(145) -- parameter theta controlling the implicit 
    #               integration, which is between 0 and 1
    #               0.  : explicit integration
    #               0.5 : recommended value
    #               1.  : fully implicit integration
    mat[144] = 0.5
    mat[145] = 1

    # parameters characterizing iteration method
    mat[152] = 0.
    mat[153] = 100
    mat[154] = 0.00001

    myConstants = tuple(mat)

    myMaterial.UserMaterial(mechanicalConstants=myConstants)
    # create section
    myModel.HomogeneousSolidSection(name='Section-Ele-{}'.format(i), material='MATERIAL-Ele-{}'.format(i), thickness=None)

myElement = myPart.elements

# create void list
element_number = []
for i in range(len(myElement)):
    element_number.append([])

for element in myElement:
    i = element.label
    element_number[i-1].append(element.label-1)

# create element set and assign materials
for set_element in element_number:
    if set_element == []:
        continue
    else:
        element = myElement[set_element[0]:set_element[0]+1]
        for i in range(1, len(set_element)):
            element += myElement[set_element[i]:set_element[i]+1]
        setName = 'Element-{}'.format(element_number.index(set_element)+1)
        p = mdb.models['Model-1'].parts['mesh']
        # region = p.sets['Element-{}'.format(element_number.index(set_element)+1)]
        region = p.Set(elements=element, name='Element-{}'.format(element_number.index(set_element)+1))
        p = mdb.models['Model-1'].parts['mesh']
        p.SectionAssignment(region=region, sectionName='Section-Ele-{}'.format(element_number.index(set_element)+1))
