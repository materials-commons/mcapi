# this script creates a 'CASM Monte Carlo Calculation' process
# and uploads the results files

# TODO - link up casm.project
# import casm.project
import mcapi
import numpy as np
import math
import os
import json
from string import ascii_lowercase
import argparse
import casm_mcapi


# TODO -- the following objects not defined
subprocess = {}
re = {}
schoenflies_symbol = ""
space_group_symbol = ""
space_group_schoenflies_symbol = ""
space_group_schoenflies_symbol = ""
space_group_schoenflies_symbol = ""
name = ""

# TODO -- stub functions - either not defined or not imported!
def _parameteric_formula():
    pass

def GcmcConditions(cond):
    pass

def path_help():
    pass

def files_help():
    pass

def prim_help():
    pass

def composition_help():
    pass

def clex_help():
    pass

def mc_help():
    pass

def add_files_recursively():
    pass

# Note assume throughout that mcapi.Project.local_abspath is set with local
# Materials Commons project directory tree location

def create_monte_carlo_process(expt, settings_local_abspath,
    prim, comp_axes, formation_energy_clex):
    """
    Create a CASM Monte Carlo Calculation process and uploads associated files
    
    Assumes expt.proj.local_abspath exists and adds files relative to that path.
    
    Arguments:
        expt: mcapi.Experiment object
        settings_local_abspath: Path to Monte Carlo input setttings file. Results
             are expected in the same directory.
        prim: Parent Crystal Structure sample
        comp_axes: Composition Axes sample
        formation_energy_clex: Formation energy Clex sample
    
    Returns:
        proc: mcapi.Process
    """
    # Ref Materials Commons project
    proj = expt.project
    
    ## Create a CASM Monte Carlo Calculation Process
    proc = expt.create_process_from_template('global_CASM Monte Carlo Calculation')

    # read the input settings file
    with open(settings_local_abspath) as f:
        settings = json.load(f)
    
    # expect results in same directory
    mc_local_abspath = os.path.dirname(settings_local_abspath)

    # Process attributes that must be set from the settings file:
    proc.set_value_of_setup_property('ensemble', settings['ensemble'])
    proc.set_value_of_setup_property('method', settings['method'])
    proc.set_value_of_setup_property('supercell_transformation_matrix', settings['supercell'])
    proc.set_value_of_setup_property('motif', settings['driver']['motif'])
    
    mode = settings['driver']['mode']
    proc.set_value_of_setup_property('mode', mode)
    if mode == 'incremental':
        init_cond = GcmcConditions(settings['driver']['initial_conditions'])
        proc.set_value_of_setup_property('initial_conditions_temperature', init_cond.T)
        proc.set_value_of_setup_property('initial_conditions_parametric_chemical_potential', init_cond.param_chem_pot)
        
        final_cond = GcmcConditions(settings['driver']['final_conditions'])
        proc.set_value_of_setup_property('final_conditions_temperature', init_cond.T)
        proc.set_value_of_setup_property('final_conditions_parametric_chemical_potential', init_cond.param_chem_pot)
        
        final_cond = GcmcConditions(settings['driver']['incremental_conditions'])
        proc.set_value_of_setup_property('incremental_conditions_temperature', init_cond.T)
        proc.set_value_of_setup_property('incremental_conditions_parametric_chemical_potential', init_cond.param_chem_pot)
        
    elif mode == 'custom':
        #custom_cond = [GcmcConditions(cond) for cond in settings['driver']['custom_conditions'] ]
        custom_cond = [GcmcConditions(cond) for cond in settings['driver']['custom_conditions']]
        
        # "custom_conditions_temperature" (1d np.array)
        custom_cond_T = np.array([cond.T for cond in custom_cond])
        proc.set_value_of_setup_property('custom_conditions_temperature', custom_cond_T)
        
        # "custom_conditions_parametric_chemical_potential" (2d np.array)
        custom_cond_param_chem_pot = np.array([cond.param_chem_pot for cond in custom_cond])
        proc.set_value_of_setup_property('custom_conditions_parametric_chemical_potential', custom_cond_param_chem_pot)
        
    else:
        # is this the best way to handle errors?
        raise Exception("Unknown Monte Carlo driver mode: " + mode)
    
    ## Add samples
    proc.add_samples_to_process([prim, comp_axes, formation_energy_clex])
    
    ## Upload files
    files = add_files_recursively(proj, mc_local_abspath)
    
    ## Add files to process
    proc.add_files(files)
    
    ## Add measurements (read from 'mc_local_abspath/results.json' or 'mc_local_abspath/results.csv')
    # TODO

    return proc

if __name__ == "__main__":
    #CommonsCLIParser()
    print "hello"

    parser = argparse.ArgumentParser(description = 'Upload CASM data to Materials Commons')
    parser.add_argument('--path', help=path_help, type=str, default=None)
    parser.add_argument('--files', help=files_help, action="store_true", default=False)
    parser.add_argument('--prim', help=prim_help, action="store_true", default=False)
    parser.add_argument('--composition', help=composition_help, action="store_true", default=False)
    parser.add_argument('--clex', help=clex_help, action="store_true", default=False)
    parser.add_argument('--mc', help=mc_help, action="store_true", default=False)
    args = parser.parse_args()
    
    ## (How to construct already existing mcapi.Project / mcapi.Experiment ? )
    #... check to find what Project I'm in ...
    proj = 'to be determined'
    
    ## Construct Experiment object (assume already created remotely)
    #... get current Experiment ...
    expt = 'to be determined'
    
    ## Set local path to Materials Commons project files
    expt.project.local_abspath = 'to be determined'
    

    # TODO - link up casm.project
    ## Do CASM things ...
    ## casm_proj = casm.project.Project(args.path)
    
    if args.mc:
        pass

    

