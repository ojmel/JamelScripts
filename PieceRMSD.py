import numpy as np

file = open("E:\PythonShit\ProteinList.tsv", "r")
List = file.readlines()
Listlength = len(List)
RMSDs = np.empty(((Listlength+1),5), dtype=object)
RMSDs[0,0]='Name'
RMSDs[0,1]='NTD'
RMSDs[0,2]='RBD'
RMSDs[0,3]='Stalk'
RMSDs[0,4]='Total'

i = 0
cmd.load("E:\Downloads\\7bbh.pdb")

cmd.remove('organic')
for line in List:
    x = line.split()
    protein = 'E:\Downloads\\' + x[0] + '.pdb'
    cmd.load(protein)
    i += 1

#You have to manually set the domains, every spike is slightly different
cmd.select('PANGNTD', selection='7bbh and resi 1-268')
cmd.select('PANGRBD', selection='7bbh and resi 269-535')
cmd.select('PANGStalk', selection='7bbh and resi 536-1063')
i=0
cmd.remove('chain A')
cmd.remove('chain C')
for line in List:
    x = line.split()
    RBD=NTD=Stalk =x[0]
    RMSDs[i+1,0]=x[0]
    NTD += ' and resi 1-268'
    RBD += ' and resi 269-535'
    Stalk += ' and resi 536-1063'
    NTDName = x[0] +'ntd'
    RBDName = x[0] +'rbd'
    StalkName = x[0] +'stalk'
    cmd.select(NTDName, selection=NTD)
    RMSD=cmd.align('PANGNTD', x[0])
    RMSDs[i+1, 1] = RMSD[0]
    cmd.select(RBDName, selection=RBD)
    RMSD = cmd.align('PANGRBD', x[0])
    RMSDs[i+1, 2] = RMSD[0]
    cmd.select(StalkName, selection=Stalk)
    RMSD = cmd.align('PANGStalk', x[0])
    RMSDs[i+1, 3] = RMSD[0]
    RMSD = cmd.align('7bbh', x[0])
    RMSDs[i+1, 4] = RMSD[0]
    i += 1

np.savetxt('E:\PythonShit\PANGPieceRMSD.tsv', RMSDs, fmt="%s", delimiter=" ")