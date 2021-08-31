#!/usr/bin/python3
#SBATCH -A kas_dev
#SBATCH -p standard
#SBATCH -t 50:00:00
#SBATCH -o seqprof.out
#SBATCH -e seqprof.err
import pickle
import numpy as np
infile=open('result_model_1.pkl','rb')
dat=pickle.load(infile)
np.savetxt('plddt.txt',dat['plddt'],fmt="%s",delimiter=" ")
import json
jfile=open('ranking_debug.json','r')
data=json.load(jfile)
data=str(data['plddts']['model_1'])
ft = open('overall.txt', 'w')
ft.write(data)

