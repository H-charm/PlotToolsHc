import ROOT
ROOT.ROOT.EnableImplicitMT()  # Enable multi-threading for RDataFrame
import argparse
import os
import config
import time
import utils
ROOT.gROOT.SetBatch(True)
ROOT.gInterpreter.ProcessLine('#include "cpp_functions.C"')

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--type', type=str, help='Type of plots', choices=['stack', 'shape'], default='stack')
args = parser.parse_args()

def create_RDF(filename):

    print(f"Creating RDF for sample {filename}")
    filename_path = os.path.join(config_file.base_dir, filename)
    df = ROOT.RDataFrame("Events", filename_path)    
   
    return df

def create_plots(config_file):
    
    samples_dict = config_file.samples_dict
    variables = config_file.vars 
    
    samples_filenames = config_file.get_samples_filenames()
    RDF_dict = {filename: create_RDF(filename) for filename in samples_filenames} 

    for variable in variables:
        print(f"Plotting var {variable[0]}")
        
        y_title = "Events" if args.type == "stack" else "Normalized to 1"
        stack = ROOT.THStack("stack", ";" + variable[2] + ";" + y_title)
        histos_dict = {}

        legend = ROOT.TLegend(0.68,0.69,0.88,0.87)
        legend.SetNColumns(2)
        legend.SetTextFont(62)
        legend.SetTextSize(0.035)
        legend.SetFillStyle(0)
        
        for sample in samples_dict.keys():
            df = RDF_dict[samples_dict[sample][0]]
            hist = df.Filter(config_file.cuts).Define("plotvar_", variable[0]).Histo1D((f"hist_{sample}_{variable[0]}", "", variable[3], variable[4], variable[5]), "plotvar_")
            hist = utils.add_underflow(hist)
            hist = utils.add_overflow(hist)
            if args.type == "stack": 
                hist.SetFillColor(config_file.colors[sample])
                hist.SetLineColor(ROOT.kBlack)
            if args.type == "shape": 
                hist.SetLineColor(config_file.colors[sample])
                hist.Scale(1/hist.Integral())
            histos_dict[sample] = hist
            legend.AddEntry(hist.GetPtr(), sample, "f" if args.type == "stack" else "l")

        for hist in histos_dict.values():
            stack.Add(hist.GetPtr())

        canvas = ROOT.TCanvas("", "", 800, 600)
        canvas.SetTicks()
        if config_file.set_logy: canvas.SetLogy()
        stack.Draw("HIST") if args.type == "stack" else stack.Draw("HIST nostack")
        if args.type == "stack": stack.SetMinimum(1)
        
        ## allow upper space for legend
        if config_file.set_logy: stack.SetMaximum(10 * stack.GetMaximum()) 
        elif config_file.set_logy and args.type == "stack": stack.SetMaximum(1.5 * stack.GetMaximum())
        
        latex = ROOT.TLatex()
        latex.DrawLatexNDC(0.7,0.91,config_file.dataset_legend)
        latex.SetTextSize(0.045)
        latex.DrawLatexNDC(0.17, 0.84,"#bf{ #font[62]{CMS} #font[52]{Preliminary} }")
        legend.Draw()
        canvas.SaveAs(os.path.join(config_file.output_plots_dir, args.type, f"{variable[1]}."+config_file.plot_format))
        

if __name__ == "__main__":
    
    start_time = time.time()

    config_file = config.Config()
    
    os.makedirs(os.path.join(config_file.output_plots_dir, args.type), exist_ok=True)

    ## samples will be stacked in this order
    config_file.add_sample(name="DYJets", root_file="DYJets_tree.root",cuts=1)
    config_file.add_sample(name="ggH", root_file="ggH_tree.root",cuts=1)
    config_file.add_sample(name="VBF", root_file="VBF_tree.root",cuts=1)
    config_file.add_sample(name="bbH", root_file="bbH_tree.root",cuts=1)
    config_file.add_sample(name="Hc", root_file="Hc_tree.root",cuts=1)
    #config_file.add_sample(name="tqH", root_file="tqH_tree.root",cuts=1)
    config_file.add_sample(name="ttH", root_file="ttH_tree.root",cuts=1)
    config_file.add_sample(name="VH", root_file="VH_tree.root",cuts=1)
    config_file.add_sample(name="ZZ", root_file="ZZ_tree.root",cuts=1)

    create_plots(config_file)
    
    end_time = time.time()
    print(f"Elapsed time: {(end_time - start_time)/60:.2f} minutes")
