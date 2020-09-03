import os
import matplotlib.pyplot as plt
import numpy as np
import openmdao.api as om

fid = os.path.join('../', 'pyCAPS', 'GA', 'driverRecorder.sql')

desVar = ['dv_Stagger.stagger', 'dv_StaggerRow.stagger_row', 'dv_Gap.gap', "dv_afCol.af_col", "dv_afRow.af_row", "dv_aspect.aspect"]
cons = []
objs = ['L2D.L2D']

cr = om.CaseReader(fid)
driverResults = cr.list_cases('driver')

dVs = np.zeros((len(driverResults),len(desVar)))
obj = np.zeros((len(driverResults),len(objs)))
con = np.zeros((len(driverResults),len(cons)))

combo = np.zeros((len(driverResults),len(desVar)+len(objs)))


for i in range(len(driverResults)):

    tmp = cr.get_case(driverResults[i])

    for j in range(len(desVar)):

        tmp2 = tmp.get_design_vars()
        dVs[i,j] = tmp2[desVar[j]]
        combo[i,j+1] = tmp2[desVar[j]]

    for k in range(len(objs)):

        tmp3 = tmp.get_objectives()
        obj[i,k] = tmp3[objs[k]]
        combo[i,0] = tmp3[objs[k]]

    for z in range(len(cons)):

        tmp4 = tmp.get_constraints()
        con[i,z] = tmp4[cons[z]]

print('#-------------------------------# \n Design Variables:')
print(dVs)
print('#-------------------------------# \n Objective:')
print(obj)
print('#-------------------------------# \n Constraints:')
print(con)

# Sort by objective
combo.sort(axis=1)
sorted = combo[np.argsort(combo[:, 0])]

# Get unique designs
unique = np.unique(sorted, axis=0)

def plotting(x, y, label, xlabel, ylabel):

    fig = plt.figure(figsize = (12,8))
    ax = fig.add_subplot(111)

    plt.plot(x, y, linewidth = 2,
                   ls = '--',
                   marker = 'o')

    plt.grid(b=True, which='major')
    plt.grid(b=True, which='minor', alpha=0.2)
    plt.minorticks_on()
    plt.tick_params(axis='both', labelsize=16)

    plt.xlabel(xlabel, fontsize=20, fontweight='bold')
    plt.ylabel(ylabel, fontsize=20, fontweight='bold')
    plt.legend(label, loc = 'best', fontsize = 20)
    fig.tight_layout()

plotting(-unique[:20,0], unique[:20,1:], label=('stagger', 'stagger_row', 'gap', "af_col", "af_row", "aspect"),
                                         xlabel='Objective (L/D)',
                                         ylabel='Design Variable Magnitude')

plt.show()
