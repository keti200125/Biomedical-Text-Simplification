from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


CODE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CODE_DIR.parent
DATA_DIR = CODE_DIR / "data" if (CODE_DIR / "data").exists() else PROJECT_ROOT / "data"
RESULTS_DIR = CODE_DIR / "results" if (CODE_DIR / "results").exists() else PROJECT_ROOT / "results"
KG_DIR = DATA_DIR / "knowledge_graph"


st.set_page_config(
    page_title="Опростяване на биомедицински текст",
    layout="wide",
)


COLUMN_LABELS = {
    "experiment": "експеримент",
    "model": "модел",
    "task": "задача",
    "dataset_rows": "брой примери",
    "BERTScore_F1": "BERTScore F1",
    "Accuracy": "точност",
    "F1_macro": "усреднена F1",
    "F1_weighted": "претеглена F1",
    "note": "бележка",
    "pair_id": "двойка",
    "sent_id": "изречение",
    "label": "етикет",
    "true_label": "истински етикет",
    "predicted_label": "предсказан етикет",
    "complex": "сложно изречение",
    "simple": "референтно опростяване",
    "prediction": "изход на модела",
    "detected_mappings": "открити връзки",
    "analysis_note_bg": "коментар",
    "subset": "подмножество",
    "rows": "брой примери",
    "system": "система",
    "BERTScore Precision": "BERTScore точност",
    "BERTScore Recall": "BERTScore пълнота",
    "BERTScore F1": "BERTScore F1",
    "delta_SARI": "разлика SARI",
    "delta_BLEU": "разлика BLEU",
    "delta_BERTScore": "разлика BERTScore",
    "coverage_pct": "покритие (%)",
    "avg_mappings_per_example": "средно връзки на пример",
    "source_norm": "сложен термин",
    "target_norm": "опростен термин",
    "frequency": "честота",
    "quality_score": "оценка за качество",
    "delete_accuracy": "точност при изтриване",
}

LABEL_VALUES = {
    "rephrase": "преформулиране",
    "delete": "изтриване",
    "ignore": "запазване",
    "split": "разделяне",
    "generate_with_biobart": "генериране с BioBART",
    "remove_sentence": "премахване на изречението",
    "keep_original_sentence": "запазване на изречението",
    "generate_with_biobart_future_split_model": "генериране с BioBART",
}

TASK_VALUES = {
    "generation": "генериране",
    "generation + KG prompt": "генериране с граф на знания",
    "subset generation": "генериране върху подмножество",
    "oracle action + generation": "истински етикети и генериране",
    "classification": "класификация",
    "classification-routed generation": "генериране след класификация",
}

MODEL_VALUES = {
    "Llama 3.1 8B via Ollama, zero-shot": "Llama 3.1 8B чрез Ollama, без дообучаване",
    "google/flan-t5-base fine-tuned": "google/flan-t5-base, дообучен",
    "GanjinZero/biobart-base fine-tuned": "GanjinZero/biobart-base, дообучен",
    "Optimized KG-BioBART, balanced graph": "KG-BioBART с оптимизиран балансиран граф",
    "Optimized KG-BioBART subset": "KG-BioBART върху подмножество",
    "Oracle gold-label action pipeline + BioBART": "Подход с истински етикети и BioBART",
    "PubMedBERT/BioBERT action classifier": "Класификатор на операции PubMedBERT/BioBERT",
    "Classifier + BioBART action pipeline": "Класификатор и BioBART",
}

NOTE_VALUES = {
    "Original zero-shot baseline; BLEU normalized to 0-100 scale.": "Първоначален базов модел без дообучаване; BLEU е в скала 0-100.",
    "Fine-tuned no-context sentence simplification.": "Дообучен модел за опростяване на изречения без допълнителен контекст.",
    "Original BioBART reported score before shared evaluator/head-to-head recomputation.": "Първоначално отчетен резултат за BioBART преди общото преизчисление.",
    "Recomputed in head-to-head using current shared evaluation logic.": "Преизчислено със същите функции за оценяване върху същите примери.",
    "Same examples as E2-current; balanced optimized induced KG.": "Същите примери като директния BioBART; използван е оптимизиран балансиран граф.",
    "Uses gold labels; not deployable. Delete accuracy=1.0.": "Използва истинските етикети; не е приложим като реална система. Точност при изтриване = 1.0.",
    "Predicts rephrase/delete/ignore/split from complex sentence only.": "Предсказва операция само от сложното изречение.",
    "Pipeline uses predicted labels: delete empty, ignore original, rephrase/split BioBART.": "Използва предсказани етикети: изтриване, запазване или генериране с BioBART.",
}

MODEL_ANALYSIS_SUMMARIES = {
    "Llama 3.1 без дообучаване": {
        "извод": "Създава четими обяснения, но не следва устойчиво стила на примерните опростявания.",
        "силни страни": "Обяснява част от медицинските понятия и често премахва излишната статистика.",
        "ограничения": "Понякога добавя бележки, променя числа или въвежда твърдения, които липсват в източника.",
    },
    "FLAN-T5 дообучен": {
        "извод": "Запазва добре съдържанието, но обикновено прави по-предпазливи промени.",
        "силни страни": "Постига високо словесно и смислово сходство с примерните опростявания.",
        "ограничения": "Често оставя сложни понятия и статистически подробности; срещат се и отделни терминологични грешки.",
    },
    "BioBART директен": {
        "извод": "Предлага най-доброто практическо равновесие между опростяване и запазване на смисъла.",
        "силни страни": "Съкращава сложни изречения и е по-подходящ за биомедицински текст от общия модел.",
        "ограничения": "Понякога почти повтаря входа или оставя трудни медицински понятия непроменени.",
    },
    "KG-BioBART първоначален граф": {
        "извод": "Първоначалният граф не променя устойчиво изхода на BioBART.",
        "силни страни": "Може да предложи по-просто съответствие при разпознат медицински термин.",
        "ограничения": "Графът съдържа малко полезни връзки и част от тях са шумни или неточни.",
    },
    "KG-BioBART оптимизиран граф": {
        "извод": "По-чистият граф помага леко върху част от примерите, но не подобрява общия резултат.",
        "силни страни": "Връзките са по-надеждни и при разпознати термини се наблюдава малко повишение на SARI.",
        "ограничения": "Покритието е ниско, а моделът невинаги използва подадената терминологична връзка.",
    },
    "Класификатор + BioBART": {
        "извод": "Грешките при избора на действие се пренасят пряко към крайното опростяване.",
        "силни страни": "Подходът ясно разделя решението за действие от създаването на опростен текст.",
        "ограничения": "Неправилното изтриване или запазване на изречение води до загуба на важна информация.",
    },
    "Подход с истински етикети": {
        "извод": "Истинските действия подобряват многоетапния подход, но не дават убедително предимство пред BioBART.",
        "силни страни": "Изтриването и запазването се изпълняват правилно и не зависят от грешки на класификатора.",
        "ограничения": "Не е приложим върху нови данни и при преформулиране остава зависим от възможностите на BioBART.",
    },
}


def localize_columns(df: pd.DataFrame) -> pd.DataFrame:
    localized = df.copy()
    for col in ["label", "true_label", "predicted_label", "pipeline_action"]:
        if col in localized.columns:
            localized[col] = localized[col].map(lambda value: LABEL_VALUES.get(str(value), value))
    if "task" in localized.columns:
        localized["task"] = localized["task"].map(lambda value: TASK_VALUES.get(str(value), value))
    if "model" in localized.columns:
        localized["model"] = localized["model"].map(lambda value: MODEL_VALUES.get(str(value), value))
    if "note" in localized.columns:
        localized["note"] = localized["note"].map(lambda value: NOTE_VALUES.get(str(value), value))
        localized["note"] = localized["note"].astype(str).str.replace("coverage_pct=", "покритие=", regex=False)
        localized["note"] = localized["note"].astype(str).str.replace("avg_mappings=", "средно връзки=", regex=False)
    if "subset" in localized.columns:
        localized["subset"] = localized["subset"].astype(str).replace({
            "all_test": "всички тестови примери",
            "with_kg_terms": "с термини от графа",
            "without_kg_terms": "без термини от графа",
            "all oracle pipeline examples": "всички примери",
            "rephrase only": "само преформулиране",
            "delete only": "само изтриване",
            "ignore only": "само запазване",
            "split only": "само разделяне",
        })
    if "system" in localized.columns:
        localized["system"] = localized["system"].astype(str).replace({
            "BioBART direct": "директен BioBART",
            "KG-BioBART optimized": "KG-BioBART с оптимизиран граф",
        })
    return localized.rename(columns={col: COLUMN_LABELS.get(col, col) for col in localized.columns})


@st.cache_data
def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data
def load_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def markdown_section(markdown_text: str, heading: str) -> str:
    """Return one second-level Markdown section by its exact heading."""
    marker = f"## {heading}"
    start = markdown_text.find(marker)
    if start < 0:
        return markdown_text
    next_heading = markdown_text.find("\n## ", start + len(marker))
    return markdown_text[start:] if next_heading < 0 else markdown_text[start:next_heading]


def metric_card(label: str, value: object, help_text: str | None = None) -> None:
    if pd.isna(value):
        display_value = "няма данни"
    elif isinstance(value, float):
        display_value = f"{value:.3f}"
    else:
        display_value = str(value)
    st.metric(label, display_value, help=help_text)


def show_prediction_examples(df: pd.DataFrame, title: str) -> None:
    st.subheader(title)
    if df.empty:
        st.info("Не е намерен файл с примери.")
        return

    label_options = ["всички"] + sorted(df["label"].dropna().astype(str).unique().tolist()) if "label" in df.columns else ["всички"]
    selected_label = st.selectbox("Филтър по етикет", label_options, key=f"{title}-label")
    filtered = df.copy()
    if selected_label != "всички" and "label" in filtered.columns:
        filtered = filtered[filtered["label"].astype(str).eq(selected_label)].copy()

    search = st.text_input("Търсене в изреченията и изхода", key=f"{title}-search")
    if search:
        text_cols = [col for col in ["complex", "simple", "prediction", "analysis_note_bg"] if col in filtered.columns]
        mask = pd.Series(False, index=filtered.index)
        for col in text_cols:
            mask = mask | filtered[col].fillna("").astype(str).str.contains(search, case=False, regex=False)
        filtered = filtered[mask].copy()

    max_rows = min(50, len(filtered))
    n_rows = st.slider("Брой примери", min_value=1, max_value=max(1, max_rows), value=min(10, max(1, max_rows)), key=f"{title}-n")

    visible = filtered.head(n_rows).copy()
    visible = localize_columns(visible)
    text_columns = [COLUMN_LABELS[col] for col in ["complex", "simple", "prediction", "analysis_note_bg", "detected_mappings"] if COLUMN_LABELS[col] in visible.columns]
    column_config = {
        col: st.column_config.TextColumn(col, width="large")
        for col in text_columns
    }

    st.dataframe(
        visible,
        width="stretch",
        hide_index=True,
        height=min(900, 180 + 180 * len(visible)),
        row_height=160,
        column_config=column_config,
    )


def clean_metric_summary(summary_df: pd.DataFrame) -> pd.DataFrame:
    if summary_df.empty:
        return summary_df
    df = summary_df.copy()
    numeric_cols = ["SARI", "BLEU", "BERTScore_F1", "Accuracy", "F1_macro", "F1_weighted"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


summary_df = clean_metric_summary(load_csv(RESULTS_DIR / "final_experiment_summary_for_analysis.csv"))
llama_examples_df = load_csv(RESULTS_DIR / "llama_examples_for_documentation.csv")
all_models_analysis_df = load_csv(RESULTS_DIR / "all_models_examples_analysis.csv")
kg_h2h_df = load_csv(RESULTS_DIR / "kg_head_to_head_comparison.csv")
kg_metrics_df = load_csv(RESULTS_DIR / "biobart_optimized_kg_metrics.csv")
oracle_metrics_df = load_csv(RESULTS_DIR / "oracle_action_pipeline_biobart_metrics.csv")
classifier_df = load_csv(RESULTS_DIR / "biobert_action_classifier_predictions.csv")


PREDICTION_FILES = {
    "Llama 3.1 без дообучаване": RESULTS_DIR / "llama_baseline_predictions.csv",
    "FLAN-T5 дообучен": RESULTS_DIR / "flan_t5_sentence_no_context_predictions.csv",
    "BioBART директен": RESULTS_DIR / "biobart_sentence_no_context_predictions.csv",
    "KG-BioBART първоначален граф": RESULTS_DIR / "biobart_knowledge_enhanced_predictions.csv",
    "KG-BioBART оптимизиран граф": RESULTS_DIR / "biobart_optimized_kg_predictions.csv",
    "Класификатор + BioBART": RESULTS_DIR / "biobert_action_pipeline_outputs.csv",
    "Подход с истински етикети": RESULTS_DIR / "oracle_action_pipeline_biobart_predictions.csv",
}


st.title("Опростяване на биомедицински текст")
st.caption("CLEF SimpleText Task 1.1 - експерименти на ниво изречение без допълнителен контекст")

tabs = st.tabs(
    [
        "Общ преглед",
        "Резултати",
        "Примери",
        "Анализ по модели",
        "Граф на знания",
        "Многоетапен подход",
    ]
)


with tabs[0]:
    st.header("Общ преглед")
    st.write(
        """
        Този екран обобщава проведените експерименти за опростяване на биомедицински изречения.
        Всички основни генеративни експерименти са без допълнителен контекст: моделът получава
        само сложното изречение и трябва да върне негово опростяване.
        """
    )

    if not summary_df.empty:
        best_sari = summary_df.dropna(subset=["SARI"]).sort_values("SARI", ascending=False).iloc[0]
        best_bleu = summary_df.dropna(subset=["BLEU"]).sort_values("BLEU", ascending=False).iloc[0]
        best_bert = summary_df.dropna(subset=["BERTScore_F1"]).sort_values("BERTScore_F1", ascending=False).iloc[0]

        col1, col2, col3 = st.columns(3)
        with col1:
            metric_card("Най-висок SARI", best_sari["SARI"], "По-висока стойност означава по-добри операции по опростяване.")
            st.caption(f"{best_sari['experiment']} - {best_sari['model']}")
        with col2:
            metric_card("Най-висок BLEU", best_bleu["BLEU"], "По-висока стойност означава по-голямо лексикално припокриване с референцията.")
            st.caption(f"{best_bleu['experiment']} - {best_bleu['model']}")
        with col3:
            metric_card("Най-висок BERTScore F1", best_bert["BERTScore_F1"], "По-висока стойност означава по-близък смисъл.")
            st.caption(f"{best_bert['experiment']} - {best_bert['model']}")

    st.subheader("Основен извод")
    st.success(
        "Директно дообученият BioBART е най-силният практически приложим модел. "
        "Вариантите с граф на знания и многоетапен подход са полезни за анализ, но не подобряват устойчиво общия резултат."
    )


with tabs[1]:
    st.header("Резултати от моделите")
    if summary_df.empty:
        st.warning("Липсва results/final_experiment_summary_for_analysis.csv")
    else:
        st.dataframe(localize_columns(summary_df), width="stretch", hide_index=True)

        generation_df = summary_df[summary_df["SARI"].notna()].copy()
        if not generation_df.empty:
            chart_metric = st.selectbox("Метрика за графиката", ["SARI", "BLEU", "BERTScore_F1"], key="metric-chart")
            chart_df = generation_df[["experiment", chart_metric]].set_index("experiment")
            st.bar_chart(chart_df)

        st.subheader("Тълкуване на метриките")
        st.markdown(
            """
            - **SARI** е най-подходящата метрика за опростяване. Тя оценява полезното запазване, премахване и добавяне на информация.
            - **BLEU** измерва припокриването по думи и фрази с референтното изречение в скала от 0 до 100.
            - **BERTScore** измерва смисловата близост между изхода на модела и референтното изречение.
            """
        )


with tabs[2]:
    st.header("Примери от моделите")
    model_name = st.selectbox("Избери модел или система", list(PREDICTION_FILES.keys()))
    prediction_path = PREDICTION_FILES[model_name]
    prediction_df = load_csv(prediction_path)

    if prediction_df.empty:
        st.warning(f"Файлът липсва или е празен: {prediction_path.relative_to(PROJECT_ROOT)}")
    else:
        if "final_output" in prediction_df.columns and "prediction" not in prediction_df.columns:
            prediction_df = prediction_df.rename(columns={"final_output": "prediction"})
        display_cols = [col for col in ["pair_id", "sent_id", "label", "true_label", "predicted_label", "complex", "simple", "prediction", "detected_mappings"] if col in prediction_df.columns]
        show_prediction_examples(prediction_df[display_cols], f"Примери: {model_name}")


with tabs[3]:
    st.header("Анализ на примери по модели")
    st.write(
        """
        Тези примери са избрани от реалните файлове с изходи на системите. Целта е да се види
        типичното поведение на всеки модел: кога опростява добре, кога копира входа, кога губи
        информация и кога греши заради предходен етап.
        """
    )
    if all_models_analysis_df.empty:
        st.info("Не е намерен общият файл с анализ на моделите.")
    else:
        model_options = ["всички"] + sorted(all_models_analysis_df["модел"].dropna().astype(str).unique().tolist())
        selected_model = st.selectbox("Избери модел", model_options, key="all-model-analysis-filter")
        analysis_view = all_models_analysis_df.copy()
        if selected_model != "всички":
            analysis_view = analysis_view[analysis_view["модел"].astype(str).eq(selected_model)].copy()

        if selected_model == "всички":
            st.info(
                "Директно дообученият BioBART има най-добро практическо равновесие. "
                "Графът на знания помага само при малка част от примерите, а многоетапният "
                "подход е ограничен главно от грешките при избора на действие."
            )
        elif selected_model in MODEL_ANALYSIS_SUMMARIES:
            model_summary = MODEL_ANALYSIS_SUMMARIES[selected_model]
            st.subheader("Обобщение")
            st.write(model_summary["извод"])
            summary_col1, summary_col2 = st.columns(2)
            with summary_col1:
                st.success(f"Силни страни: {model_summary['силни страни']}")
            with summary_col2:
                st.warning(f"Ограничения: {model_summary['ограничения']}")

        text_cols = ["сложно изречение", "примерно опростяване", "изход на модела", "коментар", "открити връзки"]
        column_config = {
            col: st.column_config.TextColumn(col, width="large")
            for col in text_cols
            if col in analysis_view.columns
        }
        st.dataframe(
            analysis_view,
            width="stretch",
            hide_index=True,
            height=min(900, 180 + 170 * min(len(analysis_view), 8)),
            row_height=150,
            column_config=column_config,
        )

        analysis_markdown = load_text(RESULTS_DIR / "all_models_examples_analysis.md")
        expander_title = "Пълен анализ" if selected_model == "всички" else "Подробен анализ на избрания модел"
        with st.expander(expander_title):
            if selected_model == "всички":
                st.markdown(analysis_markdown)
            else:
                st.markdown(markdown_section(analysis_markdown, selected_model))


with tabs[4]:
    st.header("Граф на знания и KG-BioBART")
    col1, col2, col3 = st.columns(3)
    nodes_df = load_csv(KG_DIR / "nodes.csv")
    edges_df = load_csv(KG_DIR / "edges.csv")
    balanced_df = load_csv(KG_DIR / "edges_balanced.csv")
    with col1:
        metric_card("Възли в графа", len(nodes_df))
    with col2:
        metric_card("Активни връзки", len(edges_df))
    with col3:
        metric_card("Балансирани връзки", len(balanced_df))

    st.subheader("Метрики за оптимизирания граф")
    if kg_metrics_df.empty:
        st.info("Не са намерени метрики за оптимизирания граф.")
    else:
        st.dataframe(localize_columns(kg_metrics_df), width="stretch", hide_index=True)

    st.subheader("Пряко сравнение: директен BioBART срещу KG-BioBART")
    if kg_h2h_df.empty:
        st.info("Не е намерено пряко сравнение за графа.")
    else:
        st.dataframe(localize_columns(kg_h2h_df), width="stretch", hide_index=True)
        h2h_chart = kg_h2h_df.pivot(index="subset", columns="system", values="SARI")
        st.bar_chart(h2h_chart)

    st.subheader("Балансирани връзки в графа")
    if balanced_df.empty:
        st.info("Не е намерен файлът с балансирания граф.")
    else:
        cols = [col for col in ["source_norm", "target_norm", "frequency", "quality_score"] if col in balanced_df.columns]
        st.dataframe(localize_columns(balanced_df[cols]), width="stretch", hide_index=True)


with tabs[5]:
    st.header("Класификатор на операции и подход с истински етикети")
    st.subheader("Предсказания на класификатора")
    if classifier_df.empty:
        st.info("Не е намерен файл с предсказания на класификатора.")
    else:
        col1, col2, col3 = st.columns(3)
        accuracy = (classifier_df["true_label"].astype(str) == classifier_df["predicted_label"].astype(str)).mean()
        with col1:
            metric_card("Точност на класификатора", accuracy)
        with col2:
            metric_card("Брой редове", len(classifier_df))
        with col3:
            metric_card("Предсказани класове", classifier_df["predicted_label"].nunique())

        confusion_source = classifier_df.copy()
        confusion_source["true_label"] = confusion_source["true_label"].map(lambda value: LABEL_VALUES.get(str(value), value))
        confusion_source["predicted_label"] = confusion_source["predicted_label"].map(lambda value: LABEL_VALUES.get(str(value), value))
        confusion = pd.crosstab(
            confusion_source["true_label"],
            confusion_source["predicted_label"],
            rownames=["истински етикет"],
            colnames=["предсказан етикет"],
        )
        st.dataframe(confusion, width="stretch")

    st.subheader("Метрики при подход с истински етикети")
    if oracle_metrics_df.empty:
        st.info("Не са намерени метрики за подхода с истински етикети.")
    else:
        st.dataframe(localize_columns(oracle_metrics_df), width="stretch", hide_index=True)
