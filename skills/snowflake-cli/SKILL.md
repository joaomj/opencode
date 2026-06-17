---
name: snowflake-cli
description: >
  Execute SQL, manage Snowflake objects (warehouses, stages, tables, etc.), deploy
  Streamlit/Snowpark/dbt projects, and orchestrate data pipelines using the Snowflake CLI
  (`snow`). Use this skill when you need to run SQL scripts, manage stages, deploy dbt
  project objects, create Snowpark UDFs/procedures, manage Cortex AI, or automate Snowflake
  operations from CI/CD pipelines.
---

# Snowflake CLI (`snow`)

Execute SQL, manage Snowflake objects, deploy applications (Streamlit, Snowpark, dbt), and
automate data pipelines using the official Snowflake CLI.

## Quick Reference

```bash
# Test connection
snow connection test -c <connection>

# Execute SQL
snow sql -q "SELECT CURRENT_USER()" -c <connection>
snow sql -f script.sql -c <connection>

# Stage operations
snow stage copy ./file.sql @my_stage/ -c <connection>
snow stage execute @my_stage/script.sql -c <connection> -D var=value

# Streamlit
snow streamlit deploy --replace -c <connection>

# Snowpark
snow snowpark build && snow snowpark deploy --replace -c <connection>

# dbt project management
snow dbt deploy <project_name> --source /path/to/dbt --profiles-dir ~/.dbt/
snow dbt execute <project_name> build
snow dbt execute <project_name> test
snow dbt list
snow dbt describe <project_name>
snow dbt drop <project_name>

# Object management
snow object list warehouse -c <connection>
snow object create warehouse my_wh --size SMALL -c <connection>

# Cortex AI
snow cortex search <query> -c <connection>

# Notebooks
snow notebook execute <notebook_path> -c <connection>
```

## Connection

All commands take `-c` or `--connection` to specify a named connection profile.

```bash
snow sql -c default -q "SELECT 1"
snow sql -c prod -q "SELECT 1"
```

Configure profiles in `~/.snowflake/connections.toml`:

```toml
[default]
account = "my_account"
user = "my_user"
password = "my_password"
role = "ACCOUNTADMIN"
warehouse = "COMPUTE_WH"
database = "MY_DB"
schema = "PUBLIC"
```

## SQL Execution

```bash
# Inline query
snow sql -q "SELECT * FROM my_table" -c default

# Execute SQL file
snow sql -f queries/transform.sql -c default

# Multi-statement
snow sql -q "CREATE TABLE t (c INT); INSERT INTO t VALUES (1); SELECT * FROM t" -c default

# Single transaction (all-or-nothing)
snow sql -q "INSERT INTO t VALUES (1); INSERT INTO t VALUES (2)" --single-transaction

# Async execution (end with ;>)
snow sql -q "SELECT * FROM large_table;>" -c default

# Interactive mode
snow sql -c default
```

## Variables & Templating

Three syntaxes are available:

| Syntax | Scope | Default | Example |
|--------|-------|---------|---------|
| `<% var %>` | `snow sql` inline | Yes | `snow sql -D db=PROD -q "USE <% db %>"` |
| `{{ var }}` | `snow stage execute` | Jinja | `snow stage execute @s/script.sql -D var=val` |
| `${VAR}` | Shell expansion | Always | `DB=PROD snow sql -q "USE ${DB}"` |

```bash
# Standard syntax (default)
snow sql -c default -D db=PROD -D schema=SALES -q "SELECT * FROM <% db %>.<% schema %>.orders"

# Jinja (enable explicitly for inline)
snow sql --enable-templating JINJA -c default -D table=orders -q "SELECT * FROM {{ table }}"

# All syntaxes
snow sql --enable-templating ALL -c default -D var=val -q "SELECT <% var %>, {{ var }}"

# Disable templating (e.g. if SQL contains <% literal text >)
snow sql --enable-templating NONE -c default -q "SELECT '<% literal %>'"
```

### Heredoc pattern (multi-line SQL)

```bash
DB="PROD_DB"
SCHEMA="SALES"
CONN="default"

snow sql -i -c ${CONN} -D db=$DB -D schema=$SCHEMA <<EOF
CREATE OR REPLACE VIEW <% db %>.<% schema %>.daily_metrics AS
SELECT
  date,
  COUNT(*) AS row_count,
  SUM(revenue) AS total_revenue
FROM <% db %>.<% schema %>.transactions
WHERE date >= CURRENT_DATE - 30
GROUP BY date;

GRANT SELECT ON VIEW <% db %>.<% schema %>.daily_metrics TO ROLE ANALYST;
EOF
```

## Stage Operations

```bash
# Create
snow stage create my_stage -c default

# Upload
snow stage copy ./script.sql @my_stage/scripts/ -c default
snow stage copy "./data/*.csv" @my_stage/raw/ -c default

# Download
snow stage copy @my_stage/output/report.csv ./downloads/ -c default

# List
snow stage list-files @my_stage -c default

# Execute SQL from stage (uses Jinja {{ }} automatically)
snow stage execute @my_stage/transform.sql -c default -D table=RAW_DATA

# Execute Python from stage
snow stage execute @my_stage/etl.py -c default -D env=prod

# Remove
snow stage remove my_stage old_file.sql -c default
```

## Object Management

```bash
# List
snow object list warehouse -c default
snow object list table --in database MY_DB --in schema PUBLIC -c default
snow object list function -c default
snow object list procedure -c default

# Describe
snow object describe table MY_TABLE -c default
snow object describe function my_function() -c default

# Create
snow object create warehouse my_wh --size SMALL --auto-suspend 300 -c default
snow object create database my_db -c default

# Drop
snow object drop table MY_TABLE -c default
```

## dbt Integration (`snow dbt`)

Manage dbt project objects natively in Snowflake — no dbt Core/Runner required.

### Deploy a dbt project

The project must contain `dbt_project.yml` and `profiles.yml`:

```bash
# Basic deploy
snow dbt deploy jaffle_shop --source ./dbt/jaffle_shop --profiles-dir ~/.dbt/

# Force create/replace a new version
snow dbt deploy jaffle_shop --source ./dbt --profiles-dir . --force

# Specify dbt version and external access integrations
snow dbt deploy jaffle_shop --source ./dbt \
  --profiles-dir . \
  --dbt-version 1.10.15 \
  --external-access-integration github-integration \
  --force
```

### Execute dbt commands

```bash
# Run models
snow dbt execute jaffle_shop run -c default

# Run tests
snow dbt execute jaffle_shop test -c default

# Build (run + test)
snow dbt execute jaffle_shop build -c default

# Compile only
snow dbt execute jaffle_shop compile -c default

# Install dependencies
snow dbt execute jaffle_shop deps -c default

# List models
snow dbt execute jaffle_shop list -c default

# Run specific models / selectors
snow dbt execute jaffle_shop run --select tag:daily -c default

# Async execution
snow dbt execute --run-async jaffle_shop run --select tag:nightly -c default

# Specify dbt version per execution
snow dbt execute jaffle_shop run --dbt-version '1.9.4' -c default
```

### Lifecycle

```bash
snow dbt list --like JAFFLE% --in database PRODUCT -c default
snow dbt describe jaffle_shop -c default
snow dbt drop jaffle_shop -c default
```

### CI/CD example

```yaml
- name: Deploy and run dbt
  run: |
    snow dbt deploy product_pipeline --source . --profiles-dir . --force
    snow dbt execute product_pipeline run
    snow dbt execute product_pipeline test
```

## Semantic Layer Patterns (dbt + Snowflake)

When building a semantic layer with dbt on Snowflake, common workflows include:

```bash
# Deploy semantic models as dbt project
snow dbt deploy semantic_layer --source ./semantic/ --profiles-dir . --force

# Build dimension and fact tables
snow dbt execute semantic_layer run --select tag:core -c default

# Build metrics layer
snow dbt execute semantic_layer run --select tag:metrics -c default

# Test data quality constraints
snow dbt execute semantic_layer test --select tag:unique -c default

# Deploy views for consumption tools
snow sql -f deploy_consumer_views.sql -c default
```

Typical semantic layer structure under version control:

```
semantic/
├── dbt_project.yml
├── profiles.yml
├── models/
│   ├── core/          # dimensions, facts
│   ├── metrics/       # aggregated metric tables
│   └── exports/       # views for BI tools
├── tests/
│   ├── generic/       # not_null, unique, relationships
│   └── singular/      # custom data quality checks
└── snapshots/         # Type-2 slowly changing dimensions
```

## Streamlit

```bash
# Deploy a Streamlit app from current directory
snow streamlit deploy --replace -c default

# List deployed apps
snow streamlit list -c default

# Get app URL
snow streamlit get-url my_app -c default
```

## Snowpark (UDFs / Stored Procedures)

```bash
# Init a new Snowpark project
snow init my_project --template example_snowpark

# Build the project zip
snow snowpark build -c default

# Deploy functions/procedures defined in snowflake.yml
snow snowpark deploy --replace -c default

# Execute a deployed procedure
snow snowpark execute my_procedure('arg1') -c default

# Upload external packages from Anaconda/PyPi
snow snowpark package upload numpy -c default
```

## Cortex AI

```bash
# Search
snow cortex search "how to calculate month-over-month growth" -c default

# Complete (LLM)
snow cortex complete -m snowflake-arctic -p "Write SQL to..." -c default
```

## Notebooks

```bash
# Execute a notebook
snow notebook execute @my_stage/notebooks/analysis.ipynb -c default
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Insufficient privileges` | Grant `USAGE` on stage/warehouse to the role used in the connection profile |
| Variables not substituted | Ensure correct syntax: `<% %>` for inline, `{{ }}` for stage execute |
| `snow: command not found` | Install via `pip install snowflake-cli-labs` or `brew install snowflake-cli` |
| Connection error | Run `snow connection test -c default` to diagnose |
| `$$` interpreted by shell | Escape as `\$\$` or use `-f` flag with file containing `$$` |
| `profiles.yml` contains password | Remove password from `profiles.yml` for dbt deploy (uses CLI connection instead) |

## Best Practices

- **Use bash variables for environment selection**, `<% %>` for SQL templating
- **Always use `--single-transaction`** for multi-statement migrations (all-or-nothing)
- **Keep `profiles.yml` free of passwords** when using `snow dbt deploy` (it inherits the CLI connection)
- **Version control** `snowflake.yml` project definition files
- **Test with `--silent`** flag for cleaner CI output
- **Use `--run-async`** for long-running dbt jobs in CI
- **Name stages meaningfully** (e.g. `@semantic_layer.staging`, `@analytics.consumer`)
- **Glob patterns** for stage copy/execute support selecting file subsets

## References

- [Snowflake CLI Documentation](https://docs.snowflake.com/en/developer-guide/snowflake-cli/index)
- [Command Reference](https://docs.snowflake.com/en/developer-guide/snowflake-cli/command-reference/overview)
- [dbt on Snowflake](https://docs.getdbt.com/docs/core/connect-data-platform/snowflake-setup)
