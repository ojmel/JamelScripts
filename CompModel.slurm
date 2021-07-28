#!/bin/bash


#SBATCH -A kas_dev
#SBATCH -p standard
#SBATCH -t 50:00:00
#SBATCH -o seqprof.out
#SBATCH -e seqprof.err
#Run program
/sfs/lustre/bahamut/scratch/jws6pq/ncbi-blast-2.11.0+/bin/psiblast -db /sfs/lustre/bahamut/scratch/jws6pq/ros/main/tools/fragment_tools/databases/nr -query MERS.fasta -save_pssm_after_last_round -out_pssm MERS.chk -out  MERS.asn1 -evalue 0.05 -gapopen 11 -gapextend 1 -matrix BLOSUM62 -comp_based_stats D -outfmt 9 
/sfs/lustre/bahamut/scratch/jws6pq/psipred/runpsipred_single MERS.fasta
/sfs/lustre/bahamut/scratch/jws6pq/ros/main/source/bin/fragment_picker.static.linuxgccrelease -in::file::vall /sfs/lustre/bahamut/scratch/jws6pq/ros/main/database/sampling/filtered.vall.dat.2006-05-05.gz -in::file::checkpoint MERS.chk -in::file::fasta MERS.fasta -in::file::s /sfs/lustre/bahamut/scratch/jws6pq/CMfiles/MERS_INPUT.pdb /sfs/lustre/bahamut/scratch/jws6pq/CMfiles/SARS2_INPUT.pdb /sfs/lustre/bahamut/scratch/jws6pq/CMfiles/SARS_INPUT.pdb -frags::ss_pred MERS.ss2 predA -frags::scoring::config /sfs/lustre/bahamut/scratch/jws6pq/ros/main/demos/public/fragment_picking/BestFragmentsProtocol/input_files/simple.wghts -frags::bounded_protocol -frags::frag_sizes 3,9 -frags::n_candidates 200 -frags::n_frags 200 -out::file::frag_prefix MERSfrags -frags::describe_fragments MERSfrags.fsc
cp  MERS.fasta  MERSonSARS2.fasta
cp  MERS.fasta  MERSonSARS.fasta
cp  MERS.fasta  MERSonMERS.fasta
cat /sfs/lustre/bahamut/scratch/jws6pq/CMfiles/SARS2.fasta >>  MERSonSARS2.fasta
cat /sfs/lustre/bahamut/scratch/jws6pq/CMfiles/SARS.fasta >>  MERSonSARS.fasta
cat /sfs/lustre/bahamut/scratch/jws6pq/CMfiles/MERS.fasta >>  MERSonMERS.fasta
/sfs/lustre/bahamut/scratch/jws6pq/clustalw-2.1/src/bin/clustalw2  MERSonSARS2.fasta
/sfs/lustre/bahamut/scratch/jws6pq/clustalw-2.1/src/bin/clustalw2  MERSonSARS.fasta
/sfs/lustre/bahamut/scratch/jws6pq/clustalw-2.1/src/bin/clustalw2  MERSonMERS.fasta
python3 /sfs/lustre/bahamut/scratch/jws6pq/CMfiles/3templateGrishinformatting.py
/sfs/lustre/bahamut/scratch/jws6pq/ros/main/source/bin/partial_thread.static.linuxgccrelease -in:file:fasta MERS.fasta -in:file:alignment MERSonSARS2_INPUT.grishin -in:file:template_pdb /sfs/lustre/bahamut/scratch/jws6pq/CMfiles/SARS2_INPUT.pdb 
/sfs/lustre/bahamut/scratch/jws6pq/ros/main/source/bin/partial_thread.static.linuxgccrelease -in:file:fasta MERS.fasta -in:file:alignment MERSonSARS_INPUT.grishin -in:file:template_pdb /sfs/lustre/bahamut/scratch/jws6pq/CMfiles/SARS_INPUT.pdb 
/sfs/lustre/bahamut/scratch/jws6pq/ros/main/source/bin/partial_thread.static.linuxgccrelease -in:file:fasta MERS.fasta -in:file:alignment MERSonMERS_INPUT.grishin -in:file:template_pdb /sfs/lustre/bahamut/scratch/jws6pq/CMfiles/MERS_INPUT.pdb 
mv SARS2_INPUT.pdb.pdb MERSonSARS2.pdb
mv SARS_INPUT.pdb.pdb MERSonSARS.pdb
mv MERS_INPUT.pdb.pdb MERSonMERS.pdb
/sfs/lustre/bahamut/scratch/jws6pq/ros/main/source/bin/rosetta_scripts.static.linuxgccrelease @rosetta_cm.options -nstruct 9
/sfs/lustre/bahamut/scratch/jws6pq/ros/main/source/bin/score.static.linuxgccrelease  -in:file:s S_000*