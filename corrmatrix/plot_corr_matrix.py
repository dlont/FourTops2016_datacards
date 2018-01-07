#!/usr/bin/env python

"""
Plot correlation matrix of the combine Higgs parameters
"""

import os
import re
import sys
import time
import argparse
import logging
import json
from pprint import pprint
from prettytable import  PrettyTable
from prettytable import MSWORD_FRIENDLY
#import pandas as pd
import ROOT as rt

def progress(current, total, status=''):
        fullBarLength = 80
        doneBarLength = int(round(fullBarLength * current / float(total)))

        percents = round(100.0 * current / float(total), 1)
        bar = '>' * doneBarLength + ' ' * (fullBarLength - doneBarLength)

        sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
        sys.stdout.flush()

class CorrelationMatrixBuilder(object):
	"""
	Returns decorated correlation matrix
	"""
	def __init__(self,**kw):
		if 'root_file' in kw:
			self.root_file = kw['root_file']

	def set_fit_object(self,fit_obj_name):
		self.roofit_obj_name = fit_obj_name
		pass

	def get_histogram(self,name='correlation_matrix'):
		"""
		Builds ROOT histogram with correlation matrix
		"""
		fit_result = self.root_file.Get(self.roofit_obj_name)
		orig_corr_hist = fit_result.correlationHist(name)
		logging.debug('fit result name: '+self.roofit_obj_name)
		logging.debug('original corr hist: {0}'.format(orig_corr_hist))
		return orig_corr_hist
		
class CorrMatrixWithoutBins(CorrelationMatrixBuilder):
	"""
	Rule to be applied when correlation matrix entries are retrieved
	"""
	def set_excluded_bins(self,regex):
		self.prog = re.compile(regex)

	def get_histogram(self,name):
		orig_corr_hist = super(CorrMatrixWithoutBins, self).get_histogram(name)

		#count number of bins excluding those that match regex pattern
		new_n_bins = 0
		for j in range(1,orig_corr_hist.GetNbinsY()+1):
			if self.prog.match(orig_corr_hist.GetXaxis().GetBinLabel(j)): continue
			new_n_bins += 1

		new_corr_hist = rt.TH2D('corr_matrix_filtered',name,new_n_bins,0.,1.,new_n_bins,0.,1.)
		new_i = 0
		new_j = 0
		for i in range(1,orig_corr_hist.GetNbinsX()+1):
			if self.prog.match(orig_corr_hist.GetXaxis().GetBinLabel(i)): continue
			new_i += 1
			for j in range(1,orig_corr_hist.GetNbinsY()+1):
				if self.prog.match(orig_corr_hist.GetYaxis().GetBinLabel(j)): continue
				new_j += 1
				new_corr_hist.SetBinContent(new_i,new_j,orig_corr_hist.GetBinContent(i,j))
				new_corr_hist.GetXaxis().SetBinLabel(new_i,orig_corr_hist.GetXaxis().GetBinLabel(i))
				new_corr_hist.GetYaxis().SetBinLabel(new_j,orig_corr_hist.GetYaxis().GetBinLabel(j))
				if orig_corr_hist.GetYaxis().GetBinLabel(j) is 'r' and 'TTRARE' in orig_corr_hist.GetXaxis().GetBinLabel(i):
					print orig_corr_hist.GetBinContent(i,j)
			new_j = 0

		return new_corr_hist
	

def main(arguments):
	
	rt.gStyle.SetOptStat(0)

	# input file with fit results objects
	root_file = rt.TFile.Open(arguments.infile)

	# fit results objects names
	fit_results_names = ['fit_s', 'fit_b']

	matrix_builder = CorrMatrixWithoutBins(root_file=root_file)
	matrix_builder.set_excluded_bins('prop.*')
	for fit_obj in fit_results_names:
		matrix_builder.set_fit_object(fit_obj)
		h = matrix_builder.get_histogram(fit_obj)
		c = rt.TCanvas('c')
		c.SetBottomMargin(0.3)
		c.SetLeftMargin(0.3)
		h.Draw('colz')
		h.SetAxisRange(-1.,1.,"Z")
		h.GetXaxis().LabelsOption("v")
		c.Print('{0}_{1}.{2}'.format(arguments.outfile,fit_obj,arguments.extension))
        return 0


if __name__ == '__main__':
        start_time = time.time()

        parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('infile', help="Input file")
        parser.add_argument('-o', '--outfile', help="Output file",default='corr')
        parser.add_argument('-e', '--extension', help="Output file extension", default='png')
        parser.add_argument('-j', '--config-json', type=json.loads, help="JSON configuration file")
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
