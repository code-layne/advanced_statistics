# Statistics — Course Outline

Shepherd · 2026–2027 · **9 units · 80 lessons**

Titles and focus lines are taken from each unit's cover sheet
(`unitXX/unit_cover/main.tex`) and each lesson plan (`unitXX/lessonYY/main.tex`).

| Unit | Title | Lessons | Sample test |
| --- | --- | ---: | --- |
| 1 | Exploring One-Variable Data | 10 | yes |
| 2 | Exploring Two-Variable Data | 9 | yes |
| 3 | Collecting Data | 7 | yes |
| 4 | Probability, Random Variables, and Probability Distributions | 12 | **no** |
| 5 | Sampling Distributions | 8 | yes |
| 6 | Inference for Categorical Data: Proportions | 11 | yes |
| 7 | Inference for Quantitative Data: Means | 10 | yes |
| 8 | Inference for Categorical Data: Chi-Square | 7 | yes |
| 9 | Inference for Quantitative Data: Slopes | 6 | yes |

---

## Unit 1 — Exploring One-Variable Data (10 lessons)

Introduces the foundational language and tools of statistics: classifying variables,
organizing and representing categorical and quantitative data, and describing
distributions by shape, center, spread, and unusual features. Closes with summary
statistics, boxplots, comparisons across groups, and the Normal distribution.

| # | Title | Focus |
| --- | --- | --- |
| 1.1 | Introducing Statistics | What can we learn from data? Statistical questions, individuals, variables, the data cycle |
| 1.2 | The Language of Variation | Variables vs. values; categorical vs. quantitative; distribution |
| 1.3 | Representing a Categorical Variable with Tables | Frequency and relative frequency tables; marginal and joint frequencies |
| 1.4 | Representing a Categorical Variable with Graphs | Bar graphs, segmented bar graphs, pie charts; comparing displays |
| 1.5 | Representing a Quantitative Variable with Graphs | Dotplots, stemplots, histograms; choosing a display |
| 1.6 | Describing the Distribution of a Quantitative Variable | Shape, center, spread, unusual features (SOCS); describing in context |
| 1.7 | Summary Statistics for a Quantitative Variable | Mean, median, range, IQR, standard deviation; resistance to outliers |
| 1.8 | Graphical Representations of Summary Statistics | Boxplots and modified boxplots; the 1.5 × IQR outlier rule |
| 1.9 | Comparing Distributions of a Quantitative Variable | Parallel boxplots, back-to-back stemplots; comparing shape, center, spread |
| 1.10 | The Normal Distribution and z-Scores | Properties of the Normal curve; 68–95–99.7 rule; standardized scores |

## Unit 2 — Exploring Two-Variable Data (9 lessons)

Extends statistical thinking to relationships between two variables: two-way tables and
conditional distributions for categorical pairs, then scatterplots, correlation, linear
regression, and residual analysis for quantitative pairs. Closes with power and
exponential transformations that linearize curved patterns.

| # | Title | Focus |
| --- | --- | --- |
| 2.1 | Introducing Statistics: Are Variables Related? | Statistical questions about relationships; apparent vs. real associations |
| 2.2 | Representing Two Categorical Variables | Two-way tables; joint, marginal, and conditional relative frequencies |
| 2.3 | Statistics for Two Categorical Variables | Comparing conditional distributions; segmented bar charts; association |
| 2.4 | Representing Two Quantitative Variables | Scatterplots; direction, form, strength; explanatory vs. response |
| 2.5 | Correlation | Pearson's *r*; properties and interpretation; correlation ≠ causation |
| 2.6 | Linear Regression Models | Least-squares line ŷ = a + bx; interpreting slope and intercept |
| 2.7 | Residuals | Calculating residuals; residual plots; assessing linearity |
| 2.8 | Least Squares Regression | b = r·s_y/s_x and a = ȳ − bx̄; *s* and *r*²; influential points |
| 2.9 | Analyzing Departures from Linearity | Power and exponential transformations; evaluating linearized models |

## Unit 3 — Collecting Data (7 lessons)

Examines how data are collected and why the collection method determines what conclusions
can validly be drawn — observational studies vs. experiments, sampling methods and their
bias sources, the principles of well-designed experiments, and the logic that lets random
assignment support causal claims.

| # | Title | Focus |
| --- | --- | --- |
| 3.1 | Introducing Statistics: Do the Data We Collected Tell the Truth? | Questioning collection methods; chance vs. non-chance data |
| 3.2 | Introduction to Planning a Study | Population vs. sample; observational study vs. experiment; generalization |
| 3.3 | Random Sampling and Data Collection | SRS, stratified, cluster, systematic, census; choosing a method |
| 3.4 | Potential Problems with Sampling | Voluntary response, undercoverage, nonresponse, question-wording bias |
| 3.5 | Introduction to Experimental Design | Components of experiments; principles of good design; blocking |
| 3.6 | Selecting an Experimental Design | Completely randomized, block, and matched-pairs designs |
| 3.7 | Inference and Experiments | Statistically significant results; causal conclusions; scope of inference |

## Unit 4 — Probability, Random Variables, and Probability Distributions (12 lessons)

Develops the mathematical language of chance: simulation, probability rules, conditional
probability and independence, then discrete random variables, their parameters, rules for
combining them, and the binomial and geometric models. Provides the probabilistic
foundation for Units 5–9.

| # | Title | Focus |
| --- | --- | --- |
| 4.1 | Introducing Statistics: Random and Non-Random Patterns? | Patterns in data vs. true randomness; questioning variation |
| 4.2 | Estimating Probabilities Using Simulation | Outcomes, events, simulation design; law of large numbers |
| 4.3 | Introduction to Probability | Sample spaces; classical probability; complement rule; long-run interpretation |
| 4.4 | Mutually Exclusive Events | Joint probability; disjoint events; Venn diagrams; P(A ∩ B) = 0 |
| 4.5 | Conditional Probability | P(A \| B); multiplication rule; two-way tables |
| 4.6 | Independent Events and Unions of Events | Independence vs. mutual exclusivity; addition rule P(A ∪ B) |
| 4.7 | Introduction to Random Variables and Probability Distributions | Discrete random variables; probability tables and histograms; cumulative distributions |
| 4.8 | Mean and Standard Deviation of Random Variables | μ_X = Σ x·P(X = x); σ_X; contextual interpretation |
| 4.9 | Combining Random Variables | Linear transformations; sums and differences of independent variables |
| 4.10 | Introduction to the Binomial Distribution | BINS conditions; P(X = k) = C(n,k)p^k(1−p)^(n−k); binompdf |
| 4.11 | Parameters for a Binomial Distribution | μ_X = np; σ_X = √(np(1−p)); cumulative binomcdf; interpretation |
| 4.12 | The Geometric Distribution | Trials until first success; P(X = k) = (1−p)^(k−1)p; μ_X = 1/p |

## Unit 5 — Sampling Distributions (8 lessons)

Builds the theoretical bridge between data and inference. Formalizes the sampling
distribution, revisits the Normal model, develops the Central Limit Theorem, and derives
center, spread, and shape for the sampling distributions of p̂, p̂₁ − p̂₂, x̄, and
x̄₁ − x̄₂ — the four statistics all later inference rests on.

| # | Title | Focus |
| --- | --- | --- |
| 5.1 | Introducing Statistics: Why Is My Sample Not Like Yours? | Statistics vs. parameters; sampling variability; sampling distributions defined |
| 5.2 | The Normal Distribution, Revisited | X ~ N(μ, σ); forward and inverse normal probability; model appropriateness |
| 5.3 | The Central Limit Theorem | CLT conditions; μ_x̄ = μ; σ_x̄ = σ/√n; shape |
| 5.4 | Biased and Unbiased Point Estimates | Unbiased estimators (x̄, p̂, s²); variability decreases with *n* |
| 5.5 | Sampling Distributions for Sample Proportions | μ_p̂ = p; σ_p̂ = √(p(1−p)/n); Large Counts condition |
| 5.6 | Sampling Distributions for Differences in Sample Proportions | μ = p₁ − p₂; σ = √(p₁(1−p₁)/n₁ + p₂(1−p₂)/n₂); four counts |
| 5.7 | Sampling Distributions for Sample Means | μ_x̄ = μ; σ_x̄ = σ/√n; Normal / Large Sample condition |
| 5.8 | Sampling Distributions for Differences in Sample Means | μ = μ₁ − μ₂; σ = √(σ₁²/n₁ + σ₂²/n₂); conditions |

## Unit 6 — Inference for Categorical Data: Proportions (11 lessons)

Introduces formal inference: confidence intervals for one proportion, the full
significance-testing cycle, Type I/II errors and power, then the two-sample extension.
Establishes the reasoning framework applied in every later inference unit.

| # | Title | Focus |
| --- | --- | --- |
| 6.1 | Introducing Statistics: Why Be Normal? | Distribution shape variation; bridge from sampling distributions to inference |
| 6.2 | Constructing a Confidence Interval for a Population Proportion | One-sample z-interval; conditions; SE_p̂; margin of error; sample size |
| 6.3 | Justifying a Claim Based on a Confidence Interval for a Population Proportion | Interpreting CIs; width vs. *n* and *C*; justifying claims |
| 6.4 | Setting Up a Test for a Population Proportion | H₀ and H_a; one-sample z-test; conditions (np₀ ≥ 10, etc.) |
| 6.5 | Interpreting p-Values | Test statistic *z*; p-value definition and interpretation; null distribution |
| 6.6 | Concluding a Test for a Population Proportion | Significance level α; reject / fail to reject; conclusion in context |
| 6.7 | Potential Errors When Performing Tests | Type I / Type II errors; power; factors affecting error probabilities |
| 6.8 | Confidence Intervals for the Difference of Two Proportions | Two-sample z-interval for p₁ − p₂; conditions; calculation |
| 6.9 | Justifying a Claim Based on a CI for a Difference of Population Proportions | Interpreting two-sample CIs; justifying claims about differences |
| 6.10 | Setting Up a Test for the Difference of Two Population Proportions | H₀: p₁ = p₂; two-sample z-test; pooled proportion p̂_c |
| 6.11 | Carrying Out a Test for the Difference of Two Population Proportions | Pooled z-statistic; p-value; decision and conclusion in context |

## Unit 7 — Inference for Quantitative Data: Means (10 lessons)

Moves from the z-distribution to the t-distribution: confidence intervals and
significance tests for one mean, then the two-sample setting (independent and paired),
closing with a synthesis lesson on selecting and communicating procedures.

| # | Title | Focus |
| --- | --- | --- |
| 7.1 | Introducing Statistics: Should I Worry About Error? | Revisiting error; transition to means; motivating t-procedures |
| 7.2 | Constructing a Confidence Interval for a Population Mean | One-sample t-interval; t-distribution; degrees of freedom; conditions |
| 7.3 | Justifying a Claim Based on a CI for a Population Mean | Interpreting t-intervals; width vs. *n* and *C*; justifying claims |
| 7.4 | Setting Up a Test for a Population Mean | H₀/H_a for μ; one-sample t-test; Normal / Large Sample conditions |
| 7.5 | Carrying Out a Test for a Population Mean | t-statistic; p-value; decision and conclusion; linking CI and test |
| 7.6 | Confidence Intervals for the Difference of Two Means | Two-sample t-interval for μ₁ − μ₂; conditions; calculation |
| 7.7 | Justifying a Claim Based on a CI for a Difference of Means | Interpreting two-sample t-intervals; justifying comparative claims |
| 7.8 | Setting Up a Test for the Difference of Two Population Means | H₀: μ₁ = μ₂; two-sample t-test; paired vs. independent |
| 7.9 | Carrying Out a Test for the Difference of Two Population Means | Two-sample t-statistic; p-value; decision and conclusion |
| 7.10 | Skills Focus: Selecting and Communicating Inference Procedures | Choosing z- vs. t-procedures; full four-step AP exam practice |

## Unit 8 — Inference for Categorical Data: Chi-Square (7 lessons)

Extends inference to categorical data with two or more categories: goodness of fit,
homogeneity, and independence, closing with a synthesis of all categorical procedures
from Units 6 and 8.

| # | Title | Focus |
| --- | --- | --- |
| 8.1 | Introducing Statistics: Are My Results Unexpected? | Observed vs. expected counts; motivating chi-square |
| 8.2 | Setting Up a Chi-Square Goodness of Fit Test | Chi-square distribution; hypotheses; expected counts; conditions |
| 8.3 | Carrying Out a Chi-Square Test for Goodness of Fit | χ² statistic; degrees of freedom; p-value; conclusion in context |
| 8.4 | Expected Counts in Two-Way Tables | Two-way frequency tables; computing expected cell counts |
| 8.5 | Setting Up a Chi-Square Test for Homogeneity or Independence | Choosing homogeneity vs. independence; hypotheses; conditions |
| 8.6 | Carrying Out a Chi-Square Test for Homogeneity or Independence | χ² statistic; p-value; decision and conclusion; full four-step |
| 8.7 | Skills Focus: Selecting an Appropriate Inference Procedure for Categorical Data | Choosing among z- and chi-square procedures; AP exam synthesis |

## Unit 9 — Inference for Quantitative Data: Slopes (6 lessons)

Applies the inference framework to linear regression — confidence intervals and
significance tests for the slope of a population regression model — and closes with a
course-wide procedure-selection synthesis.

| # | Title | Focus |
| --- | --- | --- |
| 9.1 | Introducing Statistics: Do Those Points Align? | Revisiting scatterplots and the LSRL; sampling variability of slope |
| 9.2 | Confidence Intervals for the Slope of a Regression Model | t-interval for slope; SE of β̂₁; conditions; interpretation |
| 9.3 | Justifying a Claim About the Slope of a Regression Model Based on a Confidence Interval | Using a CI to support or refute a claim; four-step write-up |
| 9.4 | Setting Up a Test for the Slope of a Regression Model | Hypotheses; t-statistic for slope; conditions for inference on slope |
| 9.5 | Carrying Out a Test for the Slope of a Regression Model | Computing *t* and the p-value; decision; conclusion; full four-step |
| 9.6 | Skills Focus: Selecting an Appropriate Inference Procedure | Choosing among all CI and test procedures; AP exam synthesis |

---

## Repository structure

Every lesson lives in `unitXX/lessonYY/` with the plan at `main.tex` and one
subdirectory per component: `cover`, `warmup`/`_key`, `notes`/`_key`,
`activity`/`_key`, `exit_ticket`/`_key`, `homework`/`_key`, `slides`. Units add
`unit_cover/`, `binder_cover/`, and `sample_test`/`sample_test_key`.

## Gaps found while compiling this outline

- **Slide decks exist for 24 of 80 lessons.** All of Unit 1 and Unit 3 have `slides/`;
  Unit 2 is missing 2.5, 2.8, and 2.9. Units 4–9 have no `slides/` directory at all
  (56 lessons).
- **Unit 4 has no `sample_test` / `sample_test_key`** — the only unit without one.
- **Title drift between lesson plans and unit covers** in three places; the cover text is
  used above:
  - 1.10 — cover: "The Normal Distribution and z-Scores"; plan: "The Normal Distribution"
  - 7.1 — cover: "Should I Worry About Error?"; plan: "Why Should I Worry About Error?"
  - 8.2 — cover: "Setting Up a Chi-Square Goodness of Fit Test"; plan: "Setting Up a
    Chi-Square Test for Goodness of Fit"
- **Unit 5 lesson plans 5.3–5.8 do not define `\LessonNumberName`** (they use
  `\pageheader` only), so their titles come from the unit cover rather than the plan.
