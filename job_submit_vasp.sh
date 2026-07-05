#!/bin/bash -l
#
# SBATCH --job-name=vasp_job
# SBATCH --nodes=4
# SBATCH --ntasks-per-node=72
# SBATCH --time=2:00:00
# SBATCH --export=NONE
# SBATCH --mail-user=neumeier.nicolas.1@gmail.com
# SBATCH --email-type=ALL

unset SLURM_EXPORT_ENV

module use /home/atuin/b299bb/TheoFEM/Modules/
module load VASP/6.6.0_intel


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