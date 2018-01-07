import unittest
import ROOT as rt
import json

import postfitnorm as pfn

class TestPostFitNormMethods(unittest.TestCase):
    def setUp(self):
        rt.RooArgSet.__init__._creates = False
        rt.RooRealVar.__init__._creates = False
        self.rootfile = rt.TFile.Open('fitDiagnostics_nominal.root','READ')

    def test_data_is_correct(self):
        creator_data = pfn.DataNormFromShape(self.rootfile)
    	data = creator_data.get()

        expected = [146, 25, 11, 1221, 246, 46, 401, 106, 21, 218, 71, 19,\
                    4872, 974, 111, 1770, 368, 70, 511, 135, 26]
        actual = []

        fwdItr = data.fwdIterator()
        arg = fwdItr.next()
        # fill a list with normalization parameters of all contributions
        while arg:
            actual.append(data.getRealValue(arg.GetName()))
            arg = fwdItr.next()

        self.assertListEqual(actual,expected)

    def test_single_souce_prefitunc_is_correct(self):
        #retrieve prefit normalizations
        prefit_norm_name = 'norm_prefit'
        norm_prefit = self.rootfile.Get(prefit_norm_name)
        norm_prefit_ttbar = norm_prefit.selectByName('*/ttbarTTX')

        expected = [84.63175645058388, 18.59961110121814, 52.37656086037833,\
                    303.06787113504726, 84.30994053833759, 27.951332562798356,\
                    173.71704234109384, 40.15000232109169, 11.152431735356046,\
                    305.75750397152456, 69.4196310957529, 39.614691176066295,\
                    2935.36354283777, 658.7460889115573, 81.20679217483544,\
                    1347.8241738940383, 333.2901618736515, 56.71466122957316,\
                    430.11899630057957, 138.18913734648063, 28.871522879434593]
        actual = []

        fwdItr = norm_prefit_ttbar.fwdIterator()
        arg = fwdItr.next()
        # fill a list with normalization parameters of all contributions
        while arg:
            actual.append(norm_prefit_ttbar.find(arg.GetName()).getError())
            arg = fwdItr.next()

        self.assertListEqual(actual,expected)

    def test_multisource_prefitunc_is_correct(self):
        creator_sum = pfn.OthersNorm(self.rootfile, ['EW','ST_tW'])
    	creator_sum.set_name('ew_plus_st')
	norm_prefit_sum = creator_sum.get_prefit()

        expected = [0.5155177546715211, 0.0, 0.0,\
                    3.074211630643509, 0.581615707367516, 0.11437460279046319,\
                    0.8996901929611276, 0.09104709487550655, 0.0,\
                    0.527354099578041, 0.0, 0.45723532474306183,\
                    11.052450801510185, 1.4616284179173997, 0.13878159232378723,\
                    3.370594743955008, 0.4508272092457667, 0.2554080345081216,\
                    1.2364985126100747, 0.31432623872210547, 0.0]
        actual = []

	fwdItr = norm_prefit_sum.fwdIterator()
	arg = fwdItr.next()
	# fill a list with normalization parameters of all contributions
	while arg:
		actual.append(norm_prefit_sum.find(arg.GetName()).getError())
		arg = fwdItr.next()

        self.assertListEqual(actual,expected)

if __name__ == '__main__':
    unittest.main()
