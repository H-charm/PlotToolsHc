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
parser.add_argument('-t', '--type', type=str, help='Type of plots', choices=['stack', 'shape'], default='stack')
parser.add_argument('-d', '--data', type=str, help='Real data filename (optional)', default=None)
args = parser.parse_args()

DATA_FILES = [
    # "merged_data.root"
    "DoubleMuon_merged.root",
    "SingleMuon_merged.root",
    "EGamma_merged.root",
    "MuonEG_merged.root",
    "Muon_merged.root"
]

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
    variables = config_file.vars

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
            # hist.SetLineColor(ROOT.kBlack)
            # if args.type == "stack":
            #     
            # if args.type == "shape":
            #     # hist.SetLineColor(config_file.colors[sample])
            #     hist.Scale(1 / hist.Integral())
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

        legend = CMS.cmsLeg(0.68, 0.69, 0.88, 0.87, textSize=0.025, columns=1)

        for sample, hist in histos_dict.items():
            stack_temp.Add(hist)
        
        # Adjust y-axis offsets and log scaling
        y_max = 1
        y_min = 0.0
        if config_file.set_logy:
            canvas.SetLogy()
            y_max = 10 * CMS.cmsReturnMaxY(stack_temp)
            y_min = 0.1
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

        # Draw stack plot with cmsstyle
        CMS.cmsDrawStack(stack, legend, histos_dict, data=(data_histos[variable[0]] if args.data else None))

        # Save canvas
        CMS.SaveCanvas(canvas,os.path.join(config_file.output_plots_dir, args.type, f"{variable[1]}." + config_file.plot_format), close= True)

        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Ratio plots
        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
        # CMSStyle DiCanvas
        canv_name_ratio = f"{variable[1]}_canvas_ratio"
        canvas_ratio = CMS.cmsDiCanvas(canv_name_ratio, x_min, x_max, y_min, y_max, 0, 2, variable[2], y_title, "Ratio", square=CMS.kSquare, extraSpace=0.05, iPos=0 )
        legend_ratio = CMS.cmsLeg(0.68, 0.69, 0.88, 0.87, textSize=0.025, columns=1)
        
        # Draw stack plot in the upper pad using cmsstyle
        CMS.cmsDrawStack(stack_ratio, legend_ratio, histos_dict, data=(data_histos[variable[0]] if args.data else None))
        if config_file.set_logy:
            ROOT.gPad.SetLogy()
            ROOT.gPad.Update()

        # Change to the bottom pad
        canvas_ratio.cd(2)
        
        # Sum all MC histograms to create the denominator
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
        CMS.SaveCanvas(canvas_ratio,os.path.join(config_file.output_plots_dir, args.type, f"{variable[1]}_ratio." + config_file.plot_format), close= True)

if __name__ == "__main__":
    start_time = time.time()

    config_file = config.Config()
    os.makedirs(os.path.join(config_file.output_plots_dir, args.type), exist_ok=True)

    # Samples will be stacked in this order
    
    config_file.add_sample(name="ggZZ", root_file="ggZZ_final_merged.root",cuts=1)
    config_file.add_sample(name="qqZZ", root_file="qqZZ_final_merged.root",cuts=1)
    # config_file.add_sample(name="VBFToZZ", root_file="VBFToZZ_final_merged.root",cuts=1)
    config_file.add_sample(name="WWZ", root_file="WWZ_final_merged.root",cuts=1)
    config_file.add_sample(name="WZZ", root_file="WZZ_final_merged.root",cuts=1)
    config_file.add_sample(name="ZZZ", root_file="ZZZ_final_merged.root",cuts=1)
    config_file.add_sample(name="TTWW", root_file="TTWW_final_merged.root",cuts=1)
    config_file.add_sample(name="TTZZ", root_file="TTZZ_final_merged.root",cuts=1)
    config_file.add_sample(name="WZ", root_file="WZ_final_merged.root",cuts=1)
    # config_file.add_sample(name="DYJets", root_file="DYJets.root",cuts=1)
    # config_file.add_sample(name="TTto2L2Nu", root_file="TTto2L2Nu.root",cuts=1)
    config_file.add_sample(name="ggH", root_file="ggH_final_merged.root",cuts=1)
    config_file.add_sample(name="VBF", root_file="VBF_final_merged.root",cuts=1)
    config_file.add_sample(name="WplusH", root_file="WplusH_final_merged.root",cuts=1)
    config_file.add_sample(name="WminusH", root_file="WminusH_final_merged.root",cuts=1)
    # config_file.add_sample(name="ZH", root_file="ZH.root",cuts=1)
    config_file.add_sample(name="ZH", root_file="ZH_final_merged.root",cuts=1)
    config_file.add_sample(name="ttH", root_file="ttH_final_merged.root",cuts=1)
    config_file.add_sample(name="bbH", root_file="bbH_final_merged.root",cuts=1)
    # config_file.add_sample(name="Hc", root_file="Hc_tree.root",cuts=1)
    create_plots(config_file)

    end_time = time.time()
    print(f"Elapsed time: {(end_time - start_time)/60:.2f} minutes")
