from inspect import stack
from itertools import chain
import math
import ROOT
import config_plots
import array
import os


sample_cuts_dict = {
    "tt_bb": "(genEventClassifier==9)",
    "tt_bj": "(genEventClassifier==7 || genEventClassifier==8)",
    "tt_bb_4fs": "(genEventClassifier==9)",
    "tt_bj_4fs": "(genEventClassifier==7 || genEventClassifier==8)",
    "tt_bb_5fs": "(genEventClassifier==9)",
    "tt_bj_5fs": "(genEventClassifier==7 || genEventClassifier==8)",
    "tt_cc": "(genEventClassifier==6)",
    "tt_cj": "(genEventClassifier==4 || genEventClassifier==5)",        
    "tt_lf": "(tt_category==0 && higgs_decay==0)",
    "ttZqq": "(z_decay!=5) && (z_decay!=4)",
    "ttZcc": "(z_decay==4)",
    "ttZbb": "(z_decay==5)",
    "ttH_hww": "(higgs_decay==24)",
    "": "1"
}

trg_dict = {
    "e": "(abs(lep1_pdgId)==11 && passTrigEl && !(lep1_phi>-1.57 && lep1_phi<-0.87 && lep1_eta<-1.3))", ## last part is to fix 2018 issue in hadron calo
    "m": "(abs(lep1_pdgId)==13 && passTrigMu)",
    "ee": "(abs(lep1_pdgId)==11 && abs(lep2_pdgId)==11 && (passTrigElEl || passTrig2L_extEl))",
    "mm": "(abs(lep1_pdgId)==13 && abs(lep2_pdgId)==13 && (passTrigMuMu || passTrig2L_extMu))",
    "em": "(abs(lep1_pdgId)!=abs(lep2_pdgId) && (passTrigElMu || passTrig2L_extEl || passTrig2L_extMu))",
    "FH": "(passTrig0L || passTrig0L_ext)",
    "DL": "((abs(lep1_pdgId)==11 && abs(lep2_pdgId)==11 && (passTrigElEl || passTrig2L_extEl)) || (abs(lep1_pdgId)==13 && abs(lep2_pdgId)==13 && (passTrigMuMu || passTrig2L_extMu)) || (abs(lep1_pdgId)!=abs(lep2_pdgId) && (passTrigElMu || passTrig2L_extEl || passTrig2L_extMu)))",
    "None": "1"
}

syst_weights_dict = {
    "CMS_LHE_weights_scale_muF_Up": "LHEScaleWeight[5]*LHEScaleWeightNorm[5]",
    "CMS_LHE_weights_scale_muF_Down": "LHEScaleWeight[3]*LHEScaleWeightNorm[3]",
    "CMS_LHE_weights_scale_muR_Up": "LHEScaleWeight[7]*LHEScaleWeightNorm[7]",
    "CMS_LHE_weights_scale_muR_Down": "LHEScaleWeight[1]*LHEScaleWeightNorm[1]",
    "CMS_PS_isr_Up": "PSWeight[2]*PSWeightNorm[2]",
    "CMS_PS_isr_Down": "PSWeight[0]*PSWeightNorm[0]",
    "CMS_PS_fsr_Up": "PSWeight[3]*PSWeightNorm[3]",
    "CMS_PS_fsr_Down": "PSWeight[1]*PSWeightNorm[1]",
}

category_cuts_dict = {
    "catHcc": "nnCategory10(score_ttHcc, score_ttHbb, score_ttZqq, score_ttZcc, score_ttZbb, score_ttLF, score_ttcj, score_ttcc, score_ttbj, score_ttbb)==0",
    "catHbb": "nnCategory10(score_ttHcc, score_ttHbb, score_ttZqq, score_ttZcc, score_ttZbb, score_ttLF, score_ttcj, score_ttcc, score_ttbj, score_ttbb)==1",
    "catZcc": "nnCategory10(score_ttHcc, score_ttHbb, score_ttZqq, score_ttZcc, score_ttZbb, score_ttLF, score_ttcj, score_ttcc, score_ttbj, score_ttbb)==2",
    "catZbb": "nnCategory10(score_ttHcc, score_ttHbb, score_ttZqq, score_ttZcc, score_ttZbb, score_ttLF, score_ttcj, score_ttcc, score_ttbj, score_ttbb)==3",
    "catLF": "nnCategory10(score_ttHcc, score_ttHbb, score_ttZqq, score_ttZcc, score_ttZbb, score_ttLF, score_ttcj, score_ttcc, score_ttbj, score_ttbb)==4",
    "catCJ": "nnCategory10(score_ttHcc, score_ttHbb, score_ttZqq, score_ttZcc, score_ttZbb, score_ttLF, score_ttcj, score_ttcc, score_ttbj, score_ttbb)==5",
    "catCC": "nnCategory10(score_ttHcc, score_ttHbb, score_ttZqq, score_ttZcc, score_ttZbb, score_ttLF, score_ttcj, score_ttcc, score_ttbj, score_ttbb)==6",
    "catBJ": "nnCategory10(score_ttHcc, score_ttHbb, score_ttZqq, score_ttZcc, score_ttZbb, score_ttLF, score_ttcj, score_ttcc, score_ttbj, score_ttbb)==7",
    "catBB": "nnCategory10(score_ttHcc, score_ttHbb, score_ttZqq, score_ttZcc, score_ttZbb, score_ttLF, score_ttcj, score_ttcc, score_ttbj, score_ttbb)==8",   
}

def add_overflow(h):
    nbins = h.GetNbinsX()+1
    e1 = h.GetBinError(nbins-1)
    e2 = h.GetBinError(nbins)
    h.AddBinContent(nbins-1, h.GetBinContent(nbins))
    h.SetBinError(nbins-1, math.sqrt(e1*e1 + e2*e2))
    h.SetBinContent(nbins, 0)
    h.SetBinError(nbins, 0)
    return h

def add_underflow(h):
    e1 = h.GetBinError(1)
    e0 = h.GetBinError(0)
    h.AddBinContent(1, h.GetBinContent(0))
    h.SetBinError(1, math.sqrt(e1 * e1 + e0 * e0))
    h.SetBinContent(0, 0)
    h.SetBinError(0, 0)
    return h


def get_histogram(sample_name, filename, branch, channel, sample_cuts, fill=True, isMC=True):
    """
    Create and return a histogram from ROOT RDataFrame.

    :param sample_name: Name of the sample (used for applying weights).
    :param filename: File name or list of file names to load.
    :param branch: Tuple containing branch information (name, label, etc.).
    :param channel: Channel information (not used in this version).
    :param sample_cuts: Cuts to apply to the data.
    :param fill: Boolean to determine if the histogram should be filled with color.
    :param isMC: Boolean to determine if the sample is MC.
    :param weights: Weight expression for the histogram; if None, no weights are applied.
    :return: A ROOT TH1D histogram.
    """
    print(f"Getting histogram for sample {sample_name} from {filename}:")
    config_file = config_plots.Config()
    tree = ROOT.TChain(config_file.tree_name)

    if isMC:
        tree.Add(config_file.base_dir + filename)    
    else:
        config_file.weights = "1"  # no weights for data
        if isinstance(filename, str):
            tree.Add(config_file.base_dir + "/data/" + filename)
        else:
            for i in filename:
                print(f"Adding data file {i}")
                tree.Add(config_file.base_dir + "/data/" + i)
    
    # Define weights, or use default weight if none provided
    weights = config_file.weights
    if weights is None:
        weights = "1"  # Default weight if none specified
    
    if sample_name in ["tt_bb_4fs", "tt_bj_4fs"]:
        weights += "*0.7559"  # 5FS / 4FS for tt+bb, tt+b
    if sample_name in ["tt_bb_4fs", "tt_bj_4fs", "tt_bb_5fs", "tt_bj_5fs", "tt_cj", "tt_cc", "tt_lf"]:
        weights += "*topptWeight"
    
    print(f"Weights: {weights}")

    ROOT.EnableImplicitMT()
    rdf = ROOT.RDataFrame(tree)
    
    # Use weights if specified, otherwise just use the variable itself
    if weights == "1":
        h = rdf.Define("plotvar_", branch[0]).Histo1D(("h", ";" + branch[2] + ";", branch[3], branch[4], branch[5]), "plotvar_")
    else:
        h = rdf.Define("plotvar_", branch[0]).Define("wgtvar_", weights).Histo1D(("h", ";" + branch[2] + ";", branch[3], branch[4], branch[5]), "plotvar_", "wgtvar_")
    
    # Set histogram appearance based on sample type
    if fill:
        h.SetFillColor(config_file.colors.get(sample_name, ROOT.kGray))  # Default to gray if color not found
    if isMC and fill:
        h.SetLineColor(ROOT.kBlack)
    elif isMC and not fill:
        h.SetLineColor(config_file.colors.get(sample_name, ROOT.kBlack))
    elif not isMC:
        h.SetMarkerStyle(20)
        h.SetLineColor(ROOT.kBlack)

    print(f"Bin contents: {[h.GetBinContent(i) for i in range(1, h.GetNbinsX() + 1)]}")
    print(f"Histo integral {h.Integral()}, entries {h.GetEntries()}")
    return h

    
    
def make_mcdata_ratio_plot(stack_hists,data_hist,channel,branch,leg,output_dir):
    
    config_file = config_plots.Config()
    c = ROOT.TCanvas(branch[0],"",800,800)
    c.Clear()
    c.SetTicks()
    if config_file.set_logy: 
        c.SetLogy()
    stack_ymin = config_file.stack_ymin
    stack_ymax = config_file.stack_ymax
    if config_file.set_logy and config_file.stack_ymin == 0: # log scale axis cannot start from 0
        stack_ymin = 1 
    stack_hists.SetMinimum(stack_ymin)
    stack_hists.SetMaximum(stack_ymax)

    ## total mc
    total_mc = data_hist.Clone("total_mc") #to get right dimensions
    total_mc.Reset()
    for hist in stack_hists.GetHists():
        total_mc.Add(hist)
        
    ## data / mc plot for lower pad (we remove mc / data from lower pad)
    h_data_over_mc = data_hist.Clone("h_data_over_mc") #to get right dimensions
    h_data_over_mc.Reset()
    h_data_over_mc.Divide(data_hist, total_mc)
    h_data_over_mc.SetMarkerStyle(20)
    h_data_over_mc.SetLineColor(ROOT.kBlack)
    
    ## total bkg unc
    bkg_unc = ROOT.TGraphAsymmErrors(total_mc)
    bkg_unc.SetFillColor(ROOT.kBlue)
    bkg_unc.SetFillStyle(3013)
    bkg_unc.SetLineStyle(0)
    bkg_unc.SetLineWidth(0)
    bkg_unc.SetMarkerSize(0)
    leg.AddEntry(bkg_unc,"Bkg. uncertainty","f")

    ## relative bkg unc
    hRelUnc = bkg_unc.Clone()
    for i in range(hRelUnc.GetN()):
        val = hRelUnc.GetY()[i]
        errUp = hRelUnc.GetErrorYhigh(i)
        errLow = hRelUnc.GetErrorYlow(i)
        if val==0: continue
        hRelUnc.SetPointEYhigh(i, errUp/val)
        hRelUnc.SetPointEYlow(i, errLow/val)
        hRelUnc.SetPoint(i, hRelUnc.GetX()[i], 1)

    hRelUnc.SetFillColor(ROOT.kBlue)
    hRelUnc.SetFillStyle(3013)
    hRelUnc.SetLineStyle(0)
    hRelUnc.SetLineWidth(0)
    hRelUnc.SetMarkerSize(0)

    ## ratio plot
    rp = ROOT.TRatioPlot(stack_hists,data_hist)
    rp.SetH2DrawOpt("e1p")
    rp.Draw()
    rp.GetLowYaxis().SetNdivisions(4,1,1)
    rp.GetLowerRefYaxis().SetTitle("Data / MC")
    rp.GetLowerRefYaxis().SetTitleOffset(1.55)
    # if branch[0].startswith("n_"): 
        # rp.GetLowerRefXaxis().SetNdivisions(-105,ROOT.kFALSE)
        # rp.GetLowerRefXaxis().CenterLabels()
    rp.SetGridlines([0.8,1,1.2])
    rp.SetSeparationMargin(0)
    rp.GetLowerRefGraph().SetMarkerColor(ROOT.kWhite)
    rp.GetLowerRefGraph().SetLineColor(ROOT.kWhite)
    rp.GetLowerRefGraph().SetMinimum(0.6)
    rp.GetLowerRefGraph().SetMaximum(1.4)
    rp.GetLowerPad().cd()
    hRelUnc.Draw("E2same")
    h_data_over_mc.Draw("e1p same")
    rp.GetUpperPad().cd()
    bkg_unc.Draw("E2same")
    leg.SetNColumns(2)
    leg.Draw()
    latex = ROOT.TLatex()
    latex.SetTextSize(0.05)
    latex.DrawLatexNDC(0.65,0.91,config_file.dataset_legend)
    latex.DrawLatexNDC(0.1, 0.91,config_file.plot_type)
    latex.DrawLatexNDC(0.15,0.81,channel)

    c.SaveAs(output_dir + channel + "_" + branch[1] + "." + config_file.plot_format)
    
def make_mc_only_plot(stack_hists, channel, branch, leg, output_dir):
    """
    Create and save a plot with only MC histograms stacked together.

    :param stack_hists: ROOT.THStack object with stacked MC histograms.
    :param channel: Channel name for the plot title and output file.
    :param branch: Tuple containing branch information for labeling.
    :param leg: ROOT.TLegend object to add entries.
    :param output_dir: Directory path where the plot will be saved.
    """
    config_file = config_plots.Config()
    c = ROOT.TCanvas(branch[0], "", 800, 800)
    c.Clear()
    c.SetTicks()
    
    if config_file.set_logy:
        c.SetLogy()
    
    stack_ymin = config_file.stack_ymin
    stack_ymax = config_file.stack_ymax
    
    if config_file.set_logy and stack_ymin == 0:  # Log scale axis cannot start from 0
        stack_ymin = 1
    
    stack_hists.SetMinimum(stack_ymin)
    stack_hists.SetMaximum(stack_ymax)
    
    # Draw the stack of MC histograms
    stack_hists.Draw("HIST")
    
    # Add legend entries
    leg.Draw()
    
    # Add additional plot information
    latex = ROOT.TLatex()
    latex.SetTextSize(0.05)
    latex.DrawLatexNDC(0.6, 0.91, config_file.dataset_legend)
    latex.DrawLatexNDC(0.11, 0.91, config_file.plot_type)
    
    # Save the plot
    c.SaveAs(output_dir + branch[1] + "." + config_file.plot_format)