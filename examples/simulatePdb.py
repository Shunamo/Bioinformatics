# -*- coding: utf-8 -*-
# This script was generated by OpenMM-Setup on 2024-07-05.

from openmm import *
from openmm.app import *
from openmm.unit import *

# Input Files
pdb = PDBFile('1ce1-processed-fixed.pdb')
forcefield = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')

# System Configuration
nonbondedMethod = PME  # Periodic boundary conditions을 사용하도록 변경
constraints = HBonds
rigidWater = True

# Integration Options
dt = 0.004*picoseconds
temperature = 300*kelvin
friction = 1/picosecond
pressure = 1.0*atmospheres
barostatInterval = 25

# Simulation Options
steps = 10000
equilibrationSteps = 5000
platform = Platform.getPlatformByName('Reference')

# Prepare the Simulation
print('Building system...')
topology = pdb.topology
positions = pdb.positions
system = forcefield.createSystem(topology, nonbondedMethod=nonbondedMethod,
                                 constraints=constraints, rigidWater=rigidWater)
system.addForce(MonteCarloBarostat(pressure, temperature, barostatInterval))
integrator = LangevinMiddleIntegrator(temperature, friction, dt)
simulation = Simulation(topology, system, integrator, platform)
simulation.context.setPositions(positions)

# Minimize and Equilibrate
print('Performing energy minimization...')
simulation.minimizeEnergy()
print('Equilibrating...')
simulation.context.setVelocitiesToTemperature(temperature)
simulation.step(equilibrationSteps)

# Simulate
print('Simulating...')
simulation.currentStep = 0
simulation.step(steps)
