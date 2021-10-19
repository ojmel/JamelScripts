
FastaExchangeInputs={"Fastafile1":'FullSARS2.fasta','Fastafile2':'AvianD274.fasta','Boundary1':630,'Boundary2':635,"Fastalist":'list'}
file3 = open(FastaExchangeInputs['Fastalist'], "r")
list=file3.readlines()
import RBDExchanger
for line in list:
   FastaExchangeInputs['Fastafile2']=line.rstrip()+'.fasta'
   RBDExchanger.RBDExchange(**FastaExchangeInputs)