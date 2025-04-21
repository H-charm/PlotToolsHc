import ROOT
from array import array
import os

ROOT.gStyle.SetLegendBorderSize(0)
ROOT.gStyle.SetPadLeftMargin(0.15) 
ROOT.gStyle.SetTitleYOffset(1.5) 
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetTextSize(0.035)  
ROOT.gStyle.SetGridStyle(2)
ROOT.gStyle.SetGridColor(ROOT.kGray+2)
ROOT.gStyle.SetGridWidth(1)

class Config:
  
  def __init__(self):  
  
    self.mu_prefix = "mu_"
    self.el_prefix = "el_"
    self.lep_prefix = "lep_"
    self.jet_prefix = "jet_"
    self.Z_prefix = "Z_"
    self.ZZ_prefix = "ZZ_"
    self.H_prefix = "H_"  
    self.H4e_prefix = "H4e_"
    self.H4mu_prefix = "H4mu_"
    self.H2e2mu_prefix = "H2e2mu_"
    self.ZZ4e_prefix="ZZ4e_"
    self.ZZ4mu_prefix="ZZ4mu_"
    self.ZZ2e2mu_prefix="ZZ2e2mu_"
    self.ZLall_prefix = "ZLall_"
    self.ZLalle_prefix = "ZLalle_"
    self.ZLallmu_prefix = "ZLallmu_"
    self.ZLpass_prefix = "ZLpass_"
    self.ZLpasse_prefix = "ZLpasse_"
    self.ZLpassmu_prefix = "ZLpassmu_"

    self.ZLL2P2F_prefix = "ZLL2P2F_"
    self.ZLL2P2F4e_prefix = "ZLL2P2F4e_"
    self.ZLL2P2F4mu_prefix = "ZLL2P2F4mu_"
    self.ZLL2P2F2e2mu_prefix = "ZLL2P2F2e2mu_"
    self.ZLL2P2F2mu2e_prefix = "ZLL2P2F2mu2e_"

    self.ZLL3P1F_prefix = "ZLL3P1F_"
    self.ZLL3P1F4e_prefix = "ZLL3P1F4e_"
    self.ZLL3P1F4mu_prefix = "ZLL3P1F4mu_"
    self.ZLL3P1F2e2mu_prefix = "ZLL3P1F2e2mu_"
    self.ZLL3P1F2mu2e_prefix = "ZLL3P1F2mu2e_"

    self.ZLLSSCR_prefix = "ZLLSSCR_"
    self.ZLLSSCR4e_prefix = "ZLLSSCR4e_"
    self.ZLLSSCR4mu_prefix = "ZLLSSCR4mu_"
    self.ZLLSSCR2e2mu_prefix = "ZLLSSCR2e2mu_"
    self.ZLLSSCR2mu2e_prefix = "ZLLSSCR2mu2e_"
      
    ## [branch name, plot name, x-axis label, nbins, xlow, xhigh]
    self.vars = [
      [self.ZLall_prefix + "pt2", "l_pt", "p_{T}(l) [GeV]",[5, 7, 10, 20, 30, 40, 50, 80]],
      [self.ZLalle_prefix + "pt2", "e_pt", "p_{T}(e) [GeV]",[7, 10, 20, 30, 40, 50, 80]],
      [self.ZLallmu_prefix + "pt2", "mu_pt", "p_{T}(#mu) [GeV]",[5, 7, 10, 20, 30, 40, 50, 80]],
      [self.ZLall_prefix + "eta2", "l_eta", "#eta(l) [GeV]", 48, -2.4, 2.4],
      [self.ZLalle_prefix + "eta2", "e_eta", "#eta(e) [GeV]", 48, -2.4, 2.4],
      [self.ZLallmu_prefix + "eta2", "mu_eta", "#eta(#mu) [GeV]", 48, -2.4, 2.4],
      [self.ZLpass_prefix + "pt2", "l_pass_pt", "p_{T}(l) [GeV]",[5, 7, 10, 20, 30, 40, 50, 80]],
      [self.ZLpasse_prefix + "pt2", "e_pass_pt", "p_{T}(e) [GeV]",[7, 10, 20, 30, 40, 50, 80]],
      [self.ZLpassmu_prefix + "pt2", "mu_pass_pt", "p_{T}(#mu) [GeV]",[5, 7, 10, 20, 30, 40, 50, 80]],
      [self.ZLpass_prefix + "eta2", "l_pass_eta", "#eta(l) [GeV]", 48, -2.4, 2.4],
      [self.ZLpasse_prefix + "eta2", "e_pass_eta", "#eta(e) [GeV]", 48, -2.4, 2.4],
      [self.ZLpassmu_prefix + "eta2", "mu_pass_eta", "#eta(#mu) [GeV]", 48, -2.4, 2.4],
    ]
    self.vars_ZLL =[
      [self.ZLL2P2F_prefix + "mass","2P2F_mass","m [GeV]", 40, 70, 870],
      [self.ZLL2P2F4e_prefix + "mass","2P2F_mass_4e","m(4e) [GeV]", 40, 70, 870],
      [self.ZLL2P2F4mu_prefix + "mass","2P2F_mass_4mu","m(4#mu) [GeV]", 40, 70, 870],
      [self.ZLL2P2F2e2mu_prefix + "mass","2P2F_mass_2e2mu","m(2e2#mu) [GeV]", 40, 70, 870],

      [self.ZLL3P1F_prefix + "mass","3P1F_mass","m [GeV]", 40, 70, 870],
      [self.ZLL3P1F4e_prefix + "mass","3P1F_mass_4e","m(4e) [GeV]", 40, 70, 870],
      [self.ZLL3P1F4mu_prefix + "mass","3P1F_mass_4mu","m(4#mu) [GeV]", 40, 70, 870],
      [self.ZLL3P1F2e2mu_prefix + "mass","3P1F_mass_2e2mu","m(2e2#mu) [GeV]", 40, 70, 870],

      [self.ZLLSSCR_prefix + "mass","SSCR_mass","m [GeV]", 40, 70, 870],
      [self.ZLLSSCR4e_prefix + "mass","SSCR_mass_4e","m(4e) [GeV]", 40, 70, 870],
      [self.ZLLSSCR4mu_prefix + "mass","SSCR_mass_4mu","m(4#mu) [GeV]", 40, 70, 870],
      [self.ZLLSSCR2e2mu_prefix + "mass","SSCR_mass_2e2mu","m(2e2#mu) [GeV]", 40, 70, 870],
    ]
    
    self.output_plots_dir = "plots/trees_17_04/2023/"
    self.base_dir = "/eos/user/n/nplastir/H+c/trees_17_04/mc/2023/merged"
    self.cuts = "1" # if you don't want cuts remember to put "1"
    self.weights =  "genWeight * xsecWeight * lumiwgt * puWeight * muEffWeight * elEffWeight" #"LHEScaleWeightNorm * LHEPdfWeightNorm * PSWeightNorm"
    self.plot_format = "png"
    self.set_year_dependent_values()

    self.stack_ymin = 1
    self.stack_ymax = 5e6
    self.set_logy = False 
    self.samples_dict = {}
  
  ## YOU DON'T NEED TO CHANGE ANYTHING HERE
  ## useful functions
  
  def add_sample(self,name,root_file,cuts):
    self.samples_dict[name] = [root_file,cuts]

  def get_samples_filenames(self):
    filenames = []
    for sample in self.samples_dict:
        filenames.append(self.samples_dict[sample][0])
    return filenames

  def set_year_dependent_values(self):
    # Define mapping of years to (energy, dataset_legend)
    year_settings = {
      "2015":          ("13", "19.52"),
      "2016APV":       ("13", "19.52"),
      "2016":          ("13", "16.81"),
      "2017":          ("13", "41.53"),
      "2018":          ("13", "59.74"),
      "2022":          ("13.6", "7.98"),
      "2022EE":        ("13.6", "26.67"),
      "2023":          ("13.6", "17.794"),
      "2023BPix":      ("13.6", "9.451"),
      "2022_Combined": ("13.6", "34.65"),
      "2023_Combined": ("13.6", "27.25"),
      "2022_2023":     ("13.6", "61.9"),
    }

    # Split the base_dir path and look for exact matches
    path_parts = os.path.normpath(self.base_dir).split(os.sep)

    for year_key in year_settings:
      if year_key in path_parts:
        self.energy, self.dataset_legend = year_settings[year_key]
        print(f"[INFO] Detected year: {year_key}, set energy: {self.energy}, legend: {self.dataset_legend}")
        return

    print("[WARNING] No known year found in base_dir. Using default energy and legend.")
    self.energy = "13.6"
    self.dataset_legend = "7.98"
