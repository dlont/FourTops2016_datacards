.PHONY: newlimit

TOLERANCE=0.01
COMBASYMPT=combine -M Asymptotic --minimizerTolerance=${TOLERANCE}
COMBASYMPTNOASIMOV=combine -M Asymptotic --noFitAsimov --minimizerTolerance=${TOLERANCE}
COMBMLSHAPESBG=combine -M MaxLikelihoodFit -t -1 --expectSignal=0 --saveShapes --minos=all -v2 --minimizerTolerance=${TOLERANCE}
COMBMLSHAPESSG=combine -M MaxLikelihoodFit -t -1 --expectSignal=1 --saveShapes --minos=all -v2 --minimizerTolerance=${TOLERANCE}
DIFFTOOL=python ../../../HiggsAnalysis/CombinedLimit/test/diffNuisances.py

newlimit: CombinedSingleBDT CombinedDoubleBDT TOP-combined TOP-SUS-combined
	@echo "Calculate new limits"

.PHONY: CombinedSingleBDT
CombinedSingleBDT: CombinedSingleBDT_lumisc_unc2p3.out CombinedSingleBDT_lumisc_unc2p3_noasimov.out CombinedSingleBDT_lumisc_unc2p3_mlfit.out\
		   CombinedSingleBDT_lumisc_unc2p7.out CombinedSingleBDT_lumisc_unc2p7_noasimov.out CombinedSingleBDT_lumisc_unc2p7_mlfit.out\
		   CombinedSingleBDT_lumisc_unc3p7.out CombinedSingleBDT_lumisc_unc3p7_noasimov.out CombinedSingleBDT_lumisc_unc3p7_mlfit.out

CombinedSingleBDT_lumisc_unc2p3.out: CombinedSingleBDT_lumisc_unc2p3.txt
	@echo "Processing Single lepton channel. New lumi and unc"
	${COMBASYMPT} $^ > CombinedSingleBDT_lumisc_unc2p3.out
CombinedSingleBDT_lumisc_unc2p3_noasimov.out: CombinedSingleBDT_lumisc_unc2p3.txt
	@echo "Processing Single lepton channel. New lumi and unc"
	${COMBASYMPTNOASIMOV} $^ > CombinedSingleBDT_lumisc_unc2p3_noasimov.out
CombinedSingleBDT_lumisc_unc2p3_mlfit.out: CombinedSingleBDT_lumisc_unc2p3.txt
	@echo "Processing Single lepton channel. New lumi and unc"
	${COMBMLSHAPESBG} $^ -n SingleBDT_lumisc_unc2p3_bg > CombinedSingleBDT_lumisc_unc2p3_mlfit_bg.out
	${DIFFTOOL} -a mlfitSingleBDT_lumisc_unc2p3_bg.root -g plots_mlfitSingleBDT_lumisc_unc2p3_bg.root
	${COMBMLSHAPESSG} $^ -n SingleBDT_lumisc_unc2p3_sg > CombinedSingleBDT_lumisc_unc2p3_mlfit_sg.out
	${DIFFTOOL} -a mlfitSingleBDT_lumisc_unc2p3_sg.root -g plots_mlfitSingleBDT_lumisc_unc2p3_sg.root

CombinedSingleBDT_lumisc_unc2p7.out: CombinedSingleBDT_lumisc_unc2p7.txt
	@echo "Processing Single lepton channel. New lumi and unc"
	${COMBASYMPT} $^ > CombinedSingleBDT_lumisc_unc2p7.out
CombinedSingleBDT_lumisc_unc2p7_noasimov.out: CombinedSingleBDT_lumisc_unc2p7.txt
	@echo "Processing Single lepton channel. New lumi and unc"
	${COMBASYMPTNOASIMOV} $^ > CombinedSingleBDT_lumisc_unc2p7_noasimov.out
CombinedSingleBDT_lumisc_unc2p7_mlfit.out: CombinedSingleBDT_lumisc_unc2p7.txt
	@echo "Processing Single lepton channel. New lumi and unc"
	${COMBMLSHAPESBG} $^ -n SingleBDT_lumisc_unc2p7_bg > CombinedSingleBDT_lumisc_unc2p7_mlfit_bg.out
	${DIFFTOOL} -a mlfitSingleBDT_lumisc_unc2p7_bg.root -g plots_mlfitSingleBDT_lumisc_unc2p7_bg.root
	${COMBMLSHAPESSG} $^ -n SingleBDT_lumisc_unc2p7_sg > CombinedSingleBDT_lumisc_unc2p7_mlfit_sg.out
	${DIFFTOOL} -a mlfitSingleBDT_lumisc_unc2p7_sg.root -g plots_mlfitSingleBDT_lumisc_unc2p7_sg.root

CombinedSingleBDT_lumisc_unc3p7.out: CombinedSingleBDT_lumisc_unc3p7.txt
	@echo "Processing Single lepton channel. New lumi and unc"
	${COMBASYMPT} $^ > CombinedSingleBDT_lumisc_unc3p7.out
CombinedSingleBDT_lumisc_unc3p7_noasimov.out: CombinedSingleBDT_lumisc_unc3p7.txt
	@echo "Processing Single lepton channel. New lumi and unc"
	${COMBASYMPTNOASIMOV} $^ > CombinedSingleBDT_lumisc_unc3p7_noasimov.out
CombinedSingleBDT_lumisc_unc3p7_mlfit.out: CombinedSingleBDT_lumisc_unc3p7.txt
	@echo "Processing Single lepton channel. New lumi and unc"
	${COMBMLSHAPESBG} $^ -n SingleBDT_lumisc_unc3p7_bg > CombinedSingleBDT_lumisc_unc3p7_mlfit_bg.out
	${DIFFTOOL} -a mlfitSingleBDT_lumisc_unc3p7_bg.root -g plots_mlfitSingleBDT_lumisc_unc3p7_bg.root
	${COMBMLSHAPESSG} $^ -n SingleBDT_lumisc_unc3p7_sg > CombinedSingleBDT_lumisc_unc3p7_mlfit_sg.out
	${DIFFTOOL} -a mlfitSingleBDT_lumisc_unc3p7_sg.root -g plots_mlfitSingleBDT_lumisc_unc3p7_sg.root







.PHONY: CombinedDoubleBDT
CombinedDoubleBDT: CombinedDoubleBDT_lumisc_unc2p3.out CombinedDoubleBDT_lumisc_unc2p3_noasimov.out CombinedDoubleBDT_lumisc_unc2p3_mlfit.out\
		   CombinedDoubleBDT_lumisc_unc2p7.out CombinedDoubleBDT_lumisc_unc2p7_noasimov.out CombinedDoubleBDT_lumisc_unc2p7_mlfit.out\
		   CombinedDoubleBDT_lumisc_unc3p7.out CombinedDoubleBDT_lumisc_unc3p7_noasimov.out CombinedDoubleBDT_lumisc_unc3p7_mlfit.out

CombinedDoubleBDT_lumisc_unc2p3.out: CombinedDoubleBDT_lumisc_unc2p3.txt
	@echo "Processing Double lepton channel. New lumi and unc"
	${COMBASYMPT} $^ > CombinedDoubleBDT_lumisc_unc2p3.out
CombinedDoubleBDT_lumisc_unc2p3_noasimov.out: CombinedDoubleBDT_lumisc_unc2p3.txt
	@echo "Processing Double lepton channel. New lumi and unc"
	${COMBASYMPTNOASIMOV} $^ > CombinedDoubleBDT_lumisc_unc2p3_noasimov.out
CombinedDoubleBDT_lumisc_unc2p3_mlfit.out: CombinedDoubleBDT_lumisc_unc2p3.txt
	@echo "Processing Double lepton channel. New lumi and unc"
	${COMBMLSHAPESBG} $^ -n DoubleBDT_lumisc_unc2p3_bg > CombinedDoubleBDT_lumisc_unc2p3_mlfit_bg.out
	${DIFFTOOL} -a mlfitDoubleBDT_lumisc_unc2p3_bg.root -g plots_mlfitDoubleBDT_lumisc_unc2p3_bg.root
	${COMBMLSHAPESSG} $^ -n DoubleBDT_lumisc_unc2p3_sg > CombinedDoubleBDT_lumisc_unc2p3_mlfit_sg.out
	${DIFFTOOL} -a mlfitDoubleBDT_lumisc_unc2p3_sg.root -g plots_mlfitDoubleBDT_lumisc_unc2p3_sg.root

CombinedDoubleBDT_lumisc_unc2p7.out: CombinedDoubleBDT_lumisc_unc2p7.txt
	@echo "Processing Double lepton channel. New lumi and unc"
	${COMBASYMPT} $^ > CombinedDoubleBDT_lumisc_unc2p7.out
CombinedDoubleBDT_lumisc_unc2p7_noasimov.out: CombinedDoubleBDT_lumisc_unc2p7.txt
	@echo "Processing Double lepton channel. New lumi and unc"
	${COMBASYMPTNOASIMOV} $^ > CombinedDoubleBDT_lumisc_unc2p7_noasimov.out
CombinedDoubleBDT_lumisc_unc2p7_mlfit.out: CombinedDoubleBDT_lumisc_unc2p7.txt
	@echo "Processing Double lepton channel. New lumi and unc"
	${COMBMLSHAPESBG} $^ -n DoubleBDT_lumisc_unc2p7_bg > CombinedDoubleBDT_lumisc_unc2p7_mlfit_bg.out
	${DIFFTOOL} -a mlfitDoubleBDT_lumisc_unc2p7_bg.root -g plots_mlfitDoubleBDT_lumisc_unc2p7_bg.root
	${COMBMLSHAPESSG} $^ -n DoubleBDT_lumisc_unc2p7_sg > CombinedDoubleBDT_lumisc_unc2p7_mlfit_sg.out
	${DIFFTOOL} -a mlfitDoubleBDT_lumisc_unc2p7_sg.root -g plots_mlfitDoubleBDT_lumisc_unc2p7_sg.root

CombinedDoubleBDT_lumisc_unc3p7.out: CombinedDoubleBDT_lumisc_unc3p7.txt
	@echo "Processing Double lepton channel. New lumi and unc"
	${COMBASYMPT} $^ > CombinedDoubleBDT_lumisc_unc3p7.out
CombinedDoubleBDT_lumisc_unc3p7_noasimov.out: CombinedDoubleBDT_lumisc_unc3p7.txt
	@echo "Processing Double lepton channel. New lumi and unc"
	${COMBASYMPTNOASIMOV} $^ > CombinedDoubleBDT_lumisc_unc3p7_noasimov.out
CombinedDoubleBDT_lumisc_unc3p7_mlfit.out: CombinedDoubleBDT_lumisc_unc3p7.txt
	@echo "Processing Double lepton channel. New lumi and unc"
	${COMBMLSHAPESBG} $^ -n DoubleBDT_lumisc_unc3p7_bg > CombinedDoubleBDT_lumisc_unc3p7_mlfit_bg.out
	${DIFFTOOL} -a mlfitDoubleBDT_lumisc_unc3p7_bg.root -g plots_mlfitDoubleBDT_lumisc_unc3p7_bg.root
	${COMBMLSHAPESSG} $^ -n DoubleBDT_lumisc_unc3p7_sg > CombinedDoubleBDT_lumisc_unc3p7_mlfit_sg.out
	${DIFFTOOL} -a mlfitDoubleBDT_lumisc_unc3p7_sg.root -g plots_mlfitDoubleBDT_lumisc_unc3p7_sg.root





.PHONY: TOP-combined
TOP-combined: TOP-combined_lumisc_unc2p3.out TOP-combined_lumisc_unc2p3_noasimov.out TOP-combined_lumisc_unc2p3_mlfit.out\
	      TOP-combined_lumisc_unc2p7.out TOP-combined_lumisc_unc2p7_noasimov.out TOP-combined_lumisc_unc2p7_mlfit.out\
	      TOP-combined_lumisc_unc3p7.out TOP-combined_lumisc_unc3p7_noasimov.out TOP-combined_lumisc_unc3p7_mlfit.out

TOP-combined_lumisc_unc2p3.out: TOP-combined_lumisc_unc2p3.txt
	@echo "Processing TOP Combinedlepton channel. New lumi and unc"
	${COMBASYMPT} $^ > TOP-combined_lumisc_unc2p3.out
TOP-combined_lumisc_unc2p3_noasimov.out: TOP-combined_lumisc_unc2p3.txt
	@echo "Processing TOP Combinedlepton channel. New lumi and unc"
	${COMBASYMPTNOASIMOV} $^ > TOP-combined_lumisc_unc2p3_noasimov.out
TOP-combined_lumisc_unc2p3_mlfit.out: TOP-combined_lumisc_unc2p3.txt
	@echo "Processing TOP Combinedlepton channel. New lumi and unc"
	${COMBMLSHAPESBG} $^ -n TOP_lumisc_unc2p3_bg > TOP-combined_lumisc_unc2p3_mlfit_bg.out
	${DIFFTOOL} -a mlfitTOP_lumisc_unc2p3_bg.root -g plots_mlfitTOP_lumisc_unc2p3_bg.root
	${COMBMLSHAPESSG} $^ -n TOP_lumisc_unc2p3_sg > TOP-combined_lumisc_unc2p3_mlfit_sg.out
	${DIFFTOOL} -a mlfitTOP_lumisc_unc2p3_sg.root -g plots_mlfitTOP_lumisc_unc2p3_sg.root

TOP-combined_lumisc_unc2p7.out: TOP-combined_lumisc_unc2p7.txt
	@echo "Processing TOP Combinedlepton channel. New lumi and unc"
	${COMBASYMPT} $^ > TOP-combined_lumisc_unc2p7.out
TOP-combined_lumisc_unc2p7_noasimov.out: TOP-combined_lumisc_unc2p7.txt
	@echo "Processing TOP Combinedlepton channel. New lumi and unc"
	${COMBASYMPTNOASIMOV} $^ > TOP-combined_lumisc_unc2p7_noasimov.out
TOP-combined_lumisc_unc2p7_mlfit.out: TOP-combined_lumisc_unc2p7.txt
	@echo "Processing TOP Combinedlepton channel. New lumi and unc"
	${COMBMLSHAPESBG} $^ -n TOP_lumisc_unc2p7_bg > TOP-combined_lumisc_unc2p7_mlfit_bg.out
	${DIFFTOOL} -a mlfitTOP_lumisc_unc2p7_bg.root -g plots_mlfitTOP_lumisc_unc2p7_bg.root
	${COMBMLSHAPESSG} $^ -n TOP_lumisc_unc2p7_sg > TOP-combined_lumisc_unc2p7_mlfit_sg.out
	${DIFFTOOL} -a mlfitTOP_lumisc_unc2p7_sg.root -g plots_mlfitTOP_lumisc_unc2p7_sg.root

TOP-combined_lumisc_unc3p7.out: TOP-combined_lumisc_unc3p7.txt
	@echo "Processing TOP Combinedlepton channel. New lumi and unc"
	${COMBASYMPT} $^ > TOP-combined_lumisc_unc3p7.out
TOP-combined_lumisc_unc3p7_noasimov.out: TOP-combined_lumisc_unc3p7.txt
	@echo "Processing TOP Combinedlepton channel. New lumi and unc"
	${COMBASYMPTNOASIMOV} $^ > TOP-combined_lumisc_unc3p7_noasimov.out
TOP-combined_lumisc_unc3p7_mlfit.out: TOP-combined_lumisc_unc3p7.txt
	@echo "Processing TOP Combinedlepton channel. New lumi and unc"
	${COMBMLSHAPESBG} $^ -n TOP_lumisc_unc3p7_bg > TOP-combined_lumisc_unc3p7_mlfit_bg.out
	${DIFFTOOL} -a mlfitTOP_lumisc_unc3p7_bg.root -g plots_mlfitTOP_lumisc_unc3p7_bg.root
	${COMBMLSHAPESSG} $^ -n TOP_lumisc_unc3p7_sg > TOP-combined_lumisc_unc3p7_mlfit.out
	${DIFFTOOL} -a mlfitTOP_lumisc_unc3p7_sg.root -g plots_mlfitTOP_lumisc_unc3p7_sg.root






.PHONY: TOP-SUS-combined
TOP-SUS-combined: TOP-SUS-combined_lumisc_unc2p3.out TOP-SUS-combined_lumisc_unc2p3_noasimov.out TOP-SUS-combined_lumisc_unc2p3_mlfit.out\
		  TOP-SUS-combined_lumisc_unc2p7.out TOP-SUS-combined_lumisc_unc2p7_noasimov.out TOP-SUS-combined_lumisc_unc2p7_mlfit.out\
		  TOP-SUS-combined_lumisc_unc3p7.out TOP-SUS-combined_lumisc_unc3p7_noasimov.out TOP-SUS-combined_lumisc_unc3p7_mlfit.out

TOP-SUS-combined_lumisc_unc2p3.out: TOP-SUS-combined_lumisc_unc2p3.txt.btagUncor
	@echo "Processing TOP SUS Combined lepton channel. New lumi and unc"
	${COMBASYMPT} $^ > TOP-SUS-combined_lumisc_unc2p3.out
TOP-SUS-combined_lumisc_unc2p3_noasimov.out: TOP-SUS-combined_lumisc_unc2p3.txt.btagUncor
	@echo "Processing TOP SUS Combined lepton channel. New lumi and unc"
	${COMBASYMPTNOASIMOV} $^ > TOP-SUS-combined_lumisc_unc2p3_noasimov.out
TOP-SUS-combined_lumisc_unc2p3_mlfit.out: TOP-SUS-combined_lumisc_unc2p3.txt.btagUncor
	@echo "Processing TOP SUS Combined lepton channel. New lumi and unc" > $@
	#${COMBMLSHAPESBG} $^ -n TOP-SUS_lumisc_unc2p3_bg > TOP-SUS-combined_lumisc_unc2p3_mlfit_bg.out
	#${DIFFTOOL} -a mlfitTOP-SUS_lumisc_unc2p3_bg.root -g plots_mlfitTOP-SUS_lumisc_unc2p3_bg.root
	#${COMBMLSHAPESSG} $^ -n TOP-SUS_lumisc_unc2p3_sg > TOP-SUS-combined_lumisc_unc2p3_mlfit_sg.out
	#${DIFFTOOL} -a mlfitTOP-SUS_lumisc_unc2p3_sg.root -g plots_mlfitTOP-SUS_lumisc_unc2p3_sg.root

TOP-SUS-combined_lumisc_unc2p7.out: TOP-SUS-combined_lumisc_unc2p7.txt.btagUncor
	@echo "Processing TOP SUS Combined lepton channel. New lumi and unc"
	${COMBASYMPT} $^ > TOP-SUS-combined_lumisc_unc2p7.out
TOP-SUS-combined_lumisc_unc2p7_noasimov.out: TOP-SUS-combined_lumisc_unc2p7.txt.btagUncor
	@echo "Processing TOP SUS Combined lepton channel. New lumi and unc"
	${COMBASYMPTNOASIMOV} $^ > TOP-SUS-combined_lumisc_unc2p7_noasimov.out
TOP-SUS-combined_lumisc_unc2p7_mlfit.out: TOP-SUS-combined_lumisc_unc2p7.txt.btagUncor
	@echo "Processing TOP SUS Combined lepton channel. New lumi and unc" > $@
	#${COMBMLSHAPESBG} $^ -n TOP-SUS_lumisc_unc2p7_bg > TOP-SUS-combined_lumisc_unc2p7_mlfit_bg.out
	#${DIFFTOOL} -a mlfitTOP-SUS_lumisc_unc2p7_bg.root -g plots_mlfitTOP-SUS_lumisc_unc2p7_bg.root
	#${COMBMLSHAPESSG} $^ -n TOP-SUS_lumisc_unc2p7_sg > TOP-SUS-combined_lumisc_unc2p7_mlfit_sg.out
	#${DIFFTOOL} -a mlfitTOP-SUS_lumisc_unc2p7_sg.root -g plots_mlfitTOP-SUS_lumisc_unc2p7_sg.root

TOP-SUS-combined_lumisc_unc3p7.out: TOP-SUS-combined_lumisc_unc3p7.txt.btagUncor
	@echo "Processing TOP SUS Combined lepton channel. New lumi and unc"
	${COMBASYMPT} $^ > TOP-SUS-combined_lumisc_unc3p7.out
TOP-SUS-combined_lumisc_unc3p7_noasimov.out: TOP-SUS-combined_lumisc_unc3p7.txt.btagUncor
	@echo "Processing TOP SUS Combined lepton channel. New lumi and unc"
	${COMBASYMPTNOASIMOV} $^ > TOP-SUS-combined_lumisc_unc3p7_noasimov.out
TOP-SUS-combined_lumisc_unc3p7_mlfit.out: TOP-SUS-combined_lumisc_unc3p7.txt.btagUncor
	@echo "Processing TOP SUS Combined lepton channel. New lumi and unc" > $@
	#${COMBMLSHAPESBG} $^ -n TOP-SUS_bg > TOP-SUS-combined_lumisc_unc3p7_mlfit_bg.out
	#${DIFFTOOL} -a mlfitTOP-SUS_lumisc_unc3p7_bg.root -g plots_mlfitTOP-SUS_bg.root
	#${COMBMLSHAPESSG} $^ -n TOP-SUS_lumisc_unc3p7_sg > TOP-SUS-combined_lumisc_unc3p7_mlfit.out
	#${DIFFTOOL} -a mlfitTOP-SUS_sg.root -g plots_mlfitTOP-SUS_lumisc_unc3p7_sg.root
