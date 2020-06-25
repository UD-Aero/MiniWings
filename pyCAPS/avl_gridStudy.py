
# Import pyCAPS and os module
## [import]
import pyCAPS
import os
import numpy as np
import matplotlib.pyplot as plt
## [import]

# -----------------------------------------------------------------
# Initialize capsProblem object
# -----------------------------------------------------------------
## [initateProblem]
myProblem = pyCAPS.capsProblem()
## [initateProblem]

# -----------------------------------------------------------------
# Load CSM file and Change a design parameter - area in the geometry
# Any despmtr from the avlWing.csm file are available inside the pyCAPS script
# They are: thick, camber, area, aspect, taper, sweep, washout, dihedral
# -----------------------------------------------------------------

## [geometry]
geometryScript = os.path.join("..","csmData","miniWings.csm")
myGeometry = myProblem.loadCAPS(geometryScript)
## [geometry]

# Create working directory variable
## [localVariable]
workDir = "AVLEigenTest"
## [localVariable]

# -----------------------------------------------------------------
# Load desired aim
# -----------------------------------------------------------------
print ("Loading AIM")
## [loadAIM]
myAnalysis = myProblem.loadAIM(aim = "avlAIM",
                               analysisDir = workDir)
## [loadAIM]
# -----------------------------------------------------------------
# Also available are all aimInput values
# Set new Mach/Alt parameters
# -----------------------------------------------------------------

AOA = np.arange(0,12,1)
gridStudy = [0.6, 1.0, 1.4]

CL = np.zeros((len(AOA),len(gridStudy)))
CD = np.zeros((len(AOA),len(gridStudy)))
cdo = 0.00933

for k in range(len(gridStudy)):
    for i in range(len(AOA)):

        ## [setInputs]
        myAnalysis.setAnalysisVal("Mach", 0.1)
        myAnalysis.setAnalysisVal("Alpha", AOA[i])
        myAnalysis.setAnalysisVal("Beta", 0.0)

        groups = myAnalysis.getAttributeVal("capsGroup", attrLevels=2)

        wing = []

        for j in groups:

            tmpDict = {'groupName' : j}

            tmpDict['numChord']   = 8.0*gridStudy[k]
            tmpDict['spaceChord'] = 0.0
            tmpDict['numSpanTotal'] = 18.0
            tmpDict['spaceSpan'] = 1.0

            wing.append((j, tmpDict))

        print(wing)

        myAnalysis.setAnalysisVal("AVL_Surface", wing)

        # -----------------------------------------------------------------
        # Run AIM pre-analysis
        # -----------------------------------------------------------------
        ## [preAnalysis]
        myAnalysis.preAnalysis()
        ## [preAnalysis]

        # -----------------------------------------------------------------
        # Run AVL
        # -----------------------------------------------------------------
        ## [runAVL]
        print ("Running AVL")
        currentDirectory = os.getcwd() # Get our current working directory
        os.chdir(myAnalysis.analysisDir) # Move into test directory

        os.system("avl caps < avlInput.txt > avlOutput.txt");

        os.chdir(currentDirectory) # Move back to working directory
        ## [runAVL]

        # -----------------------------------------------------------------
        # Run AIM post-analysis
        # -----------------------------------------------------------------
        ## [postAnalysis]
        myAnalysis.postAnalysis()
        ## [postAnalysis]

        # -----------------------------------------------------------------
        # Get Output Data from AVL
        # These calls access aimOutput data
        # -----------------------------------------------------------------

        ## [eigen values]
        CL[i,k] = myAnalysis.getAnalysisOutVal("CLtot")
        CD[i,k] = myAnalysis.getAnalysisOutVal("CDtot") + cdo


# -----------------------------------------------------------------
# Close CAPS
# -----------------------------------------------------------------
myProblem.closeCAPS()


print(AOA)
print(CL)
print(CD)
print(CL/(CD+cdo))


plt.figure()

for i in range(len(gridStudy)):
    plt.plot(AOA, CL[:,i]/CD[:,i])

plt.show()
