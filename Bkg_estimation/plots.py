import ROOT
import os
import cmsstyle as CMS

def set_hist_style(hist, fill_color, line_color):
    hist.SetFillColor(fill_color)
    hist.SetLineColor(line_color)
    hist.SetLineWidth(2)

def save_canvas(canvas, outname):
    canvas.SaveAs(outname + ".png")
    # canvas.SaveAs(outname + ".pdf")

def plot_data_mc(region, mc_file, zx_file, output_dir, final_states):
    f_mc = ROOT.TFile.Open(mc_file)
    f_zx = ROOT.TFile.Open(zx_file) if zx_file else None
    os.makedirs(output_dir, exist_ok=True)

    colors = {"WZ": ROOT.kMagenta-7, "ZZ": ROOT.kCyan+1, "DYJets": ROOT.kGreen+2, "TTto2L2Nu": ROOT.kBlue-4}

    CMS.SetExtraText("Preliminary")
    CMS.SetLumi("13.6 TeV, 8 fb^{-1}")
    CMS.SetEnergy("13.6")
    CMS.ResetAdditionalInfo()

    for fs in final_states:
        canvas = CMS.cmsCanvas(f"{region}_{fs if fs else 'inclusive'}", 70, 1200, 1e-2, 1, "m_{4l} [GeV]", "Events", square=CMS.kSquare, extraSpace=0.1)
        canvas.cd()

        suffix = f"ZLL{region}{fs}_mass" if fs else f"ZLL{region}_mass"

        stack = ROOT.THStack("stack", "")
        legend = CMS.cmsLeg(0.60, 0.65, 0.88, 0.88, textSize=0.035, columns=1)

        hists_mc = {}
        for proc in ["ZZ", "WZ", "TTto2L2Nu", "DYJets"]:
            hname = f"hist_{proc}_{suffix}"
            hist = f_mc.Get(hname)
            if hist:
                hist.Rebin(2)
                set_hist_style(hist, colors[proc], colors[proc])
                stack.Add(hist)
                hists_mc[proc] = hist

        h_data = f_mc.Get(f"hist_data_{suffix}")
        if not h_data:
            print(f"[WARNING] Missing data for {fs}")
            continue
        h_data.Rebin(2)
        h_data.SetMarkerStyle(20)
        h_data.SetMarkerSize(0.9)
        h_data.SetLineColor(ROOT.kBlack)
        h_data.SetBinErrorOption(ROOT.TH1.kPoisson)

        # --- Load Red Line (only if 3P1F)
        h_zx = None
        if region == "3P1F" and f_zx:
            h_zx_name = f"h_from2P2F_3P1F_2P2F_mass_{fs}"
            print(h_zx_name)
            h_zx = f_zx.Get(h_zx_name)
            h_zx.Rebin(2)
            h_zx.SetLineColor(ROOT.kRed)
            h_zx.SetLineWidth(3)
            h_zx.SetFillStyle(0)

        # --- Draw
        stack.Draw("HIST")
        stack.GetXaxis().SetTitle("m_{4l} [GeV]")
        stack.GetYaxis().SetTitle("Events")
        stack.GetYaxis().SetTitleOffset(1.6)
        stack.GetXaxis().SetTitleOffset(1.2)
        stack.SetMinimum(1e-2)
        stack.SetMaximum(h_data.GetMaximum()*2.5)

        if h_zx:
            h_zx.Draw("HIST SAME")
        h_data.Draw("E1 SAME")

        # --- Legend
        legend.AddEntry(h_data, "Data", "lep")
        if h_zx:
            legend.AddEntry(h_zx, "2P2F prediction", "l")
        for proc, hist in hists_mc.items():
            legend.AddEntry(hist, proc, "f")
        legend.Draw()

        # CMS.DrawCMS(canvas)

        # --- Save
        save_canvas(canvas, os.path.join(output_dir, f"{region}_{fs if fs else 'inclusive'}"))

        # --- Print yields
        print(f"\n--- Yields for {region} {fs if fs else 'inclusive'} ---")
        for proc, hist in hists_mc.items():
            print(f"{proc:<10}: {hist.Integral(0, hist.GetNbinsX()+1):.2f}")
        if h_zx:
            zx_yield = h_zx.Integral(0, h_zx.GetNbinsX()+1)
            print(f"2P2F extrapolation (red line): {zx_yield:.2f}")
        else:
            zx_yield = 0.0

        data_yield = h_data.Integral(0, h_data.GetNbinsX()+1)
        print(f"Data: {data_yield:.2f}")

        if region == "3P1F" and zx_yield > 0 and data_yield > 0:
            contribution = (zx_yield / data_yield) * 100
            print(f"--> 2P2F prediction contributes {contribution:.1f}% of the Data")

    f_mc.Close()
    if f_zx: f_zx.Close()


# -- Now the script to run --

final_states = ["4e", "4mu", "2e2mu", "inclusive"]  # "" = inclusive
output_dir_3p1f = "plots/3P1F"
output_dir_2p2f = "plots/2P2F"

# Plot 3P1F
plot_data_mc(
    region="3P1F",
    mc_file="DataMC_ZLL_Histos.root",
    zx_file="ZXHistos_OS.root",
    output_dir=output_dir_3p1f,
    final_states=final_states
)

# Plot 2P2F
plot_data_mc(
    region="2P2F",
    mc_file="DataMC_ZLL_Histos.root",
    zx_file=None,
    output_dir=output_dir_2p2f,
    final_states=final_states
)
