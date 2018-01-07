#!/usr/bin/env python

"""
Postfit normalization tables from combine output files.
input: fitDiagnostics.root or mlfit.root file produced with --saveNormalizations
flag
"""

import os
import sys
import time
import argparse
import logging
import json
from pprint import pprint,pformat
import ROOT as rt

def progress(current, total, status=''):
        fullBarLength = 80
        doneBarLength = int(round(fullBarLength * current / float(total)))

        percents = round(100.0 * current / float(total), 1)
        bar = '>' * doneBarLength + ' ' * (fullBarLength - doneBarLength)

        sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
        sys.stdout.flush()

class DataNormFromShape:
	def __init__(self,root_file):
		self.root_file = root_file                     				#root file handle
		self.data_dir_name = 'shapes_prefit'					#name of the folder with data graphs
		self.observation_name = 'data'						#name of the data graph
		if self.root_file:
			self.data_dir = self.root_file.Get(self.data_dir_name)
		logging.info( 'DATA directory: '+self.data_dir_name )
		pass
	def get(self):
		"""
		Create RooArgSet with the number of observed events

		:returns: RooArgSet
		"""
		data = rt.RooArgSet('data')
		#for each folder (search category) extract the
		#number of observed events and create RooAbsArg
		for fold in self.data_dir.GetListOfKeys():
			logging.debug( fold.GetName() )
			if not fold.IsFolder(): continue	#check if this is a floder
			fold.ReadObj().cd()			#cd to this folder
			gr = rt.gDirectory.Get(self.observation_name)	#retrieve graph with data observation
			n_observed_events = 0
			for ibin in range(0,gr.GetN()): n_observed_events += gr.GetY()[ibin]
			logging.info( fold.GetName()+': '+str(n_observed_events) )
			#create new RooFit object and add it to RooArgSet
			datum = rt.RooRealVar( fold.GetName()+'/observation','observation', n_observed_events )
			#datum.Print()
			data.add(datum)
		return data

class OthersNorm:
	def __init__(self,root_file,other_backgrounds):
		self.root_file = root_file                     				#root file handle
		self.prefit_norm_name = 'norm_prefit'					#RooAbsSet prefit normalizations name
		self.postfit_norm_name = 'norm_fit_s'					#RooAbsSet prefit normalizations name
		self.others_backgrounds_names = other_backgrounds			#Names of the other background
		self.name = 'others'
		if self.root_file:
			self.prefit_norm = self.root_file.Get(self.prefit_norm_name)
			self.postfit_norm = self.root_file.Get(self.postfit_norm_name)
		pass

	def set_name(self,name):
		self.name = name

	def discover_search_regions(self):
		"""
		Identify all search regions according to the name of
		the normalization variable name, e.g.
		MU_mu9J3M/ttbarTTX -> MU_mu9J3M


		:returns: list of strings with search regions names
		"""

		result = []
		# fill a list with normalization parameters of all contributions
		siter = self.prefit_norm.fwdIterator()
		arg = siter.next()
		while arg:
			result.append(arg.GetName())
			arg = siter.next()

		# save search regions names in a new list
		# remove part to the string after '/', i.e.
		# MU_mu9J3M/ttbarTTX -> MU_mu9J3M
		temp_result = []
		for item in result:
			temp_result.append(item.split('/')[0])
		# remove duplicates by converting list to set
		# and return list type instead of set type
		# IMPORTANT: set changes the order of elements in the collection
		# therefore the order has to be restored
		result = list(set(temp_result))

		logging.debug(pformat(result))

		return result


	def fill_missing_search_categories(self, bckg_roo_args_set, all_search_regions):
		"""
		RooAbsArg pre-(post-) fit objects are filled only for non-zero content,
		therefore missing objects have to be created. It is important to keep
		new objects in the same order as ttbar and tttt, otherwise entries in
		LaTeX table will be screwed.
		:param bckg_roo_args_set: RooAbsSet with existing background normalizations
		:returns: modified bckg_roo_args_set, where missing zero elements are added
		"""

		background_name = None
		existing_search_regions = []
		siter = bckg_roo_args_set.fwdIterator()
		arg = siter.next()
		while arg:
			search_region_name = arg.GetName().split('/')[0]
			background_name = arg.GetName().split('/')[1]
			existing_search_regions.append(search_region_name)

			arg = siter.next()

		missing_search_regions = [item for item in all_search_regions if item not in existing_search_regions]
		for search_region in missing_search_regions:
			#create new RooFit object and add it to RooArgSet
			entry = rt.RooRealVar( search_region+'/'+background_name, background_name, 0 )
			bckg_roo_args_set.add(entry)

		#restore sorted order of elements
		bckg_roo_args_set.sort()

		return bckg_roo_args_set

	def get(self,collection):
		"""
		Create RooArgSet with prefit or postfit values of the others backgrounds
		:param collection: prefit of postfit RooAbsSet collection
		:returns: RooArgSet
		"""

		other_backgrounds_norm_dic = {}

		search_regions_list = self.discover_search_regions()

		#fill missing search regions entries with zeros for all others backgrounds
		for bck_name in self.others_backgrounds_names:
			#select exiting RooArg objects
			roo_bckg_collection = collection.selectByName('*/'+bck_name)
			self.fill_missing_search_categories(roo_bckg_collection,search_regions_list)
			#roo_bckg_collection.Print()
			#clone updated list to the dictionary entry
			other_backgrounds_norm_dic[bck_name] = rt.RooArgSet(roo_bckg_collection)

		#sum up all other backgrounds together
		others_backgrounds = rt.RooArgSet(self.name)
		for search_region in search_regions_list:
			others_backgrounds_sum = 0
			others_backgrounds_error2 = 0
			for bck_name in other_backgrounds_norm_dic.keys():
				entry_name = '{}/{}'.format(search_region,bck_name)
				others_backgrounds_sum += other_backgrounds_norm_dic[bck_name].getRealValue(entry_name)
				error = other_backgrounds_norm_dic[bck_name].find(entry_name).getError()
				others_backgrounds_error2 += error*error
			others_entry = rt.RooRealVar( search_region+'/'+self.name, self.name, others_backgrounds_sum )
			others_entry.setError(rt.TMath.Sqrt(others_backgrounds_error2))
			others_backgrounds.add(others_entry)
		others_backgrounds.sort()
		others_backgrounds.Print()

		return others_backgrounds

	def get_prefit(self):
		return self.get(self.prefit_norm)

	def get_postfit(self):
		return self.get(self.postfit_norm)

def main(arguments):

	# Enforce no garbage collection
	rt.TH1.__init__._creates = False
	rt.TH2.__init__._creates = False
	rt.RooArgSet.__init__._creates = False
	rt.RooRealVar.__init__._creates = False

	# open root file
	root_file = rt.TFile.Open(arguments.infile,"READ")				#root file handle
	if not root_file:
		logging.error("Cannot open file: "+arguments.infile)
		sys.exit(1)

	#create data normalization RooFit Object
	creator_data = DataNormFromShape(root_file)
	data = creator_data.get()
	#data.Print()

	#create others backgrounds normalization RooFit Object
	creator_others = OthersNorm(root_file, ['EW','TTRARE_plus','ST_tW','Rare1TTHZ'])
	creator_others.set_name('other')
	#create others backgrounds normalization RooFit Object
	creator_total = OthersNorm(root_file, ['ttbarTTX','NP_overlay_ttttNLO','EW','TTRARE_plus','ST_tW', 'Rare1TTHZ'])
	creator_total.set_name('total')

	#retrieve prefit normalizations
	prefit_norm_name = 'norm_prefit'
	norm_prefit = root_file.Get(prefit_norm_name)
	norm_prefit_ttbar = norm_prefit.selectByName('*/ttbarTTX')
	#norm_prefit_ttbar.Print()
	norm_prefit_tttt = norm_prefit.selectByName('*/NP_overlay_ttttNLO')
	#norm_prefit_tttt.Print()
	#make prefit normalizations of non tt background
	norm_prefit_others = creator_others.get_prefit()
	norm_prefit_total = creator_total.get_prefit()


	#retrieve postfit normalizations
	postfit_norm_name = 'norm_fit_s'
	norm_postfit = root_file.Get(postfit_norm_name)
	norm_postfit_ttbar = norm_postfit.selectByName('*/ttbarTTX')
	#norm_postfit_ttbar.Print()
	norm_postfit_tttt = norm_postfit.selectByName('*/NP_overlay_ttttNLO')
	#norm_postfit_tttt.Print()
	norm_postfit_others = creator_others.get_postfit()
	norm_postfit_total = creator_total.get_postfit()

	#make latex table
	data.printLatex(rt.RooFit.Sibling(norm_postfit_total),
			rt.RooFit.Sibling(norm_postfit_ttbar),rt.RooFit.Sibling(norm_postfit_others),rt.RooFit.Sibling(norm_postfit_tttt),
			rt.RooFit.Sibling(norm_prefit_total),
			rt.RooFit.Sibling(norm_prefit_ttbar), rt.RooFit.Sibling(norm_prefit_others), rt.RooFit.Sibling(norm_prefit_tttt))
	#data.printLatex(rt.RooFit.Sibling(norm_postfit_ttbar),rt.RooFit.Sibling(norm_postfit_others), rt.RooFit.Sibling(norm_postfit_tttt),
	#		rt.RooFit.Sibling(norm_prefit_ttbar), rt.RooFit.Sibling(norm_prefit_others), rt.RooFit.Sibling(norm_prefit_tttt))
	#data.printLatex(rt.RooFit.Sibling(norm_postfit_ttbar),rt.RooFit.Sibling(norm_postfit_tttt),
	#		rt.RooFit.Sibling(norm_prefit_ttbar),rt.RooFit.Sibling(norm_prefit_tttt))
	#norm_prefit_tttt.printLatex(rt.RooFit.Sibling(norm_postfit_tttt))
	#norm_postfit_ttbar.printLatex(rt.RooFit.Sibling(norm_prefit_ttbar))

        return 0


if __name__ == '__main__':
        start_time = time.time()

        parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('infile', help="Input file")
        parser.add_argument('-o', '--outfile', help="Output file")
        parser.add_argument('-j', '--config-json', type=json.loads, help="JSON configuration file")
        #parser.add_argument('-b', help="ROOT batch mode", dest='isBatch', action='store_true')
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
