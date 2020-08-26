import os
import matplotlib.pyplot as plt
import numpy as np
import openmdao.api as om

fid = os.path.join('../', 'pyCAPS', 'GA', 'driverRecorder.sql')

desVar = ['dvAlpha.Alpha', 'dvStagger.stagger', 'dvStaggerRow.stagger_row']
cons = []
objs = ['L2D.L2D']

cr = om.CaseReader(fid)
driverResults = cr.list_cases('driver')

# cases =  cr.get_cases()
#
# for case in cases:
#     print(case)
#
# exit()

dVs = np.zeros((len(driverResults),len(desVar)))
obj = np.zeros((len(driverResults),len(objs)))
con = np.zeros((len(driverResults),len(cons)))


for i in range(len(driverResults)):

    tmp = cr.get_case(driverResults[i])

    for j in range(len(desVar)):

        tmp2 = tmp.get_design_vars()
        dVs[i,j] = tmp2[desVar[j]]

    for k in range(len(objs)):

        tmp3 = tmp.get_objectives()
        obj[i,k] = tmp3[objs[k]]

    for z in range(len(cons)):

        tmp4 = tmp.get_constraints()
        con[i,z] = tmp4[cons[z]]

print('#-------------------------------# \n Design Variables:')
print(dVs)
print('#-------------------------------# \n Objective:')
print(obj)
print('#-------------------------------# \n Constraints:')
print(con)

iterations = np.arange(0,len(driverResults))

################################################################################
fig = plt.figure(figsize = (12,8))
ax = fig.add_subplot(111)

plt.plot(iterations, obj, linewidth = 2, label = objs[0])

# xlimL1, xlimH1 = [0, len(driverResults)]
# ylimL1, ylimH1 = [0, np.max(obj)*2]
#
# plt.xlim([xlimL1, xlimH1])
# plt.ylim([ylimL1, ylimH1])

plt.grid(b=True, which='major')
plt.grid(b=True, which='minor', alpha=0.2)
plt.minorticks_on()
plt.tick_params(axis='both', labelsize=16)

plt.xlabel('Iteration Number', fontsize=20, fontweight='bold')
plt.ylabel('Objective Function Value', fontsize=20, fontweight='bold')
plt.title('Objective Function', fontsize=20, fontweight='bold')
plt.legend(loc = 'best', fontsize = 20)

# plt.savefig(self.resultsDir + 'Run' + str(j+1) + '/fftPoint' + str(i+1) + '.png')

################################################################################
fig = plt.figure(figsize = (12,8))
ax = fig.add_subplot(111)

for i in range(len(con[0])):
    plt.plot(iterations, con[:,i], linewidth = 2, label = cons[i])

# yRange =  np.around(np.max(np.abs(con)), decimals = 1)
#
# xlimL1, xlimH1 = [0, len(driverResults)]
# ylimL1, ylimH1 = [-yRange, yRange]
#
# plt.xlim([xlimL1, xlimH1])
# plt.ylim([ylimL1, ylimH1])

plt.grid(b=True, which='major')
plt.grid(b=True, which='minor', alpha=0.2)
plt.minorticks_on()
plt.tick_params(axis='both', labelsize=16)
plt.legend(loc = 'best', fontsize = 20)

plt.xlabel('Iteration Number', fontsize=20, fontweight='bold')
plt.ylabel('Constraint Value', fontsize=20, fontweight='bold')
plt.title('Constraints', fontsize=20, fontweight='bold')

# plt.savefig(self.resultsDir + 'Run' + str(j+1) + '/fftPoint' + str(i+1) + '.png')

################################################################################
fig = plt.figure(figsize = (12,8))
ax = fig.add_subplot(111)

for i in range(len(dVs[0])):
    plt.plot(iterations, dVs[:,i], linewidth = 2, label = desVar[i])

# yRange = np.max(np.ceil(np.abs(dVs)))
#
# xlimL1, xlimH1 = [0, len(driverResults)]
# ylimL1, ylimH1 = [-yRange, yRange]
#
# plt.xlim([xlimL1, xlimH1])
# plt.ylim([ylimL1, ylimH1])

plt.grid(b=True, which='major')
plt.grid(b=True, which='minor', alpha=0.2)
plt.minorticks_on()
plt.tick_params(axis='both', labelsize=16)
plt.legend(loc = 'best', fontsize = 20)

plt.xlabel('Iteration Number', fontsize=20, fontweight='bold')
plt.ylabel('DesVar Value', fontsize=20, fontweight='bold')
plt.title('Design Variables', fontsize=20, fontweight='bold')

# plt.savefig(self.resultsDir + 'Run' + str(j+1) + '/fftPoint' + str(i+1) + '.png')

plt.show()
