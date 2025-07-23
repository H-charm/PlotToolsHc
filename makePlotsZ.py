import ROOT
import argparse
import os
import config
import time
import utils
import cmsstyle as CMS  # Import cmsstyle
import array

ROOT.ROOT.EnableImplicitMT()  # Enable multi-threading for RDataFrame
ROOT.gInterpreter.ProcessLine('#include "cpp_functions.C"')
ROOT.gROOT.SetBatch(True)

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--type', type=str, help='Type of plots', choices=['stack', 'shape'], default='stack')
parser.add_argument('-d', '--data', type=str, help='Real data filename (optional)', default=None)
parser.add_argument('-s', '--syst', action='store_true', help='Apply systematics', default=False)
parser.add_argument('-v', '--debug', action='store_true', help='Debugging', default=False)
args = parser.parse_args()
def merge_data_RDF():
    """Create a single RDataFrame from multiple ROOT data files."""
    file_paths = [os.path.join(args.data, f) for f in DATA_FILES]
    df = ROOT.RDataFrame("Events", file_paths)
    df = df.Define("weight_data", "1")#"elTriggerWeightData* muTriggerWeightData")#"elHLT*muHLT")
    return df


# def create_SF(filename, config_file):
#     print(f"Creating SF for sample {filename}")
    
#     filename_path = os.path.join(config_file.base_dir, filename)
#     mc_df = ROOT.RDataFrame("Events", filename_path)
#     data_df = merge_data_RDF()  # Make sure this function is defined elsewhere

#     # Create histograms for data and MC weighted by trigger weights
#     data_hist = data_df.Histo1D(("data_hist", "Electron pT Data; pT; Counts", 20, 0, 100), "el_pt", "elTriggerWeightData")
#     mc_hist = mc_df.Histo1D(("mc_hist", "Electron pT MC; pT; Counts", 20, 0, 100), "el_pt", "elTriggerWeight")

#     # Clone and divide to get SF histogram
#     sf_hist = data_hist.Clone("sf_hist")
#     sf_hist.Divide(mc_hist.GetPtr())

#     # Make the sf_hist globally accessible for C++ function
#     ROOT.gROOT.cd()  # Make sure to cd to the top directory
#     sf_hist.SetDirectory(0)  # Detach from any file (important!)

#     # Register sf_hist in the global namespace to use it in the C++ function
#     ROOT.gInterpreter.ProcessLine('TH1F* sf_hist = nullptr;')
#     ROOT.gInterpreter.ProcessLine(f'sf_hist = (TH1F*) gROOT->FindObject("sf_hist");')

#     # # Declare the triggerSF function in C++
#     # ROOT.gInterpreter.Declare("""
#     # double triggerSF(double pt) {
#     #     int bin = sf_hist->FindBin(pt);
#     #     return sf_hist->GetBinContent(bin);
#     # }
#     # """)

#     mc_df = mc_df.Define("trigger_SF", 
#         "([](const ROOT::VecOps::RVec<float>& pts) {"
#         " ROOT::VecOps::RVec<double> sf;"
#         " for (auto pt : pts) {"
#         "   int bin = sf_hist->FindBin(pt);"
#         "   sf.push_back(sf_hist->GetBinContent(bin));"
#         " }"
#         " return sf;"
#         "})(el_pt)")

#     # Apply final event weight — use f-string or format correctly with config weights string
#     mc_df = mc_df.Define("final_weight", f"({config_file.weights}) * trigger_SF")

#     return mc_df

def create_RDF(filename):
    print(f"Creating RDF for sample {filename}")
    filename_path = os.path.join(config_file.base_dir, filename)
    df = ROOT.RDataFrame("Events", filename_path)

    # df = df.Define("triggerSF", "elTriggerWeight > 0 ? elTriggerWeightData / elTriggerWeight : 1.0")

    # Apply MC weights
    # df = df.Define("final_weight", f"({config_file.weights}) * triggerSF")

    df = df.Define("final_weight", config_file.weights)
    if args.syst:
        df = df.Define("final_weight_up", config_file.weights_up)
        df = df.Define("final_weight_down", config_file.weights_down)
        # if "puWeight" in config_file.weights:
        #     df = df.Define("final_weight_up", config_file.weights.replace("puWeight", "puWeightUp"))
        #     df = df.Define("final_weight_down", config_file.weights.replace("puWeight", "puWeightDown"))
    return df

def create_plots(config_file):
    samples_dict = config_file.samples_dict
    variables = config_file.vars_Z

    samples_filenames = config_file.get_samples_filenames()
    RDF_dict = {filename: create_RDF(filename) for filename in samples_filenames}
    #RDF_dict = {filename: create_SF(filename, config_file) for filename in samples_filenames}

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
            if args.syst:
                if isinstance(variable[3], list):  # Variable binning
                    bins_array = ROOT.std.vector("double")(variable[3])
                    hist_up = df.Filter(config_file.cuts).Define("plotvar_", variable[0]).Histo1D(
                        (f"hist_{sample}_{variable[0]}_up", "", len(variable[3]) - 1, bins_array.data()), 
                        "plotvar_", "final_weight_up"
                    )
                else:  # Uniform binning
                    hist_up = df.Filter(config_file.cuts).Define("plotvar_", variable[0]).Histo1D(
                    (f"hist_{sample}_{variable[0]}_up", "", variable[3], variable[4], variable[5]), "plotvar_", "final_weight_up"
                )
                if isinstance(variable[3], list):  # Variable binning
                    bins_array = ROOT.std.vector("double")(variable[3])
                    hist_down = df.Filter(config_file.cuts).Define("plotvar_", variable[0]).Histo1D(
                        (f"hist_{sample}_{variable[0]}_down", "", len(variable[3]) - 1, bins_array.data()), 
                        "plotvar_", "final_weight_down"
                    )
                else:  # Uniform binning
                    hist_down = df.Filter(config_file.cuts).Define("plotvar_", variable[0]).Histo1D(
                    (f"hist_{sample}_{variable[0]}_down", "", variable[3], variable[4], variable[5]), "plotvar_", "final_weight_down"
                )
            # hist = utils.add_underflow(hist)
            hist = utils.add_overflow(hist)
            if args.syst:
                hist_up = utils.add_overflow(hist_up)
                hist_down = utils.add_overflow(hist_down)

                histos_dict[sample] = {
                    "nominal": hist.GetPtr(),
                    "up": hist_up.GetPtr(),
                    "down": hist_down.GetPtr()
                }
            else:
                histos_dict[sample] = {
                    "nominal": hist.GetPtr()
                }

        # Process real data histogram
        if args.data:
            if isinstance(variable[3], list):  # Variable binning
                bins_array = ROOT.std.vector("double")(variable[3])
                data_hist = data_df.Filter(config_file.cuts).Define("plotvar_", variable[0]).Histo1D(
                    (f"hist_data_{variable[0]}", "", len(variable[3]) - 1, bins_array.data()), 
                    "plotvar_", "weight_data"
                )
            else:  # Uniform binning
                data_hist = data_df.Filter(config_file.cuts).Define("plotvar_", variable[0]).Histo1D(
                    (f"hist_data_{variable[0]}", "", variable[3], variable[4], variable[5]), 
                    "plotvar_", "weight_data"
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
        if args.syst:
            stack_up = ROOT.THStack("stack_up", f";{variable[2]};{y_title}")
            stack_down = ROOT.THStack("stack_down", f";{variable[2]};{y_title}")

        legend = CMS.cmsLeg(0.75, 0.66, 0.88, 0.88, textSize=0.035, columns=1)

        for sample, hist in histos_dict.items():
            stack_temp.Add(hist["nominal"])
            if args.syst:
                stack_up.Add(hist["up"])
                stack_down.Add(hist["down"])
        
        if args.syst:
            n_bins = histos_dict[next(iter(histos_dict))]["nominal"].GetNbinsX()
            sum_hist_nominal = histos_dict[next(iter(histos_dict))]["nominal"].Clone("sum_hist_nominal")
            sum_hist_up = histos_dict[next(iter(histos_dict))]["up"].Clone("sum_hist_up")
            sum_hist_down = histos_dict[next(iter(histos_dict))]["down"].Clone("sum_hist_down")
            sum_hist_up.Reset()
            sum_hist_down.Reset()

            for h in histos_dict.values():
                sum_hist_up.Add(h["up"])
                sum_hist_down.Add(h["down"])
                sum_hist_nominal.Add(h["nominal"])

            # Create TGraphAsymmErrors to represent the uncertainty band
            x_vals = []
            y_vals = []
            x_errs = []
            y_up_errs = []
            y_down_errs = []
            y_ratio_vals, y_ratio_errs_up, y_ratio_errs_down = [], [], []

            for i in range(1, n_bins + 1):
                x = sum_hist_nominal.GetBinCenter(i)
                y = sum_hist_nominal.GetBinContent(i)
                x_err = sum_hist_nominal.GetBinWidth(i) / 2
                y_up = sum_hist_up.GetBinContent(i)
                y_down = sum_hist_down.GetBinContent(i)

                # Handle direction of uncertainty
                y_err_up = max(y_up - y, 0)
                y_err_down = max(y - y_down, 0)

                x_vals.append(x)
                y_vals.append(y)
                x_errs.append(x_err)
                y_up_errs.append(y_err_up)
                y_down_errs.append(y_err_down)

                y_ratio_vals.append(1.0)  # Nominal is normalized to 1

                if y > 0:
                    y_ratio_errs_up.append(y_err_up / y)
                    y_ratio_errs_down.append(y_err_down / y)
                else:
                    y_ratio_errs_up.append(0.0)
                    y_ratio_errs_down.append(0.0)
                # y_ratio_errs_up.append(y_err_up / y)
                # y_ratio_errs_down.append(y_err_down / y)

            # Convert to ROOT arrays
            n = len(x_vals)
            gr_syst = ROOT.TGraphAsymmErrors(
                n,
                array.array("d", x_vals),
                array.array("d", y_vals),
                array.array("d", x_errs),
                array.array("d", x_errs),
                array.array("d", y_down_errs),
                array.array("d", y_up_errs),
            )
            gr_syst.SetFillColor(ROOT.kGray + 1)
            gr_syst.SetFillStyle(3001)
            gr_syst.SetLineColor(0)

            # TGraph for ratio uncertainty band
            gr_ratio_syst = ROOT.TGraphAsymmErrors(
                n,
                array.array("d", x_vals),
                array.array("d", y_ratio_vals),
                array.array("d", x_errs),
                array.array("d", x_errs),
                array.array("d", y_ratio_errs_down),
                array.array("d", y_ratio_errs_up),
            )
            gr_ratio_syst.SetFillColor(ROOT.kGray + 1)
            gr_ratio_syst.SetFillStyle(3001)
            gr_ratio_syst.SetLineColor(0)
        
        # Adjust y-axis offsets and log scaling
        y_max = 1
        y_min = 0.0
        if config_file.set_logy:
            canvas.SetLogy()
            y_max = 100 * CMS.cmsReturnMaxY(stack_temp)
            y_min = 100
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
        if "mu" in variable[0]:
            latex.DrawLatex(0.21, 0.87, "#scale[0.9]{Z #rightarrow #mu^{+}#mu^{-}}")  # Adjust coordinates & text as needed
        elif "el" in variable[0]:
            latex.DrawLatex(0.21, 0.87, "#scale[0.9]{Z #rightarrow e^{+}e^{-}}")  # Adjust coordinates & text as needed
        else:
            latex.DrawLatex(0.21, 0.87, "#scale[0.9]{Z #rightarrow l^{+}l^{-}}")  # Adjust coordinates & text as needed

        # Draw stack plot with cmsstyle
        CMS.cmsDrawStack(stack, legend, {k: v["nominal"] for k, v in histos_dict.items()}, data=(data_histos[variable[0]] if args.data else None))

        if args.syst:
            gr_syst.Draw("E2 SAME")  # Draw shaded band on top
        # Save canvas
        CMS.SaveCanvas(canvas,os.path.join(config_file.output_plots_dir, "Z", f"{variable[1]}." + config_file.plot_format), close= True)

        if args.data:
            #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            # Ratio plots
            #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            if "mu" in variable[0]:
                ratio_y_max = 1.1
            elif "el" in variable[0]:
                ratio_y_max = 1.3
            else:
                ratio_y_max = 1.5
            ratio_y_min = 0.8
            # ratio_y_max = 1.5
            # ratio_y_min = 0.5
            # CMSStyle DiCanvas
            canv_name_ratio = f"{variable[1]}_canvas_ratio"
            canvas_ratio = CMS.cmsDiCanvas(canv_name_ratio, x_min, x_max, y_min, y_max, ratio_y_min, ratio_y_max, variable[2], y_title, "Ratio", square=CMS.kSquare, extraSpace=0.05, iPos=0 )
            legend_ratio = CMS.cmsLeg(0.73, 0.65, 0.88, 0.88, textSize=0.045, columns=1)
            
            # Draw stack plot in the upper pad using cmsstyle
            CMS.cmsDrawStack(stack_ratio, legend_ratio, {k: v["nominal"] for k, v in histos_dict.items()}, data=(data_histos[variable[0]] if args.data else None))
            if args.syst:
                gr_syst.Draw("E2 SAME")  # Draw shaded band on top
            if config_file.set_logy:
                ROOT.gPad.SetLogy()
                ROOT.gPad.Update()
            
            latex_ratio = ROOT.TLatex()
            latex_ratio.SetNDC()
            latex_ratio.SetTextSize(0.045)
            latex_ratio.SetTextFont(42)
            if "mu" in variable[0]:
                latex_ratio.DrawLatex(0.18, 0.85, "#scale[0.9]{Z #rightarrow #mu^{+}#mu^{-}}")  # Adjust coordinates & text as needed
            elif "el" in variable[0]:
                latex_ratio.DrawLatex(0.18, 0.85, "#scale[0.9]{Z #rightarrow e^{+}e^{-}}")  # Adjust coordinates & text as needed
            else:
                latex_ratio.DrawLatex(0.18, 0.85, "#scale[0.9]{Z #rightarrow l^{+}l^{-}}")  # Adjust coordinates & text as needed
            
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
            ratio_hist.GetYaxis().SetRangeUser(0.5,1.5)
            ratio_hist.GetYaxis().SetNdivisions(505)
            # Format for X axis
            ratio_hist.GetXaxis().SetTitle(variable[2])
            ratio_hist.GetXaxis().SetTitleSize(0.13)
            ratio_hist.GetXaxis().SetLabelSize(0.11)
            # Draw with error bars
            ratio_hist.Draw("EP")
            if args.syst:
                gr_ratio_syst.Draw("E2 SAME")

            # Draw a horizontal line at y=1 for reference
            line = ROOT.TLine(x_min, 1, x_max, 1)
            line.SetLineStyle(2)
            line.SetLineColor(ROOT.kBlack)
            line.Draw("same")

            # Save canvas
            CMS.SaveCanvas(canvas_ratio,os.path.join(config_file.output_plots_dir, "Z", f"{variable[1]}_ratio." + config_file.plot_format), close= True)

if __name__ == "__main__":
    start_time = time.time()

    config_file = config.Config()
    os.makedirs(os.path.join(config_file.output_plots_dir, "Z"), exist_ok=True)

    path_parts = os.path.normpath(config_file.base_dir).split(os.sep)
    DATA_FILES = [
        "EGamma_merged.root",
        # "MuonEG_merged.root",
        "Muon_merged.root"
    ]
    if "2022" in path_parts:
        DATA_FILES += [
            # "DoubleMuon_merged.root",
            "SingleMuon_merged.root"
        ]
    # Samples will be stacked in this order
    if not args.debug:
        # config_file.add_sample(name="SingleTop", root_file="SingleTop_final_merged.root",cuts=1)
        # config_file.add_sample(name="Diboson", root_file="Diboson_final_merged.root",cuts=1)
        # config_file.add_sample(name="TT", root_file="TT_final_merged.root",cuts=1)
        config_file.add_sample(name="DYJets", root_file="DYJets_final_merged.root",cuts=1)
    else:
        config_file.add_sample(name="SingleTop", root_file="SingleTop_final_merged.root",cuts=1)
        config_file.add_sample(name="WW", root_file="Diboson_weighted_WW_TuneCP5_13p6TeV_pythia8.root",cuts=1)
        config_file.add_sample(name="WZ", root_file="Diboson_weighted_WZ_TuneCP5_13p6TeV_pythia8.root",cuts=1)
        config_file.add_sample(name="ZZ", root_file="Diboson_weighted_ZZ_TuneCP5_13p6TeV_pythia8.root",cuts=1)
        config_file.add_sample(name="TTto2L2Nu", root_file="TT_weighted_TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8.root",cuts=1)
        config_file.add_sample(name="TTto4Q", root_file="TT_weighted_TTto4Q_TuneCP5_13p6TeV_powheg-pythia8.root",cuts=1)
        config_file.add_sample(name="TTtoLNu2Q", root_file="TT_weighted_TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8.root",cuts=1)
        config_file.add_sample(name="DYJets50", root_file="DYJets_weighted_DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8.root",cuts=1)
        config_file.add_sample(name="DYJets10", root_file="DYJets_weighted_DYto2L-2Jets_MLL-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8.root",cuts=1)
    create_plots(config_file)

    end_time = time.time()
    print(f"Elapsed time: {(end_time - start_time)/60:.2f} minutes")
