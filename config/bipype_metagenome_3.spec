[CONFIG]
name bipype_metagenome_3
input FASTQ
scaffoldOutput [RUNDIR]/Scaffolds.fasta
location python/bipype
output megan.lite.rma
threads --threads
unpaired [FIRST]
paired_interleaved [FIRST] [SECOND]
paired [FIRST] [SECOND]
commands mkdir [RUNDIR] && \
         bipype -t 16 --out_dir [RUNDIR] -MEGAN -rapsearch rap_prot -assembler MH --mode run --input [INPUT] && \
         bipype_cheat [RUNDIR]
