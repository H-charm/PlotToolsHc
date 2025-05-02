import ROOT
import argparse
import os
import config
import time
import utils
import cmsstyle as CMS  # Import cmsstyle

ROOT.ROOT.EnableImplicitMT()  # Enable multi-threading for RDataFrame
ROOT.gInterpreter.ProcessLine('#include "cpp_functions.C"')
ROOT.gROOT.SetBatch(True)

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--data', type=str, help='Real data filename (optional)', default=None)
args = parser.parse_args()

def create_RDF(filename):
    print(f"Creating RDF for sample {filename}")
    filename_path = os.path.join(config_file.base_dir, filename)
    df = ROOT.RDataFrame("Events", filename_path)

    # Apply MC weights
    df = df.Define("final_weight", config_file.weights)
    return df

def merge_data_RDF():
    """Create a single RDataFrame from multiple ROOT data files."""
    file_paths = [os.path.join(args.data, f) for f in DATA_FILES]
    return ROOT.RDataFrame("Events", file_paths)

def create_plots(config_file):
    samples_dict = config_file.samples_dict
    variables = config_file.vars_ZL

    samples_filenames = config_file.get_samples_filenames()
    RDF_dict = {filename: create_RDF(filename) for filename in samples_filenames}

    # Load real data if provided
    data_histos = None  # Default: no data
    if args.data:
        print("Loading and merging real data...")
        data_df = merge_data_RDF()
        data_histos = {}

    # CMS Styling Settings
    CMS.SetExtraText("Preliminary")
    CMS.SetLumi(config_file.dataset_legend)
    CMS.SetEnergy(config_file.energy)
    CMS.ResetAdditionalInfo()

    # Loop for each variable
    for variable in variables:
        print(f"Plotting var {variable[0]}")
        histos_dict = {}

        for sample in samples_dict.keys():
            df = RDF_dict[samples_dict[sample][0]]
            if isinstance(variable[3], list):  # Variable binning
                bins_array = ROOT.std.vector("double")(variable[3])
                hist = df.Filter(config_file.cuts).Define("plotvar_", variable[0]).Histo1D(
                    (f"hist_{sample}_{variable[0]}", "", len(variable[3]) - 1, bins_array.data()), 
                    "plotvar_", "final_weight"
                )
            else:  # Uniform binning
                hist = df.Filter(config_file.cuts).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_{sample}_{variable[0]}", "", variable[3], variable[4], variable[5]), "plotvar_", "final_weight"
            )
            # hist = utils.add_underflow(hist)
            hist = utils.add_overflow(hist)
            histos_dict[sample] = hist.GetPtr()

        # Process real data histogram
        if args.data:
            if isinstance(variable[3], list):  # Variable binning
                bins_array = ROOT.std.vector("double")(variable[3])
                data_hist = data_df.Filter(config_file.cuts).Define("plotvar_", variable[0]).Histo1D(
                    (f"hist_data_{variable[0]}", "", len(variable[3]) - 1, bins_array.data()), 
                    "plotvar_"
                )
            else:  # Uniform binning
                data_hist = data_df.Filter(config_file.cuts).Define("plotvar_", variable[0]).Histo1D(
                    (f"hist_data_{variable[0]}", "", variable[3], variable[4], variable[5]), 
                    "plotvar_"
                )
            # data_hist = utils.add_underflow(data_hist)
            data_hist = utils.add_overflow(data_hist)
            data_hist.SetMarkerStyle(20)
            data_hist.SetMarkerColor(ROOT.kBlack)
            data_histos[variable[0]] = data_hist.GetPtr()

        # CMSStyle Canvas
        canv_name = f"{variable[1]}_canvas"
        y_title = "Events"
        if isinstance(variable[3], list):  # Variable binning
            x_min, x_max = variable[3][0], variable[3][-1]  # Use first and last bin edge
        else:  # Uniform binning
            x_min, x_max = variable[4], variable[5]  # Use configured range
        canvas = CMS.cmsCanvas(canv_name, x_min, x_max, 0, 1, variable[2], y_title, square=CMS.kSquare, extraSpace=0.05, iPos=0)

        # Define different stack plots for each case 
        stack = ROOT.THStack("stack", f";{variable[2]};{y_title}")
        stack_temp = ROOT.THStack("stack_temp", f";{variable[2]};{y_title}")
        stack_ratio = ROOT.THStack("stack_ratio", f";{variable[2]};{y_title}")

        legend = CMS.cmsLeg(0.75, 0.66, 0.88, 0.88, textSize=0.035, columns=1)

        for sample, hist in histos_dict.items():
            stack_temp.Add(hist)
        
        # Adjust y-axis offsets and log scaling
        y_max = 1
        y_min = 0.0
        if config_file.set_logy:
            canvas.SetLogy()
            y_max = 100 * CMS.cmsReturnMaxY(stack_temp)
            y_min = 1
        # elif config_file.set_logy: 
        #     y_max = 2.5 * CMS.cmsReturnMaxY(stack_temp)
        else:
            y_max = 1.2* CMS.cmsReturnMaxY(stack_temp)

        # Set the CMS canvas y-axis
        CMS.GetcmsCanvasHist(canvas).GetYaxis().SetRangeUser(y_min, y_max)
        CMS.GetcmsCanvasHist(canvas).GetYaxis().SetTitleOffset(1.6)

        scientific_notation = False
        # Scientific notation
        if scientific_notation:
            hdf = CMS.GetcmsCanvasHist(canvas)
            hdf.GetYaxis().SetMaxDigits(2)
            # Shift multiplier position
            ROOT.TGaxis.SetExponentOffset(-0.10, 0.01, "Y")

        latex = ROOT.TLatex()
        latex.SetNDC()
        latex.SetTextSize(0.04)
        latex.SetTextFont(42)
        # Optional top-left label if variable name contains "pass"
        if "passe" in variable[0]:
            latex.DrawLatex(0.21, 0.87, "#scale[0.9]{Z + e events with e passing selection}")
        elif "passmu" in variable[0]:
            latex.DrawLatex(0.21, 0.87, "#scale[0.9]{Z + #mu events with #mu passing selection}")
        elif "alle" in variable[0]:
            latex.DrawLatex(0.21, 0.87, "#scale[0.9]{Z + e events}")
        elif "allmu" in variable[0]:
            latex.DrawLatex(0.21, 0.87, "#scale[0.9]{Z + #mu events}")

        # Draw stack plot with cmsstyle
        CMS.cmsDrawStack(stack, legend, histos_dict, data=(data_histos[variable[0]] if args.data else None))

        # Save canvas
        CMS.SaveCanvas(canvas,os.path.join(config_file.output_plots_dir, "ZL", f"{variable[1]}." + config_file.plot_format), close= True)

        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Ratio plots
        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
        # CMSStyle DiCanvas
        canv_name_ratio = f"{variable[1]}_canvas_ratio"
        canvas_ratio = CMS.cmsDiCanvas(canv_name_ratio, x_min, x_max, y_min, y_max, 0, 2, variable[2], y_title, "Ratio", square=CMS.kSquare, extraSpace=0.05, iPos=0 )

        legend_ratio = CMS.cmsLeg(0.73, 0.65, 0.88, 0.88, textSize=0.045, columns=1)
        
        # Draw stack plot in the upper pad using cmsstyle
        CMS.cmsDrawStack(stack_ratio, legend_ratio, histos_dict, data=(data_histos[variable[0]] if args.data else None))
        if config_file.set_logy:
            ROOT.gPad.SetLogy()
            ROOT.gPad.Update()
        
        latex_ratio = ROOT.TLatex()
        latex_ratio.SetNDC()
        latex_ratio.SetTextSize(0.045)
        latex_ratio.SetTextFont(42)
        if "passe" in variable[0]:
            latex_ratio.DrawLatex(0.18, 0.85, "#scale[0.9]{Z + e events with e passing selection}")
        elif "passmu" in variable[0]:
            latex_ratio.DrawLatex(0.18, 0.85, "#scale[0.9]{Z + #mu events with #mu passing selection}")
        elif "alle" in variable[0]:
            latex_ratio.DrawLatex(0.18, 0.85, "#scale[0.9]{Z + e events}")
        elif "allmu" in variable[0]:
            latex_ratio.DrawLatex(0.18, 0.85, "#scale[0.9]{Z + #mu events}")

        # Change to the bottom pad
        canvas_ratio.cd(2)
        
        # Sum all MC histograms to create the dnominator
        mc_total_hist = stack_ratio.GetStack().Last().Clone("mc_total_hist")  # Get the total stacked MC histogram
        data_hist = data_histos[variable[0]]

        # Compute the ratio Data/MC
        ratio_hist = data_hist.Clone("ratio_hist")
        ratio_hist.Divide(mc_total_hist)

        # Style the ratio plot
        ratio_hist.SetMarkerStyle(20)
        ratio_hist.SetMarkerColor(ROOT.kBlack)
        ratio_hist.SetLineColor(ROOT.kBlack)
        # Format for Y axis
        ratio_hist.GetYaxis().SetTitle("Data / MC")
        ratio_hist.GetYaxis().SetTitleSize(0.13)
        ratio_hist.GetYaxis().SetLabelSize(0.11)
        ratio_hist.GetYaxis().SetTitleOffset(0.5)
        ratio_hist.GetYaxis().SetRangeUser(0,2)
        ratio_hist.GetYaxis().SetNdivisions(505)
        # Format for X axis
        ratio_hist.GetXaxis().SetTitle(variable[2])
        ratio_hist.GetXaxis().SetTitleSize(0.13)
        ratio_hist.GetXaxis().SetLabelSize(0.11)
        # Draw with error bars
        ratio_hist.Draw("EP")  

        # Draw a horizontal line at y=1 for reference
        line = ROOT.TLine(x_min, 1, x_max, 1)
        line.SetLineStyle(2)
        line.SetLineColor(ROOT.kBlack)
        line.Draw("same")

        # Save canvas
        CMS.SaveCanvas(canvas_ratio,os.path.join(config_file.output_plots_dir, "ZL", f"{variable[1]}_ratio." + config_file.plot_format), close= True)

if __name__ == "__main__":
    start_time = time.time()

    config_file = config.Config()
    os.makedirs(os.path.join(config_file.output_plots_dir, "ZL"), exist_ok=True)

    path_parts = os.path.normpath(config_file.base_dir).split(os.sep)
    DATA_FILES = [
        "EGamma_merged.root",
        "MuonEG_merged.root",
        "Muon_merged.root"
    ]
    if "2022" in path_parts:
        DATA_FILES += [
            "DoubleMuon_merged.root",
            "SingleMuon_merged.root"
        ]

    # Samples will be stacked in this order
    config_file.add_sample(name="WZ", root_file="WZ_final_merged.root",cuts=1)
    config_file.add_sample(name="TTto2L2Nu", root_file="TTto2L2Nu_final_merged.root",cuts=1)
    config_file.add_sample(name="DYJets", root_file="DYJets_final_merged.root",cuts=1)
    create_plots(config_file)

    end_time = time.time()
    print(f"Elapsed time: {(end_time - start_time)/60:.2f} minutes")
