---
name: ml-best-practices
description: Complete ML development guide using risk-based preparation and CRISP-DM. Covers data quality, evaluation, MLflow, hypothesis testing, and experiment reporting. Use when the user asks for ML work: data analysis, experiments, model training, or hypothesis testing.
license: MIT
---

# Machine Learning Best Practices

Comprehensive guide for ML development with focus on reproducibility, data quality, and proper evaluation. Use a specification when the business question, data contract, or evaluation protocol is unclear. Do not require a specification for every small experiment. TDD does not apply to ML work; evaluation rigor replaces it.

## Non-Negotiable Rules (STOP if violated)

Core rules defined in AGENTS.md. ML-specific additions:

| Rule | Violation = STOP |
|------|-----------------|
| Test set touched ONCE only | Block if multiple accesses |
| Preprocessing in Pipeline | Block if done manually |
| Confusion matrix generated | Block if missing |
| Baseline comparison done | Block if missing |

## CRISP-DM Framework

### Phase 1: Business Understanding
Document in `tech-context.md` using STAR format:

**Situation:**
- What business problem are we solving?
- What are the constraints (time, resources, data)?

**Task:**
- What is the ML objective?
- What are success metrics?
- What is the baseline performance?

**Action:**
- What data sources are available?
- What features are likely relevant?
- What evaluation approach will be used?

**Result:**
- What was the initial baseline performance?
- What are the key challenges identified?

### Phase 2: Data Understanding
Document in `tech-context.md` using STAR format:

**Situation:**
- What is the data volume and structure?
- What are the data quality issues?

**Task:**
- What EDA will be performed?
- What are the key insights from data?

**Action:**
- Exploratory data analysis
- Data quality assessment
- Feature distribution analysis

**Result:**
- Data quality report
- Initial feature selection
- Identified patterns/outliers

### Phase 3: Data Preparation
Document in `tech-context.md` using STAR format:

**Situation:**
- What preprocessing is needed?
- What are the data issues to fix?

**Task:**
- How will we handle missing values?
- How will we encode features?
- How will we split data?

**Action:**
- Feature engineering
- Handling missing values
- Feature encoding/scaling
- Train/validation/test split (test set untouched)

**Result:**
- Final feature set
- Preprocessing pipeline defined
- Data split completed

### Phase 4: Modeling
Document in `tech-context.md` using STAR format:

**Situation:**
- What modeling techniques will be used?
- What are the model constraints?

**Task:**
- What models will be tried?
- What hyperparameters will be tuned?

**Action:**
- Model training
- Hyperparameter tuning
- Cross-validation
- Model selection

**Result:**
- Best performing model
- Model performance metrics
- Feature importance analysis

### Phase 5: Evaluation
Document in `tech-context.md` using STAR format:

**Situation:**
- How will model be evaluated?
- What are the evaluation criteria?

**Task:**
- What metrics will be used?
- How does it compare to baseline?

**Action:**
- Evaluate on test set (ONCE only)
- Generate confusion matrix
- Compare to baseline
- Error analysis

**Result:**
- Final model performance
- Confusion matrix analysis
- Comparison to baseline
- Deployment recommendation

### Phase 6: Deployment
Document in `tech-context.md` using STAR format:

**Situation:**
- What are deployment constraints?
- What infrastructure is available?

**Task:**
- How will model be deployed?
- What monitoring will be in place?

**Action:**
- Model serialization
- Deployment pipeline setup
- Monitoring configuration

**Result:**
- Model deployed
- Monitoring active
- Performance tracking started

## Data Quality Rules

### Test Set Rule (CRITICAL)
```python
# BAD - touching test set multiple times
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# First use
model.fit(X_train, y_train)
score1 = model.score(X_test, y_test)

# Modify model based on test set results
model2 = ImprovedModel()
model2.fit(X_train, y_train)

# SECOND use - FORBIDDEN
score2 = model2.score(X_test, y_test)

# GOOD - use validation set for tuning
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5)

# Tune on validation set
model1.fit(X_train, y_train)
score1_val = model1.score(X_val, y_val)

# Tune based on validation results
model2 = ImprovedModel()
model2.fit(X_train, y_train)
score2_val = model2.score(X_val, y_val)

# Evaluate final model on test set ONCE
final_model.fit(np.vstack([X_train, X_val]), np.vstack([y_train, y_val]))
final_score = final_model.score(X_test, y_test)  # ONE time only
```

### Data Leakage Prevention
```python
# BAD - manual preprocessing causes leakage
X_train_scaled = StandardScaler().fit_transform(X_train)
X_test_scaled = StandardScaler().fit_transform(X_test)  # LEAKAGE!

# GOOD - use Pipeline
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression())
])

pipeline.fit(X_train, y_train)
pipeline.predict(X_test)  # No leakage
```

### Preprocessing in Pipeline (REQUIRED)
```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# Define preprocessing
numeric_features = ['age', 'income']
categorical_features = ['education', 'occupation']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ]), numeric_features),
        ('cat', Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('encoder', OneHotEncoder(handle_unknown='ignore'))
        ]), categorical_features)
    ]
)

# Create full pipeline
pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('model', RandomForestClassifier())
])

# Fit and predict (no leakage)
pipeline.fit(X_train, y_train)
predictions = pipeline.predict(X_test)
```

## Evaluation Requirements

### Confusion Matrix (REQUIRED)
```python
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt

# Generate confusion matrix
y_pred = model.predict(X_test)
cm = confusion_matrix(y_test, y_pred)

# Display confusion matrix
print(classification_report(y_test, y_pred))

# Visualize
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.savefig('confusion_matrix.png')
```

### Baseline Comparison (REQUIRED)
```python
from sklearn.dummy import DummyClassifier

# Create baseline
baseline = DummyClassifier(strategy='most_frequent')
baseline.fit(X_train, y_train)
baseline_score = baseline.score(X_test, y_test)

# Train model
model.fit(X_train, y_train)
model_score = model.score(X_test, y_test)

# Compare
print(f"Baseline accuracy: {baseline_score:.3f}")
print(f"Model accuracy: {model_score:.3f}")
print(f"Improvement: {model_score - baseline_score:.3f}")
```

### Cross-Validation
```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
print(f"CV scores: {scores}")
print(f"Mean CV score: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")
```

## Feature Importance

### Tree-Based Models
```python
import pandas as pd

# Get feature importance
importance = model.named_steps['model'].feature_importances_
feature_names = model.named_steps['preprocessor'].get_feature_names_out()

# Create DataFrame
importance_df = pd.DataFrame({
    'feature': feature_names,
    'importance': importance
}).sort_values('importance', ascending=False)

# Plot
plt.figure(figsize=(12, 8))
sns.barplot(x='importance', y='feature', data=importance_df.head(20))
plt.title('Top 20 Feature Importances')
plt.savefig('feature_importance.png')
```

### Permutation Importance
```python
from sklearn.inspection import permutation_importance

result = permutation_importance(
    model, X_test, y_test, n_repeats=10, random_state=42
)

importance_df = pd.DataFrame({
    'feature': X.columns,
    'importance': result.importances_mean
}).sort_values('importance', ascending=False)

print(importance_df)
```

## MLflow Tracking

### Setup
```bash
uv add mlflow
uv run mlflow ui
```

### Logging Experiments
```python
import mlflow
from sklearn.metrics import accuracy_score, precision_score, recall_score

with mlflow.start_run():
    # Log parameters
    mlflow.log_param("model_type", "RandomForest")
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 10)

    # Train model
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    # Log metrics
    mlflow.log_metric("accuracy", accuracy_score(y_test, predictions))
    mlflow.log_metric("precision", precision_score(y_test, predictions, average='weighted'))
    mlflow.log_metric("recall", recall_score(y_test, predictions, average='weighted'))

    # Log model
    mlflow.sklearn.log_model(model, "model")

    # Log artifacts
    mlflow.log_artifact("confusion_matrix.png")
    mlflow.log_artifact("feature_importance.png")
```

### Model Registry
```python
# Register model
mlflow.register_model(
    "runs:/<run-id>/model",
    "production_model"
)

# Load model
import mlflow.sklearn
model = mlflow.sklearn.load_model("models:/production_model/latest")
```

## Data Splitting

### Time Series Split
```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)
for train_idx, test_idx in tscv.split(X):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    # Train and evaluate
```

### Stratified Split
```python
from sklearn.model_selection import StratifiedKFold

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for train_idx, test_idx in skf.split(X, y):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    # Train and evaluate
```

## Reproducibility

### Set Random Seeds
```python
import numpy as np
import random

np.random.seed(42)
random.seed(42)
```

### Log Environment
```python
import mlflow

with mlflow.start_run():
    mlflow.log_params({
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "numpy_version": np.__version__,
        "sklearn_version": sklearn.__version__,
    })
```

## Hypothesis Testing

Apply statistical rigor before modeling:

- Explicit statistical tests with p-values and effect sizes
- Validate assumptions (normality, homogeneity, independence)
- Compare against baseline with paired tests (bootstrap, permutation, paired t-test)
- Correction for multiple comparisons (Bonferroni, FDR, Benjamini-Hochberg)
- Power analysis for sample size adequacy
- Document methodology for the experiment report

**Gate**: If no signal detected or assumptions are violated, escalate to user with findings.

## Feasibility Gates

Each CRISP-DM phase produces a verdict:

| Phase | Verdict |
|-------|---------|
| Data understanding | `feasible` / `partial` / `infeasible` |
| Hypothesis testing | `signal detected` / `no signal` / `assumptions violated` |
| Baseline | Baseline metrics recorded as reference |
| Modeling | Best candidate selected vs baseline |

If `infeasible` or significant data quality concerns, escalate to user. If `partial`, present caveats and let user decide.

## Experiment Report

Write an experiment report in academic format:

- **Executive Summary**: key findings, 1 paragraph
- **Introduction**: business question and context
- **Methodology**: data description, hypothesis tests, model architectures, evaluation protocol
- **Results**: metrics, statistical comparisons, tables and plots
- **Discussion**: interpretation, tradeoffs, limitations, caveats
- **Conclusions**: takeaway and next steps

## Patterns

These patterns extend the reproducibility baseline above and cover common deep learning and data-science scenarios.

### Deterministic Training (PyTorch)

```python
import os, random, numpy as np, torch

def lock_reproducibility(seed: int = 42) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":16:8"
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True, warn_only=True)
```

### Memory-Efficient DataFrames

For datasets larger than RAM, use lazy API + streaming:

```python
import polars as pl

result = (
    pl.scan_csv("large.csv")
    .filter(pl.col("label") == 1)
    .with_columns(pl.col("feature") * 2)
    .group_by("category")
    .agg(pl.col("feature").sum())
    .collect(engine="streaming")
)
```

### Streaming Data Loading

Stream batches from disk when dataset exceeds memory:

```python
from torch.utils.data import IterableDataset, DataLoader

class StreamingParquetDataset(IterableDataset):
    def __init__(self, path: str, batch_size: int = 1024) -> None:
        self.path = path
        self.batch_size = batch_size

    def __iter__(self):
        for batch in pl.scan_parquet(self.path).iter_slices(self.batch_size):
            yield {
                "input_ids": batch["text"].to_list(),
                "labels": batch["label"].to_numpy(),
            }

loader = DataLoader(
    StreamingParquetDataset("data/"),
    batch_size=None,
    num_workers=4,
    persistent_workers=True,
    pin_memory=True,
)
```

### Gradient Accumulation

When GPU can't fit target batch size, accumulate gradients:

```python
accumulation_steps = 4  # effective batch = batch_size * 4

for i, batch in enumerate(loader):
    loss = model(batch).loss / accumulation_steps
    loss.backward()

    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

### Atomic Checkpointing

Atomic writes prevent corrupt checkpoints on crash:

```python
import shutil
from pathlib import Path
import torch

def save_checkpoint(step, model, optimizer, path: Path) -> None:
    checkpoint = {
        "step": step,
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "rng": get_rng_state(),
    }
    temp = path / f".ckpt-{step}.pt"
    final = path / f"ckpt-{step}.pt"
    torch.save(checkpoint, temp)
    shutil.move(str(temp), str(final))  # atomic on POSIX
```

### Structured Logging

One structured line per training step:

```python
import structlog, time
logger = structlog.get_logger()

logger.info(
    "training_step",
    step=step,
    epoch=epoch,
    loss=round(loss, 6),
    lr=lr,
    gpu_mb=round(torch.cuda.memory_allocated() / 1e6, 2),
    timestamp=time.time(),
)
```

## Reference Repositories

| Domain | Repository | Study |
|--------|-----------|-------|
| Training loops | `Lightning-AI/pytorch-lightning` | `Trainer`, callbacks, `ModelCheckpoint` |
| Seed/determinism | `huggingface/transformers` | `trainer_utils.py:set_seed()` |
| Data loading | `pytorch/pytorch` | `IterableDataset`, `DataLoader` |
| DataFrames | `pola-rs/polars` | Lazy API, streaming |
| Logging | `hynek/structlog` | JSON output, context binding |
| Distributed training | `microsoft/DeepSpeed` | ZeRO sharding, activation checkpointing |

## Completion Checklist

- [ ] All CRISP-DM phases documented in tech-context.md with STAR format
- [ ] Test set accessed only ONCE
- [ ] Preprocessing done in Pipeline (not manual)
- [ ] Confusion matrix generated and saved
- [ ] Baseline model compared
- [ ] Feature importance analysis completed
- [ ] MLflow tracking enabled
- [ ] Random seeds set for reproducibility
- [ ] Cross-validation performed
