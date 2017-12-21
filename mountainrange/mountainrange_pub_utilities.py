#!/usr/bin/env python

"""
Functions for mountainrange histograms
"""

import gc
import re
import os
import sys
import time
import logging
import json
import pprint

import ROOT as rt
import array

from mountainrange_style import Style

def fillsingle(hist_master, rootfile, list_hists_in_file):
        """
        Fill long mountain range histogram including empty bins
        :param hist_master: empty histogram to fill
        :param rootfile: input rootfile with original list_hists_in_file that should be stiched
        :return: list of bins in hist_master corresponding to boundaries of
                    individual list_hists_in_file
        """
	logging.debug( 'fillsingle()' )
	stitch_edge_bins = []
	previous_stitch_bin = 0
	hist = None
	for ihist,name in enumerate(list_hists_in_file):
		logging.debug( 'Trying to read {} from {}'.format(name,rootfile.GetName()) )
		hist = rootfile.Get(name.encode('ascii'))
		nbins = hist.GetNbinsX()
		logging.debug( '{} {} {}'.format(ihist,name,nbins) )
		stitch_edge_bins.append(previous_stitch_bin + nbins)
		for ibin in range(1,nbins+1):   #range(1,nbins+1) returns 1..nbins
			#print name, nbins, ihist, ibin, previous_stitch_bin+ibin
			hist_master.SetBinContent(previous_stitch_bin+ibin,hist.GetBinContent(ibin))
			hist_master.SetBinError(previous_stitch_bin+ibin,hist.GetBinError(ibin))
		previous_stitch_bin+=nbins

	hist_master.SetTitle('{};{};{}'.format(hist.GetTitle(),hist.GetXaxis().GetTitle(),hist.GetYaxis().GetTitle()))

	return stitch_edge_bins

def fillsingle_data(rootfile, graphs, hist_template, blind=None):
    """
    Fill long master graph for data
    :param rootfile: root file handle with input graphs
    :param graphs: list of graphs names from rootfile
    :param hist_template: long master histogram for binning
    :param blind: list of coma separated names of individual hists for blinding
    :return: long root TGraph with data counts
    """
    if hist_template is None:
        raise ValueError('hist_template was not provided in fillsingle_data()')

    gr_master = rt.TGraphAsymmErrors(hist_template.GetNbinsX())
    previous_stitch_bin = 0
    gr = None

    #iterate over individual graphs
    for igr,name in enumerate(graphs):
            gr = rootfile.Get(name.encode('ascii'))
            if isinstance(gr, rt.TH1):
                    gr.SetBinErrorOption(rt.TH1.kPoisson)
                    gr = rt.TGraphAsymmErrors(gr)
            nbins = gr.GetN()       #assumes that graph has the same number of points as corresponding S or B histos
            ylist = gr.GetY()
            yhi   = gr.GetEYhigh()
            ylo   = gr.GetEYlow()
            if blind is not None:   #blind part of the spectum
                    for cat in str(blind).split(','):
                            if cat in name.encode('ascii'):
                                    ylist = [0] * nbins
                                    yhi = [0] * nbins
                                    ylo = [0] * nbins
                                    break
            for ibin in range(1,nbins+1):   #copy points from individual graphs to the master graph
                    #print nbins, igr, ibin, previous_stitch_bin+ibin
                    bincenter = hist_template.GetBinCenter(previous_stitch_bin+ibin)
                    gr_master.SetPoint(previous_stitch_bin+ibin-1,bincenter,ylist[ibin-1])
                    gr_master.SetPointError(previous_stitch_bin+ibin-1,0.,0.,ylo[ibin-1],yhi[ibin-1])
            previous_stitch_bin+=nbins
    #Fetch axes titles from the last graph in the list
    gr_master.SetTitle('{};{};{}'.format(gr.GetTitle(),gr.GetXaxis().GetTitle(),gr.GetYaxis().GetTitle()))
    return gr_master

def guess_process_by_hist_name(hist_name):
    if 'EW' in hist_name: return 'EW'
    if 'ST' in hist_name: return 'ST'
    if 'ttbar' in hist_name: return 'TTBAR'
    if 'TTH' in hist_name: return 'TTH'
    if 'TTZ' in hist_name: return 'TTZ'
    if 'TTW' in hist_name: return 'TTW'
    if 'TTRARE_plus' in hist_name: return 'TTXY'

def fillstack(stack, hist_template, rootfile, histograms):
        """
        Fill long mountain range histograms including empty bins for stack object
        """
	master_hists = []
	for isource in range(0,len(histograms[0])):
                hist_name  = histograms[0][isource]
		name  = 'source'+str(isource)
		clone = hist_template.Clone(name)
                color = Style.colors[guess_process_by_hist_name(hist_name)]
		logging.info("name: {}".format(hist_name))
		logging.info("color {}: {}".format(isource, color))
		clone.SetFillColor( color )
		clone.SetLineColor( color )
		clone.SetMarkerColor( color )
		master_hists.append(clone)
		clone.Reset()
	logging.debug( 'Length of master_hists: {}'.format( len(master_hists) ) )
	logging.debug( 'Length of mountaintrange sources: {}'.format(len(histograms)))
	previous_stitch_bin = 0
	for ichannel,channel_hists in enumerate(histograms):
		nbins = 0
		for isource,name in enumerate(channel_hists):
			hist = rootfile.Get(name.encode('ascii'))
			logging.debug('processing stack hist: %s' % name)
			if not hist:
				logging.warning('ACHTUNG!!! Histogram %s not found. Check input!!!' % name)
				continue
			nbins = hist.GetNbinsX()
			for ibin in range(1,nbins+1):
				logging.debug('processing stack hist: %s, source: %s' % (name, isource))
				master_hists[isource].SetBinContent(previous_stitch_bin+ibin,hist.GetBinContent(ibin))
				master_hists[isource].SetBinError(previous_stitch_bin+ibin,hist.GetBinError(ibin))
		previous_stitch_bin+=nbins
	for hist in master_hists:
		stack.Add(hist,'hist')
	return

def binmap(totalhist=None, sighist=None, datagr=None):
        """
        Map all non-empty bins in long histogram to sequential bin numbers
        e.g. a histogram with three bins, whith only first and third bin filled
        will be mapped to two bins 1->1, 2->None, 3->2
        """
	nonemptybinid = set()

	global_nbins = totalhist.GetNbinsX()

	if totalhist is not None:
		nbins = global_nbins
		for ibin in range(1,nbins+1):
			if totalhist.GetBinContent(ibin) > 1.E-05: nonemptybinid.add(ibin)
			#else: totalhist.Print("all"); break
	if sighist is not None:
                nbins = global_nbins
                for ibin in range(1,nbins+1):
                        if sighist.GetBinContent(ibin) > 1.E-05: nonemptybinid.add(ibin)
			#else: sighist.Print("all"); break

	if datagr is not None:
                nbins = global_nbins
		ylist = datagr.GetY()
                for ibin in range(1,nbins+1):
                        if ylist[ibin-1] > 1.E-05: nonemptybinid.add(ibin)
			#else: datagr.Print("all"); break

	#create a map between old and new bin numbers
        logging.info(nonemptybinid)
	nonemptybinid_list = list(nonemptybinid)
	nonemptybinid_list.sort()
	nonemptybin_map = dict()
 	for i in range(0,len(nonemptybinid_list)): nonemptybin_map[nonemptybinid_list[i]] = i+1
	logging.info( "Bin mapping:")
	logging.info(pprint.pformat( nonemptybin_map ) )
	return nonemptybin_map


def noemptybins(hist, nonemptybin_map):
        if hist is None:
            raise ValueError('hist was not provided in noemptybins_data()')

	title = "%s;%s;%s" % (hist.GetTitle(),hist.GetXaxis().GetTitle(),hist.GetYaxis().GetTitle())
	new_hist = rt.TH1F(hist.GetName()+'_mountain', title, len(nonemptybin_map), -0.5, len(nonemptybin_map)-0.5)
	new_hist.SetFillColor(hist.GetFillColor())

	logging.debug("non empty bins")
	for ibin in range(1,hist.GetNbinsX()+1):
		if ibin in nonemptybin_map:
			new_hist.SetBinContent(	nonemptybin_map[ibin], hist.GetBinContent(ibin) )
			new_hist.SetBinError(	nonemptybin_map[ibin], hist.GetBinError(ibin) )
	return new_hist

def noemptybins_data(gr, nonemptybin_map, hist_template):
        if hist_template is None:
            raise ValueError('hist_template was not provided in noemptybins_data()')
        if gr is None:
            raise ValueError('gr was not provided in noemptybins_data()')

	new_gr = rt.TGraphAsymmErrors(len(nonemptybin_map))
	new_gr.SetMarkerStyle(20)

	logging.debug("non empty bins")
	ylist = gr.GetY()
	yhi   = gr.GetEYhigh()
	ylo   = gr.GetEYlow()
	for ibin in range(1,gr.GetN()+1):
		if ibin in nonemptybin_map:
			x = hist_template.GetBinCenter(nonemptybin_map[ibin])
			y = ylist[ibin-1]
			eyh = yhi[ibin-1]
			eyl = ylo[ibin-1]
			new_gr.SetPoint(nonemptybin_map[ibin]-1,x,y)	#change here to remove slope
			new_gr.SetPointError(nonemptybin_map[ibin]-1,0.,0.,eyl,eyh)

	return new_gr

def fillnonemptysingle( arguments, rootfile, list_hists_in_file, name, nbins, nonemptybin_map):
        #check that individual histograms exist in the file
        root_keys = [ rootfile.Get(hname.encode('ascii')) != None for hname in list_hists_in_file ]
        if not all(root_keys): return None

        hist_master = rt.TH1F(name,arguments.distrib_title,nbins,0.5,float(nbins+0.5))
        fillsingle(hist_master, rootfile, list_hists_in_file)
        hist_noempty = noemptybins(hist_master, nonemptybin_map)
        return hist_noempty


def get_total_nbins(jsondic,inputrootfile):
        """
        Calculate total number of bins in signal histgrams from json config

        :param jsondic: dictionary with histogram names to be used for nbins calculation
        :param inputrootfile: root file from which histograms will be retrieved
        :return: sum of number of bins in histograms

        For example if the following dictionary is provided
                  'signal':['shapes_fit_s/MU_mu10J2M/NP_overlay_ttttNLO',
                            'shapes_fit_s/MU_mu10J3M/NP_overlay_ttttNLO',
                            'shapes_fit_s/MU_mu10J4M/NP_overlay_ttttNLO'],
        the routine returns sum of number of bins in three hists
        """
        nbins = 0
	logging.debug( '%s: %s' % ('signal',jsondic['signal']) )
	for hist_name in jsondic['signal']:
		logging.debug( 'hist %s' % (hist_name) )
		hist = inputrootfile.Get(hist_name.encode('ascii'))
		nb = hist.GetNbinsX()
		logging.debug( 'hist %s, nbins=%s' % (hist_name, nb) )
		nbins += nb
	logging.info('Mountain range plot nbins: ' + str(nbins))
        return nbins

def make_gr_ratio_data(gr_data_noempty,hist_bg_unc_noempty):
        gr_ratio_data = rt.TGraphAsymmErrors()
    	gr_ratio_data.SetMarkerStyle(20)
        ipoint = 0
        ydata = gr_data_noempty.GetY()
	xdata = gr_data_noempty.GetX()
	for ibin in range(0,hist_bg_unc_noempty.GetNbinsX()):
		ymc   = hist_bg_unc_noempty.GetBinContent(ibin+1)
		eymc  = hist_bg_unc_noempty.GetBinError(ibin+1)
		eyh   = gr_data_noempty.GetErrorYhigh(ibin)
		eyl   = gr_data_noempty.GetErrorYlow(ibin)

                if ydata[ibin] < 1.E-6: continue

                gr_ratio_data.SetPoint(ipoint,xdata[ibin],(ydata[ibin]-ymc)/ymc)
                gr_ratio_data.SetPointError(ipoint,0.,0.,eyl/ymc, eyh/ymc)
                ipoint+=1
        return gr_ratio_data

def get_chi2_ndf(gr_data_noempty,hist_bg_unc_noempty):
    chi2 = 0
    ndf = 0
    ydata = gr_data_noempty.GetY()
    xdata = gr_data_noempty.GetX()
    for ibin in range(0,hist_bg_unc_noempty.GetNbinsX()):
	ymc   = hist_bg_unc_noempty.GetBinContent(ibin+1)
	eymc  = hist_bg_unc_noempty.GetBinError(ibin+1)
	eyh   = gr_data_noempty.GetErrorYhigh(ibin)
	eyl   = gr_data_noempty.GetErrorYlow(ibin)
        if ymc > 1.E-6:
		#chi2+=(ydata[ibin]-ymc)**2/(((eyh+eyl)/2.)**2.)
		chi2+=(ydata[ibin]-ymc)**2/(((eyh+eyl)/2.)**2.+eymc**2.)
		ndf+=1.
    return chi2, ndf
