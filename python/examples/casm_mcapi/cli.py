import argparse

casm_name = "casm"
casm_desc = "Create CASM samples, processes, measurements, etc."

prim_help = "Upload CASM Primitive Crystal Structure sample"
composition_help = "Upload CASM Composition Axes sample"
clex_help = "Upload CASM Cluster Expansion sample"
mc_help = "Upload CASM Monte Carlo process"

def casm_subcommand():
    parser = argparse.ArgumentParser(description = 'Upload CASM data to Materials Commons')
    parser.add_argument('--prim', help=prim_help, action="store_true", default=False)
    parser.add_argument('--composition', help=composition_help, action="store_true", default=False)
    parser.add_argument('--clex', help=clex_help, action="store_true", default=False)
    parser.add_argument('--mc', help=mc_help, action="store_true", default=False)
    args = parser.parse_args()
    
    # ignore 'mc casm'
    args = parser.parse_args(sys.argv[2:])
    
    
    
    

