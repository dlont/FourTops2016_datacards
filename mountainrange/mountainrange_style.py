import ROOT as rt
import re

class Style:
    	#Modify hatch bands
	#rt.gStyle.SetHatchesLineWidth(2)
	hatchStyle = 3013
	hatchColor = rt.kBlack
        colors = {'EW':413,'ST':7,'TTH':610,'TTXY':rt.kOrange+1,
                  'TTZ':rt.kMagenta,'TTW':615,'TTBAR':633}

def set_line_color_style(drawable,lc=1,ls=1):
        drawable.SetLineWidth(3)
        drawable.SetLineColor(lc)
        drawable.SetLineStyle(ls)

def style_hist_bg_prefit_unc(hist):
    	hist.SetFillStyle(0)
	hist.SetLineColor(rt.kBlue)
	hist.GetXaxis().SetLabelSize(0)

def style_hist_bg_unc(hist):

	#hist_bg_unc.SetFillStyle(3144)
	hist.SetFillStyle(Style.hatchStyle)
	hist.SetFillColor(Style.hatchColor)
	hist.SetLineColor(Style.hatchColor)
	hist.GetXaxis().SetLabelSize(0)

def style_hist_bg_unc_noempty(hist):
        hist.SetMarkerSize(0)
	hist.SetFillStyle(Style.hatchStyle);
	hist.SetFillColor(Style.hatchColor);
	hist.SetLineWidth(0)

def style_hist_sig_noempty(hist,scale):
        hist.Scale(scale)
	hist.SetLineColor(Style.hatchColor);
	hist.SetLineWidth(2)

def style_hist_bg_prefit_unc_noempty(hist):
    #   hist.SetMarkerSize(0)
	hist.SetMarkerStyle(27)
	hist.SetFillStyle(0)
	hist.GetXaxis().SetLabelSize(0)
	hist.GetYaxis().SetTitleSize(0.07)
	hist.GetYaxis().SetTitleOffset(0.8)
    #   hist.GetXaxis().SetTitleSize(0.07)
	hist.GetXaxis().SetTitleSize(0.0)
	hist.GetXaxis().SetTitleOffset(0.7)

def style_stack_hist(hist):
        hist.SetLineWidth(2)
	hist.SetLineColor(hist.GetFillColor())

def style_hist_ratio_unity(hist,hist_mother,arguments):
    	hist.SetMarkerSize(0)
	hist.GetXaxis().SetTitleSize(0.15)
	hist.GetXaxis().SetLabelSize(0.0)
	hist.GetXaxis().SetTickLength(0.12)
	hist.GetYaxis().SetTitleSize(0.19)
	hist.GetYaxis().SetTitleOffset(0.26)
	hist.GetYaxis().SetLabelSize(0.13)
	hist.GetYaxis().SetLabelOffset(0.01)
	#hisy.GetXaxis().CenterTitle()
	hist.GetYaxis().CenterTitle()
	hist.GetYaxis().SetNdivisions(5)
        #hist.GetYaxis().SetRangeUser(-0.5,0.5)
	hist.GetYaxis().SetRangeUser(-1.,1.)
        #hist.GetYaxis().SetRangeUser(-2.,2.)

	if arguments.distrib_title_ratio is not None: hist.SetTitle(arguments.distrib_title_ratio)
	else:
		motherhistxtitle = hist_mother.GetXaxis().GetTitle()
		motherhistxtitle = ';Bin id (%s);Data/Pred.' % re.sub(r' \(.*\)', '', motherhistxtitle)
		hist.SetTitle(motherhistxtitle)
