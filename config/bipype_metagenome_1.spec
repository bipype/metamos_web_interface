[CONFIG]
name bipype_metagenome_1
input FASTQ
scaffoldOutput [RUNDIR]/Scaffolds.fasta
location python/bipype
output humann-graphlan.krona
threads --threads
unpaired [FIRST]
paired_interleaved [FIRST] [SECOND]
paired [FIRST] [SECOND]
commands mkdir [RUNDIR] && \
         bipype --out_dir [RUNDIR] -rapsearch rap_KEGG -humann --mode run -ot txt --input [INPUT] && \
         bipype_cheat [RUNDIR]
