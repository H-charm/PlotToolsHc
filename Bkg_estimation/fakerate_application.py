import ROOT
import os
import config
import argparse
import time

# Argument parser
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--data', type=str, help='Path to real data folder', required=True)
args = parser.parse_args()

# Helpers
def extract_scalar(x):
    try:
        # Try indexing, if it's an RVec or similar
        return float(x[0]) if len(x) > 0 else 0.0
    except Exception:
        # Otherwise, assume it's already scalar
        return float(x)

def get_branch(prefix, lep, var):
    return prefix + lep + "_" + var

def remove_negative_bins(hist):
    for i in range(1, hist.GetNbinsX() + 1):
        if hist.GetBinContent(i) < 0:
            hist.SetBinContent(i, 0)

# Fake Rate Reader
class FakeRateReader:
    def __init__(self, path):
        f = ROOT.TFile.Open(path)
        self.mu_eb = f.Get("FR_OS_muon_EB")
        self.mu_ee = f.Get("FR_OS_muon_EE")
        self.el_eb = f.Get("FR_OS_electron_EB")
        self.el_ee = f.Get("FR_OS_electron_EE")
        if not self.mu_eb or not self.mu_ee or not self.el_eb or not self.el_ee:
            raise ValueError("[ERROR] One or more fake rate graphs not found!")

    def get(self, pt, eta, lid):
        if abs(int(lid)) == 13:
            graph = self.mu_eb if abs(eta) < 1.2 else self.mu_ee
        else:
            graph = self.el_eb if abs(eta) < 1.5 else self.el_ee
        n = graph.GetN()
        for i in range(n):
            x = graph.GetPointX(i)
            if pt < x:
                y = graph.GetPointY(i)
                break
        else:
            y = graph.GetPointY(n-1)
        return min(max(y, 0.001), 0.999)

# RDataFrame creators
def create_RDF_from_sample(filename, config_file):
    path = os.path.join(config_file.base_dir, filename)
    df = ROOT.RDataFrame("Events", path)
    df = df.Define("final_weight", config_file.weights)
    return df

def create_RDF_from_data_folder(folder, file_list):
    paths = [os.path.join(folder, f) for f in file_list]
    return ROOT.RDataFrame("Events", paths)

# Build histograms from data
def build_zx_histograms_data(df, var, fr):
    prefix = var[0].replace("mass", "")
    bins = (var[3], var[4], var[5])
    h_from2P2F_SR = ROOT.TH1F(f"h_from2P2F_SR_{var[1]}", "", bins[0], bins[1], bins[2])
    h_from2P2F_3P1F = ROOT.TH1F(f"h_from2P2F_3P1F_{var[1]}", "", bins[0], bins[1], bins[2])
    h_from3P1F_SR = ROOT.TH1F(f"h_from3P1F_SR_{var[1]}", "", bins[0], bins[1], bins[2])

    cols = [
        var[0],
        get_branch(prefix, "lep3", "pt"), get_branch(prefix, "lep3", "eta"), get_branch(prefix, "lep3", "pdgId"),
        get_branch(prefix, "lep4", "pt"), get_branch(prefix, "lep4", "eta"), get_branch(prefix, "lep4", "pdgId")
    ]

    data = df.AsNumpy(columns=cols)

    for i in range(len(data[var[0]])):
        mass = extract_scalar(data[var[0]][i])
        pt3 = extract_scalar(data[cols[1]][i])
        eta3 = extract_scalar(data[cols[2]][i])
        id3 = extract_scalar(data[cols[3]][i])
        pt4 = extract_scalar(data[cols[4]][i])
        eta4 = extract_scalar(data[cols[5]][i])
        id4 = extract_scalar(data[cols[6]][i])


        fr3 = fr.get(pt3, eta3, id3)
        fr4 = fr.get(pt4, eta4, id4)
        if mass > 0:
            print(f"[DEBUG] Event {i}: mass={mass:.2f}, pt3={pt3:.2f}, eta3={eta3:.2f}, id3={id3}, fr3={fr3},fr4={fr4}")
            print(f"Fake rate contribute ={(fr3 / (1 - fr3)) + (fr4 / (1 - fr4))}")
            print(f"Fake rate contribute ={(fr3 / (1 - fr3))}")


        if "2P2F" in var[0]:
            h_from2P2F_SR.Fill(mass, (fr3 / (1 - fr3)) * (fr4 / (1 - fr4)))
            h_from2P2F_3P1F.Fill(mass, (fr3 / (1 - fr3)) + (fr4 / (1 - fr4)))
        elif "3P1F" in var[0]:
            h_from3P1F_SR.Fill(mass, fr3 / (1 - fr3))

    return h_from2P2F_SR, h_from2P2F_3P1F, h_from3P1F_SR

# Build MC histograms
def build_zx_histogram_mc(df, var, fr):
    prefix = var[0].replace("mass", "")
    bins = (var[3], var[4], var[5])
    h = ROOT.TH1F(f"h_from3P1F_SR_ZZonly_{var[1]}", "", bins[0], bins[1], bins[2])

    cols = [var[0], get_branch(prefix, "lep3", "pt"), get_branch(prefix, "lep3", "eta"), get_branch(prefix, "lep3", "pdgId"), "final_weight"]
    data = df.AsNumpy(columns=cols)

    for i in range(len(data[var[0]])):
        pt3 = extract_scalar(data[cols[1]][i])
        eta3 = extract_scalar(data[cols[2]][i])
        id3 = extract_scalar(data[cols[3]][i])
        w = extract_scalar(data["final_weight"][i]) * (fr.get(pt3, eta3, id3) / (1 - fr.get(pt3, eta3, id3)))
        h.Fill(extract_scalar(data[var[0]][i]), w)
    return h

# Main estimation function
def run_zx_estimation(config_file):
    start = time.time()
    os.makedirs(config_file.output_plots_dir, exist_ok=True)

    df_zz = create_RDF_from_sample(config_file.samples_dict["ZZ"][0], config_file)
    df_data = create_RDF_from_data_folder(args.data, ["EGamma_merged.root", "MuonEG_merged.root", "Muon_merged.root","DoubleMuon_merged.root", "SingleMuon_merged.root"])

    fr = FakeRateReader("fr_graphs.root")
    fout = ROOT.TFile(os.path.join(config_file.output_plots_dir, "ZXHistos_OS.root"), "RECREATE")

    final_states = ["inclusive", "4e", "4mu", "2e2mu"]
    for fs in final_states:
        b2 = config_file.branch_map_2p2f[fs]
        b3 = config_file.branch_map_3p1f[fs]

        var2 = (b2 + "mass", f"2P2F_mass_{fs}", "", 40, 70, 870)
        var3 = (b3 + "mass", f"3P1F_mass_{fs}", "", 40, 70, 870)

        h2_SR, h2_3P1F, _ = build_zx_histograms_data(df_data, var2, fr)
        _, _, h3_SR = build_zx_histograms_data(df_data, var3, fr)
        h3_ZZonly = build_zx_histogram_mc(df_zz, var3, fr)

        h3_final = h3_SR.Clone(f"h_from3P1F_SR_final_{fs}")
        h3_final.Add(h3_ZZonly, -1)
        h3_final.Add(h2_SR, -2)

        h_ZX = h3_final.Clone(f"histos_ZX_{fs}")
        h_ZX.Add(h2_SR)

        for h in [h2_SR, h2_3P1F, h3_SR, h3_ZZonly, h3_final, h_ZX]:
            remove_negative_bins(h)
            h.Write()

    fout.Close()
    print(f"[INFO] Saved ZX histograms to {fout.GetName()}")
    print(f"Elapsed time: {(time.time() - start)/60:.2f} minutes")

# MAIN
if __name__ == "__main__":
    config_file = config.Config()
    config_file.add_sample(name="ZZ", root_file="qqZZ_final_merged.root", cuts=1)
    run_zx_estimation(config_file)
