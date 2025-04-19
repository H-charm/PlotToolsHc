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
      [self.H4e_prefix + "mass","Hcandidate_mass_4e","4e mass [GeV]", 56, 70, 350],
      [self.H4mu_prefix + "mass","Hcandidate_mass_4mu","4#mu mass [GeV]", 56, 70, 350],
      [self.H2e2mu_prefix + "mass","Hcandidate_mass_2e2mu","2e2#mu mass [GeV]", 56, 70, 350],
      # [self.H_prefix + "mass_4mu","Hcandidate_mass_4mu","4#mu mass [GeV]", 56, 70, 350],
      # [self.H_prefix + "mass_4e","Hcandidate_mass_4e","4e mass [GeV]", 56, 70, 350],
      # [self.H_prefix + "mass_2e2mu","Hcandidate_mass_2e2mu","2e2#mu mass [GeV]", 56, 70, 350],
      # [self.H_prefix + "pt","Hcandidate_pt","H candidate p_{T} [GeV]", 100, 0, 200],
      # [self.H_prefix + "eta","Hcandidate_eta","H candidate #eta", 40, -8, 8],
      # [self.H_prefix + "phi","Hcandidate_phi","H candidate #phi [rad]", 40, -4, 4],
      [self.ZZ_prefix + "mass","ZZcandidate_mass","ZZ candidate mass [GeV]", 56, 70, 350],
      [self.ZZ4e_prefix + "mass","ZZcandidate_mass_4e","4e mass [GeV]", 56, 70, 350],
      [self.ZZ4mu_prefix + "mass","ZZcandidate_mass_4mu","4#mu mass [GeV]", 56, 70, 350],
      [self.ZZ2e2mu_prefix + "mass","ZZcandidate_mass_2e2mu","2e2#mu mass  [GeV]", 56, 70, 350],
      # [self.ZZ_prefix + "mass_4mu","ZZcandidate_mass_4mu","4#mu mass [GeV]", 56, 70, 350],
      # [self.ZZ_prefix + "mass_4e","ZZcandidate_mass_4e","4e mass [GeV]", 56, 70, 350],
      # [self.ZZ_prefix + "mass_2e2mu","ZZcandidate_mass_2e2mu","2e2#mu mass [GeV]", 56, 70, 350],
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
    
    self.output_plots_dir = "plots/trees_24_02/test"
    self.base_dir = "/eos/user/n/nplastir/H+c/trees_24_02/mc/2022_2023_Combined"
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
      "2022_2023_Combined":     ("13.6", "61.9"),
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