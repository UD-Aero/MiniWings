import pyCAPS
import os
import numpy as np
import matplotlib.pyplot as plt

myProblem = pyCAPS.capsProblem()
geometryScript = os.path.join("..","csmData","miniWings.csm")

myGeometry = myProblem.loadCAPS(geometryScript)
myGeometry.setGeometryVal('af_row', 1.0)
myGeometry.setGeometryVal('af_col', 1.0)
myGeometry.setGeometryVal('aspect', 10.0)

workDir = "MonoWing"

myAnalysis = myProblem.loadAIM(	aim = "frictionAIM",
                                analysisDir = workDir )

myAnalysis.setAnalysisVal("Mach", 0.1)
myAnalysis.setAnalysisVal("Altitude", 900, units= "m")
myAnalysis.preAnalysis()

# -----------------------------------------------------------------
# Run Friction
# -----------------------------------------------------------------
currentDirectory = os.getcwd() # Get our current working directory

os.chdir(myAnalysis.analysisDir) # Move into test directory
os.system("friction frictionInput.txt frictionOutput.txt > Info.out")
os.chdir(currentDirectory) # Move back to working directory

myAnalysis.postAnalysis()

Cdtotal = myAnalysis.getAnalysisOutVal("CDtotal")
CdForm  = myAnalysis.getAnalysisOutVal("CDform")
CdFric  = myAnalysis.getAnalysisOutVal("CDfric")
## [output]

print("Total drag =", Cdtotal )
print("Form drag =", CdForm)
print("Friction drag =", CdFric)

cdo = Cdtotal
myAnalysis = myProblem.loadAIM(aim = "avlAIM",
                               analysisDir = workDir)

AOA = np.array(5.0)

CL = np.zeros((len(AOA)))
CD = np.zeros((len(AOA)))

for i in range(len(AOA)):

    myAnalysis.setAnalysisVal("Mach", 0.1)
    myAnalysis.setAnalysisVal("Alpha", AOA[i])
    myAnalysis.setAnalysisVal("Beta", 0.0)

    groups = myAnalysis.getAttributeVal("capsGroup", attrLevels=2)

    wing = []

    for j in groups:

        tmpDict = {'groupName' : j}

        tmpDict['numChord']   = 8.0
        tmpDict['spaceChord'] = 0.0
        tmpDict['numSpanTotal'] = 18.0
        tmpDict['spaceSpan'] = 1.0

        wing.append((j, tmpDict))

    myAnalysis.setAnalysisVal("AVL_Surface", wing)
    myAnalysis.preAnalysis()

    currentDirectory = os.getcwd() # Get our current working directory

    os.chdir(myAnalysis.analysisDir) # Move into test directory
    os.system("avl caps < avlInput.txt > avlOutput.txt");
    os.chdir(currentDirectory) # Move back to working directory

    myAnalysis.postAnalysis()
    CL[i] = myAnalysis.getAnalysisOutVal("CLtot")
    CD[i] = myAnalysis.getAnalysisOutVal("CDtot") + cdo

myProblem.closeCAPS()
