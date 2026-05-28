#!/bin/bash -l
#
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=72
#SBATCH --time=5:00:00
#SBATCH --export=NONE
#SBATCH --mail-user=neumeier.nicolas.1@gmail.com
#SBATCH --mail-type=ALL

unset SLURM_EXPORT_ENV

module use /home/atuin/b299bb/b299bb11/TheoFEM/Modules/
module load VASP/6.6.0_intel_hdf5

module load julia
module use ~/modulefiles
module load Vampires/1.0

cd $SLURM_SUBMIT_DIR

outfile="host.info"

{
echo "Hostname: $(hostname)"
cat /etc/issue
grep "model name" /proc/cpuinfo | cut -d: -f2 | uniq -c
grep "cpu MHz" /proc/cpuinfo | head -1
grep MemTotal /proc/meminfo
free -g
ulimit -a
echo "SLURM_NODELIST=$SLURM_NODELIST"
pwd
} > "$outfile"

srun vasp_std > vasp.log