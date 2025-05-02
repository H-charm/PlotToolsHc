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
parser.add_argument('-t', '--type', type=str, help='Type of plots', choices=['stack', 'shape'], default='stack')
parser.add_argument('-d', '--data', type=str, help='Real data folder (optional)', default=None)
args = parser.parse_args()

def create_RDF(filename):
    print(f"Creating RDF for sample {filename}")
    filename_path = os.path.join(config_file.base_dir, filename)
    df = ROOT.RDataFrame("Events", filename_path)
    df = df.Define("final_weight", config_file.weights)
    return df

def merge_data_RDF():
    file_paths = [os.path.join(args.data, f) for f in DATA_FILES]
    return ROOT.RDataFrame("Events", file_paths)

def create_plots(config_file):
    samples_dict = config_file.samples_dict
    variables = config_file.vars_ZLL
    samples_filenames = config_file.get_samples_filenames()
    RDF_dict = {filename: create_RDF(filename) for filename in samples_filenames}

    data_histos = {}
    if args.data:
        print("Loading and merging real data...")
        data_df = merge_data_RDF()

    # Open ROOT file to save histograms
    output_hist_file = ROOT.TFile(os.path.join(config_file.output_plots_dir, "ZLL", "DataMC_ZLL_Histos.root"), "RECREATE")

    CMS.SetExtraText("Preliminary")
    CMS.SetLumi(config_file.dataset_legend)
    CMS.SetEnergy(config_file.energy)
    CMS.ResetAdditionalInfo()

    for variable in variables:
        print(f"Plotting variable {variable[0]}")
        histos_dict = {}

        for sample in samples_dict.keys():
            df = RDF_dict[samples_dict[sample][0]]
            if isinstance(variable[3], list):
                bins_array = ROOT.std.vector("double")(variable[3])
                hist = df.Filter(config_file.cuts).Define("plotvar_", variable[0]).Histo1D(
                    (f"hist_{sample}_{variable[0]}", "", len(variable[3])-1, bins_array.data()), "plotvar_", "final_weight")
            else:
                hist = df.Filter(config_file.cuts).Define("plotvar_", variable[0]).Histo1D(
                    (f"hist_{sample}_{variable[0]}", "", variable[3], variable[4], variable[5]), "plotvar_", "final_weight")

            hist = utils.add_overflow(hist)
            hist.Write()  # Save histogram
            histos_dict[sample] = hist.GetPtr()

        # Process real data
        if args.data:
            if isinstance(variable[3], list):
                bins_array = ROOT.std.vector("double")(variable[3])
                data_hist = data_df.Filter(config_file.cuts).Define("plotvar_", variable[0]).Histo1D(
                    (f"hist_data_{variable[0]}", "", len(variable[3])-1, bins_array.data()), "plotvar_")
            else:
                data_hist = data_df.Filter(config_file.cuts).Define("plotvar_", variable[0]).Histo1D(
                    (f"hist_data_{variable[0]}", "", variable[3], variable[4], variable[5]), "plotvar_")

            data_hist = utils.add_overflow(data_hist)
            data_hist.SetMarkerStyle(20)
            data_hist.SetMarkerColor(ROOT.kBlack)
            data_hist.Write()
            data_histos[variable[0]] = data_hist.GetPtr()

        # CMS Canvas
        canv_name = f"{variable[1]}_canvas"
        y_title = "Events"
        if isinstance(variable[3], list):
            x_min, x_max = variable[3][0], variable[3][-1]
        else:
            x_min, x_max = variable[4], variable[5]

        canvas = CMS.cmsCanvas(canv_name, x_min, x_max, 0, 1, variable[2], y_title, square=CMS.kSquare, extraSpace=0.05, iPos=0)
        stack = ROOT.THStack("stack", f";{variable[2]};{y_title}")
        stack_temp = ROOT.THStack("stack_temp", f";{variable[2]};{y_title}")
        stack_ratio = ROOT.THStack("stack_ratio", f";{variable[2]};{y_title}")
        legend = CMS.cmsLeg(0.75, 0.66, 0.88, 0.88, textSize=0.035, columns=1)

        # Fill stack
        for sample, hist in histos_dict.items():
            stack_temp.Add(hist)

        # Y-axis scaling
        y_max = 1
        y_min = 0.0

        if config_file.set_logy:
            y_min = 0.1
            canvas.SetLogy()
            y_max = 10 * CMS.cmsReturnMaxY(stack_temp)
        else:
            y_max = 1.2* CMS.cmsReturnMaxY(stack_temp)

        CMS.GetcmsCanvasHist(canvas).GetYaxis().SetRangeUser(y_min, y_max)
        CMS.GetcmsCanvasHist(canvas).GetYaxis().SetTitleOffset(1.6)

        scientific_notation = False
        # Scientific notation
        if scientific_notation:
            hdf = CMS.GetcmsCanvasHist(canvas)
            hdf.GetYaxis().SetMaxDigits(2)
            # Shift multiplier position
            ROOT.TGaxis.SetExponentOffset(-0.10, 0.01, "Y")

        CMS.GetcmsCanvasHist(canvas).GetYaxis().SetRangeUser(y_min, y_max)
        CMS.GetcmsCanvasHist(canvas).GetYaxis().SetTitleOffset(1.6)

        # Draw and save
        CMS.cmsDrawStack(stack, legend, histos_dict, data=(data_histos[variable[0]] if args.data else None))
        CMS.SaveCanvas(canvas, os.path.join(config_file.output_plots_dir, "ZLL", f"{variable[1]}.{config_file.plot_format}"), close=True)

    output_hist_file.Close()
    print(f"[INFO] All histograms saved to {output_hist_file.GetName()}")

if __name__ == "__main__":
    start_time = time.time()
    config_file = config.Config()
    os.makedirs(os.path.join(config_file.output_plots_dir, "ZLL"), exist_ok=True)

    path_parts = os.path.normpath(config_file.base_dir).split(os.sep)
    DATA_FILES = ["EGamma_merged.root", "MuonEG_merged.root", "Muon_merged.root"]
    if "2022" in path_parts:
        DATA_FILES += ["DoubleMuon_merged.root", "SingleMuon_merged.root"]

    config_file.add_sample(name="ZZ", root_file="qqZZ_final_merged.root", cuts=1)
    config_file.add_sample(name="WZ", root_file="WZ_final_merged.root", cuts=1)
    config_file.add_sample(name="TTto2L2Nu", root_file="TTto2L2Nu_final_merged.root", cuts=1)
    config_file.add_sample(name="DYJets", root_file="DYJets_final_merged.root", cuts=1)

    create_plots(config_file)

    end_time = time.time()
    print(f"Elapsed time: {(end_time - start_time)/60:.2f} minutes")

