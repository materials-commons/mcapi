import os
import json

class GcmcConditions(object):
    def __init__(self, data):
        self.T = data['temperature']
        self.param_chem_pot = data['param_chem_pot']
    
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
    p = mc_local_abspath
    dir = mcapi.misc._get_file_or_directory(proj, os.path.dirname(p))
    files = dir.add_directory_tree(os.path.basename(p), os.path.dirname(p), verbose=True)
                
    ## Add files to process
    proc.add_files(files)
    
    ## Add measurements (read from 'mc_local_abspath/results.json' or 'mc_local_abspath/results.csv')
    # TODO

    return proc

