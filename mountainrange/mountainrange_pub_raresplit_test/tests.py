import unittest
import ROOT as rt
import json

import mountainrange_pub_utilities as mr

class TestMountainRangeMethods(unittest.TestCase):
    def setUp(self):
        self.rootfile = rt.TFile.Open('fitDiagnostics_nominal.root','READ')
        self.jsondic = None
	with open('mountain_mu_pub_tttt10_prefit_combo.json') as json_data:
		self.jsondic = json.load(json_data)

    def test_nbins_retuns_sum_of_bins_in_individual_histos(self):
        """
        get_total_nbins() should return 150 for three histograms 50 bins each
        shapes_fit_s/MU_mu10J2M/NP_overlay_ttttNLO,
        shapes_fit_s/MU_mu10J3M/NP_overlay_ttttNLO,
        shapes_fit_s/MU_mu10J4M/NP_overlay_ttttNLO
        in fitDiagnostics_nominal.root
        """
	nbins = mr.get_total_nbins(self.jsondic,\
                                                            self.rootfile)
        self.assertEqual(nbins,150)

    def test_fillsingle_returns_histograms_bin_edges_on_long_mountainrange(self):
        stitch_edges = []
        nbins = mr.get_total_nbins(self.jsondic,\
                                                            self.rootfile)
        hist = rt.TH1F('hist','Title',nbins,0.5,float(nbins+0.5)) #Long stiched mountain range histogram
	stitch_edges = mr.fillsingle(hist, self.rootfile, self.jsondic['prefit_total'])
        expected = [50,100,150]
        self.assertListEqual(stitch_edges,expected)

    def test_binmap_returns_continuos_numbers_for_nonempty_bins(self):
        nbins = mr.get_total_nbins(self.jsondic,\
                                                            self.rootfile)
        hist = rt.TH1F('hist','Title',nbins,0.5,float(nbins+0.5)) #Long stiched mountain range histogram
	mr.fillsingle(hist, self.rootfile, self.jsondic['prefit_total'])

        gr_data = mr.fillsingle_data(self.rootfile, \
                                                    self.jsondic['data'],\
                                                    hist,None)
        expected = [24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,\
                    36, 37, 38, 39, 40, 41, 42, 43, 45, 81, 82, 83,\
                    84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95,\
                    96, 97, 98, 138, 139, 140, 141, 142, 143, 144,\
                    145, 146, 147, 148, 149, 150]
        #hist.Print("all")
        #gr_data.Print("all")
        binmapping = mr.binmap(hist, None, gr_data)
        actual = binmapping.keys()
        actual.sort()
        self.assertListEqual(actual,expected)

if __name__ == '__main__':
    unittest.main()
