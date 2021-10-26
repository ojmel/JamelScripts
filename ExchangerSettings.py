import numpy as np

FastaExchangeInputs={"Fastafile1":'FullSARS2.fasta','Fastafile2':'SARS2.fasta','Boundary1':319,'Boundary2':541,"Fastalist":'poop'}
file3 = open(FastaExchangeInputs['Fastalist'], "r")
list=file3.readlines()
import RBDExchanger
AlphaFoldEntry=''
ProteinList = (RBDExchanger.RBDExchange(FastaExchangeInputs['Fastafile1'], FastaExchangeInputs['Fastafile2'],FastaExchangeInputs['Boundary1'], FastaExchangeInputs['Boundary2']))

for line in list:
   FastaExchangeInputs['Fastafile2']=line.rstrip()+'.fasta'
   ProteinList2=(RBDExchanger.RBDExchange(FastaExchangeInputs['Fastafile1'],FastaExchangeInputs['Fastafile2'],FastaExchangeInputs['Boundary1'],FastaExchangeInputs['Boundary2']))
   ProteinList=np.vstack((ProteinList,ProteinList2))
print(ProteinList)
np.savetxt('RandomProteinList.tsv', ProteinList, fmt="%s", delimiter=" ")

