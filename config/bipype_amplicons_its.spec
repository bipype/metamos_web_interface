[CONFIG]
name bipype_amplicons_its
input FASTQ
scaffoldOutput [RUNDIR]/Scaffolds.fasta
location python/bipype
output ITS.krona
threads --threads
unpaired [FIRST]
paired_interleaved [FIRST] [SECOND]
paired [FIRST] [SECOND]
commands mkdir [RUNDIR] && \
         bipype --out_dir [RUNDIR] --cutadapt use_paths ITS --mode run -ITS -ot ITS --input [INPUT] && \
         bipype_cheat [RUNDIR]
