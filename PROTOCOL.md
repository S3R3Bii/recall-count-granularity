# Study 17: counting granularity in food enforcement records

## Decision, audience and success criteria

For an internal research-data review queue, how do product-record and distinct-event counts change monthly volumes and fixed threshold triggers? Preserve all products and expose both grains. Success requires complete stable source pagination, exact original-to-subset checks, unchanged coverage gates, code/threshold freeze before evaluation outcomes, independent SQL and rational reconstruction, isolated replay, legible original figures, a numerically checked manuscript, bounded publication audit and exact-head Linux/merge/tag proof. Each criterion is PASS/FAIL/UNKNOWN; all must pass before release. A grade of 4 means these scoped criteria are met, not universal correctness or peer review.

This executable scope supersedes the broader proposal's unobserved amendment lineage, human labels and future-alert evaluation. A current snapshot cannot establish those. Different legitimate products under one event are **not duplicate errors**. No NLP model is needed for published exact FDA identifiers; no NLP or learned detector claim will be made.

## Source and privacy

Sequential annual queries to https://api.fda.gov/food/enforcement.json for report_date in each calendar year 2017–2025 inclusive, sorted recall_number.exact ascending, limit=1000, skip=0,1000,... . Keep full raw responses outside Git. Extract only recall_number, event_id, report_date, classification, product_type, plus source year/page/row. Retain each exact page's URL, UTC retrieval time, bytes/hash, total, last_updated and subset hash. Require all pages' version metadata unchanged, complete annual totals and strictly increasing unique product identifiers across each annual query; final per-year count probes must match starting totals and version. Halt on an unstable snapshot or published service limit; never silently refresh an analyzed snapshot.

All fields must be nonempty strings, event_id positive decimal, recall_number unique across the complete snapshot, dates valid and inside requested year, product_type exactly Food, classification in Class I/II/III. Require all 108 calendar months to contain at least one product and at least one distinct event in the all-class panel; each class must have at least 20 nonzero calibration months. Unknown labels/missing fields/gaps fail the gate without outcome-based repair. Coverage and format totals can be computed before freeze; evaluation event fanout, thresholds and trigger outcomes cannot.

## Temporal separation and counting units

Calibration: January 2017–December 2021 (60 months). Evaluation: January 2022–December 2025 (48 months), inspected once after committed code and calibration freeze. These are report-date partitions of one later snapshot, not historical information vintages or a prospective test.

For each calendar month, compute row count P, unique product recall-number count U and distinct event-ID count E; require P=U under the uniqueness gate. Primary panel: all food records. Secondary panels: each of three classifications. Event IDs may cross months or classes; count within each month/panel and retain exact membership. Do not sum class-event counts as all-event counts or call event-month totals unique annual/new events. No cross-month deduplication, status fields, free text, first-publication dates or amendment inference.

Fanout P/E and excess P−E describe the chosen counting unit, not erroneous records or avoidable work. Within each month retain event-size distribution, maximum, top-five product fraction and sum of squared product shares. Across the snapshot retain counts of event IDs spanning multiple months/classes, described only as observed membership. No named firm/product analysis.

## Fixed threshold policies and sensitivity

The prespecified primary calibration quantile is 0.95, with 0.90 and 0.99 sensitivities. For each panel and counting grain use Hyndman–Fan type 7 linear sample quantile: h=(n−1)q, interpolate sorted counts at floor(h)/ceil(h). Represent thresholds as exact rational numerator/denominator. A review flag means count **strictly greater** than threshold; equality is not flagged. These are illustrative policy conventions, not optimized anomaly thresholds or estimates of true safety events.

Compare (A) event counts against their own event threshold; (B) product counts against that **same event threshold**, exposing a deliberately mismatched unit; and (C) product counts against their **own product-calibrated threshold**, the fair comparator. Retain every month and all 36 quantile/panel/policy combinations, including agreements. Class panels are secondary. Report flag counts, overlap and both directions of discordance relative to A; do not label them false positives/negatives, precision/recall or public safety performance. Product and event policies answer different workload questions.

For q=0.95, leave each of five calibration years out, recalibrate both grain thresholds on the remaining 48 months, and re-evaluate the fixed 48-month evaluation period. Retain every omitted-year result. No selection among thresholds/panels/scenarios. Report finite sensitivity ranges; no confidence intervals, causal attribution, exposure denominator or inference to future risk. These finite population counts do not require fabricated sampling uncertainty.

## Independent validation and presentation

Check minimized strings against every selected full-response field independently. Reconstruct counts/memberships through SQLite COUNT DISTINCT/grouping, independently reconstruct quantiles with decimal arithmetic, and compare every monthly fanout/concentration and flag using integer cross-products. Boundary fixtures must cover multi-product events, cross-month/class membership, quantile interpolation/equality, same-vs-own thresholds, duplicate identifiers and missing-month rejection. Preserve failures and targeted fixes. Fresh isolated source/calibration/analysis replay must match all stored scientific tables and certificates; public reproduction reads only the minimized snapshot, not private originals.

Three original figures: monthly all-class counts; within-month fanout/concentration; evaluation flag agreement/discordance for both threshold comparisons and fixed quantiles. Verify plotted tables independently, render every manuscript page and inspect text/units/qualifications. Executive first layer states the decision, actual finding, recommendation and limits; do not imply deployment, human audit, novel algorithms, peer review, medical advice or realized savings.

## Review and release boundaries

At most three substantive review rounds, 45 active review minutes and 60 review-specific tool calls per study; execution is separate. No subagents, external judge, paid runs or background reviews. Retain a current-version receipt with hashes, checks, gate states, grade, workload proxies and supported shared usage observations. Stop for a persistent material defect after one targeted retry; finish unaffected authorized work. A public release requires reviewed exact Git bytes, approved independent manuscript hashes, passing exact-head Linux checks, matching tested/merged trees, remote annotated tag/main and updated program accounting. Separate formal-publication projects including Azure remain private.
