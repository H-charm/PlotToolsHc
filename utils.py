import math

def add_underflow(h):
    e1 = h.GetBinError(1)
    e0 = h.GetBinError(0)
    h.AddBinContent(1, h.GetBinContent(0))
    h.SetBinError(1, math.sqrt(e1 * e1 + e0 * e0))
    h.SetBinContent(0, 0)
    h.SetBinError(0, 0)
    return h

def add_overflow(h):
    nbins = h.GetNbinsX()+1
    e1 = h.GetBinError(nbins-1)
    e2 = h.GetBinError(nbins)
    h.AddBinContent(nbins-1, h.GetBinContent(nbins))
    h.SetBinError(nbins-1, math.sqrt(e1*e1 + e2*e2))
    h.SetBinContent(nbins, 0)
    h.SetBinError(nbins, 0)
    return h