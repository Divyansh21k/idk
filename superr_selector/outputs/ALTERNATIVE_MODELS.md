# Alternative Models — SupeRR Selector Season 2, Round 1

This document describes three alternative approaches to ranking pressure performers. These are not proposals to replace the submitted model — they are presented to demonstrate the methodological trade-offs and to benchmark the existing pipeline against simpler and more rigorous alternatives.

---

## Alternative A: Leverage-Weighted Runs Above Par (RAP-L)

### Motivation

The current model has 5 steps, 3 machine-learning components, and multiple hyperparameters (shrinkage, PI threshold, KO weight, pressure slope evaluation point). A sceptical evaluator may ask: does all this complexity actually add predictive value over a simple statistic?

Leverage-weighted RAP is the simplest defensible pressure metric that uses the same underlying WP model but discards the EV model, the shrinkage machinery, and the KO adjustment.

### Definition

For each delivery t where player i acted (batted or bowled):

$$RAP\_L_i = \frac{\displaystyle\sum_{t \in HP_i} L(s_t) \times (r_t - \bar{r}_{s_t})}{\displaystyle\sum_{t \in HP_i} L(s_t)}$$

where:
- $L(s_t)$ = leverage at delivery t (WP sensitivity)
- $r_t$ = actual runs scored on delivery t (from batter perspective) or runs conceded minus expected wicket value (from bowler perspective)
- $\bar{r}_{s_t}$ = empirical mean runs for deliveries in the same game-state bin as t (balls_left_bin, wickets_bin, delivery_kind)
- HP_i = deliveries where PI ≥ 0.80

The state mean $\bar{r}_{s_t}$ is computed empirically from all deliveries in the same state bin — no regression model required.

### Why this is a viable alternative

1. **No in-sample bias:** State means are population quantities, not player-specific fits.
2. **Fully transparent:** Every component is interpretable with no latent variables.
3. **No tuning:** No shrinkage hyperparameters, no PI-threshold beyond the HP eligibility gate.
4. **Identical data requirements:** Uses the same dataset and WP model as the current pipeline.

### Limitations

1. **No shrinkage:** All estimates are sample means — high variance for small samples. A player with 50 HP deliveries has the same weight as one with 500.
2. **No uncertainty quantification built-in:** CIs require bootstrapping (match-cluster) separately.
3. **No pressure slope:** Cannot distinguish players who perform better in higher-PI situations from those who perform evenly across all HP deliveries.
4. **No KO adjustment:** KO performance is pooled with league performance.

### Eligibility

Same criteria as the current model: n_hp ≥ 50, n_hp_matches ≥ 5.

### Implementation effort

**Low.** Roughly 100 lines of Python. Can be implemented in under a day using step1 and step3 outputs.

### When to prefer this

- When the evaluator demands maximum transparency and cannot evaluate a hierarchical model.
- As a sanity check on the current model: if RAP-L top-10 and current top-10 are substantially different, the complexity of the current model is not adding stability.
- As an audit: compute Spearman correlation between current R_overall and RAP-L across all eligible players. High correlation (> 0.80) would suggest the complex model is recovering the same signal as the simple one.

---

## Alternative B: Cross-Fitted Mixed-Effects Win Probability Added (WPA-ME)

### Motivation

The current model's most critical bug is the in-sample EV fit. The most principled fix is to replace the EV model entirely with a cross-fitted Win Probability Added computation — this collapses the EV and WP models into a single, cleaner framework.

### Definition

For each delivery t where player i acted:

$$WPA_t = WP(s_{t+1}) - WP(s_t)$$

where WP is estimated using a **leave-one-match-out cross-fitted** logistic regression model with features:
- `balls_left` (continuous or binned)
- `wickets_lost` (explicit, not embedded in E_remaining)
- `runs_required` (or `run_advantage`)
- `innings`
- `competition_class` (IPL/T20I indicator)
- Interactions: `balls_left × wickets_lost`, `balls_left × runs_required`

For batter i at delivery t: $WPA_{bat,t} = WPA_t$ (positive = batter benefited)  
For bowler i at delivery t: $WPA_{bowl,t} = -WPA_t$ (positive = bowler limited damage)

Player rating:

$$R_i^{WPA} = \frac{\displaystyle\sum_{t \in HP_i} WPA_{i,t}}{\displaystyle\sqrt{n_{HP_i}}}$$

Scaling by $\sqrt{n}$ gives a "per-unit-of-exposure" statistic with comparable variance across players.

For formal inference, fit a linear mixed-effects model:

$$WPA_{i,t} = \mu_i + \theta_i \times (PI_t - \bar{PI}) + \epsilon_{it}$$
$$\mu_i \sim N(\mu_{role}, \sigma^2_{signal})$$
$$\theta_i \sim N(\theta_{role}, \sigma^2_\theta)$$
$$\epsilon_{it} \sim N(0, \sigma^2_e)$$

with match-level random effects for clustering. This is the natural generalisation of the current hierarchical model but with the EV model replaced by cross-fitted WP.

### Advantages over current model

| Issue in current model | Resolution in WPA-ME |
|------------------------|----------------------|
| EV in-sample bias (I-01) | Cross-fitting eliminates this |
| WP underspecified (I-02) | Direct WP model with more features |
| Resource non-monotone (I-04) | Replaced by direct WP — no resource table needed |
| Free-hit EV wrong (I-14) | WP correctly reflects free-hit game state |

### Limitations

1. **Harder to implement:** Cross-fitting requires running N_matches separate WP model fits or using a computationally efficient approximation (influence-function correction).
2. **WPA is noisier than RAP:** WP model errors compound into WPA values. If the WP model is miscalibrated, WPA is miscalibrated.
3. **WPA cannot decompose by delivery type:** Cannot easily separate "batter scored runs" from "batter survived wicket" contributions.
4. **Requires larger N for stable mixed-effects fit.**

### Implementation effort

**Moderate.** ~300–400 lines of Python. The key new component is cross-fitted WP estimation. With scikit-learn's cross_val_predict this can be done in ~50 lines. The mixed-effects model can be fit with `statsmodels.MixedLM`.

### When to prefer this

- If the competition requires the highest practical statistical rigour with achievable implementation effort.
- As a replication check: if WPA-ME rankings strongly agree with current R_overall rankings, confidence in the current model increases despite its bugs.
- For future rounds: WPA-ME is the recommended architecture for SupeRR Selector Season 3.

---

## Alternative C: Bayesian Hierarchical WPA with Explicit Pressure Interaction

### Motivation

The current model approximates Bayesian inference via empirical Bayes point estimates. Alternative C completes the Bayesian treatment: full posterior inference over player abilities, explicit pressure-response parameters with informed priors, and uncertainty quantification that propagates from WP estimation through to final rankings.

### Model specification

```
# Hyperpriors
mu_role ~ Normal(0, 2)              # role-level ability prior
sigma_signal ~ HalfNormal(2)        # cross-player ability variance
theta_pop ~ Normal(0, 1)            # population-level pressure slope
sigma_theta ~ HalfNormal(1)         # cross-player slope variance
sigma_e ~ HalfNormal(5)             # within-player delivery noise

# Player-level priors
mu_i ~ Normal(mu_role, sigma_signal)       # player baseline ability
theta_i ~ Normal(theta_pop, sigma_theta)   # player pressure slope

# Likelihood
WPA_{i,t} ~ Normal(mu_i + theta_i × (PI_t - 0.4), sigma_e)
```

Match-level random effects included as:

```
alpha_m ~ Normal(0, sigma_match)    # match effect
WPA_{i,t} ~ Normal(mu_i + theta_i × (PI_t - 0.4) + alpha_m, sigma_e)
```

**Eligibility replaced by CI-width gate:** Only players whose 90% posterior CI half-width < T (e.g. T = 25 R-units) are presented. This is principled and data-adaptive — high-data players automatically pass; low-data players are excluded without an arbitrary delivery count threshold.

**Ranking:** Present posterior expected rank E[rank_i] and P(rank_i ≤ 10) for each eligible player. The "top 10" becomes "players with highest P(rank ≤ 10)" — an honest probabilistic statement.

### Advantages

1. **Full uncertainty propagation:** WP estimation uncertainty, delivery noise, match clustering, and cross-player variance are all propagated to the posterior.
2. **Principled eligibility:** CI-width gate is interpretable and self-calibrating.
3. **No arbitrary thresholds:** Hyperparameters (sigma_signal, sigma_e) estimated from data.
4. **Model checking built-in:** Posterior predictive checks validate the generative model.
5. **Coherent ranking:** Probabilistic ranking is more honest and defensible than a point-estimate leaderboard.

### Limitations

1. **Significant implementation effort:** Stan or PyMC model; MCMC sampling with convergence diagnostics. Realistic timeline: 2–3 weeks including testing.
2. **Communicating uncertainty is harder:** "P(rank ≤ 10) = 0.58" is less dramatic than "rank 1." Some competitions may not accept probabilistic rankings.
3. **WP estimation uncertainty not propagated:** Even this model treats WP values as fixed inputs. Fully propagating WP uncertainty would require a hierarchical WP model, adding further complexity.
4. **Requires MCMC diagnostics:** Rhat, effective sample size, trace plots — these must be validated before results are trusted.

### Implementation effort

**High.** Stan/PyMC model: ~100 lines. Full pipeline integration: ~400 additional lines. Total: 2–3 weeks including validation.

### When to prefer this

- If the competition accepts and rewards probabilistic output.
- For academic publication of the methodology.
- For SupeRR Selector Season 3+ if the pipeline is maintained long-term.

---

## Summary Comparison

| Criterion | Current Model | RAP-L (A) | WPA-ME (B) | Bayesian (C) |
|-----------|-------------|-----------|-------------|--------------|
| In-sample bias | YES (critical) | Minimal | No | No |
| WP quality | Marginal (Brier 0.19) | Same WP | Improved | Improved |
| Shrinkage quality | EB point estimate | None | REML | Full posterior |
| Uncertainty quantification | Bootstrap CI | Bootstrap CI | REML CI | Full posterior |
| Eligibility mechanism | Delivery count | Delivery count | Delivery count | CI-width gate |
| Transparency | Moderate | High | Moderate | Lower |
| Implementation | Done | Simple (1 day) | Moderate (1 week) | Complex (3 weeks) |
| Validation coverage | Partial | Partial | Strong | Strongest |
| Competition readiness | Now | Now | 1 week | 3+ weeks |

**Recommendation for immediate use:** RAP-L as a parallel sanity check on the current rankings.  
**Recommendation for future rounds:** WPA-ME as the production architecture.  
**Recommendation for research publication:** Bayesian hierarchical WPA.
