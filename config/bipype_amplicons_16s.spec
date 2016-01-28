[CONFIG]
name bipype_amplicons_16s
input FASTQ
scaffoldOutput [RUNDIR]/Scaffolds.fasta
location python/bipype
output 16S.krona
threads --threads
unpaired [FIRST]
paired_interleaved [FIRST] [SECOND]
paired [FIRST] [SECOND]
commands mkdir [RUNDIR] && \
         bipype --out_dir [RUNDIR] --cutadapt use_paths 16S --mode run -16S -ot 16S --input [INPUT] && \
         bipype_cheat [RUNDIR]
