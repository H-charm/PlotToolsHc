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
    
    # Load WZ sample
    samples_dict = config_file.samples_dict
    samples_filenames = config_file.get_samples_filenames()
    WZ_path = os.path.join(config_file.base_dir, "WZ_final_merged.root")
    if not os.path.exists(WZ_path):
        raise FileNotFoundError(f"WZ file not found: {WZ_path}")
    wz_df = ROOT.RDataFrame("Events", WZ_path)
    wz_df = wz_df.Define("final_weight", config_file.weights)
    
    # CMS Styling Settings
    CMS.setCMSStyle
    CMS.SetExtraText("Preliminary")
    CMS.SetLumi(config_file.dataset_legend)
    CMS.SetEnergy(config_file.energy)
    CMS.ResetAdditionalInfo()

    # Get binning information from config file
    binning = None
    x_title = ""
    for var in config_file.vars:
        if var[0] == "ZLalle_pt2":
            binning = var[3]
            x_title = var[2]  # Get axis title from config
            break
    
    if not binning:
        raise ValueError("ZLalle_pt2 configuration not found in config.vars")
    
    # Process data and WZ files for both barrel and endcap regions
    def process_region(particle, cut_all, cut_pass, color, name, corr=False):
        bins_array = ROOT.std.vector("double")(binning)
        # Denominator histogram
        hist_data_all = data_df.Filter(cut_all)\
                           .Define(f"plotvar_all{particle}", f"ZLall{particle}_pt2")\
                           .Histo1D((f"hist_data_all{particle}_"+name, "", len(binning)-1, bins_array.data()), 
                                      f"plotvar_all{particle}")
        # Numerator histogram
        hist_data_pass = data_df.Filter(cut_pass)\
                            .Define(f"plotvar_pass{particle}", f"ZLpass{particle}_pt2")\
                            .Histo1D((f"hist_data_pass{particle}_"+name, "", len(binning)-1, bins_array.data()), 
                                       f"plotvar_pass{particle}")
        # Denominator correction
        hist_wz_all=wz_df.Filter(cut_all)\
                         .Define(f"plotvar_all{particle}", f"ZLall{particle}_pt2")\
                         .Histo1D((f"hist_wz_all{particle}_"+name, "", len(binning)-1, bins_array.data()), 
                                      f"plotvar_all{particle}","final_weight")
        # Numerator correction
        hist_wz_pass=wz_df.Filter(cut_pass)\
                          .Define(f"plotvar_pass{particle}", f"ZLall{particle}_pt2")\
                          .Histo1D((f"hist_wz_pass{particle}_"+name, "", len(binning)-1, bins_array.data()), 
                                      f"plotvar_pass{particle}","final_weight")

        # Add overflow
        hist_data_all = utils.add_overflow(hist_data_all.GetPtr())
        hist_data_pass = utils.add_overflow(hist_data_pass.GetPtr())
        hist_wz_all = utils.add_overflow(hist_wz_all.GetPtr())
        hist_wz_pass = utils.add_overflow(hist_wz_pass.GetPtr())

        if corr:
            # Subtract WZ contribution
            hist_data_all.Add(hist_wz_all, -1.0)
            hist_data_pass.Add(hist_wz_pass, -1.0)

        # Create Fake Rate histogram
        fr_hist = hist_data_pass.Clone("fr_hist_"+name)
        fr_hist.Divide(hist_data_all)

        # Style
        fr_hist.SetMarkerStyle(20)
        fr_hist.SetMarkerColor(color)
        fr_hist.SetLineColor(color)
        fr_hist.SetLineWidth(2)
        if corr: fr_hist.SetLineStyle(7) 
        fr_hist.GetYaxis().SetRangeUser(0, 0.35) if particle == "e" else fr_hist.GetYaxis().SetRangeUser(0, 1)
        fr_hist.GetYaxis().SetTitle("Fake Rate")
        fr_hist.GetYaxis().SetTitleSize(0.05)
        fr_hist.GetYaxis().SetLabelSize(0.05)
        fr_hist.GetYaxis().SetTitleOffset(1.5)
        fr_hist.GetXaxis().SetTitle("p_{T}(e) [GeV]") if particle == "e" else fr_hist.GetXaxis().SetTitle("p_{T}(#mu) [GeV]")
        fr_hist.GetXaxis().SetTitleSize(0.05)
        fr_hist.GetXaxis().SetLabelSize(0.05)
        fr_hist.GetXaxis().SetTitleOffset(1.2)
            
        return fr_hist

    # Create plots for both electrons and muons
    particles = ["electrons", "muons"]
    for particle in particles:
        if particle == "electrons":
            par = "e"
            cut = "1.479"
        else: 
            par = "mu"
            cut = "1.2"
        
        # Barrel cuts
        barrel_cut_all = f"ZLall{par}_eta2.size() > 0 && std::abs(ZLall{par}_eta2[0]) < {cut}"
        barrel_cut_pass = f"ZLpass{par}_eta2.size() > 0 && std::abs(ZLpass{par}_eta2[0]) < {cut}"
        
        # Endcap cuts
        endcap_cut_all = f"ZLall{par}_eta2.size() > 0 && std::abs(ZLall{par}_eta2[0]) >= {cut}"
        endcap_cut_pass = f"ZLpass{par}_eta2.size() > 0 && std::abs(ZLpass{par}_eta2[0]) >= {cut}"

        # Uncorrected fake rates
        fr_barrel = process_region(par, barrel_cut_all, barrel_cut_pass, ROOT.kBlue, "barrel")
        fr_endcap = process_region(par, endcap_cut_all, endcap_cut_pass, ROOT.kRed, "endcap")

        # Corrected fake rates (WZ subtracted)
        fr_barrel_corr = process_region(par, barrel_cut_all, barrel_cut_pass, ROOT.kBlue, "barrel_corr", corr=True)
        fr_endcap_corr = process_region(par, endcap_cut_all, endcap_cut_pass, ROOT.kRed, "endcap_corr", corr=True)

        # Create canvas
        canvas = CMS.cmsCanvas(f"fr_canvas_{particle}", binning[0], binning[-1], 0, 0.35,
                             x_title, "Fake Rate", square=CMS.kSquare, extraSpace=0.05)
        
        # Draw all four histograms
        fr_barrel.Draw("EP")
        fr_endcap.Draw("EP SAME")
        fr_barrel_corr.Draw("EP SAME")
        fr_endcap_corr.Draw("EP SAME")

        # Create legend
        legend = CMS.cmsLeg(0.6, 0.7, 0.9, 0.9, textSize=0.035, textFont=42)
        legend.AddEntry(fr_barrel, "Barrel Uncorrected", "l")
        legend.AddEntry(fr_barrel_corr, "Barrel Corrected", "l")
        legend.AddEntry(fr_endcap, "Endcap Uncorrected", "l")
        legend.AddEntry(fr_endcap_corr, "Endcap Corrected", "l")
        legend.Draw()

        # Draw Lumi and CMS text
        CMS.CMS_lumi(canvas)

        # Save plot
        output_dir = os.path.join(config_file.output_plots_dir, "fr_plots")
        os.makedirs(output_dir, exist_ok=True)
        CMS.SaveCanvas(canvas, os.path.join(output_dir, f"fr_plot_{particle}_with_correction.png"))

if __name__ == "__main__":
    start_time = time.time()
    
    config_file = config.Config()
    config_file.add_sample(name="WZ", root_file="WZ_final_merged.root",cuts=1)
    create_fr_plot(config_file)
    
    end_time = time.time()
    print(f"Elapsed time: {(end_time - start_time)/60:.2f} minutes")