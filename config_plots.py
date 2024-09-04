import ROOT

class Config:
  
  def __init__(self):  

    ## [name, plot name, x-axis label, nbins, xlow, xhigh]
    self.mcdata_branches = [
    # Lepton 1 branches
    ["lep1_pt", "lep1_pt", "Leading Lepton p_{T} [GeV]", 10, 0, 200],
    ["lep1_eta", "lep1_eta", "Leading Lepton #eta", 12, -2.5, 2.5],
    ["lep1_phi", "lep1_phi", "Leading Lepton #phi [rad]", 16, -4, 4],
    ["lep1_pdgId", "lep1_pdgId", "Leading Lepton PDG ID", 32, -16, 16],
    ["lep1_charge", "lep1_charge", "Leading Lepton Charge", 3, -1.5, 1.5],

    # Lepton 2 branches
    ["lep2_pt", "lep2_pt", "Trailing Lepton p_{T} [GeV]", 10, 0, 200],
    ["lep2_eta", "lep2_eta", "Trailing Lepton #eta", 12, -2.5, 2.5],
    ["lep2_phi", "lep2_phi", "Trailing Lepton #phi [rad]", 16, -4, 4],
    ["lep2_pdgId", "lep2_pdgId", "Trailing Lepton PDG ID", 32, -16, 16],
    ["lep2_charge", "lep2_charge", "Trailing Lepton Charge", 3, -1.5, 1.5],

    # Lepton 3 branches
    ["lep3_pt", "lep3_pt", "Third Lepton p_{T} [GeV]", 10, 0, 200],
    ["lep3_eta", "lep3_eta", "Third Lepton #eta", 12, -2.5, 2.5],
    ["lep3_phi", "lep3_phi", "Third Lepton #phi [rad]", 16, -4, 4],
    ["lep3_pdgId", "lep3_pdgId", "Third Lepton PDG ID", 32, -16, 16],
    ["lep3_charge", "lep3_charge", "Third Lepton Charge", 3, -1.5, 1.5],

    # Lepton 4 branches
    ["lep4_pt", "lep4_pt", "Fourth Lepton p_{T} [GeV]", 10, 0, 200],
    ["lep4_eta", "lep4_eta", "Fourth Lepton #eta", 12, -2.5, 2.5],
    ["lep4_phi", "lep4_phi", "Fourth Lepton #phi [rad]", 16, -4, 4],
    ["lep4_pdgId", "lep4_pdgId", "Fourth Lepton PDG ID", 32, -16, 16],
    ["lep4_charge", "lep4_charge", "Fourth Lepton Charge", 3, -1.5, 1.5],

    # Jet branches
    # ["n_jets", "n_jets", "Number of Jets", 10, 0, 10],
    # ["n_ak4", "n_ak4", "Number of AK4 Jets", 10, 0, 10],
    # ["ak4_bdisc", "ak4_bdisc", "AK4 Jet b-Discriminator", 20, 0, 1],
    # ["ak4_cvbdisc", "ak4_cvbdisc", "AK4 Jet c-Discriminator", 20, 0, 1],
    # ["ak4_cvldisc", "ak4_cvldisc", "AK4 Jet cV-l Discriminator", 20, 0, 1],

    # Z-candidate branches
    ["n_Zcandidates", "n_Zcandidates", "Number of Z Candidates", 5, 0, 5],
    ["Zcandidate_mass", "Zcandidate_mass", "Z Candidate Mass [GeV]", 30, 0, 120],
    ["Zcandidate_pt", "Zcandidate_pt", "Z Candidate p_{T} [GeV]", 20, 0, 200],
    ["Zcandidate_eta", "Zcandidate_eta", "Z Candidate #eta", 12, -2.5, 2.5],
    ["Zcandidate_phi", "Zcandidate_phi", "Z Candidate #phi [rad]", 16, -4, 4],
    ["Zcandidate_onshell_mass", "Zcandidate_onshell_mass", "On-shell Z Candidate Mass [GeV]", 30, 0, 120],
    ["Zcandidate_offshell_mass", "Zcandidate_offshell_mass", "Off-shell Z Candidate Mass [GeV]", 30, 0, 120],

    # Higgs-candidate branches
    ["n_Hcandidates", "n_Hcandidates", "Number of H Candidates", 5, 0, 5],
    ["Hcandidate_mass", "Hcandidate_mass", "H Candidate Mass [GeV]", 30, 0, 300],
    ["Hcandidate_pt", "Hcandidate_pt", "H Candidate p_{T} [GeV]", 20, 0, 200],
    ["Hcandidate_eta", "Hcandidate_eta", "H Candidate #eta", 12, -2.5, 2.5],
    ["Hcandidate_phi", "Hcandidate_phi", "H Candidate #phi [rad]", 16, -4, 4],
]

    
    
    self.output_plots_dir = "plots/"
    self.channels = [] 
    self.base_dir = "your_tree_directory"
    self.plot_format = "png"
    self.dataset_legend = "59.8 fb^{-1} (13 TeV)"
    self.plot_type = "#bf{ #font[61]{CMS} #font[52]{Preliminary} } "
    self.tree_name = "Events"
    self.stack_ymin = 1
    self.stack_ymax = 5e8
    self.set_logy = True
    self.weights = None
    self.samples_dict = {} ## leave this empty
    self.normalize_to_data = True # normalize all MC histos to Data 
    
    ## plot legend
    self.legend = {
            "DYJets": "DY+Jets",
            "VBF": "VBF",
            "WminusH": "W^{-}H",
            "WplusH": "W^{+}H",
            "ZH": "ZH",
            "ZZ": "ZZ",
            "bbH": "bbH",
            "ggH": "ggH",
            "tqH": "tqH",
            "ttH": "ttH",
        }
        
        ## plot colors
        
    cms_color_0 = ROOT.TColor.GetColor(63,144,218) #blue
    cms_color_1 = ROOT.TColor.GetColor(255,19,14) #orange
    cms_color_2 = ROOT.TColor.GetColor(189,31,1) #red
    cms_color_3 = ROOT.TColor.GetColor(131,45,182) #purple
    cms_color_4 = ROOT.TColor.GetColor(148,164,162) #gray
    cms_color_5 = ROOT.TColor.GetColor(169,107,89) #brown
    cms_color_6 = ROOT.TColor.GetColor(231,99,0) #orange
    cms_color_7 = ROOT.TColor.GetColor(185,172,112) #tan
    cms_color_8 = ROOT.TColor.GetColor(113,117,129) #gray
    cms_color_9 = ROOT.TColor.GetColor(146,218,221) #lightblue


    self.colors = {
            "DYJets": cms_color_0,
            "VBF": cms_color_1,
            "WminusH": cms_color_2,
            "WplusH": cms_color_3,
            "ZH": cms_color_4,
            "ZZ": cms_color_5,
            "bbH": cms_color_6,
            "ggH": cms_color_7,
            "tqH":cms_color_8,
            "ttH": cms_color_9,
        }
  ## YOU DON'T NEED TO CHANGE ANYTHING HERE
  ## useful functions
  def add_sample(self,name,root_file,cuts):
    self.samples_dict[name] = [root_file,cuts]
    
  def get_samples_list(self):
    return self.samples_dict

  def print_samples_info(self):
    for sample in self.samples_dict.keys():
        print(f"Sample name: {sample} \t sample file: {self.samples_dict[sample][0]} \t sample cuts: {self.samples_dict[sample][1]}")
  
  def get_sample_filename(self,sample_name):
    return self.samples_dict[sample_name][0]

  def get_data_filenames(self):
    for sample_name in self.samples_dict:
      if sample_name == "Data": return self.samples_dict[sample_name][0]
  
  def clear_samples_list(self):
    self.samples_dict.clear()
