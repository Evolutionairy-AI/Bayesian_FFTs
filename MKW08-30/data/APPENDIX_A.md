**1. BANK** (Bankruptcy). n = 50; criterion: Bankrupt = 1, 25 / 25; C1 (the larger side) is Woike's n1 category. Rows: all. Attributes (5; Woike used 5): WC/TA, RE/TA, EBIT/TA, S/TA, BVE/BVL. Excluded: Company (identifier). Split is 25/25; C1 is set to Bankrupt = 1.

**2. SOLV** (Solvency). n = 52; criterion: Solvent = 1, 27 / 25; C1 (the larger side) is Woike's n1 category. Rows: all. Attributes (8; Woike used 8): EBIT/TA, NI/TC, Sales/TA, EBIT/Sales, NI/Sales, WC/TA, Equity/TL, Equity/TA. Excluded: Firm (identifier). 

**3. ECHO** (Echocardiogram). n = 62; criterion: alive-at-1 = 1, as shipped, 18 / 44; C1 (the larger side) is its complement. Rows: 13 fields, attributes 3-9 and alive-at-1 known. Attributes (7; Woike used 7): age_at_heart_attack, pericardial_effusion, fractional_shortening, epss, lvdd, wall_motion_score, wall_motion_index. Excluded: survival, still-alive (carry the outcome); mult, name, group (to be ignored per echocardiogram.names). The shipped criterion column contradicts its own definition on these rows (README, finding 3); it is used as shipped because it is Woike's.

**4. POST** (Post-Operative). n = 86; criterion: ADM-DECS = S (sent home), 24 / 62; C1 (the larger side) is its complement. Rows: complete rows, intensive-care class (I) removed. Attributes (8; Woike used 8): L_CORE, L_SURF, L_O2, L_BP, SURF_STBL, CORE_STBL, BP_STBL, COMFORT. Excluded: none. 

**5. BWAY** (Broadway). n = 89; criterion: Show run of six months or more, 27 / 62; C1 (the larger side) is its complement. Rows: complete rows. Attributes (7; Woike used 5): Type, Revival, NYT rating, DN rating, Tony awards, Tony nominations, Week 1 attendance. Excluded: Show (identifier); Show run code (the criterion, recoded). 

**6. CRED** (Credit Score). n = 100; criterion: Application.accepted = 1, 73 / 27; C1 (the larger side) is Woike's n1 category. Rows: all. Attributes (6; Woike used 6): Age, Income.per.dependent, Monthly.credit.card.exp, Own.home, Self.employed, Derogatory.reports. Excluded: none. 

**7. ZOO** (Zoo). n = 101; criterion: type = 1 (mammal), 41 / 60; C1 (the larger side) is its complement. Rows: all. Attributes (16; Woike used 16): hair, feathers, eggs, milk, airborne, aquatic, predator, toothed, backbone, breathes, venomous, fins, legs, tail, domestic, catsize. Excluded: animal name (identifier). 

**8. IRIS** (Iris). n = 150; criterion: species = Iris-versicolor, 50 / 100; C1 (the larger side) is its complement. Rows: all. Attributes (4; Woike used 4): sepal_length, sepal_width, petal_length, petal_width. Excluded: none. Woike does not name the species. His published accuracies (logistic regression 71 to 74, CART 95 to 98) fit versicolor against the rest and no other coding. File iris.data, not bezdekIris.data.

**9. HEPA** (Hepatitis). n = 153; criterion: class = 2 (live), 121 / 32; C1 (the larger side) is Woike's n1 category. Rows: complete on AGE, SEX, STEROID, ANTIVIRALS, FATIGUE, MALAISE, ANOREXIA, HISTOLOGY. Attributes (19; Woike used 7): AGE, SEX, STEROID, ANTIVIRALS, FATIGUE, MALAISE, ANOREXIA, LIVER_BIG, LIVER_FIRM, SPLEEN_PALPABLE, SPIDERS, ASCITES, VARICES, BILIRUBIN, ALK_PHOSPHATE, SGOT, ALBUMIN, PROTIME, HISTOLOGY. Excluded: none. 

**10. STRK** (Strikes). n = 163; criterion: Wildcat strikes > 0, 86 / 77; C1 (the larger side) is Woike's n1 category. Rows: all. Attributes (4; Woike used 4): Grievances, Rotate, Union, Workforce. Excluded: Log workforce (monotone transform of Workforce; the same cue after a median cut). 

**11. WINE** (Wine). n = 178; criterion: cultivar = 2, 71 / 107; C1 (the larger side) is its complement. Rows: all. Attributes (13; Woike used 13): alcohol, malic_acid, ash, alcalinity_of_ash, magnesium, total_phenols, flavanoids, nonflavanoid_phenols, proanthocyanins, color_intensity, hue, od280_od315, proline. Excluded: none. 

**12. CYY** (Baseball CYY). n = 189; criterion: Cy Young = 1, 43 / 146; C1 (the larger side) is its complement. Rows: all. Attributes (9; Woike used 9): Year, League, Type, Wins, Win pct, Saves, ERA, Strikeouts, Innings pitched. Excluded: Pitcher (identifier). The two files (1980-92, 1993-2002) are pooled, as Woike's n requires.

**13. GLAS** (Forensic Glass). n = 214; criterion: type 1 or 2 (building windows), 146 / 68; C1 (the larger side) is Woike's n1 category. Rows: all. Attributes (9; Woike used 9): RI, Na, Mg, Al, Si, K, Ca, Ba, Fe. Excluded: Id (identifier). 

**14. HORS** (Horse Colic). n = 366; criterion: surgery = 1 (treated with surgery), 214 / 152; C1 (the larger side) is Woike's n1 category. Rows: surgery known. Attributes (20; Woike used 6): age, rectal_temperature, pulse, respiratory_rate, temperature_of_extremities, peripheral_pulse, mucous_membranes, capillary_refill_time, pain, peristalsis, abdominal_distension, nasogastric_tube, nasogastric_reflux, nasogastric_reflux_ph, rectal_examination_feces, abdomen, packed_cell_volume, total_protein, abdominocentesis_appearance, abdominocentesis_total_protein. Excluded: hospital number (identifier); outcome (known only after the decision); surgical lesion, three lesion-type codes, cp_data (established retrospectively, after surgery or necropsy). Woike's 218 cases could not be reconstructed; all 366 rows of .data and .test with a known criterion are used. Criterion per Woike et al. (2017), Table 1.

**15. SPCT** (SPECT). n = 267; criterion: diagnosis = 1 (abnormal), 212 / 55; C1 (the larger side) is Woike's n1 category. Rows: all. Attributes (22; Woike used 22): F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12, F13, F14, F15, F16, F17, F18, F19, F20, F21, F22. Excluded: none. Donor's train and test files pooled, as Woike's n requires.

**16. HUNG** (Heart (Hungaria)). n = 294; criterion: num = 1 (disease present), 106 / 188; C1 (the larger side) is its complement. Rows: all. Attributes (13; Woike used 10): age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal. Excluded: none. File processed.hungarian.data, all 294 rows; slope, ca and thal are mostly missing and enter with the missing value as a pseudo-value, as the protocol prescribes.

**17. CLEV** (Heart (Cleveland)). n = 297; criterion: num > 0 (disease present), 137 / 160; C1 (the larger side) is its complement. Rows: complete rows. Attributes (13; Woike used 13): age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal. Excluded: none. File processed.cleveland.data.

**18. ALCO** (Alcohol). n = 345; criterion: drinks > 5 half-pints, 88 / 257; C1 (the larger side) is its complement. Rows: all. Attributes (5; Woike used 5): mcv, alkphos, sgpt, sgot, gammagt. Excluded: selector (the donor's train/test flag). 

**19. IONO** (Ionosphere). n = 351; criterion: class = g (good return), 225 / 126; C1 (the larger side) is Woike's n1 category. Rows: all. Attributes (34; Woike used 33): a01, a02, a03, a04, a05, a06, a07, a08, a09, a10, a11, a12, a13, a14, a15, a16, a17, a18, a19, a20, a21, a22, a23, a24, a25, a26, a27, a28, a29, a30, a31, a32, a33, a34. Excluded: none. Attribute a02 is constant; the harness drops constant cues by itself.

**20. TOUR** (Tourism). n = 365; criterion: Trips > 0, 85 / 280; C1 (the larger side) is its complement. Rows: complete on Age, Sex, Income, Travel cost, Trips. Attributes (7; Woike used 4): Age, Sex, Income, Travel cost, Access road, Active, Passive. Excluded: Logged income (monotone transform of Income). The record with Sex = 4 is kept as it stands.

**21. VOTE** (Voting). n = 435; criterion: party = democrat, 267 / 168; C1 (the larger side) is Woike's n1 category. Rows: all. Attributes (16; Woike used 16): vote01, vote02, vote03, vote04, vote05, vote06, vote07, vote08, vote09, vote10, vote11, vote12, vote13, vote14, vote15, vote16. Excluded: none. Woike's 402 cases could not be reconstructed; all 435 rows are used, with '?' as a third value.

**22. EDUC** (Education). n = 435; criterion: Leaving Certificate taken (code 2), 211 / 224; C1 (the larger side) is its complement. Rows: educational level 2 or higher and prestige recorded. Attributes (4; Woike used 4): sex, DVRT, fathers_prestige, school_type. Excluded: educational level (determines the criterion). 

**23. CARD** (Cardiac). n = 558; criterion: any.event = 0 (no cardiac event; Woike's n1 = 469), 469 / 89; C1 (the larger side) is Woike's n1 category. Rows: all. Attributes (26; Woike used 8): bhr, basebp, basedp, pkhr, sbp, dp, dose, maxhr, pctMphr, mbp, dpmaxdo, dobdose, age, gender, baseEF, dobEF, chestpain, restwma, posSE, hxofHT, hxofDM, hxofCig, hxofMI, hxofPTCA, hxofCABG, ecg. Excluded: row index (identifier); newMI, newPTCA, newCABG, death (components of the criterion). File stressEcho.csv (hbiostat), whose event columns are coded 1 = yes.

**24. FOOT** (Football). n = 672; criterion: favorite wins (favorite points > underdog points), 451 / 221; C1 (the larger side) is Woike's n1 category. Rows: all. Attributes (4; Woike used 4): favorite_at_home, point_spread, year, week. Excluded: favorite points, underdog points (define the criterion); favorite, underdog (team names) (identifiers); night / Monday / overtime tokens (optional trailing tokens; overtime is known only after the game). Woike's text says 'home team wins'; his counts are those of 'favorite wins' (README, finding 1). The counts decide. The single tie counts as not won.

**25. BCW** (Breast Cancer). n = 683; criterion: class = 2 (benign), 444 / 239; C1 (the larger side) is Woike's n1 category. Rows: complete rows. Attributes (9; Woike used 9): clump_thickness, cell_size_uniformity, cell_shape_uniformity, marginal_adhesion, epithelial_cell_size, bare_nuclei, bland_chromatin, normal_nucleoli, mitoses. Excluded: sample id (identifier). 

**26. PIMA** (Diabetes). n = 768; criterion: tested_positive, 268 / 500; C1 (the larger side) is its complement. Rows: all. Attributes (8; Woike used 6): preg, plas, pres, skin, insu, mass, pedi, age. Excluded: none. Tabelle 6.9 prints n = 786, a transposition of 768. Zeros are kept as recorded.

**27. AUTH** (Authorship). n = 841; criterion: Author = Shakespeare, 173 / 668; C1 (the larger side) is its complement. Rows: all. Attributes (69; Woike used 69): a, all, also, an, and, any, are, as, at, be, been, but, by, can, do, down, even, every, for, from, had, has, have, her, his, if, in, into, is, it, its, may, more, must, my, no, not, now, of, on, one, only, or, our, should, so, some, such, than, that, the, their, then, there, things, this, to, up, upon, was, were, what, when, which, who, will, with, would, your. Excluded: BookID (identifies the author's books). 

**28. HOF** (Baseball HoF). n = 1320; criterion: Hall of Fame code 1 or 2, 124 / 1196; C1 (the larger side) is its complement. Rows: complete rows. Attributes (16; Woike used 15): Number seasons, Games played, At bats, Runs, Hits, Doubles, Triples, Home runs, RBIs, Walks, Strikeouts, Batting average, On base pct, Slugging pct, Fielding ave, Position. Excluded: Player (identifier). 

**29. YEAS** (Yeast). n = 1484; criterion: site = CYT, 463 / 1021; C1 (the larger side) is its complement. Rows: all. Attributes (8; Woike used 8): mcg, gvh, alm, mit, erl, pox, vac, nuc. Excluded: sequence name (identifier). 

**30. SCOT** (Supreme Court). n = 4052; criterion: Actions taken > 0, 170 / 3882; C1 (the larger side) is its complement. Rows: all. Attributes (7; Woike used 7): Liberal, Unconstitutional, Precedent alteration, Unanimous, Year of decision, Lower court disagreement, Log exposure. Excluded: none. 
