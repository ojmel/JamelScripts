import numpy as np
file=open('Caninef15.fasta',"r")
file2=open('Feline79.fasta',"r")
Fasta1=file.readlines()
Fasta2=file2.readlines()
#Default is 331
FirstSplice=270
#Sefault is 524
SecondSplice=470
Sequence1=''
Sequence2=''
for i in range(len(Fasta1)-1):
    Sequence1+=Fasta1[i+1]
for i in range(len(Fasta2)-1):
    Sequence2+=Fasta2[i+1]
Seqlength=len(Sequence1)
Seqlength2=len(Sequence2)
Sections=np.empty((3,2), dtype=object)
print(Sequence1)
print(Sequence2)
Sections[0,0]=''
Sections[1,0]=''
Sections[2,0]=''
i=0
j=0
for letter in Sequence1:
    i+=1
    if i<=Seqlength*(FirstSplice/1141):
        Sections[0,0]+=str(letter)
    elif Seqlength*(FirstSplice/1141)<i<=Seqlength*(SecondSplice/1141):
        Sections[1,0] += str(letter)
    elif Seqlength*(SecondSplice/1141)<i:
        Sections[2,0] += str(letter)
i=0
for i in range(3):
    Sections[i,1]=''
i=0
j=1
for letter in Sequence2:
    i+=1
    if i<=Seqlength2*(FirstSplice/1141):
        Sections[0,1]+=str(letter)
    elif Seqlength2*(FirstSplice/1141)<i<=Seqlength2*(SecondSplice/1141):
        Sections[1,1] += str(letter)
    elif Seqlength2*(SecondSplice/1141)<i:
        Sections[2,1] += str(letter)
NewSequence=np.empty((2,1), dtype=object)
NewSequence[0,0]='>Chimera'
NewSequence[1,0]=Sections[0,0]+Sections[1,1]+Sections[2,0]
print(Sections)
np.savetxt('Caninef15wFeline79RBD60AALeftShift.fasta',NewSequence,fmt="%s",delimiter=" ")
NewSequence2=np.empty((2,1), dtype=object)
NewSequence2[0,0]='>Chimera'
NewSequence2[1,0]=Sections[0,1]+Sections[1,0]+Sections[2,1]
#print(NewSequence2)
np.savetxt('Feline79wCaninef15RBD60AALeftShift.fasta',NewSequence2,fmt="%s",delimiter=" ")

exit()