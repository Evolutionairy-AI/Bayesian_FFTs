# Appendix B evidence digest

Source: Holte (1993), Appendix B, printed page 22 in `references/holte-1993.pdf`.

Holte states that the datasets came from the UCI collection and, unless he notes otherwise, were used as found in the April 1990 distribution. He identifies BC and LY as Ljubljana Oncology Institute data prepared for experimentation by Igor Kononenko.

The dataset-by-dataset evidence is:

- **BC:** use `breast-cancer.data` without an explicit data transformation.
- **CH:** use `kr-vs-kp.data` without an explicit data transformation.
- **GL:** use `glass.data` and delete its first attribute. Holte notes that class 4 has no observations, leaving six observed classes.
- **G2:** derive from transformed GL by combining classes 1 and 3 and deleting classes 4-7. Operationally, keep source labels 1, 2, and 3; map 3 to 1; discard 5, 6, and 7 (4 is absent).
- **HD:** use `cleve.mod` and delete its final attribute, leaving the binary class already present in the penultimate field.
- **HE:** use `hepatitis.data` without an explicit data transformation.
- **HO:** concatenate `horse-colic.data` and `horse-colic.test`; use V24 as the class; delete V3 and V25-V28.
- **HY:** use `hypothyroid.data` without an explicit data transformation.
- **IR:** use `iris.data` without an explicit data transformation.
- **LA:** the April-1990 UCI copy was unusable; Holte obtained a usable copy directly from Stan Matwin and believed it had subsequently entered UCI. The current bundle's C4.5 40-row data plus 17-row test files reproduce Holte's dimensions and baseline.
- **LY:** use `lymphography.data` without an explicit transformation. The current UCI file has later version drift: 148 rows rather than the 141 reported by Holte.
- **MU:** use `agaricus-lepiota.data` without an explicit data transformation.
- **SE:** use `sick-euthyroid.data` without an explicit data transformation.
- **SO:** use `soybean-small.data` without an explicit data transformation.
- **VO:** use `house-votes-84.data` without an explicit data transformation.
- **V1:** derive from VO by deleting the `physician-fee-freeze` predictor, the fourth predictor in the source order.

The paper also explains in Section 1.1 that the identifier-like attributes in GL and HO were manually removed because they could identify observations. Those removals are the GL first-field deletion and the HO V3 deletion specified in Appendix B.

Table 2 supplies the expected row, predictor, class, majority-baseline, and missing-value summaries reproduced in `expected-counts.csv`.
