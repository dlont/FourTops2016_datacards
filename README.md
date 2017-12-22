# Repository with datacards for 2016 tttt analysis

## Setup instructions

### Required 

- Higgs combine (81X version)
https://cms-hcomb.gitbooks.io/combine/content/


### Benchmark results

- Asymptotic limits from MVA spectrum

`combine -M Asymptotic rare_tthz_ttwxy_merge_50bins/datacard_elmu.txt`
```
-- AsymptoticLimits ( CLs ) --
Observed Limit: r < 18.8021
Expected  2.5%: r < 3.6940
Expected 16.0%: r < 5.0433
Expected 50.0%: r < 7.2188
Expected 84.0%: r < 10.4702
Expected 97.5%: r < 14.6410
```
- Signal strength

`combine -M FitDiagnostics --X-rtd MINIMIZER_analytic rare_tthz_ttwxy_merge_50bins/datacard_elmu.txt`

```
 --- FitDiagnostics ---
Best fit r: 11.9166  -11.9166/+3.68826  (68% CL)
```

- Asymptotic limits from HT spectrum. No mc stat nuisances

`combine -M Asymptotic rare_tthz_ttwxy_merge_50bins/HT/datacard_elmu.txt`

```
 -- AsymptoticLimits ( CLs ) --
Observed Limit: r < 20.6981
Expected  2.5%: r < 5.1401
Expected 16.0%: r < 6.9886
Expected 50.0%: r < 9.9688
Expected 84.0%: r < 14.4589
Expected 97.5%: r < 20.2186
```

## Post-fit plots (step 1)
`combine -M FitDiagnostics --X-rtd MINIMIZER_analytic rare_tthz_ttwxy_merge_50bins/datacard_elmu.txt --X-rtd MINIMIZER_analytic --saveShapes --saveWithUncertainties --saveNormalizations -n _nominal`
### Muon channel (step 2.a)
`python mountainrange/mountainrange_pub_raresplit.py fitDiagnostics_nominal.root -j mountainrange/mountainrange_configs_tthz_ttwxy/mountain_mu_tttt4btag_prefit.json -b -e pdf -r`
### Electron channel (step 2.b)
`python mountainrange/mountainrange_pub_raresplit.py fitDiagnostics_nominal.root -j mountainrange/mountainrange_configs_tthz_ttwxy/mountain_el_tttt4btag_prefit.json -b -e pdf -r`
