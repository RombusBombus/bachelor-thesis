#!/bin/bash -l
#
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=72
#SBATCH --time=2:00:00
#SBATCH --export=NONE

unset SLURM_EXPORT_ENV

# Check that a directory argument was provided
if [ $# -ne 1 ]; then
    echo "Usage: sbatch $0 <vasp_workdir>"
    exit 1
fi

WORKDIR="$1"

# Check that the directory exists
if [ ! -d "$WORKDIR" ]; then
    echo "Error: Directory '$WORKDIR' does not exist."
    exit 1
fi

# module use /home/atuin/b299bb/b299bb11/TheoFEM/Modules/
# module load VASP/6.6.0_intel_hdf5

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
