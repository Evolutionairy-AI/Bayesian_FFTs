# Authoritative source map

## Benchmark-definition source

- Robert C. Holte (1993), *Very Simple Classification Rules Perform Well on Most Commonly Used Datasets*, Machine Learning 11:63-91. DOI: <https://doi.org/10.1023/A:1022631118932>
- Author-hosted PDF used for verification: <https://webdocs.cs.ualberta.ca/~holte/Publications/simple_rules.pdf>
- Appendix B is printed page 22 (PDF page 22); Table 2 is printed page 3 (PDF page 3).
- Pinned local copy: `references/holte-1993.pdf`; SHA-256 `e326cdd181ea03dac696b20aed42a1d1a596ab4d2d0fb1d47ffc4d9be4d05d2d`.

## UCI mapping for the 14 originals

Holte used 14 original datasets. HY and SE are two distinct raw files in one modern UCI record, so the 14 originals map to 13 current UCI identifiers.

| Code | Current UCI record | UCI ID / DOI | Current raw file(s) used | Holte Appendix B path or note |
|---|---|---|---|---|
| BC | [Breast Cancer](https://archive.ics.uci.edu/dataset/14/breast+cancer) | 14 / `10.24432/C51P4M` | `breast-cancer.data` | `breast-cancer/breast-cancer.data` |
| CH | [Chess (King-Rook vs. King-Pawn)](https://archive.ics.uci.edu/dataset/22/chess+king+rook+vs+king+pawn) | 22 / `10.24432/C5DK5C` | `kr-vs-kp.data` | `chess-end-games/king-rook-vs-king-pawn/kr-vs-kp.data` |
| GL | [Glass Identification](https://archive.ics.uci.edu/dataset/42/glass+identification) | 42 / `10.24432/C5WW2P` | `glass.data` | `glass/glass.data` |
| HD | [Heart Disease](https://archive.ics.uci.edu/dataset/45/heart+disease) | 45 / `10.24432/C52P4X` | `cleve.mod` | `heart-disease/cleve.mod` |
| HE | [Hepatitis](https://archive.ics.uci.edu/dataset/46/hepatitis) | 46 / `10.24432/C5Q59J` | `hepatitis.data` | `hepatitis/hepatitis.data` |
| HO | [Horse Colic](https://archive.ics.uci.edu/dataset/47/horse+colic) | 47 / `10.24432/C58W23` | `horse-colic.data`, `horse-colic.test` | Historical `undocumented/taylor/` prefix; filenames survive unchanged |
| HY | [Thyroid Disease](https://archive.ics.uci.edu/dataset/102/thyroid+disease) | 102 / `10.24432/C5D010` | `hypothyroid.data` | `thyroid-disease/hypothyroid.data` |
| IR | [Iris](https://archive.ics.uci.edu/dataset/53/iris) | 53 / `10.24432/C56C76` | `iris.data` | `iris/iris.data` |
| LA | [Labor Relations](https://archive.ics.uci.edu/dataset/56/labor+relations) | 56 / `10.24432/C5CP4Q` | `C4.5/labor-neg.data`, `C4.5/labor-neg.test` | Holte obtained a usable copy from Stan Matwin; the root `labor-negotiations.*` files are email-format source material, while the C4.5 files are the usable 40+17 split matching Table 2 |
| LY | [Lymphography](https://archive.ics.uci.edu/dataset/63/lymphography) | 63 / `10.24432/C54598` | `lymphography.data` | Same filename, but current file has 148 rows rather than Holte's 141 |
| MU | [Mushroom](https://archive.ics.uci.edu/dataset/73/mushroom) | 73 / `10.24432/C5959T` | `agaricus-lepiota.data` | `mushroom/agaricus-lepiota.data` |
| SE | [Thyroid Disease](https://archive.ics.uci.edu/dataset/102/thyroid+disease) | 102 / `10.24432/C5D010` | `sick-euthyroid.data` | `thyroid-disease/sick-euthyroid.data` |
| SO | [Soybean (Small)](https://archive.ics.uci.edu/dataset/91/soybean+small) | 91 / `10.24432/C5DS3P` | `soybean-small.data` | `soybean/soybean-small.data`; now a separate UCI record from Soybean (Large) |
| VO | [Congressional Voting Records](https://archive.ics.uci.edu/dataset/105/congressional+voting+records) | 105 / `10.24432/C5C01P` | `house-votes-84.data` | Historical `voting-records/house-votes-84.data` |

## Pinned current UCI bundle URLs

The acquisition script uses the following official UCI bundles and verifies their SHA-256 hashes from `manifest.json`:

- <https://archive.ics.uci.edu/static/public/14/breast+cancer.zip>
- <https://archive.ics.uci.edu/static/public/22/chess+king+rook+vs+king+pawn.zip>
- <https://archive.ics.uci.edu/static/public/42/glass+identification.zip>
- <https://archive.ics.uci.edu/static/public/45/heart+disease.zip>
- <https://archive.ics.uci.edu/static/public/46/hepatitis.zip>
- <https://archive.ics.uci.edu/static/public/47/horse+colic.zip>
- <https://archive.ics.uci.edu/static/public/53/iris.zip>
- <https://archive.ics.uci.edu/static/public/56/labor+relations.zip>
- <https://archive.ics.uci.edu/static/public/63/lymphography.zip>
- <https://archive.ics.uci.edu/static/public/73/mushroom.zip>
- <https://archive.ics.uci.edu/static/public/91/soybean+small.zip>
- <https://archive.ics.uci.edu/static/public/102/thyroid+disease.zip>
- <https://archive.ics.uci.edu/static/public/105/congressional+voting+records.zip>

## Repository-metadata caveats

The raw files, their documentation, and Holte's Table 2 are the controlling evidence where the current UCI web metadata is internally inconsistent:

- CH raw data and names contain 36 predictors plus one target, matching Holte; the current page/API may display 35 features.
- LA's C4.5 data contains 326 literal `?` tokens and Holte marks it as having missing values, although the current page may say otherwise.
- LY raw rows contain 18 predictors plus one target, matching Holte's feature count; the current page may display 19 features because it counts the target.
- The Heart Disease bundle's page emphasizes modern processed files, but the bundle still contains the exact `cleve.mod` file named by Holte.

## Licensing and access

The current UCI records display CC BY 4.0 licensing and should be cited individually. The current Lymphography page also displays a restricted-access notice despite offering a bundle and CC BY metadata; users should check the current record before redistribution. This package is an acquisition/research copy and does not supersede upstream terms.
