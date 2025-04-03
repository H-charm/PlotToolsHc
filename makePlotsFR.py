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

    # Cuts for electrons
    barrel_cut_all_electrons = "ZLalle_eta2.size() > 0 && std::abs(ZLalle_eta2[0]) < 0.83"
    endcap_cut_all_electrons = "ZLalle_eta2.size() > 0 && std::abs(ZLalle_eta2[0]) >= 0.83"
    barrel_cut_pass_electrons = "ZLpasse_eta2.size() > 0 && std::abs(ZLpasse_eta2[0]) < 0.83"
    endcap_cut_pass_electrons = "ZLpasse_eta2.size() > 0 && std::abs(ZLpasse_eta2[0]) >= 0.83"
    # Cuts for muons
    barrel_cut_all_muons = "ZLallmu_eta2.size() > 0 && std::abs(ZLallmu_eta2[0]) < 0.83"
    endcap_cut_all_muons = "ZLallmu_eta2.size() > 0 && std::abs(ZLallmu_eta2[0]) >= 0.83"
    barrel_cut_pass_muons = "ZLpassmu_eta2.size() > 0 && std::abs(ZLpassmu_eta2[0]) < 0.83"
    endcap_cut_pass_muons = "ZLpassmu_eta2.size() > 0 && std::abs(ZLpassmu_eta2[0]) >= 0.83"

    
    # Create histograms for different regions
    def process_region(particle, cut_all, cut_pass, color, name):
        bins_array = ROOT.std.vector("double")(binning)
        
        # Denominator histogram
        hist_all = data_df.Filter(cut_all)\
                           .Define(f"plotvar_all{particle}", f"ZLall{particle}_pt2")\
                           .Histo1D((f"hist_all{particle}_"+name, "", len(binning)-1, bins_array.data()), 
                                      f"plotvar_all{particle}")
        
        # Numerator histogram
        hist_pass = data_df.Filter(cut_pass)\
                            .Define(f"plotvar_pass{particle}", f"ZLpass{particle}_pt2")\
                            .Histo1D((f"hist_pass{particle}_"+name, "", len(binning)-1, bins_array.data()), 
                                       f"plotvar_pass{particle}")

        # Add overflow
        hist_all = utils.add_overflow(hist_all.GetPtr())
        hist_pass = utils.add_overflow(hist_pass.GetPtr())

        # Create Fake Rate histogram
        fr_hist = hist_pass.Clone("fr_hist_"+name)
        fr_hist.Divide(hist_all)
        
        # Style
        fr_hist.SetMarkerStyle(20)
        fr_hist.SetMarkerColor(color)
        fr_hist.SetLineColor(color)
        fr_hist.SetLineWidth(2)
        fr_hist.GetYaxis().SetRangeUser(0, 0.35)
        
        return fr_hist

    particles = ["electrons", "muons"]  # Ensure these are strings
    fr_barrel = {}
    fr_endcap = {}
    canvases = {}

    for particle in particles:
        # Assign particle parameters
        par = "e" if particle == "electrons" else "mu"  # Ensure `e` and `mu` are defined
        
        barrel_cut_all = f"ZLall{par}_eta2.size() > 0 && std::abs(ZLall{par}_eta2[0]) < 0.83"
        endcap_cut_all = f"ZLall{par}_eta2.size() > 0 && std::abs(ZLall{par}_eta2[0]) >= 0.83"
        barrel_cut_pass = f"ZLpass{par}_eta2.size() > 0 && std::abs(ZLpass{par}_eta2[0]) < 0.83"
        endcap_cut_pass = f"ZLpass{par}_eta2.size() > 0 && std::abs(ZLpass{par}_eta2[0]) >= 0.83"
        
        # Process regions
        fr_barrel[particle] = process_region(par, barrel_cut_all, barrel_cut_pass, ROOT.kBlue, "barrel")
        fr_endcap[particle] = process_region(par, endcap_cut_all, endcap_cut_pass, ROOT.kRed, "endcap")
        
        # Create canvas
        x_min, x_max = binning[0], binning[-1]
        canvases[particle] = CMS.cmsCanvas(
            f"fr_canvas_{particle}", x_min, x_max, 0, 0.35, 
            x_title, "Fake Rate", 
            square=CMS.kSquare, extraSpace=0.05
        )
        
        # Draw histograms
        fr_barrel[particle].Draw("EP")
        fr_endcap[particle].Draw("EP SAME")
        
        # Add legend
        legend = ROOT.TLegend(0.6, 0.75, 0.85, 0.85)
        legend.SetBorderSize(0)
        legend.SetTextSize(0.04)
        legend.AddEntry(fr_barrel[particle], "Barrel (|#eta| < 0.83)", "lep")
        legend.AddEntry(fr_endcap[particle], "Endcap (|#eta| #geq 0.83)", "lep")
        legend.Draw()
        
        # Save plot
        output_dir = os.path.join(config_file.output_plots_dir, "fr_plots")
        os.makedirs(output_dir, exist_ok=True)
        CMS.SaveCanvas(canvases[particle], os.path.join(output_dir, f"fr_plot_{particle}.png"))

if __name__ == "__main__":
    start_time = time.time()
    
    config_file = config.Config()
    create_fr_plot(config_file)
    
    end_time = time.time()
    print(f"Elapsed time: {(end_time - start_time)/60:.2f} minutes")