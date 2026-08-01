---
name: ml-best-practices
description: Apply risk-based CRISP-DM practices to data analysis, experiments, model training, evaluation, and ML deployment.
---

# Machine Learning Best Practices

Use a specification when the business question, data contract, or evaluation
protocol is unclear. Do not require a specification for every small experiment.
Evaluation rigor replaces ordinary application TDD for ML work.

## Stop Conditions

- The test set is used for tuning or more than one final evaluation.
- Preprocessing leaks information across the train and evaluation boundary.
- No baseline or task-appropriate evaluation metric exists.
- A required quality check fails and the impact is not reported.

## CRISP-DM

Record the decision and evidence for each phase in the repository's experiment
record or `tech-context.md`:

| Phase | Required result |
|---|---|
| Business understanding | Business question, objective, constraints, success metric, and baseline |
| Data understanding | Sources, volume, structure, quality issues, and EDA findings |
| Data preparation | Data contract, feature set, split strategy, and preprocessing pipeline |
| Modeling | Candidate models, tuning protocol, assumptions, and selection reason |
| Evaluation | Test-set result, baseline comparison, error analysis, and limitations |
| Deployment | Serialization, serving path, monitoring, rollback, and ownership |

Stop and escalate when a phase is infeasible, assumptions are violated, or data
quality prevents a reliable conclusion.

## Data Quality

- Split data before fitting learned preprocessing.
- Put imputers, encoders, scalers, and feature selection in a pipeline.
- Use validation data for model selection and reserve the test set for one final
  evaluation.
- Select time-aware or stratified splits when the data requires them.
- Record missingness, outliers, label quality, sampling bias, and leakage risks.

## Evaluation

- Compare every candidate with a simple baseline.
- Select metrics that match the user or business cost of errors.
- Include a confusion matrix and class-level results for classification.
- Use cross-validation on the training data when it supports the task.
- Perform error analysis on representative and high-cost failures.
- Report confidence, uncertainty, data limitations, and deployment caveats.

## Experiments

Record:

- hypothesis and expected effect
- data and split identifiers
- model and preprocessing versions
- parameters and random seeds
- metrics, baseline, and error analysis
- artifacts, environment, and decision

Use MLflow or the repository's existing tracking system when available:

```bash
uv add mlflow
uv run mlflow ui
```

Do not add a tracking system only to satisfy this skill. Use the smallest
reproducible record that supports the decision.

## Statistical Rigor

- State the null hypothesis, alternative, effect size, and significance rule.
- Check assumptions before using a test.
- Correct for multiple comparisons when applicable.
- Use power or uncertainty analysis when sample size affects the decision.
- Distinguish statistical significance from practical value.

## Reproducibility

- Pin dependencies through the repository package workflow.
- Record code, data, model, and environment identifiers.
- Set and record seeds where deterministic behavior is possible.
- Preserve the exact split and evaluation protocol.
- Make checkpoint writes atomic when training can be interrupted.

## Reference Recipes

Read `references/recipes.md` for optional guidance on pipelines, time-series
splits, tracking, deterministic training, streaming data, checkpointing, and
structured training logs. Load those recipes only when the task needs them.

## Completion Checklist

- The business question and success metric are explicit.
- Data quality and leakage risks are recorded.
- The split and preprocessing protocol are reproducible.
- A baseline comparison is complete.
- The test set was used only for the final evaluation.
- Error analysis and limitations are reported.
- The deployment and monitoring decision is explicit.
