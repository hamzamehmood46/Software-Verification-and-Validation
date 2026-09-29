import json
import os
import sys
from pathlib import Path

import streamlit as st

from module_catalog import build_module_catalog
from path_coverage_module import (
    build_markdown_report,
    build_default_path_prompt,
    compare_model_checking_to_path_results,
    evaluate_llm_generated_suite,
    extract_branch_targets,
    run_branch_coverage,
    summarize_branch_targets,
)
from path_coverage_module.env_utils import load_local_env


ROOT = Path(__file__).resolve().parent
load_local_env(ROOT)
MODULE_CATALOG = build_module_catalog(ROOT)


st.set_page_config(page_title="Path Coverage Verification System", page_icon="P", layout="wide")


RECOMMENDED_MODELS = {
    "ollama": ["qwen2.5-coder:7b", "llama3.2:3b", "codellama:latest"],
    "openrouter": ["openai/gpt-4.1-mini", "qwen/qwen3-32b", "anthropic/claude-3.5-haiku"],
}


def format_missing_targets(missing_targets: list, limit: int = 15) -> str:
    if not missing_targets:
        return "All identified branch targets were exercised."
    return "\n".join(
        f"{target.function_name} line {target.line_number} [{target.outcome}] -> {target.condition}"
        for target in missing_targets[:limit]
    )


def suite_summary_card(title: str, result: dict[str, object]) -> None:
    coverage_pct = float(result["coverage_pct"])
    covered_targets = int(result["covered_targets"])
    total_targets = int(result["total_targets"])
    st.subheader(title)
    if result.get("suite_kind") == "llm_generated" and result.get("smoke_fallback_used"):
        st.error(
            "LLM generation fell back to the smoke test. Pytest passed, but no real path-covering "
            "pytest cases were retained for measurement."
        )
    elif int(result["pytest_exit_code"]) == 0:
        st.success(
            f"Pytest passed. Branch-target coverage: {coverage_pct:.1f}% "
            f"({covered_targets}/{total_targets})"
        )
    else:
        st.warning("Pytest failed, so path coverage for this suite may be incomplete.")
    st.code(str(result["pytest_output"]).strip() or "<no pytest output>", language="text")
    st.caption("Missing targets")
    st.code(format_missing_targets(result["missing_targets"]), language="text")


def build_function_coverage_rows(
    grouped_targets: dict[str, list],
    result: dict[str, object] | None,
) -> list[dict[str, object]]:
    covered_labels = set((result or {}).get("covered_labels", []))
    rows: list[dict[str, object]] = []
    for function_name, targets in grouped_targets.items():
        total_targets = len(targets)
        covered_targets = sum(1 for target in targets if target.label in covered_labels)
        missing_targets = total_targets - covered_targets
        coverage_pct = (covered_targets / total_targets * 100.0) if total_targets else 0.0
        rows.append(
            {
                "function": function_name,
                "covered_targets": covered_targets,
                "total_targets": total_targets,
                "missing_targets": missing_targets,
                "coverage_pct": round(coverage_pct, 1),
            }
        )
    return rows


def render_function_path_analysis(
    title: str,
    grouped_targets: dict[str, list],
    result: dict[str, object] | None,
) -> None:
    st.subheader(title)
    if result is None:
        st.info("Run this suite first to see its path-analysis breakdown.")
        return

    rows = build_function_coverage_rows(grouped_targets, result)
    st.dataframe(rows, use_container_width=True)
    st.caption("Missing targets for this suite")
    st.code(format_missing_targets(result.get("missing_targets", [])), language="text")


def llm_summary_card(result: dict[str, object]) -> None:
    metric_col_1, metric_col_2, metric_col_3, metric_col_4 = st.columns(4)
    metric_col_1.metric("Generated tests", int(result.get("generated_test_count", 0)))
    metric_col_2.metric("Final tests", int(result.get("final_test_count", 0)))
    metric_col_3.metric("Syntax valid", "Yes" if result.get("syntax_valid") else "No")
    metric_col_4.metric("Pytest pass", "Yes" if result.get("pytest_pass") else "No")
    st.metric("Coverage", f"{float(result.get('coverage_pct', 0.0)):.1f}%")
    if result.get("smoke_fallback_used"):
        st.error(
            "No usable pytest suite was retained. The framework stored only the fallback smoke test, "
            "so LLM path coverage is effectively zero for this run."
        )
    elif result.get("used_fallback"):
        st.warning(
            "The model needed fallback handling during generation. Review the rejection reasons before "
            "treating this suite as strong evidence."
        )
    if result.get("seed_fallback_used"):
        st.warning(
            "The run now contains deterministic seed tests because the model output could not be validated into "
            "a usable suite. You still get real pytest cases, but they are no longer purely LLM-authored."
        )
    notes = result.get("generation_notes") or []
    st.caption("Generation notes")
    st.code("\n".join(notes) if notes else "No warnings or timeouts reported.", language="text")
    reasons = result.get("rejection_reasons") or []
    st.caption("Why tests were rejected or repaired")
    st.code("\n".join(reasons) if reasons else "No rejection reasons were recorded.", language="text")


def provider_models(provider: str) -> list[str]:
    return RECOMMENDED_MODELS.get(provider, RECOMMENDED_MODELS["ollama"])


def run_llm_suite(
    python_executable: str,
    selected_module,
    provider: str,
    model_name: str,
    api_key: str | None,
    prompt_text: str,
    include_baseline: bool,
    llm_timeout: int,
    llm_fast_mode: bool,
    output_path: Path,
) -> dict[str, object]:
    return evaluate_llm_generated_suite(
        python_executable=python_executable,
        module_path=str(selected_module.module_path),
        module_name=selected_module.module_name,
        baseline_test_path=str(selected_module.baseline_test_path),
        requirements=prompt_text,
        model_name=model_name,
        output_test_path=str(output_path),
        provider=provider,
        api_key=api_key,
        include_baseline=include_baseline,
        timeout_seconds=llm_timeout,
        attempt_repair=not llm_fast_mode,
    )


def hosted_key_available(provider: str, typed_key: str) -> bool:
    if typed_key:
        return True
    if provider == "openrouter":
        return bool(os.getenv("OPENROUTER_API_KEY", "").strip())
    return True


def init_state() -> None:
    defaults = {
        "baseline_result": None,
        "reference_result": None,
        "llm_result": None,
        "llm_comparison_results": {},
        "model_check_result": None,
        "_selected_module_key": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()

st.title("GUI-Based Path Coverage Verification System")
st.caption(
    "A backend-driven Streamlit application for path analysis, suite comparison, LLM-assisted test generation, "
    "and model-checking comparison."
)

with st.sidebar:
    st.header("Configuration")
    python_executable = st.text_input(
        "Python executable",
        value=sys.executable,
        help="Use the environment that has pytest, streamlit, and any selected LLM provider dependencies installed.",
    )
    selected_module_key = st.selectbox(
        "Module under test",
        list(MODULE_CATALOG.keys()),
        index=0,
        format_func=lambda key: MODULE_CATALOG[key].display_name,
        help="Switch the whole analysis workflow to a different Python module and its matching test suites.",
    )
    selected_module = MODULE_CATALOG[selected_module_key]
    if st.session_state.get("_selected_module_key") != selected_module_key:
        st.session_state["baseline_result"] = None
        st.session_state["reference_result"] = None
        st.session_state["llm_result"] = None
        st.session_state["llm_comparison_results"] = {}
        st.session_state["model_check_result"] = None
        st.session_state["_selected_module_key"] = selected_module_key
    provider = st.selectbox(
        "LLM provider",
        ["ollama", "openrouter"],
        index=0,
        help="Use Ollama for local models, or OpenRouter for hosted generation.",
    )
    provider_model_options = provider_models(provider)
    model_name = st.selectbox(
        "Model",
        provider_model_options,
        index=0,
    )
    openrouter_api_key = st.text_input(
        "OpenRouter API key",
        value=st.session_state.get("_openrouter_api_key", ""),
        type="password",
        help="Leave blank to use OPENROUTER_API_KEY from the environment.",
        key="_openrouter_api_key",
    )
    api_key = ""
    if provider == "openrouter":
        api_key = openrouter_api_key
    llm_timeout = st.slider("LLM timeout (seconds)", min_value=5, max_value=420, value=20, step=5)
    llm_fast_mode = st.checkbox("Fast mode (skip repair pass)", value=True)
    include_baseline = st.checkbox("Merge baseline tests into LLM suite", value=False)
    default_prompt_text = build_default_path_prompt(
        module_name=selected_module.module_name,
        module_filename=selected_module.module_path.name,
        module_source=selected_module.module_path.read_text(encoding="utf-8"),
    )
    prompt_text = st.text_area("LLM prompt", value=default_prompt_text, height=220)
    if provider == "ollama":
        st.info(
            "Recommended quick local run: `llama3.2:3b` or `qwen2.5-coder:7b`, timeout 20-30 seconds."
        )
    elif provider == "openrouter":
        st.info(
            "Recommended hosted run: `openai/gpt-4.1-mini` for a strong low-cost default on OpenRouter."
        )

    st.markdown("**Recommended comparison models**")
    st.write("- `ollama`: `qwen2.5-coder:7b`")
    st.write("- `openrouter`: `openai/gpt-4.1-mini`")

module_source = selected_module.module_path.read_text(encoding="utf-8")
branch_targets = extract_branch_targets(str(selected_module.module_path))
grouped_targets = summarize_branch_targets(str(selected_module.module_path))

tab_overview, tab_paths, tab_llm, tab_model, tab_reports = st.tabs(
    ["Overview", "Path Analysis", "LLM Evaluation", "Model Checking", "Reports"]
)

with tab_overview:
    metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
    metric_col_1.metric("Functions analyzed", len(grouped_targets))
    metric_col_2.metric("Branch targets", len(branch_targets))
    metric_col_3.metric("Selected module", selected_module.module_name)

    st.subheader("System Architecture")
    st.write(
        "This GUI acts as the frontend for the reusable backend module. The backend performs the actual "
        "path extraction, coverage evaluation, LLM test generation, and model-checking comparison."
    )

    with st.expander("Module under test"):
        st.code(module_source, language="python")

    control_col_1, control_col_2, control_col_3 = st.columns(3)
    if control_col_1.button("Run Baseline Coverage", use_container_width=True):
        st.session_state["baseline_result"] = run_branch_coverage(
            python_executable, str(selected_module.module_path), str(selected_module.baseline_test_path)
        )
    if control_col_2.button("Run Reference Coverage", use_container_width=True):
        st.session_state["reference_result"] = run_branch_coverage(
            python_executable, str(selected_module.module_path), str(selected_module.reference_test_path)
        )
    if control_col_3.button("Run Model Check", use_container_width=True):
        if not selected_module.supports_model_checking:
            st.warning(f"Model checking is currently enabled only for modules with a configured formal comparison target.")
        else:
            path_reference = st.session_state["reference_result"]
            if path_reference is None:
                path_reference = run_branch_coverage(
                    python_executable,
                    str(selected_module.module_path),
                    str(selected_module.reference_test_path),
                )
                st.session_state["reference_result"] = path_reference
            st.session_state["model_check_result"] = compare_model_checking_to_path_results(
                selected_module.module_name,
                path_reference,
                branch_targets,
            )

    if st.session_state["baseline_result"] is not None:
        suite_summary_card("Baseline Suite", st.session_state["baseline_result"])
    if st.session_state["reference_result"] is not None:
        suite_summary_card("Reference Path Suite", st.session_state["reference_result"])

with tab_paths:
    st.subheader("Static Branch Targets")
    for function_name, targets in grouped_targets.items():
        st.markdown(f"**{function_name}**")
        for target in targets:
            st.write(f"- line {target.line_number} | {target.outcome.upper()} | `{target.condition}`")

    controls_col_1, controls_col_2, controls_col_3 = st.columns(3)
    if controls_col_1.button("Run Baseline Path Coverage", use_container_width=True):
        st.session_state["baseline_result"] = run_branch_coverage(
            python_executable, str(selected_module.module_path), str(selected_module.baseline_test_path)
        )
    if controls_col_2.button("Run LLM Path Coverage", use_container_width=True):
        if st.session_state["llm_result"] is None:
            st.warning("Run LLM Evaluation first so the generated test suite exists.")
        else:
            st.session_state["llm_result"] = run_branch_coverage(
                python_executable, str(selected_module.module_path), str(selected_module.generated_test_path)
            ) | {
                key: value
                for key, value in st.session_state["llm_result"].items()
                if key not in {"pytest_exit_code", "pytest_output", "total_targets", "covered_targets", "coverage_pct", "covered_labels", "missing_targets"}
            }
    if controls_col_3.button("Run Reference Path Coverage", use_container_width=True):
        st.session_state["reference_result"] = run_branch_coverage(
            python_executable, str(selected_module.module_path), str(selected_module.reference_test_path)
        )

    coverage_col_1, coverage_col_2 = st.columns(2)
    with coverage_col_1:
        st.markdown("### Baseline Coverage")
        if st.session_state["baseline_result"] is not None:
            suite_summary_card("Baseline Path Coverage", st.session_state["baseline_result"])
        else:
            st.info("Run the baseline suite to compute baseline-only path coverage.")
    with coverage_col_2:
        st.markdown("### LLM Coverage")
        if st.session_state["llm_result"] is not None:
            suite_summary_card("LLM Path Coverage", st.session_state["llm_result"])
        else:
            st.info("Run LLM evaluation first to compute LLM-only path coverage.")

    analysis_col_1, analysis_col_2 = st.columns(2)
    with analysis_col_1:
        st.markdown("### Baseline Path Analysis")
        render_function_path_analysis(
            "Baseline Path Analysis",
            grouped_targets,
            st.session_state["baseline_result"],
        )
    with analysis_col_2:
        st.markdown("### LLM Path Analysis")
        render_function_path_analysis(
            "LLM Path Analysis",
            grouped_targets,
            st.session_state["llm_result"],
        )

    if st.session_state["reference_result"] is not None:
        st.divider()
        suite_summary_card("Reference Coverage", st.session_state["reference_result"])

with tab_llm:
    st.subheader("LLM-Assisted Test Generation")
    st.write(
        "This panel evaluates the underlying LLM with respect to number of generated test cases, syntactic "
        "correctness, executable correctness under pytest, and achieved path coverage."
    )
    if st.button("Run LLM Evaluation", use_container_width=True):
        with st.spinner("Running LLM-based test generation..."):
            st.session_state["llm_result"] = run_llm_suite(
                python_executable=python_executable,
                selected_module=selected_module,
                provider=provider,
                model_name=model_name,
                api_key=api_key or None,
                prompt_text=prompt_text,
                include_baseline=include_baseline,
                llm_timeout=llm_timeout,
                llm_fast_mode=llm_fast_mode,
                output_path=selected_module.generated_test_path,
            )

    llm_result = st.session_state["llm_result"]
    if llm_result is not None:
        llm_summary_card(llm_result)
        artifact_col_1, artifact_col_2 = st.columns(2)
        with artifact_col_1:
            st.subheader("Validated final test file")
            st.code(llm_result.get("generated_tests", ""), language="python")
        with artifact_col_2:
            st.subheader("Primary model-produced test file")
            st.code(llm_result.get("primary_generated_tests", ""), language="python")

        if llm_result.get("raw_augmentation_output"):
            st.subheader("Baseline augmentation output")
            st.code(llm_result.get("raw_augmentation_output", ""), language="text")

        repair_outputs = llm_result.get("raw_repair_outputs") or []
        if repair_outputs:
            st.subheader("Repair attempts")
            for index, repair_output in enumerate(repair_outputs, start=1):
                with st.expander(f"Repair round {index}", expanded=False):
                    st.code(repair_output, language="text")

        st.subheader("Pytest output")
        st.code(str(llm_result.get("pytest_output", "")).strip() or "<no pytest output>", language="text")
        with st.expander("Full raw generation log", expanded=False):
            st.code(llm_result.get("raw_output_log", ""), language="text")
        if llm_result.get("pytest_pass") and not llm_result.get("smoke_fallback_used"):
            suite_summary_card("LLM Path Suite", llm_result)
            render_function_path_analysis("LLM Function-Level Path Analysis", grouped_targets, llm_result)
        elif llm_result.get("smoke_fallback_used"):
            st.warning(
                "Skipping the positive LLM path-suite summary because this run only preserved the smoke fallback."
            )

    st.divider()
    st.subheader("Provider Comparison")
    st.write(
        "Run the same path-oriented prompt across multiple providers so you can compare baseline, Ollama, and OpenRouter in one presentation-ready view."
    )

    compare_col_1, compare_col_2 = st.columns(2)
    ollama_compare_model = compare_col_1.selectbox(
        "Ollama comparison model",
        provider_models("ollama"),
        index=0,
        key="ollama_compare_model",
    )
    openrouter_compare_model = compare_col_2.selectbox(
        "OpenRouter comparison model",
        provider_models("openrouter"),
        index=0,
        key="openrouter_compare_model",
    )

    if st.button("Run Baseline vs Ollama vs OpenRouter", use_container_width=True):
        comparison_results: dict[str, dict[str, object]] = {}
        with st.spinner("Running multi-provider comparison..."):
            if st.session_state["baseline_result"] is None:
                st.session_state["baseline_result"] = run_branch_coverage(
                    python_executable, str(selected_module.module_path), str(selected_module.baseline_test_path)
                )
            comparison_results["baseline"] = st.session_state["baseline_result"]

            comparison_results["ollama"] = run_llm_suite(
                python_executable=python_executable,
                selected_module=selected_module,
                provider="ollama",
                model_name=ollama_compare_model,
                api_key=None,
                prompt_text=prompt_text,
                include_baseline=include_baseline,
                llm_timeout=llm_timeout,
                llm_fast_mode=llm_fast_mode,
                output_path=ROOT / f"generated_llm_path_tests_{selected_module.module_name}_ollama.py",
            )

            openrouter_key_value = st.session_state.get("_openrouter_api_key", "")
            if hosted_key_available("openrouter", openrouter_key_value):
                comparison_results["openrouter"] = run_llm_suite(
                    python_executable=python_executable,
                    selected_module=selected_module,
                    provider="openrouter",
                    model_name=openrouter_compare_model,
                    api_key=openrouter_key_value or None,
                    prompt_text=prompt_text,
                    include_baseline=include_baseline,
                    llm_timeout=llm_timeout,
                    llm_fast_mode=llm_fast_mode,
                    output_path=ROOT / f"generated_llm_path_tests_{selected_module.module_name}_openrouter.py",
                )
            else:
                st.warning("OpenRouter comparison skipped because no OpenRouter API key was provided.")

        st.session_state["llm_comparison_results"] = comparison_results

    comparison_results = st.session_state.get("llm_comparison_results") or {}
    if comparison_results:
        rows = []
        for label, result in comparison_results.items():
            rows.append(
                {
                    "suite": label,
                    "provider": result.get("provider", "baseline"),
                    "model": result.get("model_name", "baseline tests"),
                    "generated_tests": int(result.get("generated_test_count", 0)),
                    "final_tests": int(result.get("final_test_count", 0)),
                    "pytest_pass": "Yes" if result.get("pytest_pass", int(result.get("pytest_exit_code", 1)) == 0) else "No",
                    "coverage_pct": f"{float(result.get('coverage_pct', 0.0)):.1f}%",
                }
            )
        st.dataframe(rows, use_container_width=True)

        ranked = sorted(
            comparison_results.items(),
            key=lambda item: float(item[1].get("coverage_pct", 0.0)),
            reverse=True,
        )
        best_name, best_result = ranked[0]
        st.success(
            f"Best coverage in the current comparison: `{best_name}` using "
            f"`{best_result.get('provider', 'baseline')}` / `{best_result.get('model_name', 'baseline tests')}` "
            f"with {float(best_result.get('coverage_pct', 0.0)):.1f}% coverage."
        )

with tab_model:
    st.subheader("Model Checking Comparison")
    st.write(
        "A bounded explicit-state model checker is used only when the selected module has a configured formal-comparison target."
    )
    if st.button("Run Model Checking Comparison", use_container_width=True):
        if not selected_module.supports_model_checking:
            st.warning(f"No model-checking comparison is configured for `{selected_module.module_name}` yet.")
        else:
            reference_result = st.session_state["reference_result"]
            if reference_result is None:
                reference_result = run_branch_coverage(
                    python_executable,
                    str(selected_module.module_path),
                    str(selected_module.reference_test_path),
                )
                st.session_state["reference_result"] = reference_result
            st.session_state["model_check_result"] = compare_model_checking_to_path_results(
                selected_module.module_name,
                reference_result,
                branch_targets,
            )


    model_check_result = st.session_state["model_check_result"]
    if model_check_result is not None:
        model_summary = model_check_result["model_checking"]
        comparison = model_check_result["path_analysis_comparison"]
        target_function = comparison["target_function"]
        metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
        metric_col_1.metric("Explored states", model_summary["explored_state_count"])
        metric_col_2.metric("All properties passed", "Yes" if model_summary["all_properties_passed"] else "No")
        metric_col_3.metric(
            f"Covered {target_function} targets",
            f"{comparison['target_covered_targets']}/{comparison['target_total_targets']}",
        )
        st.subheader("Reachable outcomes")
        st.code(", ".join(model_summary["reachable_statuses"]), language="text")
        st.subheader("Checked properties")
        for prop in model_summary["property_results"]:
            st.write(
                f"- `{prop.name}`: {'PASS' if prop.passed else 'FAIL'} "
                f"(checked states: {prop.checked_states})"
            )

with tab_reports:
    st.subheader("Exportable Reports")
    report_inputs: dict[str, dict[str, object]] = {}
    if st.session_state["baseline_result"] is not None:
        report_inputs["baseline"] = st.session_state["baseline_result"]
    if st.session_state["reference_result"] is not None:
        report_inputs["reference"] = st.session_state["reference_result"]
    if st.session_state["llm_result"] is not None:
        report_inputs["llm_generated"] = st.session_state["llm_result"]
    if st.session_state["llm_comparison_results"]:
        for suite_name, suite_result in st.session_state["llm_comparison_results"].items():
            if suite_name == "baseline":
                continue
            report_inputs[f"comparison_{suite_name}"] = suite_result
    if st.session_state["model_check_result"] is not None:
        report_inputs["model_checking"] = st.session_state["model_check_result"]

    if report_inputs:
        markdown_report = build_markdown_report(str(selected_module.module_path), report_inputs)
        json_report = json.dumps(report_inputs, indent=2, default=str)
        st.download_button(
            "Download Markdown Report",
            data=markdown_report,
            file_name="gui_path_report.md",
            mime="text/markdown",
            use_container_width=True,
        )
        st.download_button(
            "Download JSON Report",
            data=json_report,
            file_name="gui_path_report.json",
            mime="application/json",
            use_container_width=True,
        )
        st.code(markdown_report, language="markdown")
    else:
        st.info("Run at least one analysis step first, then the report export will appear here.")
