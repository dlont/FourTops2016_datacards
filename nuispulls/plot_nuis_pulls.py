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


def main(arguments):

	rt.gStyle.SetOptStat(0)

	# input file with fit results objects
	root_file = rt.TFile.Open(arguments.infile)

	# fit results objects names
	fit_results_names = ['fit_s', 'fit_b']

	c = root_file.Get("nuisancs")

	# move Legend
	list_of_primitives = c.GetListOfPrimitives()
	legend = list_of_primitives.FindObject("TPave")
        # new_legend = rt.TLegend(0.,0.8,0.99,0.99)
        # legend.Copy(new_legend)
        print legend
	if legend:
	       legend.SetX1(0.7)
	       legend.SetX2(0.99)
	       legend.SetY1(0.9)
	       legend.SetY2(0.99)
               legend.Draw()
               legend.SetNColumns(3)
        c.Update()
        c.Modified()
	c.SaveAs('{0}.{1}'.format(arguments.outfile,arguments.extension))
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
