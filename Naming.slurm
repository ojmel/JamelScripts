#!/bin/bash


#SBATCH -A kas_dev
#SBATCH -p standard
#SBATCH -t 50:00:00
#SBATCH -o seqprof.out
#SBATCH -e seqprof.err
#Run program
mv S_0001.pdb /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERS_1.pdb
mv S_0002.pdb /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERS_2.pdb
mv S_0003.pdb /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERS_3.pdb
mv S_0004.pdb /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERS_4.pdb
mv S_0005.pdb /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERS_5.pdb
mv S_0006.pdb /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERS_6.pdb
mv S_0007.pdb /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERS_7.pdb
mv S_0008.pdb /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERS_8.pdb
mv S_0009.pdb /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERS_9.pdb
mv MERSonMERS.pdb /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERSonMERS.pdb
mv MERSonSARS.pdb /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERSonSARS.pdb
mv MERSonSARS2.pdb /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERSonSARS2.pdb
mv MERSfrags.fsc.200.9mers /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERSfrags.fsc.200.9mers
mv MERSfrags.200.9mers /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERSfrags.200.9mers
mv MERSfrags.200.3mers /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERSfrags.200.3mers
mv MERSfrags.fsc.200.3mers /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERSfrags.fsc.200.3mers
cp CompModel.slurm /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERSCompModel.slurm
cp fixed.xml /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERS.xml
cp rostta_cm.options /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERS.options
mv MERS.fasta /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERS.fasta
mv default.sc /sfs/lustre/bahamut/scratch/jws6pq/Notebook/Finished/MERS.sc
rm MERS*
rm seqprof*
rm score.sc
 