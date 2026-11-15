# Paper 1: how every rejection comment is addressed in the new version

The new manuscript (`FedTW_JoCC_manuscript.docx`) targets the **Journal of Cloud Computing** (Springer, Q1).
All experiments were re-run from scratch with new code (`../code/`); none of the old numbers are reused.

## Rejections in the last month (Sep 2026)

| Journal | Date | Decision | Main reason given |
|---|---|---|---|
| Journal of Grid Computing | 11 Sep | Desk reject | Insufficient scientific contribution; writing disconnected and informal |
| JJCIT | 12 Sep | Desk reject | Novelty / significance |
| IJIES (paper 20266114) | 20 Sep | Reject after review | Two detailed reviewers (below) |

Still under review with the **old** version: The Journal of Supercomputing (11 Sep) and Iraqi Journal of Science (15 Sep).
Do not submit the new version anywhere until both have decided (or you withdraw), to avoid a duplicate submission.

## Editor comments (Grid Computing, JJCIT)

| Comment | What changed |
|---|---|
| Contribution below threshold / novelty | New method **FedTW** (target-wise label-shift correction) + a diagnosis that overturns the old claim. Old paper = sensitivity study of μ only. |
| Writing disconnected, informal | Entire text rewritten from scratch in formal academic English, one argument per paragraph, explicit transitions, no conversational phrases. |

## IJIES Reviewer 1

| # | Comment | What changed in the new version |
|---|---|---|
| 1 | S4 gain confounded by longer training (3.6× more rounds) | Every method now gets **identical** rounds (60), local steps (25) and samples; no early stopping; checkpoint chosen on validation. Accuracy-versus-round curves (Fig. 5) and a 3× longer budget (180 rounds) are reported. Result: at an equal budget FedProx does **not** repair the loss — the old gain was the extra training. |
| 2 | S1 "IID" was consecutive chunks | IID now = uniform random assignment of windows. The chunk partition is kept, correctly named TEMP (temporal silos). |
| 3 | S4 engineered from the target; quantify divergence; more severity levels | Dirichlet target skew with α = 1.0, 0.3, 0.1 on duration, plus α = 0.1 on CPU and on memory; old S4 kept as BAND-dur. Jensen–Shannon divergence reported per target for every regime (Table 1) and related to the accuracy loss (Fig. 2). Real mechanism discussed: sites specialise in job types. |
| 4 | Leakage / validation protocol unclear | Methods section states: 72/8/20 chronological split before partitioning, windows built **inside** each period (no boundary crossing), scaler fitted on train only, checkpoint and μ tuning on validation only, test touched once. |
| 5 | "Optimum at μ = 1.0" inconsistent; extend sweep | Sweep extended to μ ∈ {0.001, 0.01, 0.1, 0.3, 1, 3, 10}; no optimum claim; large μ shown to degrade all targets. |
| 6 | Per-target μ recommended but not implemented | FedTW **is** a per-target mechanism (weights per output). A per-head proximal ablation is also reported (it does not help). |
| 7 | Only 5 seeds; multiplicity unclear | 10 seeds for all main runs; Wilcoxon signed-rank + Holm with each family stated in the table captions; paired 95% CIs; moving-block bootstrap of the test period (data-level uncertainty); 4 temporal hold-out blocks; per-seed values released. |
| 8 | Reproducibility artefact | Full code, run configurations, deterministic partitions, per-seed/per-round JSON results and table/figure scripts in the repository (Additional file 1). |
| 9 | Abstract should give numbers | Abstract reports the R² losses and FedTW gains on both traces with the significance level. |

## IJIES Reviewer 2

| # | Comment | What changed |
|---|---|---|
| 1 | Separate regularisation from optimisation budget | Same as R1-1 (matched rounds/steps/samples; curves vs round; 180-round check; τ = 5 / 300-round communication-heavy baseline). |
| 2 | Update literature; include contemporary baselines | New related-work section on drift correction (FedProx, SCAFFOLD, FedNova, FedDyn), server optimisers (FedAvgM, FedAdam), label-skew methods (FedLC, FedRS), personalised FL, federated forecasting. Baselines now include FedAvgM and FedAdam; SCAFFOLD evaluated and its incompatibility with adaptive local optimisers explained. Literature values are no longer used as rankings. |
| 3 | Generalisation broader than the partitions support; divergence measures; severity levels; multiple temporal holdouts | Divergence for every regime; 3 severity levels + skew on each target; 4 temporal hold-out blocks; limitations section states the constructed-partition caveat. |
| 4 | Seeds vs data uncertainty; calibrate wording | Block bootstrap of the test period added; "precisely estimated" and similar phrasing removed. |
| 5 | Recommendation not deployable; implement adaptive strategy or call it diagnostic | FedTW is the deployable, regime-adaptive strategy: it switches itself off under IID (weights ≈ 1) and activates only for the skewed target. |

## Things you must check before submitting

1. **References**: I only used papers I am confident exist, but please verify every entry (volume, pages, DOI), especially refs added in this version.
2. **Author names and affiliations** on the title page.
3. **Supplementary file**: zip `paper 1/JoCC_revision/code` + `results` as Additional file 1, or publish on GitHub/Zenodo and put the link in "Availability of data and materials".
4. **Cover letter** (`FedTW_JoCC_cover_letter.docx`): mention that this is a substantially new study.
5. Journal of Cloud Computing is open access with an article processing charge — check whether NTU/Iraq is eligible for a waiver.
