# Container Scanning Reference

Use this reference from Docker and CI skills. Resolve current supported action
versions before use and pin each action to a release or commit SHA.

## Local Image Scan

```bash
trivy image --severity HIGH,CRITICAL IMAGE:TAG
```

## GitHub Actions Shape

```yaml
container-scan:
  runs-on: ubuntu-latest
  timeout-minutes: 15
  steps:
    - uses: actions/checkout@<verified-release-or-sha>
    - name: Build image
      run: docker build -t app:${{ github.sha }} .
    - name: Scan image
      uses: aquasecurity/trivy-action@<verified-release-or-sha>
      with:
        image-ref: app:${{ github.sha }}
        format: sarif
        output: trivy-results.sarif
        severity: HIGH,CRITICAL
    - name: Upload scan
      uses: github/codeql-action/upload-sarif@<verified-release-or-sha>
      with:
        sarif_file: trivy-results.sarif
```

Do not copy an old action reference without verifying that the release is still
supported. Report findings and define the release policy for accepted risk.
