import numpy as np
import numpy.random.mtrand

file=open('PANG.fasta',"r")
Fasta1=file.readlines()
for line in Fasta1:
    Sequence=line
Seqlength=len(Sequence)
print(Seqlength)


NumberofSections=100
Sections=np.empty(NumberofSections, dtype=object)
SectionLength=round(Seqlength/NumberofSections)
#print(SectionLength)
i=0
for i in range(NumberofSections):
    Sections[i]=''
i=0
j=1
for letter in Sequence:
    i+=1
    if (SectionLength*(j-1))<i<=((SectionLength)*j) and j<=NumberofSections:
        Sections[(j-1)]+=str(letter)

    else:
        j+=1

#print(Sections)
Randomized=numpy.random.mtrand.permutation(Sections)
NewSequence=np.empty((2), dtype=object)
NewSequence[0]='>Chimera'
i=0
NewSequence[1]=""
print(len(Randomized))
for i in range(NumberofSections):
    NewSequence[1]+=Randomized[i]
    print(i)
    i+=1

print(len(NewSequence[1]))
#np.savetxt('PANG100sectionPermute.fasta',NewSequence,fmt="%s",delimiter=" ")
exit()