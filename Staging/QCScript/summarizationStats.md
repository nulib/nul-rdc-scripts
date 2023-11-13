## Standards from QC Tools that have been altered for this script

|Criteria|Original Value|
|:---:|:---:|
|TOUTc|<10 frames|
|SATb|<1000 frames|
|SATi|<1000 frames|
|BRNGc|<1000 frames|
|MSEfY|<10 frames|


## Knowns (rounded frames per second)

30 frames/sec <br>
3,600 sec/hr <br>
108,000 frames/hr

### Calculations for TOUTc and MSEfY
Equation: 10/((3600*timeHRs) \* 30) (This makes no sense as the values are E<sup>-5</sup>)

### Calculations for SATb, SATi, BRNGc
Equation:  1000/((3600*timeHRs) \* 30)

#### If we can assume that the 1000 benchmark value came from a video in the range of 1-2 hrs

|Time|Percent Error Allowed Exact| Percent Error Allowed Rounded|
|:---:|:---:|:---:|
1 hr|0.92592593%|0.93%
1.25 hr|0.74074074%|0.74%
1.5 hr|0.61728395%|0.62%
1.75 hr| 0.52910053%|0.53%
2 hr|0.4629629%|0.46%
||
AVG| 0.65520282%|0.66%

Theoretically 0.66% of the videos frames are allowed to be greater