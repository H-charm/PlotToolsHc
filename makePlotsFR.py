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
    variables_all_e = config_file.vars_all_e
    variables_pass_e = config_file.vars_pass_e
    variables_all_mu = config_file.vars_all_mu
    variables_pass_mu = config_file.vars_pass_mu
    
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

    barrel_cut_all_e = f"ZLalle_eta2.size() > 0 && std::abs(ZLalle_eta2[0]) < 1.479"
    endcap_cut_all_e = f"ZLalle_eta2.size() > 0 && std::abs(ZLalle_eta2[0]) >= 1.479"

    barrel_cut_all_mu = f"ZLallmu_eta2.size() > 0 && std::abs(ZLallmu_eta2[0]) < 1.2"
    endcap_cut_all_mu = f"ZLallmu_eta2.size() > 0 && std::abs(ZLallmu_eta2[0]) >= 1.2"

    barrel_cut_pass_e = f"ZLpasse_eta2.size() > 0 && std::abs(ZLpasse_eta2[0]) < 1.479"
    endcap_cut_pass_e = f"ZLpasse_eta2.size() > 0 && std::abs(ZLpasse_eta2[0]) >= 1.479"

    barrel_cut_pass_mu = f"ZLpassmu_eta2.size() > 0 && std::abs(ZLpassmu_eta2[0]) < 1.2"
    endcap_cut_pass_mu = f"ZLpassmu_eta2.size() > 0 && std::abs(ZLpassmu_eta2[0]) >= 1.2"

    # Loop for each variable
    for variable in variables_all_e:
        print(f"Plotting var {variable[0]}")
        data_histos_barrel = {}
        data_histos_endcap = {}

        if isinstance(variable[3], list):  # Variable binning
            bins_array = ROOT.std.vector("double")(variable[3])
            data_hist_barrel = data_df.Filter(barrel_cut_all_e).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_data_{variable[0]}", "", len(variable[3]) - 1, bins_array.data()), 
                "plotvar_"
            )
        else:  # Uniform binning
            data_hist_barrel = data_df.Filter(barrel_cut_all_e).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_data_{variable[0]}", "", variable[3], variable[4], variable[5]), 
                "plotvar_"
            )

        if isinstance(variable[3], list):  # Variable binning
            bins_array = ROOT.std.vector("double")(variable[3])
            data_hist_endcap = data_df.Filter(endcap_cut_all_e).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_data_{variable[0]}", "", len(variable[3]) - 1, bins_array.data()), 
                "plotvar_"
            )
        else:  # Uniform binning
            data_hist_endcap = data_df.Filter(endcap_cut_all_e).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_data_{variable[0]}", "", variable[3], variable[4], variable[5]), 
                "plotvar_"
            )

        data_hist_barrel = utils.add_overflow(data_hist_barrel)
        data_histos_barrel[variable[0]] = data_hist_barrel.GetPtr()

        data_hist_endcap = utils.add_overflow(data_hist_endcap)
        data_histos_endcap[variable[0]] = data_hist_endcap.GetPtr()

        data_hist_barrel.SetMarkerStyle(20)
        data_hist_barrel.SetMarkerColor(ROOT.kBlue)
        data_hist_barrel.SetLineColor(ROOT.kBlue)
        data_hist_barrel.SetLineWidth(2)

        canv_name_barrel = f"{variable[1]}_canvas_barrel"
        canv_name_endcap = f"{variable[1]}_canvas_endcap"
        y_title = "Events"
        if isinstance(variable[3], list):  # Variable binning
            x_min, x_max = variable[3][0], variable[3][-1]  # Use first and last bin edge
        else:  # Uniform binning
            x_min, x_max = variable[4], variable[5]  # Use configured range
        canvas_barrel = CMS.cmsCanvas(canv_name_barrel, x_min, x_max, 0, 10000, variable[2], y_title, square=CMS.kSquare, extraSpace=0.05, iPos=0)
        
        data_hist_barrel.Draw()

        output_dir = os.path.join(config_file.output_plots_dir, "debug_plots")
        os.makedirs(output_dir, exist_ok=True)
        CMS.SaveCanvas(canvas_barrel, os.path.join(output_dir, f"All_electrons_barrel_{variable[1]}.png"))

        canvas_endcap = CMS.cmsCanvas(canv_name_endcap, x_min, x_max, 0, 10000, variable[2], y_title, square=CMS.kSquare, extraSpace=0.05, iPos=0)

        data_hist_endcap.SetMarkerStyle(20)
        data_hist_endcap.SetMarkerColor(ROOT.kRed)
        data_hist_endcap.SetLineColor(ROOT.kRed)
        data_hist_endcap.SetLineWidth(2)

        data_hist_endcap.Draw()

        output_dir = os.path.join(config_file.output_plots_dir, "debug_plots")
        os.makedirs(output_dir, exist_ok=True)
        CMS.SaveCanvas(canvas_endcap, os.path.join(output_dir, f"All_electrons_endcap_{variable[1]}.png"))

    # PASSED ELECTRONS
    for variable in variables_pass_e:
        print(f"Plotting var {variable[0]} (passed electrons)")
        data_histos_barrel = {}
        data_histos_endcap = {}

        if isinstance(variable[3], list):
            bins_array = ROOT.std.vector("double")(variable[3])
            data_hist_barrel = data_df.Filter(barrel_cut_pass_e).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_data_pass_{variable[0]}", "", len(variable[3]) - 1, bins_array.data()), 
                "plotvar_"
            )
        else:
            data_hist_barrel = data_df.Filter(barrel_cut_pass_e).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_data_pass_{variable[0]}", "", variable[3], variable[4], variable[5]), 
                "plotvar_"
            )

        if isinstance(variable[3], list):
            bins_array = ROOT.std.vector("double")(variable[3])
            data_hist_endcap = data_df.Filter(endcap_cut_pass_e).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_data_pass_{variable[0]}", "", len(variable[3]) - 1, bins_array.data()), 
                "plotvar_"
            )
        else:
            data_hist_endcap = data_df.Filter(endcap_cut_pass_e).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_data_pass_{variable[0]}", "", variable[3], variable[4], variable[5]), 
                "plotvar_"
            )

        data_hist_barrel = utils.add_overflow(data_hist_barrel)
        data_histos_barrel[variable[0]] = data_hist_barrel.GetPtr()

        data_hist_endcap = utils.add_overflow(data_hist_endcap)
        data_histos_endcap[variable[0]] = data_hist_endcap.GetPtr()

        data_hist_barrel.SetMarkerStyle(21)
        data_hist_barrel.SetMarkerColor(ROOT.kGreen + 2)
        data_hist_barrel.SetLineColor(ROOT.kGreen + 2)
        data_hist_barrel.SetLineWidth(2)

        canv_name_barrel = f"{variable[1]}_canvas_barrel_pass"
        canv_name_endcap = f"{variable[1]}_canvas_endcap_pass"
        y_title = "Events"
        if isinstance(variable[3], list):
            x_min, x_max = variable[3][0], variable[3][-1]
        else:
            x_min, x_max = variable[4], variable[5]

        canvas_barrel = CMS.cmsCanvas(canv_name_barrel, x_min, x_max, 0, 10000, variable[2], y_title, square=CMS.kSquare, extraSpace=0.05, iPos=0)
        data_hist_barrel.Draw()
        CMS.SaveCanvas(canvas_barrel, os.path.join(output_dir, f"Passed_electrons_barrel_{variable[1]}.png"))

        canvas_endcap = CMS.cmsCanvas(canv_name_endcap, x_min, x_max, 0, 10000, variable[2], y_title, square=CMS.kSquare, extraSpace=0.05, iPos=0)
        data_hist_endcap.SetMarkerStyle(21)
        data_hist_endcap.SetMarkerColor(ROOT.kMagenta + 1)
        data_hist_endcap.SetLineColor(ROOT.kMagenta + 1)
        data_hist_endcap.SetLineWidth(2)
        data_hist_endcap.Draw()
        CMS.SaveCanvas(canvas_endcap, os.path.join(output_dir, f"Passed_electrons_endcap_{variable[1]}.png"))

    # ALL MUONS
    for variable in variables_all_mu:
        print(f"Plotting var {variable[0]} (all muons)")
        data_histos_barrel = {}
        data_histos_endcap = {}

        if isinstance(variable[3], list):
            bins_array = ROOT.std.vector("double")(variable[3])
            data_hist_barrel = data_df.Filter(barrel_cut_all_mu).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_data_allmu_{variable[0]}", "", len(variable[3]) - 1, bins_array.data()), 
                "plotvar_"
            )
        else:
            data_hist_barrel = data_df.Filter(barrel_cut_all_mu).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_data_allmu_{variable[0]}", "", variable[3], variable[4], variable[5]), 
                "plotvar_"
            )

        if isinstance(variable[3], list):
            bins_array = ROOT.std.vector("double")(variable[3])
            data_hist_endcap = data_df.Filter(endcap_cut_all_mu).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_data_allmu_{variable[0]}", "", len(variable[3]) - 1, bins_array.data()), 
                "plotvar_"
            )
        else:
            data_hist_endcap = data_df.Filter(endcap_cut_all_mu).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_data_allmu_{variable[0]}", "", variable[3], variable[4], variable[5]), 
                "plotvar_"
            )

        data_hist_barrel = utils.add_overflow(data_hist_barrel)
        data_histos_barrel[variable[0]] = data_hist_barrel.GetPtr()

        data_hist_endcap = utils.add_overflow(data_hist_endcap)
        data_histos_endcap[variable[0]] = data_hist_endcap.GetPtr()

        data_hist_barrel.SetMarkerStyle(22)
        data_hist_barrel.SetMarkerColor(ROOT.kOrange + 7)
        data_hist_barrel.SetLineColor(ROOT.kOrange + 7)
        data_hist_barrel.SetLineWidth(2)

        canv_name_barrel = f"{variable[1]}_canvas_barrel_allmu"
        canv_name_endcap = f"{variable[1]}_canvas_endcap_allmu"
        y_title = "Events"
        if isinstance(variable[3], list):
            x_min, x_max = variable[3][0], variable[3][-1]
        else:
            x_min, x_max = variable[4], variable[5]

        canvas_barrel = CMS.cmsCanvas(canv_name_barrel, x_min, x_max, 0, 10000, variable[2], y_title, square=CMS.kSquare, extraSpace=0.05, iPos=0)
        data_hist_barrel.Draw()
        CMS.SaveCanvas(canvas_barrel, os.path.join(output_dir, f"All_muons_barrel_{variable[1]}.png"))

        canvas_endcap = CMS.cmsCanvas(canv_name_endcap, x_min, x_max, 0, 10000, variable[2], y_title, square=CMS.kSquare, extraSpace=0.05, iPos=0)
        data_hist_endcap.SetMarkerStyle(22)
        data_hist_endcap.SetMarkerColor(ROOT.kCyan + 1)
        data_hist_endcap.SetLineColor(ROOT.kCyan + 1)
        data_hist_endcap.SetLineWidth(2)
        data_hist_endcap.Draw()
        CMS.SaveCanvas(canvas_endcap, os.path.join(output_dir, f"All_muons_endcap_{variable[1]}.png"))

    # PASSED MUONS
    for variable in variables_pass_mu:
        print(f"Plotting var {variable[0]} (passed muons)")
        data_histos_barrel = {}
        data_histos_endcap = {}

        if isinstance(variable[3], list):
            bins_array = ROOT.std.vector("double")(variable[3])
            data_hist_barrel = data_df.Filter(barrel_cut_pass_mu).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_data_passmu_{variable[0]}", "", len(variable[3]) - 1, bins_array.data()), 
                "plotvar_"
            )
        else:
            data_hist_barrel = data_df.Filter(barrel_cut_pass_mu).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_data_passmu_{variable[0]}", "", variable[3], variable[4], variable[5]), 
                "plotvar_"
            )

        if isinstance(variable[3], list):
            bins_array = ROOT.std.vector("double")(variable[3])
            data_hist_endcap = data_df.Filter(endcap_cut_pass_mu).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_data_passmu_{variable[0]}", "", len(variable[3]) - 1, bins_array.data()), 
                "plotvar_"
            )
        else:
            data_hist_endcap = data_df.Filter(endcap_cut_pass_mu).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_data_passmu_{variable[0]}", "", variable[3], variable[4], variable[5]), 
                "plotvar_"
            )

        data_hist_barrel = utils.add_overflow(data_hist_barrel)
        data_histos_barrel[variable[0]] = data_hist_barrel.GetPtr()

        data_hist_endcap = utils.add_overflow(data_hist_endcap)
        data_histos_endcap[variable[0]] = data_hist_endcap.GetPtr()

        data_hist_barrel.SetMarkerStyle(23)
        data_hist_barrel.SetMarkerColor(ROOT.kViolet - 5)
        data_hist_barrel.SetLineColor(ROOT.kViolet - 5)
        data_hist_barrel.SetLineWidth(2)

        canv_name_barrel = f"{variable[1]}_canvas_barrel_passmu"
        canv_name_endcap = f"{variable[1]}_canvas_endcap_passmu"
        y_title = "Events"
        if isinstance(variable[3], list):
            x_min, x_max = variable[3][0], variable[3][-1]
        else:
            x_min, x_max = variable[4], variable[5]

        canvas_barrel = CMS.cmsCanvas(canv_name_barrel, x_min, x_max, 0, 10000, variable[2], y_title, square=CMS.kSquare, extraSpace=0.05, iPos=0)
        data_hist_barrel.Draw()
        CMS.SaveCanvas(canvas_barrel, os.path.join(output_dir, f"Passed_muons_barrel_{variable[1]}.png"))

        canvas_endcap = CMS.cmsCanvas(canv_name_endcap, x_min, x_max, 0, 10000, variable[2], y_title, square=CMS.kSquare, extraSpace=0.05, iPos=0)
        data_hist_endcap.SetMarkerStyle(23)
        data_hist_endcap.SetMarkerColor(ROOT.kAzure + 1)
        data_hist_endcap.SetLineColor(ROOT.kAzure + 1)
        data_hist_endcap.SetLineWidth(2)
        data_hist_endcap.Draw()
        CMS.SaveCanvas(canvas_endcap, os.path.join(output_dir, f"Passed_muons_endcap_{variable[1]}.png"))


if __name__ == "__main__":
    start_time = time.time()
    
    config_file = config.Config()
    config_file.add_sample(name="WZ", root_file="WZ_final_merged.root",cuts=1)
    create_fr_plot(config_file)
    
    end_time = time.time()
    print(f"Elapsed time: {(end_time - start_time)/60:.2f} minutes")