#!/bin/bash
#SBATCH -p gpu          # partition
#SBATCH --gres=gpu:v100:1    # number of GPUs
#SBATCH -N 1            # number of nodes
#SBATCH -c 8            # number of cores
#SBATCH -t 72:00:00     # time
#SBATCH -o /sfs/lustre/bahamut/scratch/jws6pq/CMfiles/slurm.out
#SBATCH -e /sfs/lustre/bahamut/scratch/jws6pq/CMfiles/slurm.err
#SBATCH -A kas_dev
#Run program
python alpha_list.py -s=/scratch/jws6pq/Notebook/Finished/SARS2wAvianD27470AALeftShiftRBD.fasta,/scratch/jws6pq/Notebook/Finished/AvianD274wSARS270AALeftShiftRBD.fasta,/scratch/jws6pq/Notebook/Finished/SARS2wAvianD27460AALeftShiftRBD.fasta,/scratch/jws6pq/Notebook/Finished/AvianD274wSARS260AALeftShiftRBD.fasta,/scratch/jws6pq/Notebook/Finished/AvianD274wSARS250AALeftShiftRBD.fasta,/scratch/jws6pq/Notebook/Finished/SARS2wAvianD27450AALeftShiftRBD.fasta,/scratch/jws6pq/Notebook/Finished/SARS2wAvianD27440AALeftShiftRBD.fasta,/scratch/jws6pq/Notebook/Finished/AvianD274wSARS240AALeftShiftRBD.fasta,/scratch/jws6pq/Notebook/Finished/SARS2wAvianD27430AALeftShiftRBD.fasta -o=/scratch/jws6pq/Notebook/Finished
cd /scratch/jws6pq/Notebook/Finished
for d in ./*/ ; do (cd "$d" && python /sfs/lustre/bahamut/scratch/jws6pq/CMfiles/pickleopener.py && mydir="$(basename $PWD)" && mv overall.txt $mydir.overall && mv plddt.txt $mydir.plddt && mv relaxed_model_1.pdb $mydir.pdb); done