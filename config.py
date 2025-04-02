import ROOT

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
      
    ## [branch name, plot name, x-axis label, nbins, xlow, xhigh]
    self.vars = [
      # [self.el_prefix + "pt","el_pt","Electron p_{T} [GeV]", 100, 0, 200],
      # [self.mu_prefix + "pt","mu_pt","Muon p_{T} [GeV]", 100, 0, 200],
      [self.ZLall_prefix + "pt2", "l_pt", "Extra lepton p_{T} [GeV]", 100, 0, 200],
      [self.ZLalle_prefix + "pt2", "e_pt", "Extra electron p_{T} [GeV]", 100, 0, 200],
      [self.ZLallmu_prefix + "pt2", "mu_pt", "Extra muon p_{T} [GeV]", 100, 0, 200],
      [self.ZLall_prefix + "eta2", "l_eta", "Extra lepton #eta [GeV]", 100, -3, 3],
      [self.ZLalle_prefix + "eta2", "e_eta", "Extra electron #eta [GeV]", 100, -3, 3],
      [self.ZLallmu_prefix + "eta2", "mu_eta", "Extra muon #eta [GeV]", 100, -3, 3],
      [self.ZLpass_prefix + "pt2", "l_pass_pt", "Extra lepton passed p_{T} [GeV]", 100, 0, 200],
      [self.ZLpasse_prefix + "pt2", "e_pass_pt", "Extra electron passed p_{T} [GeV]", 100, 0, 200],
      [self.ZLpassmu_prefix + "pt2", "mu_pass_pt", "Extra muon passed p_{T} [GeV]", 100, 0, 200],
      [self.ZLpass_prefix + "eta2", "l_pass_eta", "Extra lepton passed #eta [GeV]", 100, -3, 3],
      [self.ZLpasse_prefix + "eta2", "e_pass_eta", "Extra electron passed #eta [GeV]", 100, -3, 3],
      [self.ZLpassmu_prefix + "eta2", "mu_pass_eta", "Extra muon passed #eta [GeV]", 100, -3, 3],
      ]
    
    self.output_plots_dir = "plots/trees_01_04/"
    self.base_dir = "/eos/user/n/nplastir/H+c/trees_01_04/mc/2022/merged"
    self.cuts = "1" # if you don't want cuts remember to put "1"
    self.weights =  "genWeight * xsecWeight * lumiwgt * puWeight * muEffWeight * elEffWeight" #"LHEScaleWeightNorm * LHEPdfWeightNorm * PSWeightNorm"
    self.plot_format = "png"
    self.energy = "13.6"
    self.dataset_legend = "7.98"
#     lumi_dict = {
#     "2016APV": 19.52,
#     "2016": 16.81,
#     "2017": 41.53,
#     "2018": 59.74,
#     "2022": 7.98, 
#     "2022EE": 26.67, 
#     "2023": 17.794, 
#     "2023BPix": 9.451
# }
    self.stack_ymin = 1
    self.stack_ymax = 5e6
    self.set_logy = False 
    self.samples_dict = {}
    
    # ## plot legend
    # self.legend = {
    #   "ggH":"ggH", 
    #   "VBF":"VBF", 
    #   "WplusH":"WplusH", 
    #   "WminusH":"WminusH", 
    #   "ZH":"ZH", 
    #   "ttH":"ttH",
    #   "bbH":"bbH",
    #   "qqZZ": "qqZZ",
    #   "ggZZ": "ggZZ",
    #   # "WWZ": "WWZ",
    #   # "WZZ": "WZZ",
    #   # "ZZZ": "ZZZ",
    #   # "TTWW": "TTWW",
    #   # "TTZZ": "TTZZ",
    #   # "WZ": "WZ",
    #   # "DYJets":"DYJets",
    #   # "TTto2L2Nu":"TTto2L2Nu",
    #   # "Hc":"Hc",
    # }   
    
  ## YOU DON'T NEED TO CHANGE ANYTHING HERE
  ## useful functions
  
  def add_sample(self,name,root_file,cuts):
    self.samples_dict[name] = [root_file,cuts]

  def get_samples_filenames(self):
    filenames = []
    for sample in self.samples_dict:
        filenames.append(self.samples_dict[sample][0])
    return filenames