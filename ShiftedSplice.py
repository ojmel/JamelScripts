import numpy as np
import sys
import argparse
def SplicingFastas(Fasta1,Fasta2,Boundary1,Boundary2,NumofShifts,ShiftLength,MobileBoundary):
    file=open(Fasta1,"r")
    file2=open(Fasta2,"r")
    Fasta1=file.readlines()
    Fasta2=file2.readlines()
    #Default is 319
    FirstRBDBoundary=int(Boundary1)
    #Sefault is 541
    SecondRBDBoundary=int(Boundary2)
    NumberofShifts=int(NumofShifts)
    ShiftLength=int(ShiftLength)
    CurrentShift=0
    DirectionofShift=MobileBoundary
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

        i=0
        for i in range(3):
            Sections[i,1]=''
        i=0
        j=1
        if DirectionofShift == 'Left':
            Sections[0,0]=Sequence1[0:Chimera1SpliceStart-CurrentShift-1]
            Sections[1, 0] = Sequence1[(Chimera1SpliceStart-CurrentShift):Chimera1SpliceEnd]
            Sections[2, 0] = Sequence1[Chimera1SpliceEnd:]
            Sections[0, 1] = Sequence2[0:Chimera2SpliceStart - CurrentShift - 1]
            Sections[1, 1] = Sequence2[(Chimera2SpliceStart - CurrentShift):Chimera2SpliceEnd]
            Sections[2, 1] = Sequence2[Chimera2SpliceEnd:]
        if DirectionofShift == 'Right':
            Sections[0,0]=Sequence1[0:Chimera1SpliceStart-1]
            Sections[1, 0] = Sequence1[Chimera1SpliceStart:Chimera1SpliceEnd+CurrentShift]
            Sections[2, 0] = Sequence1[Chimera1SpliceEnd+CurrentShift:]
            Sections[0, 1] = Sequence2[0:Chimera2SpliceStart - 1]
            Sections[1, 1] = Sequence2[Chimera2SpliceStart:Chimera2SpliceEnd+CurrentShift]
            Sections[2, 1] = Sequence2[Chimera2SpliceEnd+CurrentShift:]
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
        print(len(Sections[0,0]))
    Title3=Protein1 + '-' +Protein2 + DirectionofShift +'ProteinList.tsv'
    #print(ProteinList)
    np.savetxt(Title3, ProteinList, fmt="%s", delimiter=" ")
    print(AlphaFoldEntry)
