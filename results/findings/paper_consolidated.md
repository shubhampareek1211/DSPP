# Cash Transfers, Banking Infrastructure, and Women's Financial Empowerment in India

**Working Paper**

---

## Abstract

We study how women-directed direct benefit transfer (DBT) programs interact with banking infrastructure to shape women's financial inclusion and household empowerment in India. Using seven complementary analyses spanning national, state, and district levels, we find that cross-state variation in Pradhan Mantri Matru Vandana Yojana (PMMVY) enrollment intensity does not significantly predict differential improvements in women's bank-account use or own-money autonomy at the national level between NFHS-4 (2015–16) and NFHS-5 (2019–21): the estimates are positive but statistically insignificant (+2.1pp bank account, p = 0.18; +1.2pp autonomy, p = 0.31). At the district level in Uttar Pradesh, the association between PMMVY intensity and women's participation in health-care decisions is stronger where pre-existing banking infrastructure is denser (+0.062 per SD of branch density, p = 0.009); the average own-money-autonomy association is negative (−3.9pp, p = 0.041). Replications across Himachal Pradesh, Assam, Madhya Pradesh, and West Bengal produce positive and significant banking interactions for own-money autonomy in Assam (+0.051, p = 0.007) and Madhya Pradesh (+0.030, p = 0.002), an imprecise positive estimate in West Bengal, and a negative estimate in underpowered Himachal Pradesh. Across 544 Indian districts, pre-2013 branch density is associated with lower child marriage (−1.3pp per SD, p = 0.049), lower teen pregnancy (−0.7pp per SD, p = 0.036), and higher female schooling completion (+1.7pp per SD, p < 0.001) in 2019–21. The 2013 baseline stock predicts these outcomes while 2013–2020 banking growth does not. Taken together, selected results are consistent with complementarity, but the mixed findings, observational designs, and non-random program intensity limit causal interpretation.

---

## 1. Introduction

India has committed significant public resources to two interrelated policy agendas over the past decade: expanding women-directed direct benefit transfers and deepening rural financial infrastructure. The Pradhan Mantri Matru Vandana Yojana, launched in 2017, provides Rs. 5,000 in conditional cash transfers to first-live-birth mothers, reaching over 36 million women by 2024. The Jan Dhan Yojana, launched in 2014, opened over 500 million basic bank accounts, of which a large share belong to women who were previously unbanked. Parallel investments in business correspondents, micro-ATM networks, and digital payment infrastructure brought formal financial services to districts and villages that had been effectively excluded from the formal economy.

The central question this paper addresses is whether these two policy streams — cash transfers to women and financial infrastructure expansion — are complements that reinforce each other, or whether each operates independently of the other. The answer has substantial implications for policy prioritisation. If cash transfers work equally well regardless of local financial infrastructure, then rolling out programs in low-banking districts is as effective as in banking-dense ones. If, instead, the effects of cash transfers are conditional on financial infrastructure — as a growing body of experimental evidence from sub-Saharan Africa and South Asia suggests — then sequencing matters: expanding banking infrastructure before or alongside cash transfer programs may substantially amplify their empowerment effects.

We address this question using seven empirical analyses that collectively span the national, state, and district levels, two decades of financial data, and outcomes ranging from bank account ownership and mobile finance use to child marriage rates and secondary school completion. The seven studies are:

1. **All-India PMMVY DiD:** A treatment-intensity difference-in-differences using state-level PMMVY enrollment variation and NFHS-4/5 individual data (34 states, 230,264 women for the main outcomes).
2. **Uttar Pradesh District DiD:** A district-level DiD with a banking interaction (73 matched districts, 29,226 women; 19,834 for decision outcomes).
3. **Multi-State District DiD Replication:** The same district-level framework applied to four additional states — Himachal Pradesh, Assam, Madhya Pradesh, and West Bengal — using district PMMVY enrollment data (98 matched district units and 31,961 women for the main outcomes).
4. **National Cross-Section:** Cross-sectional OLS with state fixed effects, testing banking infrastructure associations with women's outcomes across 544 Indian districts.
5. **Banking Stock vs. Expansion:** A district-level decomposition testing whether the 2013 banking stock or the 2013–2020 expansion predicts 2019–21 outcomes.
6. **State Panel:** A three-round (NFHS-3/4/5) state panel linking banking depth to women's financial access over time.
7. **UPI Event Study:** A state × month panel testing whether women-directed state DBT program launches accelerated digital payment adoption.

The seven analyses produce a qualified but broadly consistent pattern. Average national PMMVY intensity estimates are positive but statistically inconclusive, while several district-level models show stronger PMMVY associations where banking infrastructure is denser. The banking-empowerment gradient is large and nationally present as an association, with the historical banking stock predicting outcomes more consistently than recent expansion. Aggregate state-level UPI activity does not show a robust response to program launches and is too coarse to measure behavioral changes among women beneficiaries directly.

These findings speak to several strands of literature. On cash transfers, they complement research on behavioral and empowerment outcomes of unconditional and conditional transfers in low- and middle-income countries (Baird et al., 2011; Haushofer and Shapiro, 2016; Banerjee et al., 2021). On women's financial inclusion, they examine a setting in which DBT disbursement requirements make account access especially relevant. On banking infrastructure, they extend the descriptive record following Burgess and Pande (2005): pre-existing banking stock remains associated with women's outcomes in 2019–21, and several district specifications show heterogeneous PMMVY associations by local banking depth.

Section 2 describes the data and institutional context. Sections 3–9 present each study in turn. Section 10 discusses the findings jointly and draws policy implications. Section 11 concludes.

---

## 2. Background, Data, and Institutional Context

### 2.1 The PMMVY Program

The Pradhan Mantri Matru Vandana Yojana (PMMVY) was launched on January 1, 2017 under the Ministry of Women and Child Development. It provides Rs. 5,000 in three installments to women pregnant with their first live child, conditional on antenatal care visits and institutional delivery. Payments are made directly to beneficiaries' bank accounts via the DBT framework. The program targets women from economically disadvantaged households and is implemented through the ICDS network of anganwadi centres.

By November 2024, 36.6 million women had been enrolled nationally. Enrollment intensity varies substantially across states, from zero in Odisha and Telangana (which opted out in favour of state-run schemes) to ~121 per 1,000 in Madhya Pradesh, reflecting differences in state policy choices, administrative capacity, and program awareness. This variation — in both participation status and enrollment intensity — is the source of identification in the national DiD analysis.

### 2.2 Banking Infrastructure in India

India's formal banking network has undergone two distinct phases of expansion relevant to this paper. The first, documented by Burgess and Pande (2005), ran from the early 1970s to the early 1990s under the Social Control banking policy, which mandated branch openings in underbanked areas in exchange for permission to open urban branches. This expansion substantially increased rural banking access and, Burgess and Pande show, reduced rural poverty.

The second phase began after 2014 with the Jan Dhan Yojana, followed by the Pradhan Mantri Jan Suraksha Yojana (2015) and the broader DBT infrastructure expansion. Between 2013 and 2019–20, branch density increased in 96% of Indian districts, with a mean increase of 33%. However, this expansion was broadly uniform — the distribution of growth rates is narrow (SD = 0.15 on the log scale) — and, as we show, adds no predictive power for women's outcomes beyond the 2013 baseline.

The 2013 RBI district census — the source of the banking moderator in both the UP DiD and the national cross-section — thus captures a pre-existing stock of infrastructure that reflects cumulative investment decisions made over decades, including the Burgess-Pande era expansion. This pre-existing stock is plausibly predetermined relative to the outcomes studied here.

### 2.3 Data Sources

**National Family Health Survey (NFHS).** The NFHS is India's primary source of data on women's health, nutrition, and social outcomes. We use three rounds:
- *NFHS-3* (2005–06): state-level factsheets for 35 states. Used in the state panel only.
- *NFHS-4* (2015–16): individual-level data for 699,686 women across 37 states plus the Uttar Pradesh state module (15,387 women); district-level factsheets.
- *NFHS-5* (2019–21): individual-level data for 724,115 women; district-level factsheets covering 699 districts.

Key outcome variables include: bank account ownership and self-use (all rounds from NFHS-4), mobile phone ownership and self-use, own money autonomy (whether a woman has personal money she controls), participation in household decisions (health care, large purchases), delivery financial assistance (used as a PMMVY receipt proxy), women's literacy, child marriage rates, teen pregnancy rates, and secondary school completion rates.

**Reserve Bank of India (RBI) Banking Data.**
- *December 2013 district census:* Reporting offices (bank branches) and deposits by district, used as the banking baseline in the UP DiD, national cross-section, and banking stock analysis.
- *Statement 4a quarterly data (2017–18 Q1 to 2022–23 Q3):* Parsed to extract Q4 2019–20 district snapshots, used in the banking expansion analysis.
- *Basic Statistical Returns (BSR-2) annual:* State-level deposits 2009–17, used in the state panel.

**PMMVY beneficiary data.** State-wise cumulative beneficiary counts from the MoWCD portal (as of November 2024) and UP district-level PMMVY beneficiaries for 2017–19 and 2019–20.

**NPCI UPI monthly data.** State × month UPI transaction volume and value, April 2023 – December 2025 (32 months, October 2024 absent), used in the UPI event study.

**Census 2011.** District-level population data used as denominators for per-capita measures.

---

## 3. Study 1: All-India PMMVY DiD

### 3.1 Design

We exploit two sources of cross-state variation in PMMVY exposure between NFHS-4 (2015–16, pre-PMMVY) and NFHS-5 (2019–21, post-PMMVY): (i) whether a state participated in PMMVY at all, and (ii) the intensity of enrollment among participating states.

**Participation variation.** Although PMMVY is a central government scheme available to all states, states vary on a spectrum from full implementation to deliberate non-participation. Three states stand in distinct positions:

*Full non-participants:* **Odisha** (MAMATA scheme; six recorded PMMVY beneficiaries, coded zero) and **Telangana** (own state maternity scheme; zero beneficiaries) are coded as zero-intensity non-participants in the main specification. Telangana was carved from Andhra Pradesh in 2014, after the 2011 Census, so its female-population denominator is estimated as 41.4% of undivided Andhra Pradesh's female population. A legacy robustness specification assigns the same share of Andhra Pradesh's reported enrollment to Telangana; it is retained only for comparison and is not the preferred coding.

*Low-absorption participant:* **Tamil Nadu** officially enrolled in PMMVY (1.56 million cumulative beneficiaries, 43 per 1,000 women) but has a competing state scheme — the Dr. Muthulakshmi Reddy Maternity Benefit Scheme — that provides Rs. 18,000 per birth across the first two children, nearly four times PMMVY's Rs. 5,000. The NFHS data confirms state scheme dominance: Tamil Nadu women's delivery financial assistance rate was already 55.4% in NFHS-4 (2015–16), before PMMVY launched in January 2017, compared to a national average below 30%. Tamil Nadu's low PMMVY uptake reflects rational crowding out by a superior existing alternative, not administrative failure. In the main specification Tamil Nadu is included at its actual low intensity; a robustness specification treating Tamil Nadu as a non-participant does not materially change results.

These states provide useful comparison variation, but they are not randomized controls and their alternative maternity schemes and implementation environments differ. The coefficient therefore captures a conditional association with PMMVY intensity relative to lower- or zero-intensity states; it should not be read as the effect of cash relative to no program.

**Intensity variation.** Among states enrolled in PMMVY, enrollment intensity varies substantially — from 36.8 beneficiaries per 1,000 women in West Bengal to 120.8 in Madhya Pradesh — reflecting differences in administrative capacity, anganwadi network density, awareness campaigns, and state-level implementation effort. This within-participation variation identifies whether states that enrolled a larger share of eligible women saw disproportionately larger improvements in outcomes, after absorbing common trends through state and round fixed effects.

The estimating equation combines both sources of variation. The primary specification uses continuous intensity (including zero for Odisha and Telangana), with a binary participation indicator as a robustness check:

> Y_i = α + β × (intensity\_s × post\_i) + state\_FE + round\_FE + age\_i + age²\_i + education\_i + rural\_i + wealth\_i + ε\_i

where *intensity\_s* is PMMVY cumulative beneficiaries per 1,000 women (Census 2011 female population), standardised across all 34 states including the two non-participants at zero. Standard errors are clustered at the state level. The coefficient β measures the additional improvement in outcome Y associated with a one-standard-deviation higher PMMVY enrollment intensity.

The key identifying assumption is that, absent variation in PMMVY intensity, the NFHS-4→NFHS-5 change in outcomes would be uncorrelated with which states enrolled more women. Odisha and Telangana provide zero-intensity observations, but only one pre-program survey round is available, so parallel trends cannot be directly tested. The coefficient is therefore best interpreted as a conditional dose-response association rather than a definitive causal effect.

### 3.2 PMMVY Intensity Distribution

Among participating states, PMMVY intensity ranges from 36.8 to 120.8 beneficiaries per 1,000 women. Madhya Pradesh is the highest-intensity state (120.8), followed by Himachal Pradesh (90.7) and Karnataka (86.8). West Bengal (36.8), Nagaland (41.0), and Meghalaya (41.5) are the lowest-intensity full participants. Tamil Nadu sits below most full participants at about 43 per 1,000. Including Odisha and Telangana at zero extends the observed treatment range. The variation plotted in Figure 3.1 supplies the empirical contrast, but non-random program intensity remains a central limitation.

**Table 3.1: NFHS-4→NFHS-5 change by PMMVY intensity tercile**

| Tercile | N states | Avg. intensity | ΔBank account | ΔAutonomy | ΔDecision |
|---|---|---|---|---|---|
| Low | 12 | 38.0 per 1,000 | +21.7 pp | +6.5 pp | +3.9 pp |
| Mid | 11 | 63.6 | +26.7 pp | +10.4 pp | +6.2 pp |
| High | 12 | 83.8 | +28.8 pp | +11.9 pp | +7.1 pp |

High-intensity states improved 7.1 pp more on bank account ownership and 5.4 pp more on own money autonomy than low-intensity states in the raw NFHS-4→NFHS-5 comparison.

### 3.3 Main Results

**Table 3.2: PMMVY intensity DiD — individual-level estimates (N = 230,264)**

| Outcome | Coeff (intensity × post) | SE | p-value |
|---|---|---|---|
| Bank account ownership | +0.021 | 0.016 | 0.180 |
| Mobile phone self-use | −0.003 | 0.005 | 0.534 |
| Own money autonomy | +0.012 | 0.011 | 0.312 |
| Health-care decision has say | +0.004 | 0.006 | 0.492 |

A one-standard-deviation increase in PMMVY enrollment intensity is associated with a 2.1 pp improvement in bank account ownership and a 1.2 pp improvement in own money autonomy, but neither reaches statistical significance. Results are directionally consistent across all four outcomes but precisely estimated as small and insignificant. Excluding the three largest states (UP, Bihar, Maharashtra) yields nearly identical estimates (bank accounts: +0.017, p = 0.296; autonomy: +0.011, p = 0.321), confirming the result is not driven by large-state leverage. Coding Tamil Nadu as a non-participant (given its dominant state scheme) moves the bank account coefficient to +0.023 (p = 0.074), approaching marginal significance.

The absence of a significant average national effect is consistent with the district-level findings in Studies 2 and 3, where PMMVY intensity alone generally fails to predict differential improvement after district fixed effects are included. The positive raw tercile gradient (+21.7pp to +28.8pp in bank-account gains from low- to high-intensity states) motivates heterogeneity tests, but it does not by itself establish that the program caused the difference.

**Bank account ownership** is the most proximate expected outcome because PMMVY requires a bank account for DBT receipt. The coefficient is positive but statistically insignificant, so it does not independently validate the treatment-intensity measure.

**Own money autonomy** — whether a woman has personal money she controls — is substantively important, but the positive +1.2 pp national estimate is imprecise. It is directionally consistent with the UP district-level interaction for decision-making, but neither estimate alone establishes that PMMVY increased bargaining power.

**Mobile phone use** has a small, statistically insignificant estimate (−0.3 pp, p = 0.53). The analysis does not detect a differential mobile-use change by PMMVY intensity.

**Household decision-making** shows a positive but imprecisely estimated coefficient (+0.4pp, p = 0.492). The state-level intensity measure is a noisier signal for an individual-level behavioral outcome than the district-level treatment assignment used in the UP DiD.

---

## 4. Study 2: Uttar Pradesh District DiD with Banking Interaction

### 4.1 Design

The UP analysis studies finer-grained district heterogeneity. Using district-level PMMVY beneficiary data matched to 73 Uttar Pradesh districts and the NFHS state-module subsample (29,226 women; 19,834 for decision outcomes), we estimate a triple interaction between PMMVY intensity, pre-treatment banking infrastructure (branch density per 100,000 population, 2013), and the post-period indicator. The identifying assumption is that absent PMMVY, district-level women's outcomes would have followed parallel trends regardless of local banking density.

The estimating equation for the amplification test is:

> Y_i = district\_FE + post + post×PMMVY + post×banking + post×PMMVY×banking + controls + ε_i

The triple interaction coefficient `post × PMMVY × banking` estimates how the PMMVY-intensity association differs with banking density, conditional on the included fixed effects and controls.

### 4.2 Average Treatment Effect: No Differential Concentration

Without the banking interaction, six of seven outcome estimates are statistically insignificant after absorbing district fixed effects. The exception is own-money autonomy, which has a negative coefficient (−3.9 pp, p = 0.041). This result cautions against describing the UP average association as uniformly positive or simply null.

### 4.3 Banking Interaction Estimates

**Table 4.1: Triple interaction — PMMVY × Banking infrastructure × Post (UP)**

| Component | Health-care decisions | Large purchases |
|---|---|---|
| Post × PMMVY | +0.037\* | +0.036\* |
| Post × banking | +0.042\* | +0.021 |
| **Post × PMMVY × banking** | **+0.062\*\*** | **+0.043†** |

For health-care decisions, moving from mean branch density to one standard deviation above the mean is associated with a 6.2-percentage-point larger PMMVY-intensity coefficient (p = 0.009). Because PMMVY intensity and banking density are not randomly assigned, this interaction is not by itself attributable to their joint causal effect.

The large-purchase interaction (+0.043, p = 0.055) is directionally consistent but does not meet the conventional 5% threshold. The health-care result is the primary interaction estimate.

### 4.4 Mechanism and Robustness Limits

The release pipeline does not identify a mediation channel and does not currently reproduce earlier exploratory specifications using alternative banking moderators or district-specific trends. Branch density may proxy for agents, ATMs, familiarity with banking, local development, or social norms. These possibilities should be tested directly before making a mechanism claim.

---

## 5. Study 3: Multi-State District DiD Replication

### 5.1 Design and Motivation

The UP district DiD (Study 2) established that banking infrastructure amplifies PMMVY's effect on women's household decision-making power. A key question is whether this finding is specific to Uttar Pradesh — a large, diverse, and administratively distinctive state — or whether it generalises across India's heterogeneous social and economic geography. To test external validity, we apply the same district-level repeated cross-section DiD framework to four additional states for which district-level PMMVY enrollment data were obtained: Himachal Pradesh (HP), Assam, Madhya Pradesh (MP), and West Bengal (WB).

Each state-level analysis uses an identical specification to Study 2:

> Y_i = district\_FE + post + post×PMMVY\_std + post×banking\_std + post×PMMVY\_std×banking\_std + controls + ε_i

Controls: age, age², education, urban residence, wealth index. Standard errors clustered at the district level. The PMMVY treatment variable is the cumulative enrollment rate (beneficiaries per 1,000 Census 2011 population), standardised within each state. The banking moderator is RBI December 2013 branch density per 100,000 population, standardised within each state.

**Data coverage:**

| State | PMMVY period | Districts (source) | Matched estimation districts | Women in main outcomes |
|---|---|---|---|---|
| Himachal Pradesh | Up to Aug 2023 | 12 | 10 | 3,756 |
| Assam | Up to Jan 2022 | 33 | 24 | 7,278 |
| Madhya Pradesh | Up to Mar 2023 | 52 | 47 | 15,768 |
| West Bengal | Up to Jan 2022 | 23 | 17 | 5,159 |

**Design note on treatment timing:** The PMMVY data for Assam and West Bengal extend to January 2022, close to the NFHS-5 fieldwork window. HP and MP data extend to 2023, after NFHS-5, so those intensity measures may contain post-outcome enrollment and should be interpreted as proxies rather than clean pre-outcome treatments.

**Note on HP:** With only 10 matched district clusters, conventional cluster-robust inference is unreliable. HP results are reported for completeness but should be treated as descriptive, not inferential.

### 5.2 Main DiD Results

**Table 5.1: Post × PMMVY intensity — average treatment effect by state**

| State | Bank account | Own money autonomy | Healthcare decisions | Mobile phone |
|---|---|---|---|---|
| HP (10 dist, n=3,756) | −0.033 | +0.041 | −0.050 | +0.016 |
| Assam (24 dist, n=7,278) | +0.004 | −0.026 | −0.070 | −0.030 |
| MP (47 dist, n=15,768) | +0.020 | +0.007 | **+0.076\*\*** | +0.009 |
| West Bengal (17 dist, n=5,159) | −0.013 | −0.008 | +0.018 | −0.017 |

Consistent with the UP result (Study 2, Table 2), no state shows a statistically significant average DiD effect on bank account ownership or mobile phone use. Madhya Pradesh is the exception for healthcare decisions (+0.076, p = 0.011), where its nationally high enrollment intensity — the highest among all states at 120.8 beneficiaries per 1,000 women — generates sufficient variation to detect a direct average effect. This is substantively consistent: the state-level national DiD (Study 1) found no average effect on decision-making, but MP's extreme intensity may place it above the threshold where program density alone shifts outcomes.

### 5.3 Banking Amplification — Triple Interaction

**Table 5.2: Post × PMMVY × banking (branch density 2013) — amplification coefficient by state**

| State | Bank account | Own money autonomy | Healthcare decisions | Mobile phone |
|---|---|---|---|---|
| UP *(Study 2)* | +0.001 | +0.018 | **+0.062\*\*** | −0.024† |
| HP ⚠️ | +0.071 | −0.084\*\*\* | +0.097 | −0.007 |
| Assam | +0.025 | **+0.051\*\*\*** | +0.110 | +0.008 |
| MP | +0.010 | **+0.030\*\*\*** | +0.041 | −0.010 |
| West Bengal | +0.051 | +0.046 | +0.028 | +0.041 |

⚠️ HP triple-interaction inference is unreliable with only 10 matched clusters. The negative autonomy coefficient is therefore treated as descriptive and potentially sensitive to individual districts.

**The positive banking interaction for own-money autonomy appears in Assam and MP** at conventional significance levels. Uttar Pradesh does not show that outcome-specific interaction; its clearest result is for health-care decisions. All estimates remain subject to the limitations of observational treatment intensity:

- **Assam** (northeastern India, tea plantation economy, tribal districts): +0.051\*\*\*, p = 0.007
- **Madhya Pradesh** (central India, high PMMVY intensity, tribal belts): +0.030\*\*\*, p = 0.002
- **Uttar Pradesh** *(Study 2)*: +0.018, p = 0.498 for autonomy; +0.062, p = 0.009 for health-care decisions

The magnitude is largest in Assam, where banking infrastructure varies considerably across districts — from dense urban Kamrup Metro to sparsely served tribal districts — creating strong identifying variation for the interaction.

### 5.4 West Bengal Null Result

West Bengal shows no statistically significant average or banking-interaction estimate. Its PMMVY enrollment intensity is lower than Madhya Pradesh's, which may reduce usable treatment variation, but the present analysis cannot determine why the estimate is imprecise. The result should be treated as a non-replication rather than evidence for a threshold effect.

### 5.5 Cross-State Synthesis

**Table 5.3: Banking amplification on own money autonomy — summary across all district-level analyses**

| State | Triple coef (post × PMMVY × banking) | p-value | PMMVY intensity (median, per 1k pop) | Districts |
|---|---|---|---|---|
| Madhya Pradesh | +0.030 | 0.002 | ~9.5 | 47 |
| Assam | +0.051 | 0.007 | ~8.1 | 24 |
| Uttar Pradesh | +0.018 | 0.498 | 6.3 | 73 |
| West Bengal | +0.046 | 0.375 | ~4.2 | 17 |
| Himachal Pradesh ⚠️ | −0.084 | 0.005 | ~8.3 | 10 |

Across the better-powered samples, several interaction estimates are positive, but the outcome differs: Uttar Pradesh's clearest result concerns health-care decision-making, while Assam and Madhya Pradesh show own-money-autonomy interactions. West Bengal does not replicate these estimates, and Himachal Pradesh is underpowered. The pattern motivates a banking-complementarity hypothesis; it does not establish a common mechanism or broad external validity.

---

## 6. Study 4: Banking Infrastructure and Women's Outcomes — National Cross-Section

### 6.1 Design

The national cross-section asks a broader question: is banking infrastructure associated with better women's outcomes not just through PMMVY interactions, but across the full distribution of Indian districts? This provides a check on whether the UP-based mechanism generalises, and extends the analysis to outcomes not available in the UP subsample — child marriage and teen pregnancy.

Using NFHS-5 district factsheets (699 districts) and the 2013 RBI district census, we estimate:

> Y_d = α + β × log(branch\_density\_2013)_d + controls_d + state\_FE + ε_d

Controls include household electricity access, clean cooking fuel use, and female school attendance (all from NFHS-5). State fixed effects absorb all between-state variation, leaving only within-state comparisons. The 2013 banking measure predates the 2019–21 outcomes, improving temporal ordering but not eliminating omitted-variable bias. Sample: 544 districts matched across both datasets.

### 6.2 The National Banking–Outcomes Gradient

**Table 6.1: Raw gradient by banking tercile**

| Outcome | Low tercile | High tercile | High − Low |
|---|---|---|---|
| Child marriage (%) | 27.9 | 12.2 | **−15.7 pp** |
| Teen pregnancy (%) | 8.3 | 4.0 | **−4.3 pp** |
| Literacy (%) | 67.8 | 83.5 | **+15.8 pp** |
| Women with 10+ yrs schooling (%) | 30.9 | 53.0 | **+22.2 pp** |

The raw gradient is large: moving from the lowest to the highest banking tercile is associated with halving the child marriage rate and nearly doubling female higher-secondary schooling. States with the lowest branch density — Bihar (4.8 per 100,000), Assam (5.5), Jharkhand (7.1), West Bengal (7.3) — also have the highest child marriage rates (41%, 31%, 33%, 40% respectively).

### 6.3 Within-State Estimates

**Table 6.2: OLS with state fixed effects (log branch density, standardised)**

| Outcome | Coeff | SE | p-value |
|---|---|---|---|
| **Child marriage** | **−1.26\*\*** | 0.641 | 0.049 |
| **Teen pregnancy** | **−0.69\*\*** | 0.328 | 0.036 |
| Literacy | +0.04 | 0.330 | 0.907 |
| **Women with 10+ yrs schooling** | **+1.71\*\*\*** | 0.491 | < 0.001 |

After absorbing state fixed effects, a one-standard-deviation increase in log branch density is associated with 1.3 pp lower child marriage (p = 0.049), 0.7 pp lower teen pregnancy (p = 0.036), and 1.7 pp more women with secondary schooling (p < 0.001). The within-state literacy coefficient is statistically insignificant; this does not imply that the remaining variation is attributable to local banking.

About half of the raw national gradient is explained by state-level confounders (states like Kerala and Himachal Pradesh have both dense banking and better outcomes for reasons beyond banking alone). The within-state estimates — comparing districts within the same state on the same development trajectory — provide a more credible measure of the banking-outcomes relationship.

Physical bank presence (branches per capita) is more consistently associated with these outcomes than deposits per capita in the reported specifications. This comparison is consistent with an accessibility explanation, but it does not show that branch presence changed behavior or household norms.

---

## 7. Study 5: Banking Stock vs. Banking Expansion

### 7.1 Design

The national cross-section raises a question about timing. Is the banking-outcomes relationship associated more strongly with the pre-2013 stock of infrastructure or with branches added during 2013–2020? A stronger relationship with the historical stock would be consistent with, but would not prove, a long-run exposure mechanism involving sustained access and community norms.

We match the 2013 RBI district census to an RBI Statement 4a 2019–20 Q4 snapshot for 514 districts, and decompose the banking-outcomes relationship into level (baseline stock) and growth (expansion) components:

| Specification | Description |
|---|---|
| Level (2013 only) | Effect of pre-existing stock |
| Level (2020 only) | Effect of contemporaneous stock |
| Growth only | Effect of 7-year expansion |
| Level (2013) + Growth | Joint decomposition |

### 7.2 Results: Stock Matters; Expansion Does Not

**Table 6.1: Level vs. expansion as predictors of 2019–21 outcomes**

| Outcome | 2013 level | 2020 level | Growth 2013→20 |
|---|---|---|---|
| Child marriage | −1.30\*\* | −0.96 (n.s.) | +0.33 (n.s.) |
| Teen pregnancy | −0.70\*\* | −0.38 (n.s.) | +0.24 (n.s.) |
| Literacy | +0.03 (n.s.) | −0.33 (n.s.) | −0.29 (n.s.) |
| Women with 10+ yrs schooling | +1.69\*\*\* | +1.58\*\*\* | +0.27 (n.s.) |

The 2013 banking baseline is the stronger predictor for child marriage and teen pregnancy: the 2013 level is significant while the 2020 contemporaneous level is not. Banking growth over the 7-year period (mean: +33%) predicts none of the four outcomes. In the joint regression, the 2013 level retains its significance and growth adds no explanatory power.

The null growth result reflects two structural factors. First, with 96% of districts expanding their branch networks, the 2013→2020 period offers insufficient within-state variation in growth rates (SD = 0.15) to identify differential effects. Second, outcomes determined over long periods — a girl's secondary school completion depends on investments made when she was 6–14 — cannot respond to branches opened in 2016–2020 by the time NFHS-5 was fielded in 2019–21.

The older snapshot's stronger association is consistent with long-run banking exposure mattering more than contemporaneous access. It does not eliminate selection bias, because persistent district development differences may influence both historical banking and later women's outcomes.

---

## 8. Study 6: Banking Depth and Women's Access — State Panel

### 8.1 Design

The national cross-section and banking stock analyses focus on variation across districts at a point in time. The state panel adds a time dimension: does within-state variation in banking depth over three NFHS rounds (2005–06, 2015–16, 2019–21) predict women's financial access?

The estimating equation is a two-way fixed effects panel:

> Y_{st} = α + β × log(deposits per capita)_{st} + state\_FE + round\_FE + ε_{st}

with standard errors clustered at the state level. The log deposits per capita variable is drawn from RBI BSR-2 annual data for NFHS-3/4 periods and RBI 4a for NFHS-5. Sample: 34 states × 2–3 rounds.

### 8.2 Results

**Table 8.1: State TWFE panel — log deposits per capita (standardised)**

| Outcome | Coeff | SE | p-value | N | R² |
|---|---|---|---|---|---|
| Bank account use (%) | +30.9† | 15.83 | 0.051 | 93 | 0.959 |
| Mobile phone use (%) | +10.7 | 16.77 | 0.524 | 66 | 0.975 |
| Decisions (%) | +0.6 | 10.12 | 0.955 | 93 | 0.746 |
| Child marriage (%) | −11.4 | 12.74 | 0.371 | 93 | 0.908 |
| Literacy (%) | +7.3 | 11.88 | 0.537 | 93 | 0.963 |

The three-round bank-account estimate is positive and marginal (+30.9 pp per SD, p = 0.051). The cleaner NFHS-4-to-NFHS-5 specification is also positive but imprecise (+24.7 pp, p = 0.319). The state panel therefore provides suggestive—not robust—evidence of a within-state banking-depth association.

Other empowerment outcomes are not significant after state and round fixed effects. The panel has only 34 states and at most three observations per state; high R² values largely reflect the fixed effects, while coefficient uncertainty remains substantial.

The bank-account finding complements Study 1 descriptively: banking depth is associated with account ownership at the state level, while the national PMMVY-intensity coefficient for account-use change is positive but statistically insignificant. These analyses do not establish a causal chain from infrastructure through program reach to access.

---

## 9. Study 7: UPI Event Study — Digital Payments and Women's DBT Programs

### 9.1 Design and Context

India's UPI transaction volume grew from 7.7 billion per month in April 2023 to 12.5 billion in December 2025 (+62%), providing strong contextual evidence of rapid digital financial infrastructure expansion. We test whether this aggregate growth was accelerated in states that launched new women-specific cash transfer programs — an event study using a state × month panel (36 states × 32 months, N = 1,152).

Three states launched new women-directed cash transfer programs within the panel window with sufficient pre-treatment periods for identification: Chhattisgarh (Mahtari Vandan Yojana, February 2024), Maharashtra (Ladki Bahin Yojana, August 2024), and Jharkhand (Maiya Samman Yojana, November 2024).

### 9.2 Results: Null, With Pre-Trend Violation for Maharashtra

The pooled two-way fixed effects DiD produces a slightly negative, marginally significant coefficient for transaction volume (−0.138, p = 0.082) — the opposite of the hypothesis. This result is driven by Maharashtra, which was already on a declining relative UPI trajectory before Ladki Bahin launched: pre-trend coefficients are significantly negative from t = −5 onwards (p < 0.001 at t = −3, −4, −5). The parallel trends assumption fails for Maharashtra, and its estimate is not causally interpretable.

Chhattisgarh shows a marginal positive effect on transaction value (+0.047, p = 0.054) but not volume. Jharkhand shows a brief positive spike at launch (+0.045, p = 0.018) that fades within two months. Per-cohort 2×2 estimates are uninformative.

### 9.3 Why Null Is Expected

The null finding is structurally expected for three reasons. First, the scale of detection: even if all 23 million Ladki Bahin enrollees in Maharashtra made one additional UPI transaction per month, the signal would be roughly 2–3% of the state's UPI volume — small relative to ongoing secular growth and monthly variability. Second, population targeting: women receiving state DBT programs are predominantly rural, low-income, and have lower smartphone ownership and baseline UPI usage than the general population. Third, transfer mechanism: DBT payments go to bank accounts, not UPI wallets. The path from bank account receipt to UPI adoption requires additional behavioral steps (app download, UPI registration, merchant acceptance) that do not follow immediately from a cash transfer, particularly in low-digital-literacy settings.

The UPI event study contextualizes the broader financial-infrastructure findings, but aggregate state activity cannot reveal whether transactions were made by women or program beneficiaries. Detecting subgroup-specific changes requires individual-level or gender-disaggregated administrative transaction data.

---

## 10. Discussion

### 10.1 A Consistent Picture Across Seven Studies

Five district-level analyses provide mixed evidence. Uttar Pradesh shows its clearest banking interaction for health-care decisions; Assam and Madhya Pradesh show significant own-money-autonomy interactions; West Bengal's estimates are imprecise; and Himachal Pradesh has too few clusters for reliable inference. The results are geographically varied but do not establish that one mechanism generalizes across settings.

Himachal Pradesh's 10 matched districts fall below common thresholds for reliable cluster-robust inference. West Bengal has lower PMMVY intensity and imprecise estimates, but sample size or treatment variation cannot be assumed to explain its result without further diagnostics. Both results appropriately qualify the cross-state pattern.

The seven analyses provide a broadly coherent, though qualified, picture of how cash transfers and banking infrastructure jointly relate to women's financial empowerment in India.

At the national level, PMMVY enrollment intensity has positive but statistically insignificant associations with improvements in bank-account use and own-money autonomy (Study 1). At the district level in UP, the PMMVY association with health-care decisions is stronger in districts with denser pre-existing banking infrastructure, while the average autonomy association is negative (Study 2). The multi-state autonomy interactions are positive in Assam and Madhya Pradesh but not uniform across all settings (Study 3). Across Indian districts, banking infrastructure is associated with lower child marriage, lower teen pregnancy, and higher female schooling (Study 4). The older banking stock is more consistently associated with outcomes than recent expansion in the joint specification (Study 5). The corrected state panel shows a marginal three-round bank-account association that is imprecise in the cleaner two-round window (Study 6). The UPI event study does not detect a robust program-launch effect in aggregate state activity and cannot identify women's transactions (Study 7).

Together, these findings are consistent with—but do not prove—the view that cash transfers and financial infrastructure are complements. Several district estimates are larger where formal financial systems are deeper, while the national average and two state replications are inconclusive. The banking stock also predates the measured outcomes, although persistent district differences remain a plausible confounder.

### 10.2 The Mechanism: Financial Ecosystem, Not Just Accounts

The UP interaction remains essentially unchanged after controlling for whether a woman has a bank account. This shows that the measured account-ownership variable does not explain the interaction in that specification; it does not identify the remaining channel or establish formal mediation.

A plausible hypothesis is that branch density proxies for a broader local financial ecosystem—agents, business correspondents, micro-ATMs, familiarity with banking, or social norms around women's transactions. These proposed channels are not observed in the current data and require direct measurement before they can be distinguished.

Greater within-state variation may help explain why an interaction is detectable in the UP district analysis but not in the 34-state national model. That explanation is plausible but is not directly tested here.

### 10.3 What Null Results Tell Us

Four of the seven studies produce null or qualified results, and these are informative rather than merely negative.

The *null average national DiD result* (Study 1) is a useful constraint. In UP, six of seven average associations are insignificant, while own-money autonomy is borderline negative. Positive raw gradients and selected interactions motivate heterogeneity analysis, but they do not demonstrate that true effects are necessarily conditioned on banking infrastructure.

The *absence of an average PMMVY treatment-intensity association in UP* (Study 2, Table 2), alongside the banking interaction, is consistent with heterogeneous relationships across financial environments. The design cannot determine that low-banking infrastructure caused districts to experience smaller gains.

The *null banking growth result* (Study 5) is consistent with long-run exposure mattering more than recent expansion, but it does not rule out persistent omitted development differences. The pre-2013 stock predicts outcomes in 2019–21 in a way that recent expansion does not in these specifications.

The *UPI event study null* (Study 7) highlights a scale problem in aggregate data analysis: possible effects on targeted subgroups may be difficult to detect in state-level aggregates. Individual-level or gender-disaggregated administrative data would be needed for a direct evaluation of digital financial inclusion among women beneficiaries.

### 10.4 Policy Implications

Several policy-relevant conclusions follow from these findings.

**Test coordinated infrastructure and transfer delivery.** The interaction estimates motivate piloting and evaluating cash-transfer delivery alongside banking access, agent coverage, and digital-literacy support. The current observational evidence is not sufficient to prescribe sequencing or to rank districts by expected causal returns.

**Broaden measurement beyond account opening.** Branch density, deposits per capita, and account ownership capture different parts of the financial environment. Future evaluations should measure agent access, transaction use, digital capability, and norms directly rather than treating an unobserved community mechanism as established.

**Program intensity matters, but is not sufficient on its own.** The wide variation in PMMVY intensity (0 to 121 per 1,000 women) is not random — it reflects administrative capacity, awareness, implementation quality, and state policy choices. The consistently positive but imprecise national estimates suggest that closing the enrollment gap between high- and low-intensity states may improve women's financial access, but the district-level results indicate these gains will be substantially larger where financial infrastructure already supports women's independent financial agency. Intensity expansion without accompanying infrastructure investment risks producing smaller returns in the states where expansion is most needed.

**Digital payment targets should account for population heterogeneity.** The UPI event study documents the aggregate growth in digital payments but shows that this growth is disconnected from the program-specific experiences of rural women DBT beneficiaries. Policy targets that aggregate urban and rural, or general-population and program-beneficiary, digital payment activity will overstate financial inclusion progress for the most vulnerable populations.

---

## 11. Conclusion

Across seven complementary analyses, selected results are consistent with women-directed cash transfers and pre-existing banking infrastructure acting as complements, but the evidence is mixed. The national state-level DiD is statistically inconclusive; in UP, six of seven average associations are insignificant and own-money autonomy is negative. Selected district interaction estimates are positive and significant in Uttar Pradesh, Assam, and Madhya Pradesh, while results do not replicate in West Bengal and are underpowered in Himachal Pradesh. The current models do not identify a mechanism. National cross-sectional and temporal analyses show a banking-empowerment gradient associated with the older stock of infrastructure rather than recent expansion.

These findings contribute hypotheses to two policy conversations. On women's financial inclusion, selected district interactions suggest heterogeneity by banking infrastructure that should be tested with stronger designs. On banking policy, the persistent association between older branch stock and contemporary outcomes motivates research on long-run exposure, while leaving selection and omitted development differences unresolved.

The null results are equally instructive. Banking expansion from 2013–2020 adds no predictive power for the selected outcomes above the 2013 stock in these specifications, and aggregate UPI data show no robust program-launch response. These results may reflect limited variation, aggregation, timing, measurement, or true null effects; the present study cannot distinguish among them.

---

---

## Appendix A: Spatial Analysis of Financial Inclusion and PMMVY Enrollment

This appendix documents the spatial maps produced to support the descriptive and diagnostic sections of the paper. All maps were generated using the India district boundary shapefile (2022), NFHS district factsheet estimates, RBI Statement 4a banking data, and Census 2011 population. Scripts: `make_spatial_maps.py`, `make_up_pmmvy_map.py`, `make_up_percapita_map.py`.

---

### A.1 National Women's Financial Inclusion (All Districts, NFHS-4 and NFHS-5)

**Files:** `map_bank_account_nfhs4.png`, `map_bank_account_nfhs5.png`, `map_bank_account_change.png`

These three maps document the baseline, endpoint, and change in women's bank account ownership across all Indian districts.

**NFHS-4 (2015–16):** Bank account self-use ranges from below 20% in low-access districts concentrated in Uttar Pradesh, Bihar, Rajasthan, and Odisha, to above 80% in parts of Kerala, Himachal Pradesh, and the northeastern states. The spatial gradient is pronounced — southern and western districts are substantially ahead of northern and eastern ones, reflecting longstanding regional disparities in banking infrastructure, literacy, and program penetration.

**NFHS-5 (2019–21):** The geographic pattern narrows substantially. Most districts above 80% remain high, but large portions of the Hindi heartland move from the 30–50% range to 60–80%. The steepest gains are in districts in Uttar Pradesh, Bihar, Madhya Pradesh, and Rajasthan — precisely the states where PMMVY enrollment intensity is highest and where Jan Dhan account openings were most numerous.

**Change map (NFHS-4 → NFHS-5):** The change map shows gains of 20–50 percentage points in large parts of the northern plains and Madhya Pradesh, with modest gains (5–15pp) in southern and northeastern states where baseline ownership was already high. Districts in the top quartile of PMMVY intensity overlap substantially with the darkest-green regions of the change map, providing visual confirmation of the descriptive gradient in the national analysis (+7.1pp raw bank account gain from low to high intensity tercile).

---

### A.2 Microfinance Knowledge and Use (All Districts, NFHS-5)

**Files:** `map_micro_knowledge_nfhs5.png`, `map_micro_use_nfhs5.png`

**Knowledge of microcredit programmes:** Spatially clustered in Andhra Pradesh, Telangana, Tamil Nadu, and Maharashtra — states with historically deep SHG and MFI penetration. Knowledge is strikingly low across the northern plains, with most UP, Bihar, and Rajasthan districts below 15%. This North–South divide reinforces the interpretation that formal financial inclusion in northern India is primarily account-based (PMJDY-driven) rather than microfinance-based.

**Microfinance use:** Even lower and more concentrated than knowledge. Southern districts show use rates of 10–25%, while virtually all northern districts are below 5%. This spatial pattern is consistent with the sector's origins in the southern SHG movement and its slower diffusion northward.

---

### A.3 Women's Labor Force Participation (All Districts, NFHS-5)

**Files:** `map_women_worked_12m.png`, `map_women_self_employed.png`, `map_women_earned_cash.png`

**Worked in past 12 months:** High in southern and northeastern states (40–60%), with a sharp discontinuity at the northern plains boundary. Rajasthan's desert districts show moderate participation, consistent with agricultural labor demand. The Hindi heartland — UP, Bihar, Jharkhand — shows among the lowest rates nationally (10–20%), combining cultural constraints on female labor force participation with limited formal-sector employment opportunities.

**Self-employment:** Highest in hilly and tribal districts (Northeastern states, Jharkhand, Chhattisgarh), where non-wage agricultural and artisanal work predominates. Urban clusters around Delhi, Mumbai, and Chennai show low self-employment relative to their high overall participation, reflecting the composition of urban employment toward wage work.

**Earned cash:** The cash earnings map largely tracks overall participation, but the gap between "worked" and "earned cash" is particularly large in UP and Bihar — indicative of unpaid family farm labor that shows up in participation statistics but not in cash income. This gap is relevant to the PMMVY mechanism: the program transfers cash directly to women's accounts, providing a source of monetized income in districts where women's work is predominantly unpaid and non-monetized.

---

### A.4 PMMVY Enrollment Status — Uttar Pradesh Districts

**Files:** `map_up_pmmvy_enrollment_log.png`, `map_up_pmmvy_enrollment_status.png`

These maps show district-level PMMVY enrollment intensity for Uttar Pradesh's 75 districts using data from April 2017 to March 2019. The enrollment rate is beneficiaries per 1,000 population (Census 2011). Districts are classified into four quartiles.

**Enrollment rate distribution:**

| Quartile | Rate range (per 1,000 pop) | Districts |
|---|---|---|
| Q1 Low | 1.8 – 5.1 | 19 |
| Q2 Medium-Low | 5.1 – 6.3 | 18 |
| Q3 Medium-High | 6.4 – 7.1 | 18 |
| Q4 High | 7.3 – 10.1 | 18 |

**Spatial pattern:** High-enrollment districts (Q4) cluster in the central and eastern belt — Maharajganj, Sitapur, Ambedkar Nagar, Shravasti, Mau, Hardoi, Mahoba. These are predominantly rural, lower-wealth districts, consistent with PMMVY's targeting design. Low-enrollment districts (Q1) include several urban and peri-urban districts — Ghaziabad, Gautam Buddha Nagar, Lucknow, Agra — where smaller eligible populations (first live birth + eligible women) relative to total population mechanically suppress the rate, and where alternative healthcare resources reduce dependence on ICDS-linked anganwadi centres through which PMMVY is delivered.

**Design implication:** The spatial concentration of high-intensity districts in rural, lower-banking eastern UP contributes to the baseline imbalance documented in Table 5. Because treatment intensity and banking are correlated, the interaction requires overlap diagnostics and cautious interpretation rather than a claim that the map identifies a joint causal effect.

*Note: Jhansi and Lalitpur districts appear grey (no data) in the UP maps. These districts are absent from the NFHS-5 UP state module, which is the primary women-level outcome dataset. All results in Studies 2 and 3 are based on 73 districts.*

---

### A.5 District Banking Per Capita — Aligned to PMMVY Enrollment Window

**Files:** `map_up_banking_percapita_panel.png`, `map_up_enrollment_vs_banking.png`

These maps extract RBI Statement 4a district banking data for two snapshots that bracket the PMMVY enrollment window:
- **March 2018 (2017-18 Q4):** 12 months into PMMVY enrollment
- **March 2019 (2018-19 Q4):** End of the 2017-19 enrollment period

**Per capita summary (2018-19 Q4, 73 UP districts):**

| Metric | Min | Median | Max |
|---|---|---|---|
| Deposits per capita (₹) | 8,371 | 29,904 | 534,331 |
| Credit per capita (₹) | 5,455 | 12,634 | 273,324 |
| Bank branches per 100k population | 2 | 7 | 29 |

**Spatial pattern — deposits per capita:** Lucknow, Agra, Ghaziabad, Kanpur Nagar, and Gautam Buddha Nagar consistently show the highest deposits per capita — a 6–18× gap versus the lowest districts. The geography of banking depth closely mirrors the geography of urban concentration. Districts in the Poorvanchal (eastern UP) subregion — Azamgarh, Mau, Ghazipur, Sonbhadra, Mirzapur — cluster at the low end, with deposits per capita of ₹8,000–15,000 in 2018-19, compared to ₹400,000+ in Lucknow.

**Side-by-side: Enrollment vs Deposits (March 2019):** The `map_up_enrollment_vs_banking.png` panel visualises a negative spatial correlation between PMMVY enrollment intensity and banking depth. Because treatment intensity and banking are not independently assigned, this pattern underscores the need for overlap diagnostics and cautious interpretation of the triple interaction.

**Between-quarter stability:** Deposits and credit per capita are highly stable between March 2018 and March 2019 at the district level (correlation r > 0.99). This supports their use as stable measures of the local financial environment and connects the UP analysis to the stock-versus-growth decomposition in Study 5.

---

### A.6 Multi-State PMMVY Enrollment and Outcomes — HP, Assam, MP, West Bengal

**Files:** `map_hp_pmmvy_enrollment.png`, `map_assam_pmmvy_enrollment.png`, `map_mp_pmmvy_enrollment.png`, `map_wb_pmmvy_enrollment.png`, `map_hp_bank_change.png`, `map_assam_bank_change.png`, `map_mp_bank_change.png`, `map_wb_bank_change.png`

**Enrollment maps (log-scale + quartile):** Each state map displays district-level PMMVY enrollment intensity (cumulative beneficiaries per 1,000 Census 2011 population) in two panels: a continuous log-scale choropleth annotating the top districts, and a discrete quartile-status map with all district names labeled.

**Bank account change maps:** Each state map shows the NFHS-4 to NFHS-5 change in women's bank account self-use by district (percentage points), using a diverging red-yellow-green palette. Districts with the largest gains are annotated. These maps serve as a visual pre-test for the DiD: if banking amplification is operating, the darkest-green districts should cluster in areas with both high PMMVY enrollment and dense pre-2013 banking infrastructure.

Key spatial patterns by state:

- **Himachal Pradesh:** Enrollment is highest in Kangra and Mandi — the most populous hill districts — and lowest in Kinnaur and Lahul and Spiti, which are remote tribal districts with low eligible-population density. Bank account gains are broadly uniform across the 12 small districts, consistent with the inconclusive DiD result.

- **Assam:** Enrollment is concentrated in Nagaon, Barpeta, and Cachar — districts with high baseline poverty and strong ICDS infrastructure. New districts created after 2011 (Biswanath, Hojai, Charaideo) appear in NFHS-5 only and have lower coverage. Bank account gains are largest in central Assam, where banking infrastructure improved most over the period.

- **Madhya Pradesh:** Enrollment is highest in Indore, Bhopal, Jabalpur, and Sagar — the major urban and semi-urban administrative centres with strong ICDS delivery. Rural tribal districts in the east (Dindori, Mandla, Umaria) show lower enrollment despite high program need, reflecting administrative capacity constraints. Bank account gains are largest in the Malwa plateau region (Indore, Ujjain, Dewas), consistent with both high PMMVY penetration and relatively dense pre-existing banking.

- **West Bengal:** Enrollment is highest in Murshidabad, Medinipur West, and Medinipur East — large, densely populated districts with high poverty rates. Kolkata and Kalimpong show very low enrollment, reflecting small eligible populations relative to district size. Bank account gains are broadly distributed, with no clear spatial alignment with enrollment intensity, consistent with WB's null DiD result.

---

## Data and Replication

All analysis was conducted in Python 3 using pandas, statsmodels, and numpy. Scripts are available in the `scripts/` directory of this project repository. Key scripts:

| Script | Study |
|---|---|
| `run_pmmvy_national_did.py` | All-India PMMVY DiD (Study 1) |
| `run_up_did_estimation.py` | UP District DiD (Study 2) |
| `build_multistate_pmmvy_analysis.py` | Multi-State Replication — HP, Assam, MP, WB (Study 3) |
| `run_national_crosssection.py` | National Cross-Section (Study 4) |
| `run_study_b_district_expansion.py` | Banking Stock vs. Expansion (Study 5) |
| `run_study_a_state_panel.py` | State Panel (Study 6) |
| `run_upi_dbt_event_study.py` | UPI Event Study (Study 7) |
| `make_spatial_maps.py` | National spatial maps (Appendix A) |
| `make_up_pmmvy_map.py` | UP PMMVY enrollment maps (Appendix A) |
| `make_up_percapita_map.py` | UP banking per capita maps (Appendix A) |

---

## References

Baird, S., Ferreira, F. H. G., Özler, B., & Woolcock, M. (2011). Conditional, unconditional and everything in between: a systematic review of the effects of cash transfer programmes on schooling outcomes. *Journal of Development Effectiveness*, 6(1), 1–43.

Banerjee, A., Duflo, E., Goldberg, N., Karlan, D., Osei, R., Parienté, W., Shapiro, J., Thuysbaert, B., & Udry, C. (2021). A multifaceted program causes lasting progress for the very poor: evidence from six countries. *Science*, 348(6236).

Burgess, R., & Pande, R. (2005). Do rural banks matter? Evidence from the Indian social banking experiment. *American Economic Review*, 95(3), 780–795.

Dupas, P., & Robinson, J. (2013). Savings constraints and microenterprise development: evidence from a field experiment in Kenya. *American Economic Journal: Applied Economics*, 5(1), 163–192.

Haushofer, J., & Shapiro, J. (2016). The short-term impact of unconditional cash transfers to the poor: experimental evidence from Kenya. *Quarterly Journal of Economics*, 131(4), 1973–2042.

---

*Analysis sample summary:*
- *Study 1:* 34 states × 2 rounds; N = 230,264 for the main outcomes (163,165 for decision-making)
- *Study 2:* 73 matched UP districts × 2 rounds; N = 29,226 women (19,834 for decision outcomes)
- *Study 3:* HP (10 matched districts, N=3,756) + Assam (24, N=7,278) + MP (47, N=15,768) + WB (17, N=5,159)
- *Study 4:* 544 districts; NFHS-5 (2019–21) × RBI 2013
- *Study 5:* 514 districts; NFHS-5 × RBI 2013 + RBI 2019–20
- *Study 6:* 34 states × 2–3 NFHS rounds; N = 66–93 state-round cells
- *Study 7:* 36 states × 32 months; N = 1,152 state-month observations
