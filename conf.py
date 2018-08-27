model = higgs_datacard.build_model("rare_tthz_ttwxy_merge_50bins/datacard_elmu_noscale.txt")
#model = higgs_datacard.build_model("rare_tthz_ttwxy_merge_50bins/datacard_elmu.txt")
model_summary(model)

options = Options()
options.set('minimizer', 'strategy', 'robust')
options.set('minimizer', 'minuit_tolerance_factor', '1000') 

result = mle(model, input = 'data', n = 1)
print "result: ", result
report.write_html('htmlout')

