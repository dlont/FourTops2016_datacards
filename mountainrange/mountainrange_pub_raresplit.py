#!/usr/bin/env python

"""
Script for mountain range plots with post-fit uncertainties from combine
"""

import gc
import re
import os
import sys
import time
import argparse
import logging
import json
import pprint

import ROOT as rt
import array

import tdrstyle
import CMS_lumi
import mountainrange_pub_utilities as mr
from mountainrange_style import *

def draw_legend(**kwargs):
	"""
	Add legend to the canvas
	"""

	logging.debug("draw_legend() arguments")
	logging.debug(pprint.pformat(kwargs))

	canvas = None
	legend = None
	if 'canvas' in kwargs: canvas = kwargs['canvas']
	if 'legend' in kwargs:
		if 'coord' in kwargs['legend']:
			coords = kwargs['legend']['coord']
			logging.debug('legend coordinates: %s %s %s %s' % (coords[0],coords[1],coords[2],coords[3]))
			legend = rt.TLegend(coords[0],coords[1],coords[2],coords[3])
	else: legend = rt.TLegend(0.6,0.75,0.9,0.9)

	datagr = None
	if 'data' in kwargs: datagr = kwargs['data']

	if 'header' in kwargs['legend']:
		#legend.SetHeader(kwargs['legend']['header'])
		header = rt.TLatex()
		header.DrawLatexNDC(0.2,0.85,kwargs['legend']['header'])

	if canvas is not None:
		legend.SetNColumns(4)
		legend.SetBorderSize(0)
		#legend.SetFillStyle(0)

		if datagr: legend.AddEntry(datagr,"Data",'pe')
		if 'hist_tt' in kwargs:
			hist_tt = kwargs['hist_tt']
			if hist_tt: legend.AddEntry(hist_tt,"t#bar{t}(stack)",'lf')
		if 'hist_st' in kwargs:
			hist_st = kwargs['hist_st']
                        if hist_st: legend.AddEntry(hist_st,"tX(stack)",'lf')
		if 'hist_ew' in kwargs:
			hist_ew = kwargs['hist_ew']
                        if hist_ew: legend.AddEntry(hist_ew,"EW(stack)",'lf')	#for slepton
                        #if : legend.AddEntry(hist_ew,"DY",'lf')	#for dilepton
		if 'hist_rare' in kwargs:
			hist_rare = kwargs['hist_rare']
                        if hist_rare: legend.AddEntry(hist_rare,"Rare",'lf')
		if 'hist_tttt' in kwargs:
			hist_tttt = kwargs['hist_tttt']
			if hist_tttt: legend.AddEntry(hist_tttt,"t#bar{t}t#bar{t} (postfit)",'lf')
		if 'hist_pre' in kwargs:
			hist_pre = kwargs['hist_pre']
			if hist_pre: legend.AddEntry(hist_pre,"Prefit unc.","fe")
		if 'hist_post' in kwargs:
			hist_post = kwargs['hist_post']
			if hist_post: legend.AddEntry(hist_post,"Postfit unc.","fe")

                if 'hist_tth_pre' in kwargs:
			hist_tth = kwargs['hist_tth_pre']
			if hist_tth: legend.AddEntry(hist_tth,kwargs['legend']['prefit_Rare1TTH'],'lf')
                if 'hist_tth_b' in kwargs:
			hist_tth = kwargs['hist_tth_b']
			if hist_tth: legend.AddEntry(hist_tth,kwargs['legend']['fitb_Rare1TTH'],'lf')
                if 'hist_tth_s' in kwargs:
			hist_tth = kwargs['hist_tth_s']
			if hist_tth: legend.AddEntry(hist_tth,kwargs['legend']['fits_Rare1TTH'],'lf')

                if 'hist_ttz_pre' in kwargs:
			hist_ttz = kwargs['hist_ttz_pre']
			if hist_ttz: legend.AddEntry(hist_ttz,"t#bar{t}Z (prefit)",'lf')
                if 'hist_ttz_b' in kwargs:
			hist_ttz = kwargs['hist_ttz_b']
			if hist_ttz: legend.AddEntry(hist_ttz,"t#bar{t}Z (b-only)",'lf')
                if 'hist_ttz_s' in kwargs:
			hist_ttz = kwargs['hist_ttz_s']
			if hist_ttz: legend.AddEntry(hist_ttz,"t#bar{t}Z (s+b)",'lf')

                if 'hist_ttw_pre' in kwargs:
			hist_ttw = kwargs['hist_ttw_pre']
			if hist_ttw: legend.AddEntry(hist_ttw,"t#bar{t}W (prefit)",'lf')
                if 'hist_ttw_b' in kwargs:
			hist_ttw = kwargs['hist_ttw_b']
			if hist_ttw: legend.AddEntry(hist_ttw,"t#bar{t}W (b-only)",'lf')
                if 'hist_ttw_s' in kwargs:
			hist_ttw = kwargs['hist_ttw_s']
			if hist_ttw: legend.AddEntry(hist_ttw,"t#bar{t}W (s+b)",'lf')

                if 'hist_ttxy_pre' in kwargs:
			hist_ttxy = kwargs['hist_ttxy_pre']
			if hist_ttxy: legend.AddEntry(hist_ttxy,kwargs['legend']['prefit_TTRARE_plus'],'lf')
                if 'hist_ttxy_b' in kwargs:
			hist_ttxy = kwargs['hist_ttxy_b']
			if hist_ttxy: legend.AddEntry(hist_ttxy,kwargs['legend']['fitb_TTRARE_plus'],'lf')
                if 'hist_ttxy_s' in kwargs:
			hist_ttxy = kwargs['hist_ttxy_s']
			if hist_ttxy: legend.AddEntry(hist_ttxy,kwargs['legend']['fits_TTRARE_plus'],'lf')

		canvas.cd(3)
		legend.Draw()

def draw_bin_labels(c,masterhist,labels,ycoord,edges=None):
	'''
	Add labels below the X axis
	'''
	tex = rt.TLatex()
	tex.SetTextSize(0.025)
	tex.SetTextAlign(31)
	c.cd()

	if isinstance(labels,dict):
		for entry in labels:
			x = masterhist.GetBinCenter(int(entry))
			print labels[entry], x
			xmax = masterhist.GetXaxis().GetXmax()
			xmin = masterhist.GetXaxis().GetXmin()
			xndc=(x - xmin)/(xmax - xmin)
			tex.DrawLatexNDC(xndc,ycoord,labels[entry])
	if isinstance(labels,list):
		for entry,label in enumerate(labels):
			x = masterhist.GetBinCenter(edges[entry])
			print labels[entry], x
			xmax = masterhist.GetXaxis().GetXmax()
			xmin = masterhist.GetXaxis().GetXmin()
			xndc=(x - xmin)/(xmax - xmin)
			tex.DrawLatexNDC(xndc,ycoord,label)

def draw_subhist_separators(c,stitch_edge_bins,binmapping,labels,conf,hist_template):

        #calculate position of separator vertical lines on mountain range plot
        #without empty bins
	mappedbins = binmapping.keys()
	mappedbins.sort()
	mapped_edge_bins = []
	for edge in stitch_edge_bins:   #for each boundary bin in long histogram
		mappededge = -1
		for mb in mappedbins:   #find rightmost nonempty bin before boundary bin
			if mb <= edge: mappededge = mb
			else:
				mapped_edge_bins.append(mappededge)
				break

        #boundary bins on histogram without empty bins
	separator_bins = [binmapping[x] for x in mapped_edge_bins]
	logging.debug( "Stitching bins:" )
	logging.debug(pprint.pformat( stitch_edge_bins ) )
	logging.debug( "Separator bins:" )
	logging.debug(pprint.pformat( separator_bins ) )

	c.cd()

        ycoord = conf['ypos']

	for item, isep in enumerate(separator_bins):
		x = hist_template.GetBinLowEdge(isep)+hist_template.GetBinWidth(isep)
		#ymin = hist_template.GetYaxis().GetXmin()
		ymin = hist_template.GetMinimum()
		ymax = hist_template.GetMaximum()
		#print x, hist_template.GetMaximum()
		l = rt.TLine(x,ymin,x,ymax); l.SetLineColor(rt.kBlack); l.SetLineWidth(2)
		l.Draw()

		if isinstance(labels,list):
			tex = rt.TLatex()
                        if 'size' in conf: tex.SetTextSize(conf['size'])
                        else: tex.SetTextSize(0.045)
			tex.SetTextAlign(32)
			#tex.SetTextAngle(45)
			cxmin=c.GetLeftMargin()
			cxmax=1.-c.GetRightMargin()
			cymin=c.GetXlowNDC()
			xmax = hist_template.GetXaxis().GetXmax()
			xmin = hist_template.GetXaxis().GetXmin()
                        if isinstance(labels[item],list) and len(labels[item])>1: x = labels[item][1]
			xndc= cxmin + (x - xmin)/(xmax - xmin) * (cxmax - cxmin)
			#xndc= c.GetLeftMargin()
			logging.debug('Separator|Label: {} | {} {} {}'.format( isep,xndc,ycoord,labels[item][0] ) )
			tex.DrawLatexNDC(xndc-0.05,ycoord,labels[item][0])
			if (item == len(separator_bins)-1):
                            if isinstance(labels[item+1],list) and len(labels[item+1])>1:
                                x = labels[item+1][1]
			        xndc= cxmin + (x - xmin)/(xmax - xmin) * (cxmax - cxmin)
                                tex.DrawLatexNDC(xndc-0.05,ycoord,labels[item+1][0])
                            else: #last search region
                                tex.DrawLatexNDC(cxmax-0.05,ycoord,labels[item+1][0])
        rt.gPad.RedrawAxis()

def draw_chi2_ndf(c,chi2,ndf):
	c.cd()
	text = '#chi^{{2}}/NDF = {0:.2f}/{1:d}, p-val={2:.2f}'.format(chi2,int(ndf),rt.TMath.Prob(chi2, int(ndf)))
	tex = rt.TLatex()
	tex.SetTextAngle(90)
	tex.DrawLatexNDC(0.99,0.2,text)


def self_ratio(hist):
        hist.Sumw2()
    	hist.Divide(hist)
        for ibin in range(0,hist.GetNbinsX()):
                hist.SetBinContent(ibin+1,0.)

def make_mountainrange_plots(jsondic,arguments,stitch_edges,binmapping,**kwargs):
        hist_bg_prefit_unc_noempty = kwargs['hist_bg_prefit_unc_noempty']
        hist_st_noempty = kwargs['hist_st_noempty']
        hist_bg_unc_noempty = kwargs['hist_bg_unc_noempty']
        hist_sig_noempty = kwargs['hist_sig_noempty']
        gr_data_noempty = kwargs['gr_data_noempty']

        hist_prefit_TTRARE_plus_noempty = None
        if 'hist_prefit_TTRARE_plus_noempty' in kwargs: hist_prefit_TTRARE_plus_noempty = kwargs['hist_prefit_TTRARE_plus_noempty']
        hist_prefit_Rare1TTH_noempty = None
        if 'hist_prefit_Rare1TTH_noempty' in kwargs: hist_prefit_Rare1TTH_noempty = kwargs['hist_prefit_Rare1TTH_noempty']
        hist_prefit_Rare1TTZ_noempty = None
        if 'hist_prefit_Rare1TTZ_noempty' in kwargs: hist_prefit_Rare1TTZ_noempty = kwargs['hist_prefit_Rare1TTZ_noempty']
        hist_prefit_Rare1TTW_noempty = None
        if 'hist_prefit_Rare1TTW_noempty' in kwargs: hist_prefit_Rare1TTW_noempty = kwargs['hist_prefit_Rare1TTW_noempty']
        hist_fitb_TTRARE_plus_noempty = None
        if 'hist_fitb_TTRARE_plus_noempty' in kwargs: hist_fitb_TTRARE_plus_noempty = kwargs['hist_fitb_TTRARE_plus_noempty']
        hist_fitb_Rare1TTH_noempty = None
        if 'hist_fitb_Rare1TTH_noempty' in kwargs: hist_fitb_Rare1TTH_noempty = kwargs['hist_fitb_Rare1TTH_noempty']
        hist_fitb_Rare1TTZ_noempty = None
        if 'hist_fitb_Rare1TTZ_noempty' in kwargs: hist_fitb_Rare1TTZ_noempty = kwargs['hist_fitb_Rare1TTZ_noempty']
        hist_fitb_Rare1TTW_noempty = None
        if 'hist_fitb_Rare1TTW_noempty' in kwargs: hist_fitb_Rare1TTW_noempty = kwargs['hist_fitb_Rare1TTW_noempty']
        hist_fits_TTRARE_plus_noempty = None
        if 'hist_fits_TTRARE_plus_noempty' in kwargs: hist_fits_TTRARE_plus_noempty = kwargs['hist_fits_TTRARE_plus_noempty']
        hist_fits_Rare1TTH_noempty = None
        if 'hist_fits_Rare1TTH_noempty' in kwargs: hist_fits_Rare1TTH_noempty = kwargs['hist_fits_Rare1TTH_noempty']
        hist_fits_Rare1TTZ_noempty = None
        if 'hist_fits_Rare1TTZ_noempty' in kwargs: hist_fits_Rare1TTZ_noempty = kwargs['hist_fits_Rare1TTZ_noempty']
        hist_fits_Rare1TTW_noempty = None
        if 'hist_fits_Rare1TTW_noempty' in kwargs: hist_fits_Rare1TTW_noempty = kwargs['hist_fits_Rare1TTW_noempty']

    	c = rt.TCanvas('c',"CMS",5,45,1000,750)
	if arguments.is_ratio and gr_data_noempty:
		c.Divide(1,3)
		c.cd(3)
		rt.gPad.SetPad(0.,0.,1.,0.1)
		c.cd(2)
		rt.gPad.SetPad(0.,0.1,1.,0.375);rt.gPad.SetFillStyle(4000)
		c.cd(1)
		rt.gPad.SetPad(0.,0.3,1.,1.);rt.gPad.SetFillStyle(4000)
	hist_bg_prefit_unc_noempty.Draw("E2")
	ymin = hist_bg_prefit_unc_noempty.GetMinimum()
	ymax = 10.*hist_bg_prefit_unc_noempty.GetMaximum()
        ytitle = None
	if "axes" in jsondic:
		if "ymin" in jsondic['axes']: ymin = jsondic['axes']['ymin']
		if "ymax" in jsondic['axes']: ymax = jsondic['axes']['ymax']
                if "ytitle" in jsondic['axes']:
                    ytitle = jsondic['axes']['ytitle']
	            hist_bg_prefit_unc_noempty.GetYaxis().SetTitle(ytitle)
	hist_bg_prefit_unc_noempty.SetAxisRange(ymin, ymax, "Y")

        #Signal
	hist_st_noempty.Draw("same")
        #Total pre- and post-fit backgounds and background stack
	hist_bg_prefit_unc_noempty.Draw("E2 same")
	hist_bg_unc_noempty.Draw("E2 same")
	hist_sig_noempty.Draw("hist same")
        #Rare backgrounds as histograms
        if hist_prefit_TTRARE_plus_noempty: hist_prefit_TTRARE_plus_noempty.Draw("hist same")
        if hist_prefit_Rare1TTH_noempty:    hist_prefit_Rare1TTH_noempty.Draw("hist same")
        if hist_prefit_Rare1TTZ_noempty:    hist_prefit_Rare1TTZ_noempty.Draw("hist same")
        if hist_prefit_Rare1TTW_noempty:    hist_prefit_Rare1TTW_noempty.Draw("hist same")
        if hist_fitb_TTRARE_plus_noempty:   hist_fitb_TTRARE_plus_noempty.Draw("hist same")
        if hist_fitb_Rare1TTH_noempty:      hist_fitb_Rare1TTH_noempty.Draw("hist same")
        if hist_fitb_Rare1TTZ_noempty:      hist_fitb_Rare1TTZ_noempty.Draw("hist same")
        if hist_fitb_Rare1TTW_noempty:      hist_fitb_Rare1TTW_noempty.Draw("hist same")
        if hist_fits_TTRARE_plus_noempty:   hist_fits_TTRARE_plus_noempty.Draw("hist same")
        if hist_fits_Rare1TTH_noempty:      hist_fits_Rare1TTH_noempty.Draw("hist same")
        if hist_fits_Rare1TTZ_noempty:      hist_fits_Rare1TTZ_noempty.Draw("hist same")
        if hist_fits_Rare1TTW_noempty:      hist_fits_Rare1TTW_noempty.Draw("hist same")
        #Data
	if gr_data_noempty: gr_data_noempty.Draw("same pe")

        #Legend
	draw_legend(canvas=c,legend=jsondic['legend'],
                        data=gr_data_noempty,
                        hist_pre=hist_bg_prefit_unc_noempty,
                        hist_post=hist_bg_unc_noempty,
			hist_tttt=hist_sig_noempty,
			hist_tt=hist_st_noempty.GetHists()[0],
			hist_st=hist_st_noempty.GetHists()[1],
			hist_ew=hist_st_noempty.GetHists()[2],
#			hist_rare=hist_st_noempty.GetHists()[6],
                        #
                        hist_ttxy_pre = hist_prefit_TTRARE_plus_noempty,
                        hist_tth_pre  = hist_prefit_Rare1TTH_noempty,
                        hist_ttz_pre  = hist_prefit_Rare1TTZ_noempty,
                        hist_ttw_pre  = hist_prefit_Rare1TTW_noempty,
                        #
                        hist_ttxy_b   = hist_fitb_TTRARE_plus_noempty,
                        hist_tth_b    = hist_fitb_Rare1TTH_noempty,
                        hist_ttz_b    = hist_fitb_Rare1TTZ_noempty,
                        hist_ttw_b    = hist_fitb_Rare1TTW_noempty,
                        #
                        hist_ttxy_s   = hist_fits_TTRARE_plus_noempty,
                        hist_tth_s    = hist_fits_Rare1TTH_noempty,
                        hist_ttz_s    = hist_fits_Rare1TTZ_noempty,
                        hist_ttw_s    = hist_fits_Rare1TTW_noempty
                        )

	draw_subhist_separators(c.cd(1),stitch_edges,binmapping, jsondic['binlabels']['labels'],jsondic['binlabels'], hist_bg_prefit_unc_noempty)
	rt.gPad.RedrawAxis()

	if arguments.is_ratio and gr_data_noempty:
		c.cd(2)
		#hist_ratio_unity = hist_bg_prefit_unc_noempty.Clone("hist_ratio_unity")
		hist_ratio_unity = hist_bg_unc_noempty.Clone("hist_ratio_unity")
                self_ratio(hist_ratio_unity)
                style_hist_ratio_unity(hist_ratio_unity,hist_bg_unc_noempty,arguments)

                gr_ratio_data = mr.make_gr_ratio_data(gr_data_noempty,hist_bg_unc_noempty)
		logging.debug("number of bins/points: %d %d" % (hist_ratio_unity.GetNbinsX(), gr_data_noempty.GetN()))
		hist_ratio_unity.Draw("hist e2")
		gr_ratio_data.Draw("same pe")

                chi2,ndf = mr.get_chi2_ndf(gr_data_noempty, hist_bg_unc_noempty)
                if ndf > 0:
                    print "chi2/ndf=", chi2,"/",ndf,"=",chi2/ndf

                if arguments.draw_chi2:
                    draw_chi2_ndf(rt.gPad,chi2,ndf)
		draw_subhist_separators(c.cd(2),stitch_edges,binmapping, None,jsondic['binlabels'], hist_ratio_unity)


	CMS_lumi.CMS_lumi(c.cd(1),4,0)
	if arguments.outfile:
		c.Print(arguments.outfile+'_lin.'+arguments.extension)
		c.cd(1); rt.gPad.SetLogy();
		c.Print(arguments.outfile+'_log.'+arguments.extension)
	else:
		if 'filename' in jsondic:
			c.Print(arguments.dir+'/'+jsondic['filename']+'_lin.'+arguments.extension)
			c.cd(1); rt.gPad.SetLogy();
			c.Print(arguments.dir+'/'+jsondic['filename']+'_log.'+arguments.extension)

def print_toys_pval(arguments):
    	if arguments.gof_data is not None and arguments.gof_toys is not None:
            f_toys = rt.TFile.Open(arguments.gof_toys, "READ")
            t_toys = f_toys.Get("limit")
            f_data = rt.TFile.Open(arguments.gof_data, "READ")
            t_data = f_data.Get("limit")
            stat_data = 100000000.
            for entr in t_data: stat_data = entr.limit
            pval = 0
            for entr in t_toys:
                logging.debug("Toy p-val: %f" % (entr.limit))
                if entr.limit > stat_data: pval += 1
            pval /= t_toys.GetEntries()
            print "Data: ", stat_data
            print "p-value: ", pval

def main(arguments):

	#Apply TDR style
	tdrstyle.setTDRStyle()

	#Manipulate python garbage collection
	rt.TLegend.__init__._creates = False
	rt.TLine.__init__._creates = False

    #Load combine FitDiagnostics.root or mlfit.root file
    #produced with --saveShapes --saveWithUncertainties flags
	inputrootfile = rt.TFile.Open(arguments.infile, 'READ')

    #Load configuration .json file
	jsondic = None
	with open(arguments.config_json) as json_data:
		jsondic = json.load(json_data)
		logging.debug(pprint.pformat(jsondic))

	#count number of bins for mountain range plot
	nbins = mr.get_total_nbins(jsondic, inputrootfile)

	#create individual histograms for signal, background and data that will be added to the stack plot
	#clone entries and uncertainties from individual search regions to the master histograms

	#Signal
	hist_sig = rt.TH1F('hist_sig',arguments.distrib_title,nbins,0.5,float(nbins+0.5))
	stitch_edges = mr.fillsingle(hist_sig, inputrootfile, jsondic['signal'])

	#Background components
    	hist_st = rt.THStack('hist_st','background stack;Bin id;events')
	mr.fillstack(hist_st, hist_sig, inputrootfile, jsondic['stack'])

	#Total bg with uncertainties
	#prefit shapes and unc
	hist_bg_prefit_unc = rt.TH1F('hist_bg_prefit_unc',arguments.distrib_title,nbins,0.5,float(nbins+0.5))
    	style_hist_bg_prefit_unc(hist_bg_prefit_unc)
    	mr.fillsingle(hist_bg_prefit_unc, inputrootfile, jsondic['prefitbg'])

	#postfit shapes and unc
	hist_bg_unc = rt.TH1F('hist_bg_unc',arguments.distrib_title,nbins,0.5,float(nbins+0.5))
    	style_hist_bg_unc(hist_bg_unc)
    	mr.fillsingle(hist_bg_unc, inputrootfile, jsondic['totalbg'])

	gr_data = None
	if 'data' in jsondic:
		gr_data = mr.fillsingle_data(inputrootfile,jsondic['data'],\
                                          hist_sig,arguments.blind)
        gr_data.SetMarkerStyle(20)

	binmapping = mr.binmap(hist_bg_unc, hist_sig, gr_data)

        #remove empty bins from long histograms
	hist_bg_unc_noempty = mr.noemptybins(hist_bg_unc, binmapping);
	style_hist_bg_unc_noempty(hist_bg_unc_noempty)

	hist_sig_noempty    = mr.noemptybins(hist_sig, binmapping);
    	style_hist_sig_noempty(hist_sig_noempty,arguments.scale_signal)

	hist_st_noempty = rt.THStack('hist_st_mountain','background stack;Bin id;events')
	for hist in hist_st.GetHists():
		hist_noempty = mr.noemptybins(hist, binmapping)
        	style_stack_hist(hist_noempty)
		hist_st_noempty.Add(hist_noempty,'hist')

	hist_bg_prefit_unc_noempty = mr.noemptybins(hist_bg_prefit_unc, binmapping)
        style_hist_bg_prefit_unc_noempty(hist_bg_prefit_unc_noempty)

        hist_prefit_TTRARE_plus_noempty = None
        hist_prefit_Rare1TTH_noempty = None
        hist_prefit_Rare1TTZ_noempty = None
        hist_prefit_Rare1TTW_noempty = None
        if 'prefit_TTRARE_plus' in jsondic: hist_prefit_TTRARE_plus_noempty = mr.fillnonemptysingle(arguments, inputrootfile, jsondic['prefit_TTRARE_plus'], 'hist_prefit_TTRARE_plus', nbins, binmapping)
        if hist_prefit_TTRARE_plus_noempty: set_line_color_style(hist_prefit_TTRARE_plus_noempty,Style.colors['TTXY'],3)
        if 'prefit_Rare1TTH' in jsondic: hist_prefit_Rare1TTH_noempty    = mr.fillnonemptysingle(arguments, inputrootfile, jsondic['prefit_Rare1TTH'], 'hist_prefit_Rare1TTH', nbins, binmapping)
        if hist_prefit_Rare1TTH_noempty: set_line_color_style(hist_prefit_Rare1TTH_noempty,Style.colors['TTH'],3)
        if 'prefit_Rare1TTZ' in jsondic: hist_prefit_Rare1TTZ_noempty    = mr.fillnonemptysingle(arguments, inputrootfile, jsondic['prefit_Rare1TTZ'], 'hist_prefit_Rare1TTZ', nbins, binmapping)
        if hist_prefit_Rare1TTZ_noempty: set_line_color_style(hist_prefit_Rare1TTZ_noempty,Style.colors['TTZ'],3)
        if 'prefit_Rare1TTW' in jsondic: hist_prefit_Rre1TTW_noempty    = mr.fillnonemptysingle(arguments, inputrootfile, jsondic['prefit_Rare1TTW'], 'hist_prefit_Rare1TTW', nbins, binmapping)
        if hist_prefit_Rare1TTW_noempty: set_line_color_style(hist_prefit_Rare1TTW_noempty,Style.colors['TTW'],3)

        hist_fitb_TTRARE_plus_noempty = None
        hist_fitb_Rare1TTH_noempty = None
        hist_fitb_Rare1TTZ_noempty = None
        hist_fitb_Rare1TTW_noempty = None
        if 'fitb_TTRARE_plus' in jsondic: hist_fitb_TTRARE_plus_noempty = mr.fillnonemptysingle(arguments, inputrootfile, jsondic['fitb_TTRARE_plus'], 'hist_fitb_TTRARE_plus', nbins, binmapping)
        if hist_fitb_TTRARE_plus_noempty: set_line_color_style(hist_fitb_TTRARE_plus_noempty,Style.colors['TTXY'],2)
        if 'fitb_Rare1TTH' in jsondic: hist_fitb_Rare1TTH_noempty    = mr.fillnonemptysingle(arguments, inputrootfile, jsondic['fitb_Rare1TTH'], 'hist_fitb_Rare1TTH', nbins, binmapping)
        if hist_fitb_Rare1TTH_noempty: set_line_color_style(hist_fitb_Rare1TTH_noempty,Style.colors['TTH'],2)
        if 'fitb_Rare1TTZ' in jsondic: hist_fitb_Rare1TTZ_noempty    = mr.fillnonemptysingle(arguments, inputrootfile, jsondic['fitb_Rare1TTZ'], 'hist_fitb_Rare1TTZ', nbins, binmapping)
        if hist_fitb_Rare1TTZ_noempty: set_line_color_style(hist_fitb_Rare1TTZ_noempty,Style.colors['TTZ'],2)
        if 'fitb_Rare1TTW' in jsondic: hist_fitb_Rare1TTW_noempty    = mr.fillnonemptysingle(arguments, inputrootfile, jsondic['fitb_Rare1TTW'], 'hist_fitb_Rare1TTW', nbins, binmapping)
        if hist_fitb_Rare1TTW_noempty: set_line_color_style(hist_fitb_Rare1TTW_noempty,Style.colors['TTW'],2)

        hist_fits_TTRARE_plus_noempty = None
        hist_fits_Rare1TTH_noempty = None
        hist_fits_Rare1TTZ_noempty = None
        hist_fits_Rare1TTW_noempty = None
        if 'fits_TTRARE_plus' in jsondic: hist_fits_TTRARE_plus_noempty = mr.fillnonemptysingle(arguments, inputrootfile, jsondic['fits_TTRARE_plus'], 'hist_fits_TTRARE_plus', nbins, binmapping)
        if hist_fits_TTRARE_plus_noempty: set_line_color_style(hist_fits_TTRARE_plus_noempty,Style.colors['TTXY'],1)
        if 'fits_Rare1TTH' in jsondic: hist_fits_Rare1TTH_noempty    = mr.fillnonemptysingle(arguments, inputrootfile, jsondic['fits_Rare1TTH'], 'hist_fits_Rare1TTH', nbins, binmapping)
        if hist_fits_Rare1TTH_noempty: set_line_color_style(hist_fits_Rare1TTH_noempty,Style.colors['TTH'],1)
        if 'fits_Rare1TTZ' in jsondic: hist_fits_Rare1TTZ_noempty    = mr.fillnonemptysingle(arguments, inputrootfile, jsondic['fits_Rare1TTZ'], 'hist_fits_Rare1TTZ', nbins, binmapping)
        if hist_fits_Rare1TTZ_noempty: set_line_color_style(hist_fits_Rare1TTZ_noempty,Style.colors['TTZ'],1)
        if 'fits_Rare1TTW' in jsondic: hist_fits_Rare1TTW_noempty    = mr.fillnonemptysingle(arguments, inputrootfile, jsondic['fits_Rare1TTW'], 'hist_fits_Rare1TTW', nbins, binmapping)
        if hist_fits_Rare1TTW_noempty: set_line_color_style(hist_fits_Rare1TTW_noempty,Style.colors['TTW'],1)

	gr_data_noempty = None
	if gr_data: gr_data_noempty = mr.noemptybins_data(gr_data, binmapping, hist_noempty)

	rt.gStyle.SetOptStat(0)

        make_mountainrange_plots(jsondic,arguments,stitch_edges,binmapping,
                                    gr_data_noempty                 = gr_data_noempty,
                                    hist_sig_noempty                = hist_sig_noempty,
                                    hist_bg_prefit_unc_noempty      = hist_bg_prefit_unc_noempty,
                                    hist_bg_unc_noempty             = hist_bg_unc_noempty,
                                    hist_st_noempty                 = hist_st_noempty,
                                    hist_prefit_TTRARE_plus_noempty = hist_prefit_TTRARE_plus_noempty,
                                    hist_prefit_Rare1TTH_noempty    = hist_prefit_Rare1TTH_noempty,
                                    hist_prefit_Rare1TTZ_noempty    = hist_prefit_Rare1TTZ_noempty,
                                    hist_prefit_Rare1TTW_noempty    = hist_prefit_Rare1TTW_noempty,
                                    hist_fitb_TTRARE_plus_noempty   = hist_fitb_TTRARE_plus_noempty,
                                    hist_fitb_Rare1TTH_noempty      = hist_fitb_Rare1TTH_noempty,
                                    hist_fitb_Rare1TTZ_noempty      = hist_fitb_Rare1TTZ_noempty,
                                    hist_fitb_Rare1TTW_noempty      = hist_fitb_Rare1TTW_noempty,
                                    hist_fits_TTRARE_plus_noempty   = hist_fits_TTRARE_plus_noempty,
                                    hist_fits_Rare1TTH_noempty      = hist_fits_Rare1TTH_noempty,
                                    hist_fits_Rare1TTZ_noempty      = hist_fits_Rare1TTZ_noempty,
                                    hist_fits_Rare1TTW_noempty      = hist_fits_Rare1TTW_noempty,
                                    )


	# Extracting p-values from files
        print_toys_pval(arguments)

        return 0


if __name__ == '__main__':
        start_time = time.time()

        parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('infile', help="Input file")
        parser.add_argument('-o', '--outfile', help="Output file")
        parser.add_argument('-r', '--ratio', help="Make ratio plot", dest='is_ratio', action='store_true')
        parser.add_argument('-j', '--config-json', help="JSON configuration file")
        parser.add_argument('-e', '--extension', help="Plot file extension (.C, .root, .png, .pdf)", default='png')
        parser.add_argument('--dir', help="Plots output directory", default='./')
        parser.add_argument('--blind', help="Blind datapoints from these categories [CAT1,CAT2]", default=None, type=str)
        parser.add_argument('--scale-signal', help="Scale signal", default=1., type=float)
        parser.add_argument('--gof-toys', help="ROOT file with GOF toys for p-value calculation", default=None)
        parser.add_argument('--gof-data', help="ROOT file with observed p-value", default=None)
        parser.add_argument('--distrib-title', help="Histogram title settings", default=';;Events')
        parser.add_argument('--distrib-title-ratio', help="Ratio histogram title settings", default=None)
        parser.add_argument('--draw-chi2', help="Plot chi2 on the plot", dest='draw_chi2', action='store_true', default=False)
        #parser.add_argument('--distrib-title-ratio', help="Ratio histogram title settings", default=';Bin id (D_{t#bar{t}t#bar{t}}^{lj});Rel. diff.')
        parser.add_argument('-b', help="ROOT batch mode", dest='isBatch', action='store_true')

        parser.add_argument(
                        '-d', '--debug',
                        help="Print lots of debugging statements",
                        action="store_const", dest="loglevel", const=logging.DEBUG,
                        default=logging.WARNING,
                        )
        parser.add_argument(
                        '-v', '--verbose',
                        help="Be verbose",
                        action="store_const", dest="loglevel", const=logging.INFO,
                        )

        args = parser.parse_args(sys.argv[1:])

        print(args)

        logging.basicConfig(level=args.loglevel)

        logging.info( time.asctime() )
        exitcode = main(args)
        logging.info( time.asctime() )
        logging.info( 'TOTAL TIME IN MINUTES:' + str((time.time() - start_time) / 60.0))
        sys.exit(exitcode)
