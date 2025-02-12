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


weights ={
    "DYJets": "puWeight * genWeight * 9.6 * 1000 * 5558.0 * (1.0/27096229)",
    "ggZZ_2E2Mu": "puWeight * genWeight * 9.6 * 1000 * 0.00624157 * (1.0/150000) ",
    "ggZZ_2E2Tau": "puWeight * genWeight * 9.6 * 1000 *  0.00624157 * (1.0/144855)", 
    "ggZZ_2Mu2Tau": "puWeight * genWeight * 9.6 * 1000 * 0.00624157  * (1.0/146285)",
    "ggZZ_4E": "puWeight * genWeight * 9.6 * 1000 * 0.00305851 * (1.0/298185) ",
    "ggZZ_4Mu": "puWeight * genWeight * 9.6 * 1000 * 0.00303575 * (1.0/296985)",
    "ggZZ_4Tau": "puWeight * genWeight * 9.6 * 1000 * 0.00303575 * (1.0/298152)",
    "qqZZ": "puWeight * genWeight * 9.6 * 1000 * 1.39 * (1.0 / 20341593)",
    "ggH": "puWeight * genWeight * 9.6 * 1000 * 0.014337135 * (1.0 / 11272230)",
    "VBF": "puWeight * genWeight * 9.6 * 1000 * 0.001119411 * 1.0/(410391)",
    "WplusH": "puWeight * genWeight * 9.6 * 1000 * 0.00024400305 * 1.0/(454256)",
    "WminusH": "puWeight * genWeight * 9.6 * 1000 * 0.00015583365 * 1.0/(285614)",
    "ZH": "puWeight * genWeight * 9.6 * 1000 * 0.00077523450 * 1.0/(675815)",
    "ttH": "puWeight * genWeight * 9.6 * 1000 * 0.0031184814 * 1.0/(56096)",
    "bbH": "puWeight * genWeight * 9.6 * 1000 * 0.0001445517 * 1.0/(100000)",
    "TTWW": "puWeight * genWeight * 9.6 * 1000 * 0.008203 * (1.0/448443)",
    "TTZZ": "puWeight * genWeight * 9.6 * 1000 * 0.001579 * (1.0/443238)",
    "TTto2L2Nu": "puWeight * genWeight * 9.6 * 1000 * 762.1 * (1.0/1912899360)",
    "WWZ": "puWeight * genWeight * 9.6 * 1000 * 0.1851 * (1.0/361167)",
    "WZZ": "puWeight * genWeight * 9.6 * 1000 * 0.0621 * (1.0/123328)",
    "ZZZ": "puWeight * genWeight * 9.6 * 1000 * 0.0159 * (1.0/31382)",
    "WZ": "puWeight * genWeight * 9.6 * 1000 * 4.924 * (1.0/13670481) "
}

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--type', type=str, help='Type of plots', choices=['stack', 'shape'], default='stack')
parser.add_argument('-d', '--data', type=str, help='Real data filename (optional)', default=None)
args = parser.parse_args()

DATA_FILES = [
    # "merged_data.root"
    "DoubleMuon_tree.root",
    "EGamma_tree.root",
    "MuonEG_tree.root",
    "Muon_tree.root",
    "SingleMuon_tree.root"
    # "merged_eraE.root",
    # "merged_eraF.root",
    # "merged_eraG.root"
]

# def create_RDF(filename):
#     print(f"Creating RDF for sample {filename}")
#     filename_path = os.path.join(config_file.base_dir, filename)
#     df = ROOT.RDataFrame("Events", filename_path)

#     # Apply MC weights
#     df = df.Define("final_weight", config_file.weights)
#     return df

def create_RDF(filename):
    print(f"Creating RDF for sample {filename}")
    filename_path = os.path.join(config_file.base_dir, filename)
    df = ROOT.RDataFrame("Events", filename_path)

    # Determine the sample name from the filename
    sample_name = None
    for key in weights.keys():
        if key in filename:
            sample_name = key
            break

    if sample_name is None:
        print(f"Warning: No weight found for {filename}. Using default weight = 1.0")
        weight_expr = "1.0"
    else:
        weight_expr = weights[sample_name]

    # Apply the correct weight
    df = df.Define("final_weight", weight_expr)
    return df


def merge_data_RDF():
    """Create a single RDataFrame from multiple ROOT data files."""
    file_paths = [os.path.join(args.data, f) for f in DATA_FILES]
    return ROOT.RDataFrame("Events", file_paths)
    # """Merge all data ROOT files into a single RDataFrame."""
    # rdf_list = []
    # for f in DATA_FILES:
    #     filename_path = os.path.join(args.data, f)
    #     df = ROOT.RDataFrame("Events", filename_path)
    #     rdf_list.append(df)
    # return ROOT.RDataFrame.Merge(rdf_list)

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
    CMS.SetEnergy("13.6")
    CMS.ResetAdditionalInfo()

    for variable in variables:
        print(f"Plotting var {variable[0]}")
        histos_dict = {}

        for sample in samples_dict.keys():
            df = RDF_dict[samples_dict[sample][0]]
            hist = df.Filter(config_file.cuts).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_{sample}_{variable[0]}", "", variable[3], variable[4], variable[5]), "plotvar_", "final_weight"
            )
            # hist = utils.add_underflow(hist)
            hist = utils.add_overflow(hist)
            if args.type == "stack":
                hist.SetLineColor(ROOT.kBlack)
            if args.type == "shape":
                # hist.SetLineColor(config_file.colors[sample])
                hist.Scale(1 / hist.Integral())
            histos_dict[sample] = hist.GetPtr()

        # Process real data histogram
        if args.data:
            data_hist = data_df.Filter(config_file.cuts).Define("plotvar_", variable[0]).Histo1D(
                (f"hist_data_{variable[0]}", "", variable[3], variable[4], variable[5]), "plotvar_"
            )
            # data_hist = utils.add_underflow(data_hist)
            data_hist = utils.add_overflow(data_hist)
            data_hist.SetMarkerStyle(20)  # Marker style for data points
            data_hist.SetMarkerColor(ROOT.kBlack)
            # data_hist.Scale(1 / data_hist.Integral())
            data_histos[variable[0]] = data_hist.GetPtr()

        # total_integral = sum(hist.Integral() for hist in histos_dict.values())
        # for hist in histos_dict.values():
        #     hist.Scale(1.0 / total_integral)

        # CMSStyle Canvas and Legend
        canv_name = f"{variable[1]}_canvas"
        y_title = "Events" if args.type == "stack" else "Normalized to 1"
        canvas = CMS.cmsCanvas(canv_name, variable[4], variable[5], 0, 1, variable[2], y_title, square=CMS.kSquare, extraSpace=0.05, iPos=0)

        stack = ROOT.THStack("stack", f";{variable[2]};{y_title}")
        stack2 = ROOT.THStack("stack2", f";{variable[2]};{y_title}")
        legend = CMS.cmsLeg(0.22, 0.65, 0.92, 0.88, textSize=0.025, columns=4)
        
        for sample, hist in histos_dict.items():
            stack2.Add(hist)

        
        # Adjust y-axis offsets and log scaling
        y_max = 1
        y_min = 0.0
        if config_file.set_logy:
            canvas.SetLogy()
            y_max = 10 * CMS.cmsReturnMaxY(stack2)
            y_min = 1.0
        elif config_file.set_logy and args.type == "stack": 
            y_max = 2.5 * CMS.cmsReturnMaxY(stack2)
        else:
            y_max = 1.2* CMS.cmsReturnMaxY(stack2)

        # Set the CMS canvas y-axis
        CMS.GetcmsCanvasHist(canvas).GetYaxis().SetRangeUser(y_min, y_max)
        CMS.GetcmsCanvasHist(canvas).GetYaxis().SetTitleOffset(1.6)
        # Scientific notation
        hdf = CMS.GetcmsCanvasHist(canvas)
        hdf.GetYaxis().SetMaxDigits(2)
        # Shift multiplier position
        ROOT.TGaxis.SetExponentOffset(-0.10, 0.01, "Y")

        CMS.cmsDrawStack(stack, legend, histos_dict, data=(data_histos[variable[0]] if args.data else None))

        # Save the canvas
        canvas.SaveAs(os.path.join(config_file.output_plots_dir, args.type, f"{variable[1]}." + config_file.plot_format))

if __name__ == "__main__":
    start_time = time.time()

    config_file = config.Config()
    os.makedirs(os.path.join(config_file.output_plots_dir, args.type), exist_ok=True)

    # Samples will be stacked in this order
    
    config_file.add_sample(name="ggZZ_2E2Mu", root_file="ggZZ_2E2Mu.root",cuts=1)
    config_file.add_sample(name="ggZZ_2E2Tau", root_file="ggZZ_2E2Tau.root",cuts=1)
    config_file.add_sample(name="ggZZ_2Mu2Tau", root_file="ggZZ_2Mu2Tau.root",cuts=1)
    config_file.add_sample(name="ggZZ_4E", root_file="ggZZ_4E.root",cuts=1)
    config_file.add_sample(name="ggZZ_4Mu", root_file="ggZZ_4Mu.root",cuts=1)
    config_file.add_sample(name="ggZZ_4Tau", root_file="ggZZ_4Tau.root",cuts=1)
    config_file.add_sample(name="qqZZ", root_file="qqZZ_tree.root",cuts=1)
    config_file.add_sample(name="WWZ", root_file="WWZ_tree.root",cuts=1)
    config_file.add_sample(name="WZZ", root_file="WZZ_tree.root",cuts=1)
    config_file.add_sample(name="ZZZ", root_file="ZZZ_tree.root",cuts=1)
    config_file.add_sample(name="TTWW", root_file="TTWW_tree.root",cuts=1)
    config_file.add_sample(name="TTZZ", root_file="TTZZ_tree.root",cuts=1)
    config_file.add_sample(name="WZ", root_file="WZ_tree.root",cuts=1)
    # config_file.add_sample(name="DYJets", root_file="DYJets_tree.root",cuts=1)
    # config_file.add_sample(name="TTto2L2Nu", root_file="TTto2L2Nu_tree.root",cuts=1)
    config_file.add_sample(name="ggH", root_file="ggH_tree.root",cuts=1)
    config_file.add_sample(name="VBF", root_file="VBF_tree.root",cuts=1)
    config_file.add_sample(name="WplusH", root_file="WplusH_tree.root",cuts=1)
    config_file.add_sample(name="WminusH", root_file="WminusH_tree.root",cuts=1)
    config_file.add_sample(name="ZH", root_file="ZH_tree.root",cuts=1)
    config_file.add_sample(name="ttH", root_file="ttH_tree.root",cuts=1)
    config_file.add_sample(name="bbH", root_file="bbH_tree.root",cuts=1)
    # config_file.add_sample(name="Hc", root_file="Hc_tree.root",cuts=1)
 

    create_plots(config_file)

    end_time = time.time()
    print(f"Elapsed time: {(end_time - start_time)/60:.2f} minutes")
