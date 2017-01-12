# this script creates a 'CASM Monte Carlo Calculation' process
# and uploads the results files

import numpy as np
import math
import os
import json
from string import ascii_lowercase

# Note assume throughout that mcapi.Project.local_abspath is set with local
# Materials Commons project directory tree location

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
space_group_number_map = {
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
  'C4v': '99:110',
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

# The following create and set measurments, updating 'create_sample_process'

def _set_measurement(create_sample_process, attrname, measurement_data):
    measurement = create_sample_process.create_measurement(data=measurement_data)
    
    measurement_property = {
        "attribute":attrname
    }
    
    return create_sample_process.set_measurements_for_process_samples(
        measurement_property, [measurement])

def _add_integer_measurement(create_sample_process, attrname, value):
    measurement_data = {
        "attribute": attrname,
        "otype": "integer",
        "value": value,
        "is_best_measure": True
    }
    return _set_measurement(create_sample_process, attrname, measurement_data)
        

def _add_number_measurement(create_sample_process, attrname, value):
    measurement_data = {
        "attribute": attrname,
        "otype": "number",
        "value": value,
        "is_best_measure": True
    }
    return _set_measurement(create_sample_process, attrname, measurement_data)

def _add_boolean_measurement(create_sample_process, attrname, value):
    measurement_data = {
        "attribute": attrname,
        "otype": "boolean",
        "value": value,
        "is_best_measure": True
    }
    return _set_measurement(create_sample_process, attrname, measurement_data)

def _add_string_measurement(create_sample_process, attrname, value):
    measurement_data = {
        "attribute": attrname,
        "otype": "string",
        "value": value,
        "is_best_measure": True
    }
    return _set_measurement(create_sample_process, attrname, measurement_data)

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
    return _set_measurement(create_sample_process, attrname, measurement_data)

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
    return _set_measurement(create_sample_process, attrname, measurement_data)

def _add_list_measurement(create_sample_process, attrname, value, value_type):
    """
    Add a measurement that is a list of some type of object.
    
    Not sure how this JSON should look...
    """
    measurement_data = {
        "attribute": attrname,
        "otype": "vector",
        "value": {
            "dimensions": len(value),
            "otype":  value_type ,
            "value": value
        },
        "is_best_measure": True
    }
    return _set_measurement(create_sample_process, attrname, measurement_data)

def _add_file_measurement(create_sample_process, attrname, file_obj):
    """
    Add a measurement that is a data file
    
    Not sure how this JSON should look...
    """
    measurement_data = {
        "attribute": attrname,
        "otype": "file",
        "value": {
            "file_id": file_obj.id,
            "file_name": file_obj.name
        },
        "is_best_measure": True
    }
    return _set_measurement(create_sample_process, attrname, measurement_data)

def _add_sample_measurement(create_sample_process, attrname, sample):
    """
    Add a measurement that is a sample
    
    Not sure how this JSON should look...
    """
    measurement_data = {
        "attribute": attrname,
        "otype": "file",
        "value": {
            "sampled_id": sample.id,
            "sample_name": sample.name
        },
        "is_best_measure": True
    }
    return _set_measurement(create_sample_process, attrname, measurement_data)


def _add_file(proj, local_file_abspath, filename=None):
    """
    Upload a file, matching local directory structure and creating intermediate
    remote directories as necessary. Uses local filename.
    
    Arguments:
        proj: mcapi.Project object
        local_file_abspath: absolute path to local file
        filename: name to give file on Materials Commons (default=os.path.basename(local_file_abspath))
            
    """
    file_relpath = os.path.relpath(proj.local_abspath, local_file_abspath)
    top = proj.get_top_directory()
    
    # get mcapi.Directory to add file, creating intermediates as necessary
    directory = top.get_descendent_list_by_path(os.path.dirname(file_relpath))[-1]
    
    if filename is None:
        filename = os.path.basename(local_file_abspath)
    return directory.add_file(filename, local_file_abspath)


def _add_files_recursively(proj, local_dir_abspath):
    """
    Arguments:
        proj: mcapi.Project object
        local_dir_abspath: absolute path to local directory to add files from, recursively
    
    Returns:
        files: List of mcapi.File objects
    """
    files = []
    for root, dirs, files in os.walk(local_dir_abspath):
        for file in files:
            p=os.path.join(root,file)
            files.append(_add_file(proj, os.path.abspath(p)))
    return files


def create_prim_sample(expt, casm_proj):
    """
    Create a CASM Primitive Crystal Structure Sample
    
    Assumes expt.proj.local_abspath exists and adds files relative to that path.
    
    Arguments:
        expt: mcapi.Experiment object
        casm_proj: casm.project.Project object
    
    Returns:
        create_sample_process: mcapi.Process that created the sample
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
    
#    def _lattice_symmetry(casm_proj):
#        """
#        Parse from 'casm sym', return Schoenflies form
#        """
#        def parse(stdout):
#            for line in stdout.split('\n'):
#                if re.search('Lattice point group is:', line):
#                    return line.split()[-1]
#            return None
#
#        proc = subprocess.Popen(["casm", "sym"], stdout=subprocess.PIPE)
#        stdout = proc.communicate()[0]
#        return parse(stdout)
    
    def _lattice_system(schoenflies_symbol):
        """
        Determine from lattice symmetry
        """
        return latsysmap[schoenflies_symbol]
    
#    def _crystal_symmetry(casm_proj):
#        """
#        Parse from 'casm sym', return Schoenflies form
#        """
#        def parse(stdout):
#            for line in stdout.split('\n'):
#                if re.search('Crystal point group is:', line):
#                   return line.split()[-1]
#            return None
#
#        proc = subprocess.Popen(["casm", "sym"], stdout=subprocess.PIPE)
#        stdout = proc.communicate()[0]
#        return parse(stdout)
    
    def _crystal_symmetry_hm(schoenflies_symbol):
        """
        Parse from 'casm sym', return Hermann-Mauguin form
        """
        return symmap[schoenflies_symbol]
    
#    def _crystal_system(casm_proj):
#        """
#        Determine crystal system from crystal symmetry
#        """
#        for key, val in xtalsysmap:
#            if schoenflies_symbol in val:
#                return key
#        return None
    
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
    create_sample_process = expt.create_process_from_template("global_Primitive Crystal Structure")

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
    name = raw_proj_set['name']
    _add_string_measurement(create_sample_process, 'name', name)

    # "lattice"
    #     "matrix"
    #     "parameters" (a, b, c, alpha, beta, gamma)
    #     "system" ("triclinic", "monoclinic", "orthorhombic", "tetragonal", "hexagonal", "rhombohedral", "cubic")
    #     "symmetry" (Schönflies symbol)
    lattice_matrix = np.array(raw_prim['lattice_vectors']).transpose()
    _add_matrix_measurement(create_sample_process, 'lattice', lattice_matrix)

    lattice_parameters = _lattice_parameters(lattice_matrix)
    _add_vector_measurement(create_sample_process, 'parameters', lattice_parameters)

#    lattice_symmetry = _lattice_symmetry(casm_proj)
#    _add_string_measurement(create_sample_process, 'symmetry', lattice_symmetry)

#    lattice_system = _lattice_system(lattice_symmetry)
#    _add_string_measurement(create_sample_process, 'system', lattice_system)

    # "space_group"
    #      "schonflies_symbol"
    #      "hermann_mauguin_symbol"
    #      "number"
    #      "family" ("triclinic", "monoclinic", "orthorhombic", "tetragonal", "hexagonal", "cubic")
    #      "system" ("triclinic", "monoclinic", "orthorhombic", "tetragonal", "hexagonal", "trigonal", "cubic")
#    crystal_pg_schoenflies_symbol = _crystal_symmetry(casm_proj)
#    _add_string_measurement(create_sample_process, 'schonflies_space_group_symbol', crystal_pg_schoenflies_symbol)

#    crystal_pg_hermann_mauguin_symbol = _crystal_symmetry_hm(space_group_symbol)
#    _add_string_measurement(create_sample_process, 'hermann_mauguin_space_group_symbol', crystal_pg_hermann_mauguin_symbol)

#    crystal_family = _crystal_family(space_group_schoenflies_symbol)
#    _add_string_measurement(create_sample_process, 'crystal_family', crystal_family)

#    crystal_system = _crystal_system(space_group_schoenflies_symbol)
#    _add_string_measurement(create_sample_process, 'crystal_system', crystal_system)

    # right now, this is a string giving a range of possible values based on the
    #   crystal point group
#    space_group_number = space_group_number_map[space_group_schoenflies_symbol]
#    _add_string_measurement(create_sample_process, 'space_group_number', space_group_number)

    # "file"
    # filename = dir.prim()  
#    file = _add_file(expt.proj, dir.prim())
#    _add_file_measurement(create_sample_process, 'casm_prism_file', file)

    # "elements" - currently only elemental components are allowed
    elements = _elements(casm_proj)
    _add_list_measurement(create_sample_process, 'elements', elements, 'string')  #check
    
    # "n_elements" 
    n_elements = len(elements)
    _add_integer_measurement(create_sample_process, 'n_elements', n_elements)
    
    # "components" - currently only elemental components are allowed
    components = _components(casm_proj)
    _add_list_measurement(create_sample_process, 'components', components, 'string')  #check
    
    # "n_components"
    n_components = len(components)
    _add_integer_measurement(create_sample_process, 'n_components', n_components)
    
    # "n_independent_compositions"
    n_independent_compositions = _n_independent_compositions(casm_proj)
    _add_integer_measurement(create_sample_process, 'n_independent_compositions', n_independent_compositions)
    
    # "degrees_of_freedom" ("occupation", "displacement", "strain")
    degrees_of_freedom = _degrees_of_freedom(casm_proj)
    _add_string_measurement(create_sample_process, 'degrees_of_freedom', degrees_of_freedom)
    
    return create_sample_process
    

def create_composition_axes_sample(expt, casm_proj, prim, clex_desc, axes_name):
    """
    Create a CASM Composition Axes Sample
    
    Assumes expt.proj.local_abspath exists and adds files relative to that path.
    
    Arguments:
        expt: mcapi.Experiment object
        casm_proj: casm.project.Project object
        prim: mcapi.Sample object of type CASM "global_Primitive Crystal Structure"
        clex_desc: casm.project.ClexDescription object
        axes_name: str, naming composition axes
    
    Returns:
        create_sample_process: mcapi.Process that created the sample
    """
    def _end_members(casm_proj, axes_name):
        """
        Currently only 'standard_axes'
        
        Arguments:
            casm_proj: casm.project.Project object
            axes_name: string, naming composition axes
            
        """
        # raw composition_axes.json (for some properties not yet supported in the casm.project API)
        result = dict()
        with open(dir.composition_axes()) as f:
            j = json.load(f)
            result['origin'] = j['standard_axes'][axes_name]['origin']
            for c in ascii_lowercase:
                if c in j['standard_axes'][axes_name]:
                    result[c] = j['standard_axes'][axes_name][c]
                else:
                    break
        return result
    
    def _formula(casm_proj, axes_name):
        """
        Currently only 'standard_axes'
        
        Arguments:
            casm_proj: casm.project.Project object
            axes_name: string, naming composition axes
            
        """
        # raw composition_axes.json (for some properties not yet supported in the casm.project API)
        result = dict()
        with open(dir.composition_axes()) as f:
            j = json.load(f)
            return j['standard_axes'][axes_name]['mol_formula']
    
    def _parametric_formula(casm_proj, axes_name):
        """
        Currently only 'standard_axes'
        
        Arguments:
            casm_proj: casm.project.Project object
            axes_name: string, naming composition axes
            
        """
        # raw composition_axes.json (for some properties not yet supported in the casm.project API)
        result = dict()
        with open(dir.composition_axes()) as f:
            j = json.load(f)
            return j['standard_axes'][axes_name]['param_formula']
    
    ## Create Sample
    create_sample_process = expt.create_process_from_template('global_Composition Axes')
    sample = create_sample_process.create_samples(
        sample_names=[axes_name]
    )[0]
    
    # casm.project.DirectoryStructure instance
    dir = casm_proj.dir
    
    # "prim"
    _add_sample_measurement(create_sample_process, 'prim', prim)
    
    # end members:
    #     "origin"
    #     "a", "b", etc.
    end_members = _end_members(casm_proj, axes_name)
    for key in end_members:
        _add_vector_measurement(create_sample_process, key, end_members[key])
    
    # "formula"
    formula = _formula(casm_proj, axes_name)
    _add_string_measurement(create_sample_process, 'formula', formula)
    
    # "parametric_formula"
#    parametric_formula = _parameteric_formula(casm_proj, axes_name)
#    _add_string_measurement(create_sample_process, 'parametric_formula', parametric_formula)
    
    return create_sample_process


def create_clex_sample(expt, casm_proj, prim, clex_desc):
    """
    Create a CASM Cluster Expansion Effective Hamiltonian Sample
    
    Assumes expt.proj.local_abspath exists and adds files relative to that path.
    
    Arguments:
        expt: mcapi.Experiment object
        casm_proj: casm.project.Project object
        prim: mcapi.Sample object of type CASM "global_Primitive Crystal Structure"
        clex_desc: casm.project.ClexDescription object
    
    Returns:
        create_sample_process: mcapi.Process that created the sample
    """
    ## Create Sample
    create_sample_process = expt.create_process_from_template('global_Cluster Expansion Effective Hamiltonian')
    
    # casm.project.DirectoryStructure instance
    dir = casm_proj.dir
    
    # "prim" (sample)
    _add_sample_measurement(create_sample_process, 'prim', prim)
    
    # "bspecs" (file)
    file_obj = _add_file(expt.proj, dir.bspecs(clex_desc))
    _add_file_measurement(create_sample_process, 'bspecs', file_obj)
    
    # "eci" (file)
    file_obj = _add_file(expt.proj, dir.eci(clex_desc))
    _add_file_measurement(create_sample_process, 'eci', file_obj.id, file_obj.name)
    
    return create_sample_process

    
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
#    if mode == 'incremental':
#        init_cond = GcmcConditions(settings['driver']['initial_conditions')
#        proc.set_value_of_setup_property('initial_conditions_temperature', init_cond.T)
#        proc.set_value_of_setup_property('initial_conditions_parametric_chemical_potential', init_cond.param_chem_pot)
#
#        final_cond = GcmcConditions(settings['driver']['final_conditions')
#        proc.set_value_of_setup_property('final_conditions_temperature', init_cond.T)
#        proc.set_value_of_setup_property('final_conditions_parametric_chemical_potential', init_cond.param_chem_pot)
#
#        final_cond = GcmcConditions(settings['driver']['incremental_conditions')
#        proc.set_value_of_setup_property('incremental_conditions_temperature', init_cond.T)
#        proc.set_value_of_setup_property('incremental_conditions_parametric_chemical_potential', init_cond.param_chem_pot)
        
#    elif mode == 'custom':
        #custom_cond = [GcmcConditions(cond) for cond in settings['driver']['custom_conditions'] ]
#        custom_cond = [GcmcConditions(cond) for cond in settings['driver']['custom_conditions']]
        
        # "custom_conditions_temperature" (1d np.array)
#        custom_cond_T = np.array([cond.T for cond in custom_cond])
#        proc.set_value_of_setup_property('custom_conditions_temperature', custom_cond_T)
        
        # "custom_conditions_parametric_chemical_potential" (2d np.array)
#        custom_cond_param_chem_pot = np.array([cond.param_chem_pot for cond in custom_cond])
#        proc.set_value_of_setup_property('custom_conditions_parametric_chemical_potential', custom_cond_param_chem_pot)
        
#    else:
        # is this the best way to handle errors?
#        raise Exception("Unknown Monte Carlo driver mode: " + mode)
    
    ## Add samples
    proc.add_samples_to_process([prim, comp_axes, formation_energy_clex])
    
    ## Upload files
    # TODO - different name/logic for function
    # files = add_files_recursively(proj, mc_local_abspath)
    
    ## Add files to process
    # proc.add_files(files)
    
    ## Add measurements (read from 'mc_local_abspath/results.json' or 'mc_local_abspath/results.csv')
    # TODO - Add measurements...

    return proc

