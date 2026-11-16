# Manual review of the extras exception rows (Stage 4 Step 1)

Method: each exception row was printed with the three deliveries before and after it, its over was checked for six legal rows, and the innings total was checked against the raw runs + extras1 + extras2. Scope and eligibility come from `outputs/step1/deliveries_analysis.csv.gz`.

## Match 17555 (T20I, England in Pakistan 2022; pressure-eligible)
```
position  match_id  innings  over  ball       striker          bowler  runs extras_type  extras1  extras2  wicket
      -3     17555        1     5     1   Dawid Malan      Haris Rauf     0         NaN        0        0   False
      -2     17555        1     5     2   Dawid Malan      Haris Rauf     0         NaN        0        0   False
      -1     17555        1     5     3   Dawid Malan      Haris Rauf     0         NaN        0        0   False
THIS ROW     17555        1     5     4   Dawid Malan      Haris Rauf     0         NaN        0        1   False
      +1     17555        1     5     5 William Jacks      Haris Rauf     4         NaN        0        0   False
      +2     17555        1     5     6 William Jacks      Haris Rauf     4         NaN        0        0   False
      +3     17555        1     6     1   Dawid Malan Shahnawaz Dhani     0         NaN        0        0   False
```
One extra run in `extras_2_runs`, `extras_type` blank, bat runs 0, on over 5 ball 4. The over has exactly 6 rows with ball numbers 1-6 and no illegal label, so this is a legal delivery. Extras2 is otherwise used only on no-ball-like deliveries; on a legal ball it can only be a bye or leg-bye with the label missing. **Decision:** keep as a legal delivery, ball faced, bat runs 0, run not charged to the bowler (`untyped_extra`). A bye or a leg-bye would be treated identically, so the decision does not depend on which it was.

## Match 36097 (T20I, South Africa in West Indies 2024; pressure-eligible)
```
position  match_id  innings  over  ball               striker           bowler  runs extras_type  extras1  extras2  wicket
      -3     36097        2     8     3 Rassie van der Dussen Romario Shepherd     1         NaN        0        0   False
      -2     36097        2     8     4        Tristan Stubbs Romario Shepherd     1         NaN        0        0   False
      -1     36097        2     8     5 Rassie van der Dussen Romario Shepherd     0         NaN        0        0   False
THIS ROW     36097        2     8     6 Rassie van der Dussen Romario Shepherd     0         NaN        1        0   False
      +1     36097        2     9     1 Rassie van der Dussen   Gudakesh Motie     1         NaN        0        0   False
      +2     36097        2     9     2        Tristan Stubbs   Gudakesh Motie     1         NaN        0        0   False
      +3     36097        2     9     3 Rassie van der Dussen   Gudakesh Motie     0         NaN        0        0   False
```
One extra run in `extras1_runs`, `extras_type` blank, bat runs 0, over 8 ball 6; six legal rows in the over. A wide or no-ball would carry a label and break the over structure, so it is again an unlabelled bye or leg-bye. **Decision:** same as above.

## Match 37099 (Emerging Teams Asia Cup 2024; out of scope, no eligible rows)
```
position  match_id  innings  over  ball          striker             bowler  runs extras_type  extras1  extras2  wicket
      -3     37099        1    13     4  Nimesh Vimukthi Sharafuddin Ashraf     1         NaN        0        0   False
      -2     37099        1    13     5 Sahan Arachchige Sharafuddin Ashraf     1         NaN        0        0   False
      -1     37099        1    13     6  Nimesh Vimukthi Sharafuddin Ashraf     0     legbyes        1        0   False
THIS ROW     37099        1    14     1  Nimesh Vimukthi         Qais Ahmad     1     legbyes        0        0   False
      +1     37099        1    14     2 Sahan Arachchige         Qais Ahmad     2         NaN        0        0   False
      +2     37099        1    14     3 Sahan Arachchige         Qais Ahmad     1         NaN        0        0   False
      +3     37099        1    14     4  Nimesh Vimukthi         Qais Ahmad     2         NaN        0        0   False
```
Labelled `legbyes` but `runs`=1 and `extras1`=0 (a leg-bye normally has runs 0 and extras1 >= 1). The leg-bye one ball earlier (13.6) has runs 0 and extras1=1, so this row looks like an ordinary single carrying the wrong label. **Decision:** treat as an ordinary delivery (bat run credited, bowler charged one run). Impact: none, the match is out of scope.

## Other extras checks
- **Penalty row** (match 16753, innings 2, over 6 ball 4): `runs`=0, `extras1`=5, the over has six rows and is complete, so the row occupies a legal ball position; 5 penalty runs are charged to nobody. The match is a revised match (first innings reduced to 66 balls) and is not pressure-eligible, so it has no effect on ratings.
- **`extras_2_runs` on no-ball-like deliveries:** 35 rows (21 Overstep, 14 other), values 1 or 4, bat runs 0 in every row. This supports, but does not prove, that they are byes/leg-byes off the no-ball (assumption A11). One further legal-ball row also has extras2=1 (match 17555 above).
- **Free hits:** 918 deliveries follow a no-ball-like delivery (a wide in between does not use the free hit up). Wicket rate 0.44% (4 run-outs) against 5.44% elsewhere; boundary rate 33.6% against 17.9%. This is the same for `other` as for `Overstep`, which supports treating `other` as no-ball-like (A1).
