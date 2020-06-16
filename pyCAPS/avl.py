
# Import pyCAPS and os module
## [import]
import pyCAPS
import os
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
workDir = os.path.join(str(args.workDir[0]), workDir)

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

## [setInputs]
myAnalysis.setAnalysisVal("Mach", 0.5)
myAnalysis.setAnalysisVal("Alpha", 1.0)
myAnalysis.setAnalysisVal("Beta", 0.0)

wing = {"groupName"    : "Wing", # Notice Wing is the value for the capsGroup attribute
        "numChord"     : 8,
        "spaceChord"   : 1.0,
        "numSpanTotal" : 24,
        "spaceSpan"    : 1.0}

myAnalysis.setAnalysisVal("AVL_Surface", [("Wing", wing)])

mass = 0.1773
x    =  0.02463
y    = 0.
z    = 0.2239
Ixx  = 1.350
Iyy  = 0.7509
Izz  = 2.095

myAnalysis.setAnalysisVal("Lunit", 1, units="m")
myAnalysis.setAnalysisVal("MassProp", ("Aircraft",{"mass":[mass,"kg"], "CG":[[x,y,z],"m"], "massInertia":[[Ixx, Iyy, Izz], "kg*m^2"]}))
myAnalysis.setAnalysisVal("Gravity", 32.18, units="ft/s^2")
myAnalysis.setAnalysisVal("Density", 0.002378, units="slug/ft^3")
myAnalysis.setAnalysisVal("Velocity", 64.5396, units="ft/s")
## [setInputs]

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
EigenValues = myAnalysis.getAnalysisOutVal("EigenValues")
print ("EigenValues ", EigenValues)
## [eigen values]

# -----------------------------------------------------------------
# Close CAPS
# -----------------------------------------------------------------
myProblem.closeCAPS()
