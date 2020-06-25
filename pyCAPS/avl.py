
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

CL = np.zeros((len(AOA)))
CD = np.zeros((len(AOA)))

for i in range(len(AOA)):

    ## [setInputs]
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
    CL[i] = myAnalysis.getAnalysisOutVal("CLtot")
    CD[i] = myAnalysis.getAnalysisOutVal("CDtot") + cdo


# -----------------------------------------------------------------
# Close CAPS
# -----------------------------------------------------------------
myProblem.closeCAPS()


print(AOA)
print(CL)
print(CD)
print(CL/(CD))

CL_vsp = np.array([0.00000, 0.029176, 0.061672, 0.097286, 0.136768, 0.17849, 0.222624,
           0.268426, 0.316302, 0.36612, 0.417314, 0.47004, 0.524426, 0.581612,
           0.637318, 0.69279, 0.748682, 0.806806	])
CD_vsp = np.array([0.00933, 0.009518, 0.01014, 0.011284, 0.013078, 0.015558, 0.018868, 0.022978,
           0.027834, 0.033578, 0.040444, 0.047924, 0.05629, 0.06557, 0.07534,
            0.085574, 0.097742, 0.109666   ])


CL_wt = np.array([0.001188158, 0.012396452, 0.028356654, 0.048560202, 0.071526728,
                0.096041747, 0.12207918, 0.147892021, 0.172358845, 0.200432115,
                0.224363337, 0.251822052, 0.277720076, 0.298518762, 0.325209293,
                0.348050237, 0.37004265, 0.392125735, 0.4146746])
CD_wt = np.array([0.029861511, 0.033223537, 0.034715381, 0.036216291, 0.038166627,
                0.041748289, 0.045035197, 0.046592488, 0.053519293, 0.061718418,
                0.066820847, 0.075445686, 0.084582568, 0.093377667, 0.104621074,
                0.115726463, 0.127971984, 0.142028796, 0.157799279])

AOA_vsp = np.arange(0,18,1)
AOA_wt = np.arange(0,19,1)

print(len(AOA_vsp))
print(len(CL_vsp))
print(len(CD_vsp))
print(len(CL_wt))
print(len(CD_wt))

two_pi = (np.radians(AOA_vsp)*2*np.pi)*0.3

plt.figure()
plt.plot(AOA, CL/CD, 'b', label='AVL')
plt.plot(AOA_vsp, CL_vsp/CD_vsp, 'r', label='VSP')
plt.plot(AOA_wt, CL_wt/CD_wt, 'k', label='WT')

plt.legend()

plt.figure()
plt.plot(AOA, CL, 'b', label='AVL')
plt.plot(AOA_vsp, CL_vsp, 'r', label='VSP')
plt.plot(AOA_wt, CL_wt, 'k', label='WT')
plt.plot(AOA_vsp, two_pi, 'g')
plt.legend()

plt.figure()
plt.plot(AOA, CD, 'b', label='AVL')
plt.plot(AOA_vsp, CD_vsp, 'r', label='VSP')
plt.plot(AOA_wt, CD_wt, 'k', label='wt')

plt.legend()


plt.show()
