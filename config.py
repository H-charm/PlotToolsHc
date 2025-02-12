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
      
    ## [branch name, plot name, x-axis label, nbins, xlow, xhigh]
    self.vars = [
      # [self.el_prefix + "pt","el_pt","Electron p_{T} [GeV]", 100, 0, 200],
      # [self.mu_prefix + "pt","mu_pt","Muon p_{T} [GeV]", 100, 0, 200],
      # [self.Z_prefix + "mass","Zcandidate_mass","Z candidate mass [GeV]", 100, 0, 150],
      # [self.Z_prefix + "pt","Zcandidate_pt","Z candidate p_{T} [GeV]", 100, 0, 200],
      # [self.Z_prefix + "eta","Zcandidate_eta","Z candidate #eta", 40, -8, 8],
      # [self.Z_prefix + "phi","Zcandidate_phi","Z candidate #phi [rad]", 40, -4, 4],
      # [self.Z_prefix + "onshell_mass","Zcandidate_onshell_mass","on-shell Z candidate mass [GeV]", 100, 0, 120],
      # [self.Z_prefix + "offshell_mass","Zcandidate_offshell_mass","off-shell Z candidate mass [GeV]", 60, 0, 120],
      [self.H_prefix + "mass","Hcandidate_mass","H candidate mass [GeV]", 56, 70, 350],
      [self.H_prefix + "mass_4mu","Hcandidate_mass_4mu","4#mu mass [GeV]", 56, 70, 350],
      [self.H_prefix + "mass_4e","Hcandidate_mass_4e","4e mass [GeV]", 56, 70, 350],
      [self.H_prefix + "mass_2e2mu","Hcandidate_mass_2e2mu","2e2#mu mass [GeV]", 56, 70, 350],
      # [self.H_prefix + "pt","Hcandidate_pt","H candidate p_{T} [GeV]", 100, 0, 200],
      # [self.H_prefix + "eta","Hcandidate_eta","H candidate #eta", 40, -8, 8],
      # [self.H_prefix + "phi","Hcandidate_phi","H candidate #phi [rad]", 40, -4, 4],
      [self.ZZ_prefix + "mass","ZZcandidate_mass","ZZ candidate mass [GeV]", 56, 70, 350],
      [self.ZZ_prefix + "mass_4mu","ZZcandidate_mass_4mu","4#mu mass [GeV]", 56, 70, 350],
      [self.ZZ_prefix + "mass_4e","ZZcandidate_mass_4e","4e mass [GeV]", 56, 70, 350],
      [self.ZZ_prefix + "mass_2e2mu","ZZcandidate_mass_2e2mu","2e2#mu mass [GeV]", 56, 70, 350],
      # [self.ZZ_prefix + "pt","ZZcandidate_pt","ZZ candidate p_{T} [GeV]", 100, 0, 200],
      # [self.ZZ_prefix + "eta","ZZcandidate_eta","ZZ candidate #eta", 40, -8, 8],
      # [self.ZZ_prefix + "phi","ZZcandidate_phi","ZZ candidate #phi [rad]", 40, -4, 4],
      # [self.jet_prefix + "mass[0]","ak4_mass_0","leading jet mass [GeV]", 100, 0, 200],
      # [self.jet_prefix + "pt[0]","ak4_pt_0","leading jet p_{T} [GeV]", 100, 0, 200],
      # [self.jet_prefix + "eta[0]","ak4_eta_0","leading jet #eta", 80, -8, 8],
      # [self.jet_prefix + "cvbdisc[0]","ak4_cvbdisc_0","leading jet c vs b score", 50, 0, 1],
      # [self.jet_prefix + "cvldisc[0]","ak4_cvldisc_0","leading jet c v l score", 50, 0, 1],      
      # [self.jet_prefix + "bdisc[0]","ak4_bdisc_0","leading jet b score", 50, 0, 1],
      # ["deltaR(lep1_eta, lep2_eta, lep1_phi, lep2_phi)","dR_lep1_lep_2","#DeltaR(lep1,lep2)", 60, 0, 6],
      # ["deltaR(lep1_eta, lep3_eta, lep1_phi, lep3_phi)","dR_lep1_lep_3","#DeltaR(lep1,lep3)", 60, 0, 6],
      # ["deltaR(lep1_eta, lep4_eta, lep1_phi, lep4_phi)","dR_lep1_lep_4","#DeltaR(lep1,lep4)", 60, 0, 6],
      # ["deltaR(lep2_eta, lep3_eta, lep2_phi, lep3_phi)","dR_lep2_lep_3","#DeltaR(lep2,lep3)", 60, 0, 6],
      # ["deltaR(lep2_eta, lep4_eta, lep2_phi, lep4_phi)","dR_lep2_lep_4","#DeltaR(lep2,lep4)", 60, 0, 6],
      # ["deltaR(lep3_eta, lep4_eta, lep3_phi, lep4_phi)","dR_lep3_lep_4","#DeltaR(lep3,lep4)", 60, 0, 6],
      ]
    
    self.output_plots_dir = "plots/trees_11_02_lepflav/weighted_test_wpu/2022"
    self.base_dir = "/eos/user/n/nplastir/H+c/trees_11_02_lepflav/mc/2022/merged"
    self.cuts = "1" # if you don't want cuts remember to put "1"
    self.weights =  "genWeight * 7.98 * 1000 " #"genWeight * xsecWeight * puWeight" #"LHEScaleWeightNorm * LHEPdfWeightNorm * PSWeightNorm"
    self.plot_format = "png"
    self.dataset_legend = "9.6" #"34.7"
    self.stack_ymin = 1
    self.stack_ymax = 5e6
    self.set_logy = False 
    self.samples_dict = {}
    
    ## plot legend
    self.legend = {
      "ggH":"ggH",
      "VBF":"VBF",
      "WplusH":"WplusH",
      "WminusH":"WminusH",
      "ZH":"ZH",
      "ttH":"ttH",
      "bbH":"bbH",
      "qqZZ": "qqZZ",
      "ggZZ": "ggZZ",
      # "WWZ": "WWZ",
      # "WZZ": "WZZ",
      # "ZZZ": "ZZZ",
      # "TTWW": "TTWW",
      # "TTZZ": "TTZZ",
      # "WZ": "WZ",
      # "DYJets":"DYJets",
      # "TTto2L2Nu":"TTto2L2Nu",
      # "Hc":"Hc",
    }
    
    ## plot colors
    self.colors = {
      "DYJets": 829,
      # "ggH": 38,
      # "VBF": 43,
      # "bbH": 821,
      # "Hc": 880,
      # "tqH": 829,
      # "ttH": 811,
      # "VH": 859,
      "WZ": 859,
      "ZZ": 623,
    }  
    
    
    
  ## YOU DON'T NEED TO CHANGE ANYTHING HERE
  ## useful functions
  
  def add_sample(self,name,root_file,cuts):
    self.samples_dict[name] = [root_file,cuts]

  def get_samples_filenames(self):
    filenames = []
    for sample in self.samples_dict:
        filenames.append(self.samples_dict[sample][0])
    return filenames