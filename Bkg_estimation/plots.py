import ROOT
import argparse
import os
import config
import time
import cmsstyle as CMS  # CMS styling utilities

# Enable multi-threading and batch mode
ROOT.ROOT.EnableImplicitMT()
ROOT.gROOT.SetBatch(True)

palette = ["#00cccc","#ff66ff","#3333ff","#009900"]

# Argument parser
parser = argparse.ArgumentParser()
parser.add_argument('-y', '--year', type=str, help='Dataset year (e.g., 2022, 2022EE)', required=True)
args = parser.parse_args()

def plot_data_mc(region, mc_file, zx_file, output_dir, final_states):
    config_file = config.Config()
    f_mc = ROOT.TFile.Open(mc_file)
    f_zx = ROOT.TFile.Open(zx_file) if zx_file else None
    os.makedirs(output_dir, exist_ok=True)

    # CMS Style Settings
    CMS.SetExtraText("Preliminary")
    CMS.SetLumi(config_file.dataset_legend)
    CMS.SetEnergy(config_file.energy)
    CMS.ResetAdditionalInfo()

    for fs in final_states:
        x_title = fs
        if fs == "4mu":
            x_title = "4#mu"
        elif fs == "2e2mu":
            x_title = "2e2#mu"
        suffix = f"ZLL{region}{fs}_mass" if fs else f"ZLL{region}_mass"
        canvas = CMS.cmsCanvas(f"{region}_{fs}", 70, 870, 1e-2, 1,
                              f"m({x_title}) [GeV]", "Events", square=CMS.kSquare, extraSpace=0.05, iPos=0)

        # Create stack and legend
        stack = ROOT.THStack("stack", f";m({x_title}) [GeV];Events")
        legend = CMS.cmsLeg(0.60, 0.65, 0.95, 0.88, textSize=0.035, columns=1)

        # Load MC histograms
        histos_dict = {}
        for proc in ["ZZ", "WZ", "TTto2L2Nu", "DYJets"]:
            hname = f"hist_{proc}_{suffix}"
            hist = f_mc.Get(hname)
            if hist:
                histos_dict[proc] = hist

        # Load data
        h_data = f_mc.Get(f"hist_data_{suffix}")
        if not h_data:
            print(f"[WARNING] Missing data for {fs}")
            continue

        y_max = 1.3 * h_data.GetMaximum()
        CMS.GetcmsCanvasHist(canvas).GetYaxis().SetRangeUser(0, y_max)
        CMS.GetcmsCanvasHist(canvas).GetYaxis().SetTitleOffset(1.4)

        # --- Load Red Line (only if 3P1F)
        h_zx = None
        if region == "3P1F" and f_zx:
            zx_name = f"h_from2P2F_3P1F_2P2F_mass_{fs}"
            h_zx = f_zx.Get(zx_name)
            h_zx.SetLineColor(ROOT.kRed)
            h_zx.SetLineWidth(3)
            h_zx.SetFillStyle(0)
        
        CMS.cmsDrawStack(stack, legend, histos_dict, data=h_data, palette=palette)

        # Overlay ZX if present
        if h_zx:
            h_zx.Draw("HIST SAME")
            legend.AddEntry(h_zx, "2P2F extrapolation", "l")  # Add red line to legend

        # Save canvas as PNG
        outpath = os.path.join(output_dir, f"{region}_{fs or 'inclusive'}.png")
        CMS.SaveCanvas(canvas, outpath, close=True)

        # Print yields
        print(f"\n--- Yields for {region} {fs or 'inclusive'} ---")
        for proc, hist in histos_dict.items():
            print(f"{proc:<10}: {hist.Integral(0, hist.GetNbinsX()+1):.2f}")
        if h_zx:
            print(f"2P2F extrapolation (red line): {h_zx.Integral(0, h_zx.GetNbinsX()+1):.2f}")
        print(f"Data: {h_data.Integral(0, h_data.GetNbinsX()+1):.2f}")
        if region == "3P1F" and h_zx:
            pct = (h_zx.Integral(0, h_zx.GetNbinsX()+1) /
                   h_data.Integral(0, h_data.GetNbinsX()+1) * 100)
            print(f"--> 2P2F prediction contributes {pct:.1f}% of the Data")

    # Close files
    f_mc.Close()
    if f_zx:
        f_zx.Close()


if __name__ == "__main__":
    start = time.time()

    config_file = config.Config()

    final_states = ["4e", "4mu", "2e2mu", "inclusive"]  # "" = inclusive
    output_dir_3p1f = f"plots_ZX_alt_{args.year}/3P1F_fit"
    output_dir_2p2f = f"plots_ZX_alt_{args.year}/2P2F_fit"

    # Plot 3P1Fs
    plot_data_mc(
        region="3P1F",
        mc_file=f"plots_ZX_alt_{args.year}/ZLL/DataMC_ZLL_Histos.root",
        zx_file=f"plots_ZX_alt_{args.year}/ZXHistos_OS_{args.year}.root",
        output_dir=output_dir_3p1f,
        final_states=final_states
    )
    # Plot 2P2F
    plot_data_mc(
        region="2P2F",
        mc_file=f"plots_ZX_alt_{args.year}/ZLL/DataMC_ZLL_Histos.root",
        zx_file=None,
        output_dir=output_dir_2p2f,
        final_states=final_states
    )
    print(f"Elapsed time: {(time.time() - start)/60:.2f} minutes")
