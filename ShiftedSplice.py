import numpy as np
file=open('SARS2.fasta',"r")
file2=open('MurineA59.fasta',"r")
Fasta1=file.readlines()
Fasta2=file2.readlines()
#Default is 319
FirstRBDBoundary=319
#Sefault is 541
SecondRBDBoundary=541
NumberofShifts=7
ShiftLength=10
CurrentShift=0
DirectionofShift='Right'
Protein1=file.name.replace('.fasta','')
Protein2=file2.name.replace('.fasta','')
ProteinList=np.empty((((NumberofShifts*4)+4),4), dtype=object)
l=0
m=4
AlphaFoldEntry=''
for l in range(NumberofShifts):
    CurrentShift+=ShiftLength
    Title= Protein1 +'w'+Protein2+'_'+ str(CurrentShift) + 'AA' + DirectionofShift + 'ShiftRBD.fasta'
    Path= 'E:\Fastas\\'  + Title
    Title2=Protein2+'w'+Protein1+'_'+ str(CurrentShift) + 'AA' + DirectionofShift + 'ShiftRBD.fasta'
    Path2='E:\Fastas\\' + Title2
    Sequence1=''
    Sequence2=''
    ProteinList[0,0] =Protein1 + '.plddt'
    ProteinList[1,0] =Protein2 + '.plddt'
    ProteinList[2,0] =Protein1 +'w'+Protein2+ "RBD" + '.plddt'
    ProteinList[3,0] =Protein2 +'w'+Protein1+ "RBD" + '.plddt'
    ProteinList[m,0]=Protein1 + '.plddt'
    ProteinList[m+1,0] =Protein2 + '.plddt'
    ProteinList[m+2,0] = 'E:\Plddt\\' +Protein1 +'w'+Protein2+ '_'+str(CurrentShift) + 'AA' + DirectionofShift + 'ShiftRBD.plddt'
    ProteinList[m+3,0] = 'E:\Plddt\\' +Protein2+'w'+Protein1+ '_'+str(CurrentShift) + 'AA' + DirectionofShift + 'ShiftRBD.plddt'
    for i in range(len(Fasta1)-1):
        Sequence1+=Fasta1[i+1].rstrip()
    for i in range(len(Fasta2)-1):
        Sequence2+=Fasta2[i+1].rstrip()
    Seqlength=len(Sequence1)
    Seqlength2=len(Sequence2)
    Sections=np.empty((3,2), dtype=object)
    Sections[0,0]=''
    Sections[1,0]=''
    Sections[2,0]=''
    i=0
    j=0
    Chimera1SpliceStart=int((FirstRBDBoundary/1273)*Seqlength)
    Chimera1SpliceEnd=int((SecondRBDBoundary/1273)*Seqlength)
    Chimera2SpliceStart=int((FirstRBDBoundary/1273)*Seqlength2)
    Chimera2SpliceEnd=int((SecondRBDBoundary/1273)*Seqlength2)
    ProteinList[0,1]=ProteinList[2,1]=Chimera1SpliceStart-1
    ProteinList[1, 1] = ProteinList[3, 1] =Chimera2SpliceStart-1
    ProteinList[1, 2] = ProteinList[2, 2] =Chimera2SpliceEnd-Chimera2SpliceStart
    ProteinList[0, 2] = ProteinList[3, 2] = Chimera1SpliceEnd - Chimera1SpliceStart
    ProteinList[1, 3] = ProteinList[3, 3] = Seqlength2- Chimera2SpliceEnd
    ProteinList[0, 3] = ProteinList[2, 3] = Seqlength - Chimera1SpliceEnd

    for letter in Sequence1:
        i+=1
        if i<(Chimera1SpliceStart-CurrentShift) and DirectionofShift=='Left':
            Sections[0,0]+=str(letter)
        elif (Chimera1SpliceStart-CurrentShift)<i<=Chimera1SpliceEnd and DirectionofShift=='Left':
            Sections[1,0] += str(letter)
        elif Chimera1SpliceEnd<i and DirectionofShift=='Left':
            Sections[2,0] += str(letter)
        if i<(Chimera1SpliceStart) and DirectionofShift=='Right':
            Sections[0,0]+=str(letter)
        elif (Chimera1SpliceStart)<i<=(Chimera1SpliceEnd+CurrentShift) and DirectionofShift=='Right':
            Sections[1,0] += str(letter)
        elif (Chimera1SpliceEnd+CurrentShift)<i and DirectionofShift=='Right':
            Sections[2,0] += str(letter)
    i=0
    for i in range(3):
        Sections[i,1]=''
    i=0
    j=1
    for letter in Sequence2:
        i+=1
        if i < (Chimera2SpliceStart - CurrentShift) and DirectionofShift == 'Left':
            Sections[0, 1] += str(letter)
        elif (Chimera2SpliceStart - CurrentShift) < i <= Chimera2SpliceEnd and DirectionofShift == 'Left':
            Sections[1, 1] += str(letter)
        elif Chimera2SpliceEnd < i and DirectionofShift == 'Left':
            Sections[2, 1] += str(letter)
        if i <(Chimera2SpliceStart - CurrentShift) and DirectionofShift == 'Right':
            Sections[0, 1] += str(letter)
        elif Chimera2SpliceStart < i <= (Chimera2SpliceEnd+CurrentShift) and DirectionofShift == 'Right':
            Sections[1, 1] += str(letter)
        elif (Chimera2SpliceEnd+CurrentShift) < i and DirectionofShift == 'Right':
            Sections[2, 1] += str(letter)
    NewSequence=np.empty((2,1), dtype=object)
    NewSequence[0,0]='>Chimera'
    NewSequence[1,0]=Sections[0,0]+Sections[1,1]+Sections[2,0]
    np.savetxt(Path,NewSequence,fmt="%s",delimiter=" ")
    NewSequence2=np.empty((2,1), dtype=object)
    NewSequence2[0,0]='>Chimera'
    NewSequence2[1,0]=Sections[0,1]+Sections[1,0]+Sections[2,1]
    np.savetxt(Path2,NewSequence2,fmt="%s",delimiter=" ")
    #print(CurrentShift)
    ProteinList[m, 1]  = ProteinList[m+2,1]=len(Sections[0,0])
    ProteinList[m+1, 1] = ProteinList[m + 3, 1] =len(Sections[0, 1])
    ProteinList[m, 2] =ProteinList[m+3,2]=len(Sections[1, 0])
    ProteinList[m + 2, 2] =ProteinList[m+1,2]=len(Sections[1, 1])
    ProteinList[m,3]=ProteinList[m+2,3]=len(Sections[2, 0])
    ProteinList[m+3, 3]  = ProteinList[m+1,3]=len(Sections[2, 1])
    AlphaFoldEntry+= "/scratch/jws6pq/Notebook/Finished/" + Title +',' +"/scratch/jws6pq/Notebook/Finished/" + Title2 + ','
    m+=4
print(Sections)
print(NewSequence)

Title3=Protein1 + '-' +Protein2 + DirectionofShift +'ProteinList.tsv'
#print(ProteinList)
np.savetxt(Title3, ProteinList, fmt="%s", delimiter=" ")
#print(AlphaFoldEntry)
