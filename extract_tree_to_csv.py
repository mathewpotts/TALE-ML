#!/usr/bin/python3

import ROOT
import argparse
import math

def extract_tree_to_csv(input_file, tree_name, output_file, branches):
    # Open the ROOT file
    root_file = ROOT.TFile.Open(input_file)
    if not root_file or root_file.IsZombie():
        print("Error: Cannot open ROOT file", input_file)
        return
    
    # Get the tree from the file
    tree = root_file.Get(tree_name)
    if not tree:
        print("Error: Cannot find tree", tree_name, "in the ROOT file")
        root_file.Close()
        return

    # Create CSV file
    csv_file = open(output_file, 'w')

    # Write header
    csv_file.write(','.join(branches) + '\n')

    # Loop over the tree entries and extract values
    special_branches = ['mir_ngtube','mir_id','mir_nmir'] # branches that need a index of 0 not iminc
    i = 0 # event number
    for entry in tree:
        values = []
        es = True
        iminc = entry.GetLeaf("iminc").GetValue()
        for branch in branches:
            if branch in special_branches:
                iminc = 0
            if iminc == 0 and branch not in special_branches: # reset iminc to its value when not using special_branches
                iminc = entry.GetLeaf("iminc").GetValue()
            print("Evt: ", i, "branch: ", branch, " ,iminc: ", iminc)
            value = entry.GetLeaf(branch).GetValue(int(iminc))
            if math.isnan(value): # if nan value is present break out of loop and don't include event
                es = False
                break
            print("value: ", value)
            values.append(str(value))
        if es: # if branch for loop isn't ended prematurely, write row to csv file
            csv_file.write(','.join(values) + '\n')
        i = i + 1 # add to event counter

    # Close files and cleanup
    csv_file.close()
    root_file.Close()

if __name__ == "__main__":
    # Define user inputs
    par = argparse.ArgumentParser(description='Program designed to extract ROOT tree values out of a flat tree.',
                                  epilog='Author: Mathew Potts, Last Updated: 02/14/2024')
    par.add_argument('-infile',
                     metavar='infile.root',
                     help='Input ROOT filename. (Ex: /path/to/input.root)')
    par.add_argument('-outfile',
                     metavar='outfile.csv',
                     help='Output CSV filename. (Ex: /path/to/output.csv)')

    # Grab user inputs
    args = par.parse_args()
    #print(args)
    
    # Input ROOT file and tree name
    input_file = args.infile
    tree_name = "mdps5"

    # Output CSV file
    output_file = args.outfile

    # List of branches to extract
    # note for later use the pass2 signals from tubes to train model instead of what is below
    branches_to_extract = [
        # Branch: ps4fit
        "xcore", # xcore
        "ycore", # ycore
        "th",    # shower track zenith angle
        "phi",   # azimuthal angle
        "rp",    # magnitude of rp vector
        "psi",   # psi angle
        "en",    # shower energy (EeV)
        "x0",    # G-H fit parameter (g/cm^2)
        "xf",    # depth of first seen point
        "xm",    # depth of shower max
        "dxm",   # error on the xmax
        "c2t",   # X^2 on timing fit
        "c2p",   # X^2 on profile fit
        "xl",    # depth of last seen point ( xl-xf = tracklength (g/cm^2) )
        "sz",    # shower size/1e9 
        "fscin", # % scintillation light
        "fckov", # % cherenkov light
        "fscat", # % Scattered light
        # Branch: mir_view
        "mir_id",    # Mirror ID
        "mir_nmir",  # Number of mirrors in event
        "mir_ngtube",# Number of good tubes in event
        # Branch: ps4fit
        "ra",    # RA
        "dec",   # Dec
        # Branch: ps4mc
        "mcip"   # primary id: 1=proton, 2=iron, 3=photon, 4=helium, 5=nitrogen
    ]

    # Call function to extract tree to CSV
    extract_tree_to_csv(input_file, tree_name, output_file, branches_to_extract)
