import ROOT
import argparse
import os
import math
import array
import config
import utils
import time

ROOT.ROOT.EnableImplicitMT()
ROOT.gInterpreter.ProcessLine('#include "cpp_functions.C"')
ROOT.gROOT.SetBatch(True)

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--data', type=str, help='Path to data files directory', required=True)
args = parser.parse_args()

pt_bins = [5, 7, 10, 15, 20, 25, 30, 40, 60, 100]
flavors = {"e": "electron", "mu": "muon"}
regions = {"barrel": 0.5, "endcap": 1.5}

def remove_negative_bins(hist):
    for i in range(1, hist.GetNbinsX() + 1):  # bins start at 1
        if hist.GetBinContent(i) < 0:
            hist.SetBinContent(i, 0)


def merge_data_RDF(data_files):
    file_paths = [os.path.join(args.data, f) for f in data_files]
    return ROOT.RDataFrame("Events", file_paths)

def process_region(particle, cut_all, cut_pass, name, binning, data_df, wz_df, weight_expr, correct_wz=False):
    bins_array = ROOT.std.vector("double")(binning)

    hist_data_all = data_df.Filter(cut_all)\
        .Define(f"plotvar_all{particle}", f"ZLall{particle}_pt2")\
        .Histo1D((f"hist_data_all{particle}_{name}", "", len(binning)-1, bins_array.data()), 
                 f"plotvar_all{particle}")
    
    hist_data_pass = data_df.Filter(cut_pass)\
        .Define(f"plotvar_pass{particle}", f"ZLpass{particle}_pt2")\
        .Histo1D((f"hist_data_pass{particle}_{name}", "", len(binning)-1, bins_array.data()), 
                 f"plotvar_pass{particle}")

    hist_wz_all = wz_df.Filter(cut_all)\
        .Define(f"plotvar_all{particle}", f"ZLall{particle}_pt2")\
        .Histo1D((f"hist_wz_all{particle}_{name}", "", len(binning)-1, bins_array.data()), 
                 f"plotvar_all{particle}", weight_expr)
    
    hist_wz_pass = wz_df.Filter(cut_pass)\
        .Define(f"plotvar_pass{particle}", f"ZLall{particle}_pt2")\
        .Histo1D((f"hist_wz_pass{particle}_{name}", "", len(binning)-1, bins_array.data()), 
                 f"plotvar_pass{particle}", weight_expr)

    hist_data_all = utils.add_overflow(hist_data_all.GetPtr())
    hist_data_pass = utils.add_overflow(hist_data_pass.GetPtr())
    hist_wz_all = utils.add_overflow(hist_wz_all.GetPtr())
    hist_wz_pass = utils.add_overflow(hist_wz_pass.GetPtr())

    if correct_wz:
        hist_data_all.Add(hist_wz_all, -1.0)
        hist_data_pass.Add(hist_wz_pass, -1.0)

    hist2D_all = ROOT.TH2F(f"denominator_{particle}_{name}", "", 
                           len(binning)-1, bins_array.data(), 2, 0, 2)
    hist2D_pass = ROOT.TH2F(f"passing_{particle}_{name}", "", 
                            len(binning)-1, bins_array.data(), 2, 0, 2)

    for i in range(1, hist_data_all.GetNbinsX() + 1):
        pt_center = hist_data_all.GetBinCenter(i)
        ybin = 0.5 if "barrel" in name else 1.5
        val_all = hist_data_all.GetBinContent(i)
        val_pass = hist_data_pass.GetBinContent(i)

        hist2D_all.Fill(pt_center, ybin, val_all)
        hist2D_pass.Fill(pt_center, ybin, val_pass)

    return hist2D_all, hist2D_pass

def save_histograms(hist_dict, output_file):
    fout = ROOT.TFile(output_file, "RECREATE")
    for group in hist_dict.values():
        for region_hist in group.values():
            region_hist.Write()
    fout.Close()

def get_xbin_range(hist, low, high):
    xaxis = hist.GetXaxis()
    return xaxis.FindBin(low), xaxis.FindBin(high) - 1

def make_graph(name, h_pass, h_all, pt_bins, y_val):
    x_vals = []
    y_vals = []
    ex_vals = []
    ey_vals = []

    for i in range(len(pt_bins) - 1):
        pt_low = pt_bins[i]
        pt_high = pt_bins[i+1]
        if name.startswith("electron") and pt_low == 5:
            continue

        xbin1, xbin2 = get_xbin_range(h_pass, pt_low, pt_high)
        ybin = h_pass.GetYaxis().FindBin(y_val)

        np, np_err2 = 0, 0
        na, na_err2 = 0, 0

        for xbin in range(xbin1, xbin2 + 1):
            np_bin = h_pass.GetBinContent(xbin, ybin)
            na_bin = h_all.GetBinContent(xbin, ybin)
            np_err2 += h_pass.GetBinError(xbin, ybin) ** 2
            na_err2 += h_all.GetBinError(xbin, ybin) ** 2
            np += np_bin
            na += na_bin

        if na > 0:
            fr = np / na
            err = math.sqrt((na / (na**2))**2 * np_err2 + (np / (na**2))**2 * na_err2)
            x_center = (pt_low + pt_high) / 2
            x_width = (pt_high - pt_low) / 2

            x_vals.append(x_center)
            ex_vals.append(x_width)
            y_vals.append(fr)
            ey_vals.append(err)

    graph = ROOT.TGraphErrors(
        len(x_vals),
        array.array('d', x_vals),
        array.array('d', y_vals),
        array.array('d', ex_vals),
        array.array('d', ey_vals)
    )
    graph.SetName(name)
    return graph

def main():
    start_time = time.time()

    config_file = config.Config()
    config_file.add_sample(name="WZ", root_file="WZ_final_merged.root", cuts=1)

    data_files = ["EGamma_merged.root", "MuonEG_merged.root", "Muon_merged.root"]
    if "2022" in os.path.normpath(config_file.base_dir).split(os.sep):
        data_files += ["DoubleMuon_merged.root", "SingleMuon_merged.root"]

    data_df = merge_data_RDF(data_files)
    wz_df = ROOT.RDataFrame("Events", os.path.join(config_file.base_dir, "WZ_final_merged.root"))\
              .Define("final_weight", config_file.weights)

    for var in config_file.vars:
        if var[0] == "ZLallmu_pt2":
            binning = var[3]
            break
    else:
        raise ValueError("ZLallmu_pt2 configuration not found in config.vars")

    passing_hists, denominator_hists = {}, {}

    for particle in ["electrons", "muons"]:
        par = "e" if particle == "electrons" else "mu"
        cut = "1.479" if par == "e" else "1.2"

        barrel_all_cut = f"ZLall{par}_eta2.size() > 0 && abs(ZLall{par}_eta2[0]) < {cut}"
        barrel_pass_cut = f"ZLpass{par}_eta2.size() > 0 && abs(ZLpass{par}_eta2[0]) < {cut}"
        endcap_all_cut = f"ZLall{par}_eta2.size() > 0 && abs(ZLall{par}_eta2[0]) >= {cut}"
        endcap_pass_cut = f"ZLpass{par}_eta2.size() > 0 && abs(ZLpass{par}_eta2[0]) >= {cut}"

        den_barrel, pass_barrel = process_region(par, barrel_all_cut, barrel_pass_cut, "barrel", binning, data_df, wz_df, "final_weight", correct_wz=True)
        den_endcap, pass_endcap = process_region(par, endcap_all_cut, endcap_pass_cut, "endcap", binning, data_df, wz_df, "final_weight", correct_wz=True)

        denominator_hists.setdefault(par, {})["barrel"] = den_barrel
        passing_hists.setdefault(par, {})["barrel"] = pass_barrel
        denominator_hists[par]["endcap"] = den_endcap
        passing_hists[par]["endcap"] = pass_endcap

    os.makedirs("fr_histos", exist_ok=True)
    save_histograms(passing_hists, "fr_histos/passing_hists.root")
    save_histograms(denominator_hists, "fr_histos/denominator_hists.root")

    passing_file = ROOT.TFile("fr_histos/passing_hists.root")
    denominator_file = ROOT.TFile("fr_histos/denominator_hists.root")
    fout = ROOT.TFile("fr_graphs.root", "RECREATE")

    for flav_key, flav_name in flavors.items():
        for region_key, y_val in regions.items():
            h_pass = passing_file.Get(f"passing_{flav_key}_{region_key}")
            h_all = denominator_file.Get(f"denominator_{flav_key}_{region_key}")
            graph_name = f"FR_OS_{flav_name}_{'EB' if region_key == 'barrel' else 'EE'}"
            graph = make_graph(graph_name, h_pass, h_all, pt_bins, y_val)
            graph.Write()

    fout.Close()
    print("[INFO] Fake Rate graphs saved to fr_graphs.root")
    print(f"[INFO] Total elapsed time: {(time.time() - start_time)/60:.2f} min")

if __name__ == "__main__":
    main()
