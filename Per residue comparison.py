import math
import numpy as np
k=1
file5=open('ProteinList.tsv','r')
ProteinList=file5.readlines()
l=0
j=0
h=0
p=0
Quadrupletsperlist=int(len(ProteinList)/4)
PercentDifference=np.empty((len(ProteinList),2), dtype=object)
Plddtfiles=np.empty((len(ProteinList)), dtype=object)
for line in ProteinList:
    x=line.split()
    Plddtfiles[l]=''
    Plddtfiles[l]=x[0]
    l+=1
for h in range(len(ProteinList)):
    PercentDifference[h]=''
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
    FirstSplice=319/1273
    SecondSplice=541/1273
    LengthofProtein1=len(Score1)
    LengthofProtein2=len(Score2)
    LengthofChimera1=len(Score3)
    BeforeSpliceLengthforChimera1=int(FirstSplice*LengthofProtein1)
    SpliceLengthofChimera1=int(SecondSplice*LengthofProtein2-FirstSplice*LengthofProtein2)
    AfterSpliceLengthofChimera1=LengthofChimera1-BeforeSpliceLengthforChimera1-SpliceLengthofChimera1

    i=0
    Sumofnonsplice1=0
    Sumofsplice1=0
    for i in range(LengthofChimera1):
        if i<BeforeSpliceLengthforChimera1:
            Sumofnonsplice1+=float(Score3[i])
            i+=1
        elif (SpliceLengthofChimera1+BeforeSpliceLengthforChimera1)>i>=BeforeSpliceLengthforChimera1:
            Sumofsplice1+=float(Score3[i])
            i+=1
        elif i>= (SpliceLengthofChimera1+BeforeSpliceLengthforChimera1):
            Sumofnonsplice1+=float(Score3[i])
            i+=1
    Averageofsplice1=(Sumofsplice1/SpliceLengthofChimera1)
    Averageofnonsplice1=(Sumofnonsplice1/(LengthofChimera1-SpliceLengthofChimera1))

    LengthofChimera2=len(Score4)
    BeforeSpliceLengthforChimera2=int(FirstSplice*LengthofProtein2)
    SpliceLengthofChimera2=int(SecondSplice*LengthofProtein1-FirstSplice*LengthofProtein1)
    AfterSpliceLengthofChimera2=LengthofChimera2-BeforeSpliceLengthforChimera2-SpliceLengthofChimera2
    i=0
    Sumofnonsplice2=0
    Sumofsplice2=0
    for i in range(LengthofChimera2):
        if i<BeforeSpliceLengthforChimera2:
            Sumofnonsplice2+=float(Score4[i])
            i+=1
        elif (SpliceLengthofChimera2+BeforeSpliceLengthforChimera2)>i>=BeforeSpliceLengthforChimera2:
            Sumofsplice2+=float(Score4[i])
            i+=1
        elif i>= (SpliceLengthofChimera2+BeforeSpliceLengthforChimera2):
            Sumofnonsplice2+=float(Score4[i])
            i+=1
    Averageofsplice2=(Sumofsplice2/SpliceLengthofChimera2)
    Averageofnonsplice2=(Sumofnonsplice2/(LengthofChimera2-SpliceLengthofChimera2))


    i=0
    Sumofnonrbd2=0
    Sumofrbd2=0
    for i in range(LengthofProtein2):
        if i<BeforeSpliceLengthforChimera2:
            Sumofnonrbd2+=float(Score2[i])
            i+=1
        elif (SpliceLengthofChimera1+BeforeSpliceLengthforChimera2)>i>=BeforeSpliceLengthforChimera2:
            Sumofrbd2+=float(Score2[i])
            i+=1
        elif i>= (SpliceLengthofChimera1+BeforeSpliceLengthforChimera2):
            Sumofnonrbd2+=float(Score2[i])
            i+=1
    Averageofrbd2=(Sumofrbd2/SpliceLengthofChimera1)
    Averageofnonrbd2=(Sumofnonrbd2/(LengthofProtein2-SpliceLengthofChimera1))


    i=0
    Sumofnonrbd1=0
    Sumofrbd1=0
    for i in range(LengthofProtein1):
        if i<BeforeSpliceLengthforChimera1:
            Sumofnonrbd1+=float(Score1[i])
            i+=1
        elif (SpliceLengthofChimera2+BeforeSpliceLengthforChimera1)>i>=BeforeSpliceLengthforChimera1:
            Sumofrbd1+=float(Score1[i])
            i+=1
        elif i>= (SpliceLengthofChimera1+BeforeSpliceLengthforChimera1):
            Sumofnonrbd1+=float(Score1[i])
            i+=1
    Averageofrbd1=(Sumofrbd1/SpliceLengthofChimera2)
    Averageofnonrbd1=(Sumofnonrbd1/(LengthofProtein1-SpliceLengthofChimera1))

    #PercentError=np.zeros((len(Score1),2))

    #print(Score1[1])
    #Lengthofover10=0
    #for i in range(len(Score1)):
        #PercentError[i,0]=((math.fabs(float(Score1[i])-float(Score3[i])))/float(Score1[i]))*100
        #PercentError[i,1]=int(i+1)
        #if PercentError[i,0]>10:
            #Lengthofover10+=1
    #print(Lengthofover10)
    #PercentErrorover10=np.zeros((Lengthofover10,2))
    #i=0
    #j=0
    #for j in range(len(Score1)):
        #if PercentError[j,0]>10:
            #PercentErrorover10[i,0]=PercentError[j,0]
            #PercentErrorover10[i, 1] = PercentError[j, 1]
            #i+=1
    Chimera1 = file3.name.replace('RBD.plddt', 'NonRBD')
    Chimera1RBD = file3.name.replace('RBD.plddt', 'RBD')
    Chimera2 = file4.name.replace('RBD.plddt', 'NonRBD')
    Chimera2RBD = file4.name.replace('RBD.plddt', 'RBD')
    DifferenceofNonRBD1Averages=((Averageofnonrbd1-Averageofnonsplice1)/Averageofnonrbd1)*100
    DifferenceofRBD1Averages=((Averageofrbd1-Averageofsplice2)/Averageofrbd1)*100
    DifferenceofNonRBD2Averages=((Averageofnonrbd2-Averageofnonsplice2)/Averageofnonrbd2)*100
    DifferenceofRBD2Averages=((Averageofrbd2-Averageofsplice1)/Averageofrbd2)*100
    PercentDifference[p,0]=Chimera1
    PercentDifference[p,1]=DifferenceofNonRBD1Averages
    PercentDifference[p+1, 0] = Chimera1RBD
    PercentDifference[p+1, 1] = DifferenceofRBD1Averages
    PercentDifference[p + 2, 0] = Chimera2
    PercentDifference[p + 2, 1] = DifferenceofNonRBD2Averages
    PercentDifference[p + 3, 0] = Chimera2RBD
    PercentDifference[p + 3, 1] = DifferenceofRBD2Averages
    j += 4
    p+=4
print(PercentDifference)
np.savetxt('AveragePerResiduePercentDifferencesRightShift.tsv',PercentDifference,fmt="%s,%s",delimiter=" ")
