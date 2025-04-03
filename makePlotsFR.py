import ROOT
import argparse
import os
import config
import time
import utils
import cmsstyle as CMS

ROOT.ROOT.EnableImplicitMT()
ROOT.gInterpreter.ProcessLine('#include "cpp_functions.C"')
ROOT.gROOT.SetBatch(True)

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--data', type=str, help='Path to data files directory', required=True)
args = parser.parse_args()

DATA_FILES = [
    "DoubleMuon_merged.root",
    "SingleMuon_merged.root",
    "EGamma_merged.root",
    "MuonEG_merged.root",
    "Muon_merged.root"
]

def merge_data_RDF():
    """Create a single RDataFrame from multiple ROOT data files."""
    file_paths = [os.path.join(args.data, f) for f in DATA_FILES]
    return ROOT.RDataFrame("Events", file_paths)

def create_fr_plot(config_file):
    # Load and merge data
    print("Loading and merging real data...")
    data_df = merge_data_RDF()
    
    # CMS Styling Settings
    CMS.SetExtraText("Preliminary")
    CMS.SetLumi(config_file.dataset_legend)
    CMS.SetEnergy(config_file.energy)
    CMS.ResetAdditionalInfo()
    
    # Get binning information from config
    binning = None
    x_title = ""
    for var in config_file.vars:
        if var[0] == "ZLalle_pt2":
            binning = var[3]
            x_title = var[2]  # Get axis title from config
            break
    
    if not binning:
        raise ValueError("ZLalle_pt2 configuration not found in config.vars")

    # Create histograms
    bins_array = ROOT.std.vector("double")(binning)
    
    # Denominator histogram (ZLalle_pt2)
    hist_alle = data_df.Filter(config_file.cuts)\
                       .Define("plotvar_alle", "ZLalle_pt2")\
                       .Histo1D(("hist_alle", "", len(binning)-1, bins_array.data()), 
                       "plotvar_alle")
    
    # Numerator histogram (ZLpasse_pt2)
    hist_passe = data_df.Filter(config_file.cuts)\
                        .Define("plotvar_passe", "ZLpasse_pt2")\
                        .Histo1D(("hist_passe", "", len(binning)-1, bins_array.data()), 
                        "plotvar_passe")

    # Add overflow
    hist_alle = utils.add_overflow(hist_alle.GetPtr())
    hist_passe = utils.add_overflow(hist_passe.GetPtr())

    # Create Fake Rate histogram
    fr_hist = hist_passe.Clone("fr_hist")
    fr_hist.Divide(hist_alle)
    
    # Create canvas
    x_min, x_max = binning[0], binning[-1]
    canvas = CMS.cmsCanvas("fr_canvas", x_min, x_max, 0, 0.35, 
                          x_title, "Fake Rate", 
                          square=CMS.kSquare, extraSpace=0.05)

    # Style the histogram
    fr_hist.SetMarkerStyle(20)
    fr_hist.SetMarkerColor(ROOT.kBlack)
    fr_hist.SetLineColor(ROOT.kBlack)
    fr_hist.SetLineWidth(2)

    fr_hist.GetYaxis().SetRangeUser(0, 0.35)
    
    # Draw the histogram
    fr_hist.Draw("EP")
   
    # Save plot
    output_dir = os.path.join(config_file.output_plots_dir, "fr_plots")
    os.makedirs(output_dir, exist_ok=True)
    CMS.SaveCanvas(canvas, os.path.join(output_dir, f"fake_rate.{config_file.plot_format}"))

if __name__ == "__main__":
    start_time = time.time()
    
    config_file = config.Config()
    create_fr_plot(config_file)
    
    end_time = time.time()
    print(f"Elapsed time: {(end_time - start_time)/60:.2f} minutes")