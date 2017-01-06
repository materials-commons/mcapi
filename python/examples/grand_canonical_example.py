# this script creates a 'CASM Monte Carlo Calculation' process
# and uploads the results files

import casm.project 
import mcapi
import numpy as np
import math

# specify the version of casm these functions work for
casm_version = "0.2.0"

# Schoenflies to Hermann-Mauguin
symmap = {
  'C1': '1',
  'Ci': '-1',
  'S2': '-1',
  'C2': '2',
  'Cs': 'm',
  'C1h': 'm',
  'C2h': '2/m',
  'D2': '222',
  'V': '222',
  'C2v': 'mm2',
  'D2h': 'mmm',
  'Vh': 'mmm',
  'C4': '4',
  'S4': '-4',
  'C4h': '4/m',
  'D4': '422',
  'C4v': '4mm',
  'D2d': '-42m',
  'Vd': '-42m',
  'D4h': '4/mmm',
  'C3': '3',
  'S6': '-3',
  'C3i': '-3',
  'D3': '32',
  'C3v': '3m',
  'D3d': '-3m',
  'C6': '6',
  'C3h': '-6',
  'C6h': '6/m',
  'D6': '622',
  'C6v': '6mm',
  'D3h': '-6m2',
  'D6h': '6/mmm',
  'T': '23',
  'Th': 'm-3',
  'O': '432',
  'Td': '-43m',
  'Oh': 'm-3m',
}

# lattice system
latsysmap = {
  'Ci': 'triclinic',
  'S2': 'triclinic',
  'C2h': 'monoclinic',
  'D2h': 'orthorhombic',
  'D4h': 'tetragonal',
  'D3d': 'rhombohedral',
  'D6h': 'hexagonal',
  'Oh': 'cubic',
}

# crystal system to Schoenflies
xtalsysmap = {
  'triclinic': ['C1', 'Ci', 'S2'],
  'monoclinic': ['C2', 'Cs', 'C1h', 'C2h'],
  'orthorhombic': ['D2', 'V', 'C2v', 'D2h', 'Vh'],
  'tetragonal': ['C4', 'S4', 'C4h', 'D4', 'C4v', 'D2d', 'Vd', 'D4h'],
  'trigonal': ['C3', 'S6', 'C3i', 'D3', 'C3v', 'D3d'],
  'hexagonal': ['C6', 'C3h', 'C6h', 'D6', 'C6v', 'D3h', 'D6h'],
  'cubic': ['T', 'Th', 'O', 'Td', 'Oh']
}

# crystal family to Schoenflies
xtalfamilymap = {
  'triclinic': ['C1', 'Ci', 'S2'],
  'monoclinic': ['C2', 'Cs', 'C1h', 'C2h'],
  'orthorhombic': ['D2', 'V', 'C2v', 'D2h', 'Vh'],
  'tetragonal': ['C4', 'S4', 'C4h', 'D4', 'C4v', 'D2d', 'Vd', 'D4h'],
  'hexagonal': ['C3', 'S6', 'C3i', 'D3', 'C3v', 'D3d', 'C6', 'C3h', 'C6h', 'D6', 'C6v', 'D3h', 'D6h'],
  'cubic': ['T', 'Th', 'O', 'Td', 'Oh']
}

# crystal family to Schoenflies
space_group_number_map {
  'C1': '1',
  'Ci': '2',
  'S2': '2',
  'C2': '3:5',
  'Cs': '6:9',
  'C1h': '6:9',
  'C2h': '10:15',
  'D2': '16:24',
  'V': '16:24',
  'C2v': '25:46',
  'D2h': '47:74',
  'Vh': '47:74',
  'C4': '75:80',
  'S4': '81:82',
  'C4h': '83:88',
  'D4': '89:98',
  'C4v': '99:110,
  'D2d': '111:122',
  'Vd': '111:122',
  'D4h': '123:142',
  'C3': '143:146',
  'S6': '147:148',
  'C3i': '149:155',
  'D3': '149:155',
  'C3v': '156:161',
  'D3d': '162:167',
  'C6': '168:173',
  'C3h': '174',
  'C6h': '175:176',
  'D6': '177:182',
  'C6v': '183:186',
  'D3h': '187:190',
  'D6h': '191:194',
  'T': '195:199',
  'Th': '200:206',
  'O': '207:214',
  'Td': '215:220',
  'Oh': '221:230',
}

def _add_string_measurement(create_sample_process, attrname, value):
    measurement_data = {
        "attribute": attrname,
        "otype": "string",
        "value": value,
        "is_best_measure": True
    }
    return create_sample_process.create_measurement(data=measurement_data)

def _add_matrix_measurement(create_sample_process, attrname, value):
    measurement_data = {
        "attribute": attrname,
        "otype": "matrix",
        "value": {
            "dimensions": list(value.shape),
            "otype":  "float" ,
            "value": value
        },
        "is_best_measure": True
    }
    return create_sample_process.create_measurement(data=measurement_data)

def _add_vector_measurement(create_sample_process, attrname, value):
    measurement_data = {
        "attribute": attrname,
        "otype": "vector",
        "value": {
            "dimensions": len(value),
            "otype":  "float" ,
            "value": value
        },
        "is_best_measure": True
    }
    return create_sample_process.create_measurement(data=measurement_data)


def add_files_recursively(project, remote_dir, local_dirpath):
    """
    Arguments:
        project: mcapi.Project object
        remote_dir: mcapi.Directory object, where contents of local_dirpath 
            should be uploaded to
        local_dirpath: path to local directory to add file from, recursively
    
    Returns:
        files: List of mcapi.File objects
    """
    ... code ...


def create_prim_sample(expt, casm_proj):
    """
    Arguments:
        expt: mcapi.Experiment object
        casm_proj: casm.project.Project object
    """
    def _angle(a, b):
        return math.acos(np.dot(a,b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    def _lattice_parameters(L):
        """
        Arguments:
            L: lattice as column vector array-like
        
        Returns:
            {"a":a, "b":b, "c":c, "alpha":alpha, "beta":beta, "gamma":gamma}
        """
        a = np.linalg.norm(L[:,0])
        b = np.linalg.norm(L[:,1])
        c = np.linalg.norm(L[:,2])
        alpha = _angle(L[:,1], L[:,2])
        beta = _angle(L[:,0], L[:,2])
        gamma = _angle(L[:,0], L[:,1])
        return {"a":a, "b":b, "c":c, "alpha":alpha, "beta":beta, "gamma":gamma}
    
    def _lattice_symmetry(casm_proj):
        """
        Parse from 'casm sym', return Schoenflies form
        """
        def parse(stdout):
            for line in stdout.split('\n'):
                if re.search('Lattice point group is:', line):
                    return line.split()[-1]
            return None

        proc = subprocess.Popen(["casm", "sym"], stdout=subprocess.PIPE)
        stdout = proc.communicate()[0]
        return parse(stdout)
    
    def _lattice_system(schoenflies_symbol):
        """ 
        Determine from lattice symmetry
        """
        return latsysmap[schoenflies_symbol]
    
    def _crystal_symmetry(casm_proj):
        """
        Parse from 'casm sym', return Schoenflies form
        """
        def parse(stdout):
            for line in stdout.split('\n'):
                if re.search('Crystal point group is:', line):
                    return line.split()[-1]
            return None

        proc = subprocess.Popen(["casm", "sym"], stdout=subprocess.PIPE)
        stdout = proc.communicate()[0]
        return parse(stdout)
    
    def _crystal_symmetry_hm(schoenflies_symbol):
        """
        Parse from 'casm sym', return Hermann-Mauguin form
        """
        return symmap[schoenflies_symbol]
    
    def _crystal_system(casm_proj):
        """ 
        Determine crystal system from crystal symmetry
        """
        for key, val in xtalsysmap:
            if schoenflies_symbol in val:
                return key
        return None
    
    def _crystal_family(schoenflies_symbol):
        """ 
        Determine crystal family from crystal symmetry
        """
        for key, val in xtalfamilymap:
            if schoenflies_symbol in val:
                return key
        return None
    
    def _components(casm_proj):
        # raw composition_axes.json (for some properties not yet supported in the casm.project API)
        with open(dir.composition_axes()) as f:
            raw_composition_axes = json.load(f)
            comp = raw_composition_axes["standard_axes"]["0"]["components"]
        return comp

    def _elements(casm_proj):
        # currently identical to components
        return _components(casm_proj)

    def _n_independent_compositions(casm_proj):
        # raw composition_axes.json (for some properties not yet supported in the casm.project API)
        with open(dir.composition_axes()) as f:
            raw_composition_axes = json.load(f)
            n = raw_composition_axes["standard_axes"]["0"]["independent_compositions"]
        return n

    def _degrees_of_freedom(casm_proj):
        """
        Get allowed types of DoF, as vector
        """
        # currently only "occupation"
        return ["occupation"]
    
    ## Create Sample
    create_sample_process = expt.create_process_from_template("")

    # casm.project.ProjectSettings instance
    proj_set = casm_proj.settings
    
    # casm.project.DirectoryStructure instance
    dir = casm_proj.dir
    
    # raw project_settings.json (for some properties not yet supported in the casm.project API)
    with open(dir.project_settings()) as f:
      raw_proj_set = json.load(f)
    
    # raw prim.json (for some properties not yet supported in the casm.project API)
    with open(dir.prim()) as f:
      raw_prim = json.load(f)
    
    # Sample attributes (how to check names?):
    # "name"
    name = raw_proj_set["name"]
    _add_string_measurement(create_sample_process, 'name', name)

    # "lattice"
    #     "matrix"
    #     "parameters" (a, b, c, alpha, beta, gamma)
    #     "system" ("triclinic", "monoclinic", "orthorhombic", "tetragonal", "hexagonal", "rhombohedral", "cubic")
    #     "symmetry" (Schönflies symbol)
    lattice_matrix = np.array(raw_prim["lattice_vectors"]).transpose()
    _add_matrix_measurement(create_sample_process, 'lattice', lattice_matrix)

    lattice_parameters = _lattice_parameters(lattice_matrix)
    _add_vector_measurement(create_sample_process, 'parameters', lattice_parameters)

    lattice_symmetry = _lattice_symmetry(casm_proj)
    _add_string_measurement(create_sample_process, 'symmetry', lattice_symmetry)

    lattice_system = _lattice_system(lattice_symmetry)
    _add_string_measurement(create_sample_process, 'system', lattice_system)

    # "space_group"
    #      "schonflies_symbol"
    #      "hermann_mauguin_symbol"
    #      "number"
    #      "family" ("triclinic", "monoclinic", "orthorhombic", "tetragonal", "hexagonal", "cubic")
    #      "system" ("triclinic", "monoclinic", "orthorhombic", "tetragonal", "hexagonal", "trigonal", "cubic")
    crystal_pg_schoenflies_symbol = _crystal_symmetry(casm_proj)
    _add_string_measurement(create_sample_process, 'schonflies_space_group_symbol', crystal_pg_schoenflies_symbol)

    crystal_pg_hermann_mauguin_symbol = _crystal_symmetry_hm(space_group_symbol)
    _add_string_measurement(create_sample_process, 'hermann_mauguin_space_group_symbol', crystal_pg_hermann_mauguin_symbol)

    crystal_family = _crystal_family(space_group_schoenflies_symbol)
    _add_string_measurement(create_sample_process, 'crystal_family', crystal_family)

    crystal_system = _crystal_system(space_group_schoenflies_symbol)
    _add_string_measurement(create_sample_process, 'crystal_system', crystal_system)

    # right now, this is a string giving a range of possible values based on the
    #   crystal point group
    space_group_number = space_group_number_map[space_group_schoenflies_symbol]
    _add_string_measurement(create_sample_process, 'space_group_number', space_group_number)

    # "file"
    # filename = dir.prim()  
    ... need to get datafile ...
    _add_file_measurement(create_sample_process, 'casm_prism_file', file_id, filename)

    # "elements" - currently only elemental components are allowed
    elements = _elements(casm_proj)
    ...
    
    # "n_elements" 
    n_elements = len(elements)
    ...
    
    # "components" - currently only elemental components are allowed
    components = _components(casm_proj)
    ...     

    # "n_components"
    n_components = len(components)
    ...
    
    # "n_independent_compositions"
    n_independent_compositions = _n_independent_compositions(casm_proj)
    ...
    
    # "degrees_of_freedom" ("occupation", "displacement", "strain")
    degrees_of_freedom = _degrees_of_freedom(casm_proj)
    ...
    
    

def create_composition_axes_sample(expt, casm_proj, axes_id=None):

    ## Create Sample
    
    # "prim"
    
    # end members:
    #     "origin"
    #     "a", "b", et.c
    
    # "formula"
    
    # "parametric_formula"
    

def create_clex_sample(expt, casm_proj):
    """
    Arguments:
       
       clex_desc: casm.project.ClexDescription object
       
    """

    # "prim"
    
    # "bspecs" (file)
    
    # "eci" (file)

    
def create_monte_carlo_process(expt, settings_path, mc_dir_localpath, mc_dir_remotepath,
    prim, comp_axes, formation_energy_clex):
    """
    Arguments:
        expt: mcapi.Experiment object
        settings_path: Path to Monte Carlo input setttings file
        mc_dir_localpath: Path to local directory containing Monte Carlo results
        mc_dir_localpath: Path to remote directory to create to hold Monte Carlo results
        prim: Parent Crystal Structure sample
        comp_axes: Composition Axes sample
        formation_energy_clex: Formation energy Clex sample
    """
    # Ref Materials Commons project
    project = expt.project
    
    ## Create a Process
    mc_template = "global_CASM Monte Carlo Calculation"
    proc = expt.create_process_from_template(mc_template)

    # read the input settings file
    with open(mc_settings_path) as f:
        settings = json.load(f)

    # Process attributes that must be set from the settings file:
    proc.set_value_of_setup_property('ensemble', settings['ensemble'])
    proc.set_value_of_setup_property('method', settings['method'])
    proc.set_value_of_setup_property('supercell_transformation_matrix', settings['supercell'])
    proc.set_value_of_setup_property('motif', settings['driver']['motif'])
    
    mode = settings['driver']['mode']
    proc.set_value_of_setup_property('mode', mode)
    if mode == 'incremental':
        init_cond = GcmcConditions(settings['driver']['initial_conditions')
        proc.set_value_of_setup_property('initial_conditions_temperature', init_cond.T)
        proc.set_value_of_setup_property('initial_conditions_parametric_chemical_potential', init_cond.param_chem_pot)
        
        final_cond = GcmcConditions(settings['driver']['final_conditions')
        proc.set_value_of_setup_property('final_conditions_temperature', init_cond.T)
        proc.set_value_of_setup_property('final_conditions_parametric_chemical_potential', init_cond.param_chem_pot)
        
        final_cond = GcmcConditions(settings['driver']['incremental_conditions')
        proc.set_value_of_setup_property('incremental_conditions_temperature', init_cond.T)
        proc.set_value_of_setup_property('incremental_conditions_parametric_chemical_potential', init_cond.param_chem_pot)
        
    elif mode == 'custom':
        #custom_cond = [GcmcConditions(cond) for cond in settings['driver']['custom_conditions'] ]
        # "custom_conditions_temperature"
        # "custom_conditions_parametric_chemical_potential"
        print "CASM Monte Carlo Calculation template needs an update to support custom conditions"
        
    else:
        # is this the best way to handle errors?
        raise Exception("Unknown Monte Carlo driver mode: " + mode)
    
    ## Add samples
    proc.add_samples_to_process([prim, comp_axes, formation_energy_clex])
    
    ## Upload files
    # create directory
    mc_dir_remote = project.add_directory(mc_dir_remotepath),
    
    # upload files
    files = add_files_recursively(project, mc_dir_remote, mc_dir_localpath)
    
    ## Add files to process
    proc.add_files(files)
    
    ## Add measurements (read from results)
    # TODO

    




