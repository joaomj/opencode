# ML Reference Recipes

Use only the recipe that answers the current implementation question. Keep the
main skill focused on experiment decisions and evaluation quality.

## Pipelines

Use one pipeline for learned preprocessing and the estimator. Fit it only on
training data. Apply the fitted pipeline to validation and test data without
refitting.

## Splits

- Use chronological splits for time-dependent data.
- Use stratification when class proportions must be preserved.
- Keep a final test set outside model selection.

## Tracking

Track parameters, metrics, artifacts, data identifiers, source revision, and
environment versions in the existing experiment system.

## Deterministic Training

Record seeds for the language runtime, numerical libraries, model framework,
data loader, and CUDA when applicable. Report when the framework cannot provide
full determinism.

## Large Data

Use lazy scans, streaming batches, bounded memory, and explicit data ordering.
Measure the result before adding workers or persistent caches.

## Checkpoints

Write checkpoints to a temporary path, flush them, and atomically move them to
the final path. Include model, optimizer, step, configuration, and random state
when recovery requires them.

## Training Logs

Use structured records with step, epoch, loss, learning rate, resource usage,
timestamp, and run identifier. Do not log data, credentials, or sensitive
features.
