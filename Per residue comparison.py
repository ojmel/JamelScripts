import math
import numpy as np
k=1
file5=open('SARS2-MurineA59RightProteinList.tsv','r')
Title='E:\Research\\' + file5.name.replace('ProteinList.tsv', 'PercentDifference.tsv')
Title2='E:\Research\\' + file5.name.replace('ProteinList.tsv', 'RBDPercentDifference.tsv')
ProteinList=file5.readlines()
l=0
j=0
h=0
p=0
z=0
Quadrupletsperlist=int(len(ProteinList)/4)
PercentDifference=np.empty(((int(len(ProteinList)/4)),4), dtype=object)
PercentDifferenceRBD=np.empty(((int(len(ProteinList)/4)),4), dtype=object)
Plddtfiles=np.empty((len(ProteinList)), dtype=object)
for line in ProteinList:
    x=line.split()
    Plddtfiles[l]=''
    Plddtfiles[l]=x[0]
    l+=1
for h in range(int(len(ProteinList)/4)):
    PercentDifference[h]=''
    PercentDifferenceRBD[h]=''
    h+=1
for k in range(Quadrupletsperlist):
    file=open(Plddtfiles[0+j],"r")
    file2=open(Plddtfiles[1+j],"r")
    file3=open(Plddtfiles[2+j],"r")
    file4=open(Plddtfiles[3+j],"r")
    Score1=file.readlines()
    Score2=file2.readlines()
    Score3=file3.readlines()
    Score4=file4.readlines()
    LengthofProtein1=len(Score1)
    LengthofProtein2=len(Score2)
    LengthofChimera1=len(Score3)
    i=0
    Sumofnonsplice1=0
    Sumofsplice1=0
    for i in range(LengthofChimera1):

        if i<(int(ProteinList[z+2].split()[1])):
            Sumofnonsplice1+=float(Score3[i])
            i+=1
        elif (int(ProteinList[z+2].split()[2])+int(ProteinList[z+2].split()[1]))>i>=int(ProteinList[z+2].split()[1]):
            Sumofsplice1+=float(Score3[i])
            i+=1
        elif i>= (int(ProteinList[z+2].split()[1])+int(ProteinList[z+2].split()[2])):
            Sumofnonsplice1+=float(Score3[i])
            i+=1
    Averageofsplice1=(Sumofsplice1/int(ProteinList[z+2].split()[2]))
    Averageofnonsplice1=(Sumofnonsplice1/(LengthofChimera1-int(ProteinList[z+2].split()[2])))

    LengthofChimera2=len(Score4)
    i=0
    Sumofnonsplice2=0
    Sumofsplice2=0
    for i in range(LengthofChimera2):
        if i<int(ProteinList[z+3].split()[1]):
            Sumofnonsplice2+=float(Score4[i])
            i+=1
        elif (int(ProteinList[z+3].split()[2])+int(ProteinList[z+3].split()[1]))>i>=int(ProteinList[z+3].split()[1]):
            Sumofsplice2+=float(Score4[i])
            i+=1
            print(i)
        elif i>= (int(ProteinList[z+3].split()[2])+int(ProteinList[z+3].split()[1])):
            Sumofnonsplice2+=float(Score4[i])
            i+=1
    Averageofsplice2=(Sumofsplice2/int(ProteinList[z+3].split()[2]))
    Averageofnonsplice2=(Sumofnonsplice2/(LengthofChimera2-int(ProteinList[z+3].split()[2])))



    i=0
    Sumofnonrbd2=0
    Sumofrbd2=0
    for i in range(LengthofProtein2):
        if i<int(ProteinList[z+1].split()[1]):
            Sumofnonrbd2+=float(Score2[i])
            i+=1
        elif (int(ProteinList[z+1].split()[1])+int(ProteinList[z+1].split()[2]))>i>=int(ProteinList[z+1].split()[1]):
            Sumofrbd2+=float(Score2[i])

            i+=1
        elif i>= (int(ProteinList[z+1].split()[2])+int(ProteinList[z+1].split()[1])):
            Sumofnonrbd2+=float(Score2[i])
            i+=1
    Averageofrbd2=(Sumofrbd2/int(ProteinList[z+1].split()[2]))
    Averageofnonrbd2=(Sumofnonrbd2/(LengthofProtein2-int(ProteinList[z+2].split()[2])))


    i=0
    Sumofnonrbd1=0
    Sumofrbd1=0
    for i in range(LengthofProtein1):
        if i<int(ProteinList[z].split()[1]):
            Sumofnonrbd1+=float(Score1[i])
            i+=1
        elif (int(ProteinList[z].split()[2])+int(ProteinList[z].split()[1]))>i>=int(ProteinList[z].split()[1]):
            Sumofrbd1+=float(Score1[i])


            i+=1
        elif i>= (int(ProteinList[z].split()[2])+int(ProteinList[z].split()[1])):
            Sumofnonrbd1+=float(Score1[i])
            i+=1
    #how can i name this better with different situations?
    Averageofrbd1=(Sumofrbd1/int(ProteinList[z].split()[2]))
    Averageofnonrbd1=(Sumofnonrbd1/(LengthofProtein1-int(ProteinList[z].split()[2])))
    Chimera1 = file3.name.replace('RBD.plddt', 'NonRBD')
    Chimera1RBD = file3.name.replace('RBD.plddt', 'RBD')
    Chimera2 = file4.name.replace('RBD.plddt', 'NonRBD')
    Chimera2RBD = file4.name.replace('RBD.plddt', 'RBD')
    Chimera1 = Chimera1.replace('E:\\Plddt\\', '')
    Chimera1RBD = Chimera1RBD.replace('E:\\Plddt\\', '')
    Chimera2 = Chimera2.replace('E:\\Plddt\\', '')
    Chimera2RBD = Chimera2RBD.replace('E:\\Plddt\\', '')
    print(Averageofsplice2)
    print(Averageofrbd1)
    DifferenceofNonRBD1Averages=((Averageofnonrbd1-Averageofnonsplice1)/Averageofnonrbd1)*100
    DifferenceofRBD1Averages=((Averageofrbd2-Averageofsplice1)/Averageofrbd2)*100
    DifferenceofNonRBD2Averages=((Averageofnonrbd2-Averageofnonsplice2)/Averageofnonrbd2)*100
    DifferenceofRBD2Averages=((Averageofrbd1-Averageofsplice2)/Averageofrbd1)*100
    PercentDifference[p,0]=Chimera1
    PercentDifference[p,1]=DifferenceofNonRBD1Averages
    PercentDifferenceRBD[p, 0] = Chimera1RBD
    PercentDifferenceRBD[p, 1] = DifferenceofRBD1Averages
    PercentDifference[p, 2] = Chimera2
    PercentDifference[p, 3] = DifferenceofNonRBD2Averages
    PercentDifferenceRBD[p, 2] = Chimera2RBD
    PercentDifferenceRBD[p, 3] = DifferenceofRBD2Averages
    j += 4
    p+=1
    z+=4
print(PercentDifferenceRBD)

np.savetxt(Title,PercentDifference,fmt="%s,%s,%s,%s",delimiter=" ")
np.savetxt(Title2,PercentDifferenceRBD,fmt="%s,%s,%s,%s",delimiter=" ")
