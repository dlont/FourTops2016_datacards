# Repository with datacards for 2016 tttt analysis

## Setup instructions

### Required 

- Higgs combine (81X version)
https://cms-hcomb.gitbooks.io/combine/content/


### Benchmark results

- Asymptotic limits from MVA spectrum

Convert .txt datacard to RooStat workspace in .root file
`text2workspace.py --channel-masks combined_elmu.txt`

Actual limit setting
`combine -M Asymptotic combined_elmu.root --run blind`

```
 -- AsymptoticLimits ( CLs ) --
Expected  2.5%: r < 7.1919
Expected 16.0%: r < 9.4119
Expected 50.0%: r < 12.8750
Expected 84.0%: r < 17.7504
Expected 97.5%: r < 23.5186

```
- Signal strength in control regions
Blind the most sensitive control regions mu10J4M and el10J4M
`combine -M FitDiagnostics --X-rtd MINIMIZER_analytic combined_elmu.root --setParameters mask_MU_mu10J4M=1,mask_EL_el10J4M=1`

```
 --- FitDiagnostics ---
Best fit r: 6.24278e-12  -6.24278e-12/+3.12414  (68% CL)
```

- Blind signal significance
`combine -M Significance --X-rtd MINIMIZER_analytic combined_elmu.root -t -1 --expectSignal=1`
```
 -- Significance -- 
Significance: 0.138035
```


## Post-fit plots (step 1)
`combine -M FitDiagnostics --X-rtd MINIMIZER_analytic rare_tthz_ttwxy_merge_50bins/datacard_elmu.txt --X-rtd MINIMIZER_analytic --saveShapes --saveWithUncertainties --saveNormalizations -n _nominal`
### Muon channel (step 2.a)
`python mountainrange/mountainrange_pub_raresplit.py fitDiagnostics_nominal.root -j mountainrange/mountainrange_configs_tthz_ttwxy/mountain_mu_tttt4btag_prefit.json -b -e pdf -r`
### Electron channel (step 2.b)
`python mountainrange/mountainrange_pub_raresplit.py fitDiagnostics_nominal.root -j mountainrange/mountainrange_configs_tthz_ttwxy/mountain_el_tttt4btag_prefit.json -b -e pdf -r`

## Post-fit normalizations
`python postfitnorm/postfitnorm.py fitDiagnostics_nominal.root`

## Correlation matrices
`python corrmatrix/plot_corr_matrix.py fitDiagnostics_nominal.root -b -e pdf`

## Nuisance pulls
```
python nuispulls/diffNuisances_denys.py fitDiagnostics_nominal.root -A -a -g out.root
python nuispulls/plot_nuis_pulls.py -b -e pdf out.root
```

# Using theta

```
theta/utils2/theta-auto.py conf.py 
```
