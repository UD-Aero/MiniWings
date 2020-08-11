
# Import pyCAPS and os module
## [import]
import pyCAPS
import os
import numpy as np
import matplotlib.pyplot as plt
## [import]
## Comment

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
myAnalysis = myProblem.loadAIM(	aim = "frictionAIM",
                                analysisDir = workDir )
## [loadAIM]

# -----------------------------------------------------------------
# Set new Mach/Alt parameters
# -----------------------------------------------------------------
print ("Setting Mach & Altitude Values")
## [setInputs]
myAnalysis.setAnalysisVal("Mach", 0.1)

# Note: friction wants kft (defined in the AIM) - Automatic unit conversion to kft
myAnalysis.setAnalysisVal("Altitude", 900, units= "m")
## [setInputs]

# -----------------------------------------------------------------
# Run AIM pre-analysis
# -----------------------------------------------------------------
## [preAnalysis]
myAnalysis.preAnalysis()
## [preAnalysis]

# -----------------------------------------------------------------
# Run Friction
# -----------------------------------------------------------------
currentDirectory = os.getcwd() # Get our current working directory

os.chdir(myAnalysis.analysisDir) # Move into test directory

os.system("friction frictionInput.txt frictionOutput.txt > Info.out")

os.chdir(currentDirectory) # Move back to working directory

# -----------------------------------------------------------------
# Run AIM post-analysis
# -----------------------------------------------------------------
## [postAnalysis]
myAnalysis.postAnalysis()
## [postAnalysis]

# -----------------------------------------------------------------
# Get Output Data from Friction
# -----------------------------------------------------------------
## [output]
Cdtotal = myAnalysis.getAnalysisOutVal("CDtotal")
CdForm  = myAnalysis.getAnalysisOutVal("CDform")
CdFric  = myAnalysis.getAnalysisOutVal("CDfric")
## [output]

print("Total drag =", Cdtotal )
print("Form drag =", CdForm)
print("Friction drag =", CdFric)
# # -----------------------------------------------------------------
# # Close CAPS
# # -----------------------------------------------------------------
#
cdo = Cdtotal
#


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

AOA = np.arange(0,20,2)
staggerRow = np.arange(0,-1.25,-0.25)

CL = np.zeros((len(AOA), len(staggerRow)))
CD = np.zeros((len(AOA), len(staggerRow)))

for i in range(len(staggerRow)):
    for z in range(len(AOA)):

        ## [setInputs]
        myAnalysis.setAnalysisVal("Mach", 0.1)
        myAnalysis.setAnalysisVal("Alpha", AOA[z])
        myAnalysis.setAnalysisVal("Beta", 0.0)

        myGeometry.setGeometryVal('gap', 1.0)
        myGeometry.setGeometryVal('stagger', 1.0)
        myGeometry.setGeometryVal('stagger_row', staggerRow[i])

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

        print(myAnalysis.getAnalysisOutVal("CLtot"))
        print(myAnalysis.getAnalysisOutVal("CDtot"))

        ## [eigen values]
        CL[z,i] = myAnalysis.getAnalysisOutVal("CLtot")
        CD[z,i] = myAnalysis.getAnalysisOutVal("CDtot") + 0.0001


# -----------------------------------------------------------------
# Close CAPS
# -----------------------------------------------------------------
myProblem.closeCAPS()


print(AOA)
print(CL)
print(CD)
print(CL/(CD))

plt.figure()
for k in range(len(staggerRow)):
    plt.plot(AOA, CL[:,k]/CD[:,k], label='stagger_row = ' + str(staggerRow[k]))
plt.legend()

plt.figure()
for k in range(len(staggerRow)):
    plt.plot(AOA, CL[:,k], label='stagger_row = ' + str(staggerRow[k]))
plt.legend()

plt.figure()
for k in range(len(staggerRow)):
    plt.plot(AOA, CD[:,k], label='stagger_row = ' + str(staggerRow[k]))
plt.legend()


plt.show()
