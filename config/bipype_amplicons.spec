[CONFIG]
name bipype_amplicons
input FASTQ
scaffoldOutput [RUNDIR]/Scaffolds.fasta
location python/bipype
output 16S_ITS.krona
threads --threads
unpaired [FIRST]
paired_interleaved [FIRST] [SECOND]
paired [FIRST] [SECOND]
commands mkdir [RUNDIR] && \
         bipype --out_dir [RUNDIR] --cutadapt use_paths both --mode run -ITS -16S -ot ITS 16S --input [INPUT] && \
         bipype_cheat [RUNDIR]
