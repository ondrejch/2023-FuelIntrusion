#!/bin/bash
#PBS -V
#PBS -N MSFR_S2
#PBS -q fill
#PBS -l nodes=1:ppn=32

hostname
rm -f done.dat
cd ${PBS_O_WORKDIR}

s2inputfile=lats2

/opt/serpent_o/bin/sss2 -omp $PBS_NUM_PPN  ${s2inputfile}  > out.out
awk 'BEGIN{ORS="\t"} /ANA_KEFF/ || /CONVERSION/ {print $7" "$8;}' ${s2inputfile}_res.m > done.out
