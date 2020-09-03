import pyCAPS
import os
import numpy as np
import matplotlib.pyplot as plt
from openmdao.api import Problem, Group, IndepVarComp, ExplicitComponent, ScipyOptimizeDriver
import openmdao.api as om
# Problem context:
# Determine 'optimal design' for C-130 - like aircraft.
# Use distributed lift wing set to compare with monowing and evaluate range
# based L/D.
#
# Design Variables:
# gap
# stagger
# stagger_row
# af_col
# af_row
# aspect

geometryScript = os.path.join("..","csmData","miniWings.csm")
workDir = 'GA'

myProblem = pyCAPS.capsProblem()
myGeometry = myProblem.loadCAPS(geometryScript)

# Load AVL aim
avl = myProblem.loadAIM(aim = "avlAIM",
                        altName = "avl",
                        analysisDir = workDir)

groups = avl.getAttributeVal("capsGroup", attrLevels=2)
wing = []

for j in groups:

    tmpDict = {'groupName' : j}

    tmpDict['numChord']   = 8.0
    tmpDict['spaceChord'] = 0.0
    tmpDict['numSpanTotal'] = 18.0
    tmpDict['spaceSpan'] = 1.0

    wing.append((j, tmpDict))

avl.setAnalysisVal("AVL_Surface", wing)
avl.setAnalysisVal("Alpha", 5.0)

# Create OpenMDAOComponent - ExternalCode
avlComponent = avl.createOpenMDAOComponent(["gap", "stagger", 'stagger_row', 'af_col', 'af_row', 'aspect'], # Geometry design variables
                                            ["CDtot", "CLtot", "Cmtot"], # Output parameters
                                            changeDir = True, # Change in the analysis directory during execution
                                            executeCommand = ["avl", "caps"],
                                            stdin     = "avlInput.txt", # Modify stdin and stdout
                                            stdout    = "avlOutput.txt", # for avl execution
                                            setSensitivity = {"type": "fd",  # Set sensitivity information for the
                                                              "form" : "central", # component
                                                              "step_size" : 1.0E-3})

# Friction model
friction = myProblem.loadAIM(aim = "frictionAIM",
                             altName = 'friction',
                             analysisDir = workDir )

friction.setAnalysisVal("Mach", 0.1)
friction.setAnalysisVal("Altitude", 900, units= "m")

frictionComponent = friction.createOpenMDAOComponent(["gap", "stagger", 'stagger_row', 'af_col', 'af_row', 'aspect'], # Geometry design variables
                                                      ["CDtotal"], # Output parameters
                                                      changeDir = True, # Change in the analysis directory during execution
                                                      executeCommand = ["friction", "frictionInput.txt", "frictionOutput.txt > Info.out"],
                                                      stdin     = "frictionInput.txt", # Modify stdin and stdout
                                                      stdout    = "frictionOutput.txt", # for avl execution
                                                      setSensitivity = {"type": "fd",  # Set sensitivity information for the
                                                                        "form" : "central", # component
                                                                        "step_size" : 1.0E-3})

# Setup and run OpenMDAO model
print("Setting up and running OpenMDAO model")

# Create a component that calculates the lift to drag ratio
class l2dComponent(ExplicitComponent):
    def __init__(self):
        super(l2dComponent,self).__init__()
        self.add_input("CL", val = 0.0)
        self.add_input("CD", val = 0.0)
        self.add_input("CDf", val = 0.0)

        self.add_output("L2D", shape=1)

    def compute(self, params, unknowns):

        unknowns["L2D"] = -params["CL"] / (params["CD"] + params["CDf"]) # Minus since we want to maximize L/D in the objective

# Create a Group class for our design problem
class MaxLtoD(Group):
    def __init__(self):
        super(MaxLtoD, self).__init__()

        # Add design variables
        self.add_subsystem('dv_Gap', IndepVarComp('gap'))
        self.add_subsystem('dv_Stagger', IndepVarComp('stagger'))
        self.add_subsystem('dv_StaggerRow', IndepVarComp('stagger_row'))
        self.add_subsystem('dv_afCol', IndepVarComp('af_col'))
        self.add_subsystem('dv_afRow', IndepVarComp('af_row'))
        self.add_subsystem('dv_aspect', IndepVarComp('aspect'))

        # Add AVL component
        self.add_subsystem("AVL", avlComponent)
        self.add_subsystem("Friction", frictionComponent)

        self.add_subsystem("L2D", l2dComponent())

        # Make connections between design variables and inputs to AVL and geometry
        self.connect("dv_Gap.gap",                 "AVL.gap")
        self.connect("dv_Stagger.stagger",         "AVL.stagger")
        self.connect("dv_StaggerRow.stagger_row" , "AVL.stagger_row")
        self.connect("dv_afCol.af_col" ,           "AVL.af_col")
        self.connect("dv_afRow.af_row" ,           "AVL.af_row")
        self.connect("dv_aspect.aspect" ,          "AVL.aspect")

        # Make connections between design variables and inputs to Friction and geometry
        self.connect("dv_Gap.gap",                 "Friction.gap")
        self.connect("dv_Stagger.stagger",         "Friction.stagger")
        self.connect("dv_StaggerRow.stagger_row" , "Friction.stagger_row")
        self.connect("dv_afCol.af_col" ,           "Friction.af_col")
        self.connect("dv_afRow.af_row" ,           "Friction.af_row")
        self.connect("dv_aspect.aspect" ,          "Friction.aspect")

        # Connect AVL outputs to L2D calculation inputs
        self.connect("AVL.CDtot", "L2D.CD")
        self.connect("AVL.CLtot", "L2D.CL")
        self.connect("Friction.CDtotal", "L2D.CDf")

# Iniatate the the OpenMDAO problem
openMDAOProblem = Problem()
openMDAOProblem.model = MaxLtoD()

# Set design driver parameters
openMDAOProblem.driver = om.SimpleGADriver()
# openMDAOProblem.driver.options['bits'] = {'dvStagger.stagger': 8,
#                                           'dvStaggerRow.stagger_row': 8,
#                                           'dvGap.gap': 8,}
openMDAOProblem.driver.options['max_gen'] = 10
openMDAOProblem.driver.options['pop_size'] = 50
openMDAOProblem.driver.options['run_parallel'] = True
openMDAOProblem.driver.options['procs_per_model'] = 2
openMDAOProblem.driver.options['debug_print'] = ['desvars', 'objs', 'totals']

openMDAOProblem.model.add_design_var("dv_Gap.gap",                lower=0.5, upper=5.0) # Geometry design values
openMDAOProblem.model.add_design_var("dv_Stagger.stagger",        lower=0.5, upper=5.0) # Geometry design values
openMDAOProblem.model.add_design_var("dv_StaggerRow.stagger_row", lower=0.0, upper=5.0)
openMDAOProblem.model.add_design_var("dv_afCol.af_col",           lower=1.0, upper=5.0)
openMDAOProblem.model.add_design_var("dv_afRow.af_row",           lower=1.0, upper=5.0)
openMDAOProblem.model.add_design_var("dv_aspect.aspect",          lower=5.0, upper=10.0)

# Set objective
openMDAOProblem.model.add_objective('L2D.L2D')

openMDAOProblem.driver.recording_options['record_objectives'] = True
openMDAOProblem.driver.recording_options['record_constraints'] = True
openMDAOProblem.driver.recording_options['record_desvars'] = True

openMDAOProblem.recording_options['includes'] = []
openMDAOProblem.recording_options['record_objectives'] = True
openMDAOProblem.recording_options['record_constraints'] = True
openMDAOProblem.recording_options['record_desvars'] = True

driverRecorder = om.SqliteRecorder('GA/driverRecorder.sql')
problemRecorder = om.SqliteRecorder('GA/problemRecorder.sql')

openMDAOProblem.driver.add_recorder(driverRecorder)
openMDAOProblem.driver.add_recorder(problemRecorder)

# Setup and run
openMDAOProblem.setup()

openMDAOProblem.set_val('dv_Gap.gap',                1.0)
openMDAOProblem.set_val('dv_Stagger.stagger',        1.0)
openMDAOProblem.set_val('dv_StaggerRow.stagger_row', 0.0)
openMDAOProblem.set_val("dv_afCol.af_col",           1.0)
openMDAOProblem.set_val("dv_afRow.af_row",           1.0)
openMDAOProblem.set_val("dv_aspect.aspect",          8.0)

openMDAOProblem.run_driver()

print("Aero Properties:")
print('CL: ', openMDAOProblem.get_val('AVL.CLtot'))
print('CDi: ', openMDAOProblem.get_val('AVL.CDtot'))
print('CDf: ', openMDAOProblem.get_val('Friction.CDtotal'))

print('Design Variables:')
print('Gap: ', openMDAOProblem.get_val('dv_Gap.gap'))
print('Stagger: ', openMDAOProblem.get_val('dv_Stagger.stagger'))
print('Stagger Row: ', openMDAOProblem.get_val('dv_StaggerRow.stagger_row'))

myProblem.closeCAPS()
