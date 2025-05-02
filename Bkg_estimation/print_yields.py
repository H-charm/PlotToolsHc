import ROOT
import ctypes

def print_all_histogram_yields(root_file_path, output_txt_file):
    file = ROOT.TFile.Open(root_file_path)
    if not file or file.IsZombie():
        print(f"[ERROR] Cannot open file: {root_file_path}")
        return

    with open(output_txt_file, "w") as f_out:
        f_out.write("==============================================================\n")
        f_out.write("[INFO] Yield and error for all TH1F histograms\n")
        f_out.write("==============================================================\n")

        print("\n==============================================================")
        print("[INFO] Yield and error for all TH1F histograms")
        print("==============================================================")

        for key in file.GetListOfKeys():
            obj = key.ReadObj()
            if isinstance(obj, ROOT.TH1F):
                stat = ctypes.c_double(0.0)
                yield_nominal = obj.IntegralAndError(0, obj.GetNbinsX() + 1, stat)
                histo_name = key.GetName()

                line = (f"Histogram: {histo_name}\n"
                        f"Yield: {yield_nominal:.2f} +/- {stat.value:.2f} (statistical only)\n"
                        "--------------------------------------------------------------\n")
                print(line, end="")
                f_out.write(line)

    file.Close()
    print(f"[INFO] Yields saved to {output_txt_file}")

if __name__ == "__main__":
    root_file = "ZXHistos_OS.root"
    output_txt = "All_ZX_yields.txt"
    print_all_histogram_yields(root_file, output_txt)
