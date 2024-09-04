from ctypes import util
from typing import ChainMap
import ROOT
import config_plots
import utils
import os
import argparse
import sys

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetLegendBorderSize(0)
ROOT.gStyle.SetTitleOffset(1.5, "Y") 
ROOT.gStyle.SetOptStat(0)
ROOT.gInterpreter.ProcessLine('#include "cpp_functions.C"')

def draw_mc_only():
    config_file = config_plots.Config()
    print(f"**** Making MC-only plots ****")

    output_dir = config_file.output_plots_dir + "MC_Only_Plots/"
    if not os.path.exists(output_dir): 
        os.makedirs(output_dir)

    ## Add MC samples using new ROOT trees
    config_file.add_sample(name="DYJets", root_file="DYJets_tree.root", cuts=utils.sample_cuts_dict[""])
    config_file.add_sample(name="VBF", root_file="VBF_tree.root", cuts=utils.sample_cuts_dict[""])
    config_file.add_sample(name="WminusH", root_file="WminusH_tree.root", cuts=utils.sample_cuts_dict[""])
    config_file.add_sample(name="WplusH", root_file="WplusH_tree.root", cuts=utils.sample_cuts_dict[""])
    config_file.add_sample(name="ZH", root_file="ZH_tree.root", cuts=utils.sample_cuts_dict[""])
    config_file.add_sample(name="ZZ", root_file="ZZ_tree.root", cuts=utils.sample_cuts_dict[""])
    config_file.add_sample(name="bbH", root_file="bbH_tree.root", cuts=utils.sample_cuts_dict[""])
    config_file.add_sample(name="ggH", root_file="ggH_tree.root", cuts=utils.sample_cuts_dict[""])
    config_file.add_sample(name="tqH", root_file="tqH_tree.root", cuts=utils.sample_cuts_dict[""])
    config_file.add_sample(name="ttH", root_file="ttH_tree.root", cuts=utils.sample_cuts_dict[""])

    samples = config_file.get_samples_list()
    config_file.print_samples_info()
                
    for branch in config_file.mcdata_branches:
        print(f"=== branch {branch[0]} ===")

        hs_bkg = ROOT.THStack("hs_bkg_" + branch[0], ";" + branch[2] + ";Events")
        leg = ROOT.TLegend(0.55,0.69,0.88,0.87) # Adjusted legend position and size
        leg.SetNColumns(2)
        leg.SetTextFont(62)
        leg.SetTextSize(0.025)  # Reduced text size

       

        ## MC samples
        mc_histos = []
        for sample_name in samples:
            sample_filename = samples[sample_name][0]
            sample_cuts = samples[sample_name][1]
            h = utils.get_histogram(sample_name=sample_name, filename=sample_filename, branch=branch, channel=None, sample_cuts=sample_cuts)
            h = h.Clone() # needed for RDF histos
            h = utils.add_overflow(h)
            mc_histos.append(h)
            leg.AddEntry(h, config_file.legend[sample_name], "f")
        
        ## Fill stack with MC histograms
        [hs_bkg.Add(hist) for hist in mc_histos] 
        
        # Create the stacked plot without data
        utils.make_mc_only_plot(stack_hists=hs_bkg, channel=None, branch=branch, leg=leg, output_dir=output_dir)

if __name__ == "__main__":
    ## parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--mconly', help='MC-only comparison', action='store_true')
    args = parser.parse_args()

    config_file = config_plots.Config()
    print(f"Base_dir: {config_file.base_dir}")

    if args.mconly: 
        draw_mc_only()
        
    print("============ DONE ============")

