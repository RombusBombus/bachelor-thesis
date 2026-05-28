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

module load lammps

cd $SLURM_SUBMIT_DIR

srun lmp -in in.simulation