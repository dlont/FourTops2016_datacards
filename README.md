# Repository with datacards for 2016 tttt analysis

## Setup instructions

### Required 

- Higgs combine (81X version)
https://cms-hcomb.gitbooks.io/combine/content/


### Benchmark results
- Asymptotic limits from MVA spectrum
`combine -M Asymptotic rare_tthz_ttwxy_merge_50bins/datacard_elmu.txt`
 -- AsymptoticLimits ( CLs ) --
Observed Limit: r < 18.8021
Expected  2.5%: r < 3.6940
Expected 16.0%: r < 5.0433
Expected 50.0%: r < 7.2188
Expected 84.0%: r < 10.4702
Expected 97.5%: r < 14.6410


- Asymptotic limits from HT spectrum. No mc stat nuisances
`combine -M Asymptotic rare_tthz_ttwxy_merge_50bins/HT/datacard_elmu.txt`

 -- AsymptoticLimits ( CLs ) --
Observed Limit: r < 20.6981
Expected  2.5%: r < 5.1401
Expected 16.0%: r < 6.9886
Expected 50.0%: r < 9.9688
Expected 84.0%: r < 14.4589
Expected 97.5%: r < 20.2186


