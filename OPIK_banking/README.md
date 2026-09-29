# Path Coverage Module

This project provides a practical implementation of path-oriented test analysis for Python programs.
It was prepared as a final-year software verification and validation artifact and is designed to work
both as:

- a reusable Python module
- a command-line tool
- a Streamlit application for presentation purposes

## What It Does

The module performs:

- static extraction of branch targets from a Python module
- lightweight instrumentation of decision points
- execution of pytest suites against the instrumented module
- calculation of branch-target coverage percentages
- comparison of baseline and path-focused test suites
- optional LLM-based test generation evaluation
- generation of Markdown and JSON reports

In this project, path coverage is operationalized as exercising the true and false outcomes of
identified decision points and verifying the behavior with pytest assertions.

## Project Structure

- `path_coverage_module/` : reusable implementation
- `banking.py` : banking system under test
- `program.py` : compact validation demo under test
- `ecommerce.py` : e-commerce decision-logic demo under test
- `access_control.py` : access-control and session-risk demo under test
- `insurance.py` : insurance underwriting and claims-processing demo under test
- `test_banking.py` : baseline test suite
- `test_banking_path_reference.py` : path-focused reference suite
- `test_program.py` : baseline suite for `program.py`
- `test_program_path_reference.py` : path-focused reference suite for `program.py`
- `test_ecommerce.py` : baseline suite for `ecommerce.py`
- `test_ecommerce_path_reference.py` : path-focused reference suite for `ecommerce.py`
- `test_access_control.py` : baseline suite for `access_control.py`
- `test_access_control_path_reference.py` : path-focused reference suite for `access_control.py`
- `test_insurance.py` : baseline suite for `insurance.py`
- `test_insurance_path_reference.py` : path-focused reference suite for `insurance.py`
- `demo_app.py` : Streamlit interface
- `run_demo.py` : simple command-line demonstration script
- `llm_path_prompt.txt` : reusable prompt for LLM-based path-test generation

## Command-Line Usage

Run the module directly:

```powershell
& "C:\Users\hamza\.conda\envs\mutpy310\python.exe" -m path_coverage_module.cli `
  --python "C:\Users\hamza\.conda\envs\mutpy310\python.exe" `
  --module "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\banking.py" `
  --suite baseline="C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\test_banking.py" `
  --suite reference="C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\test_banking_path_reference.py" `
  --report-md "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\path_report.md"
```

## Current Verified Result

Using the supplied banking example:

- baseline suite coverage: `67.1%` (`47/70`)
- reference path suite coverage: `100.0%` (`70/70`)

## LLM Evaluation Workflow

The project also supports evaluation of the underlying LLM with respect to:

- number of generated test cases
- syntactic correctness
- executable correctness under pytest
- achieved path coverage

Supported LLM providers:

- `ollama` for local models
- `openrouter` for hosted multi-model access using `OPENROUTER_API_KEY`

Recommended models for final comparison:

- `ollama`: `qwen2.5-coder:7b`
- `openrouter`: `openai/gpt-4.1-mini`

The Streamlit app can now compare `baseline vs ollama vs openrouter` side by side from the `LLM Evaluation` tab, and it can switch between multiple modules under test:

- banking
- program
- ecommerce
- access_control
- insurance

You can either:

- enter the API key in the Streamlit sidebar, or
- set it in your shell before running the CLI

Example environment setup in Anaconda Prompt:

```powershell
set OPENROUTER_API_KEY=your_openrouter_key_here
```

Example command:

```powershell
& "C:\Users\hamza\.conda\envs\mutpy310\python.exe" -m path_coverage_module.cli `
  --python "C:\Users\hamza\.conda\envs\mutpy310\python.exe" `
  --module "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\banking.py" `
  --suite baseline="C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\test_banking.py" `
  --suite reference="C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\test_banking_path_reference.py" `
  --llm-provider "ollama" `
  --llm-model "qwen2.5-coder:7b" `
  --llm-prompt-file "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\llm_path_prompt.txt" `
  --llm-output-tests "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\generated_llm_path_tests.py" `
  --llm-include-baseline `
  --report-md "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\path_report_with_llm.md" `
  --report-json "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\path_report_with_llm.json"
```

OpenRouter example:

```powershell
& "C:\Users\hamza\.conda\envs\mutpy310\python.exe" -m path_coverage_module.cli `
  --python "C:\Users\hamza\.conda\envs\mutpy310\python.exe" `
  --module "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\banking.py" `
  --suite baseline="C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\test_banking.py" `
  --suite reference="C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\test_banking_path_reference.py" `
  --llm-provider "openrouter" `
  --llm-model "openai/gpt-4.1-mini" `
  --llm-prompt-file "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\llm_path_prompt.txt" `
  --llm-output-tests "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\generated_llm_path_tests_openrouter.py" `
  --llm-include-baseline `
  --llm-timeout-seconds 30 `
  --llm-min-tests 6 `
  --report-md "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\path_report_with_llm_openrouter.md"
```

This command evaluates three suites:

- baseline
- reference path suite
- LLM-generated suite

You can also swap the analyzed module. For example, the smaller `program.py` demo can be run with:

```powershell
& "C:\Users\hamza\.conda\envs\mutpy310\python.exe" -m path_coverage_module.cli `
  --python "C:\Users\hamza\.conda\envs\mutpy310\python.exe" `
  --module "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\program.py" `
  --suite baseline="C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\test_program.py" `
  --suite reference="C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\test_program_path_reference.py" `
  --report-md "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\path_report_program.md"
```

The generated report includes explicit LLM metrics so the project can address the requirement of
evaluating LLM performance with respect to correctness and number of generated test cases.

For a faster run, use:

```powershell
& "C:\Users\hamza\.conda\envs\mutpy310\python.exe" -m path_coverage_module.cli `
  --python "C:\Users\hamza\.conda\envs\mutpy310\python.exe" `
  --module "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\banking.py" `
  --suite baseline="C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\test_banking.py" `
  --llm-provider "ollama" `
  --llm-model "llama3.2:1b" `
  --llm-prompt-file "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\llm_path_prompt.txt" `
  --llm-output-tests "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\generated_llm_path_tests_fast.py" `
  --llm-timeout-seconds 45 `
  --llm-fast-mode `
  --report-md "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\path_report_with_llm_fast.md"
```

This faster mode:

- uses a smaller local model
- skips the repair pass
- enforces timeouts so the workflow still produces visible results

For a stronger final-quality LLM run, use:

```powershell
& "C:\Users\hamza\.conda\envs\mutpy310\python.exe" -m path_coverage_module.cli `
  --python "C:\Users\hamza\.conda\envs\mutpy310\python.exe" `
  --module "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\banking.py" `
  --suite baseline="C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\test_banking.py" `
  --suite reference="C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\test_banking_path_reference.py" `
  --llm-provider "ollama" `
  --llm-model "llama3.2:3b" `
  --llm-prompt-file "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\llm_path_prompt.txt" `
  --llm-output-tests "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\generated_llm_path_tests_quality.py" `
  --llm-include-baseline `
  --llm-timeout-seconds 30 `
  --llm-min-tests 6 `
  --llm-max-attempts 4 `
  --report-md "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\path_report_with_llm_quality.md" `
  --report-json "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\path_report_with_llm_quality.json"
```

This quality mode:

- requires a larger minimum usable test suite
- retries generation if the model returns too few tests
- is better suited for final-report evidence than the ultra-fast mode

## Model Checking Comparison

The project also includes bounded explicit-state model-checking support for all configured modules.
Each module has a representative target function:

- `banking.py` -> `process_withdrawal`
- `program.py` -> `validate_transaction`
- `ecommerce.py` -> `checkout_risk`
- `access_control.py` -> `authorize_transfer`
- `insurance.py` -> `renewal_decision`

Each checker exhaustively explores a finite state space of representative inputs and verifies
safety-style properties for the selected function.

Example command:

```powershell
& "C:\Users\hamza\.conda\envs\mutpy310\python.exe" -m path_coverage_module.cli `
  --python "C:\Users\hamza\.conda\envs\mutpy310\python.exe" `
  --module "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\banking.py" `
  --suite baseline="C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\test_banking.py" `
  --suite reference="C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\test_banking_path_reference.py" `
  --model-check `
  --report-md "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\path_report_with_model_checking.md"
```

This adds a formal-comparison section to the report so the path-analysis results can be compared
against a model-checking tool output.

## Streamlit App

```powershell
& "C:\Users\hamza\.conda\envs\mutpy310\python.exe" -m streamlit run "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\demo_app.py"
```

## Simple Script Demo

```powershell
& "C:\Users\hamza\.conda\envs\mutpy310\python.exe" "C:\Users\hamza\Downloads\Class_work\Software Verification and validation\OPIK_banking\run_demo.py"
```

## Why This Is Suitable For A Final Submission

This artifact does not depend on mutation-testing instability. Instead, it provides:

- a reproducible implementation
- a measurable coverage metric
- a reusable code module
- a clear comparison between baseline and path-focused suites
- a direct connection to software verification and validation concepts
