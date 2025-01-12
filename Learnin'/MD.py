import subprocess
import pandas as pd
# Run the C program
# result = subprocess.run(["./example"], capture_output=True, text=True)
with open(r"C:\Research\3mer6vsbwBATHKU9S1.pdb",'r') as pdb:
    pdb=pd.DataFrame([x.split() for x in pdb.readlines()],columns=['Type','Atom#','ElementwPos','Acid','Chain','Res#','X','Y','Z','unk1','unk2','Element'])
