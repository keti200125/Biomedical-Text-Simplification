"""Build Bulgarian qualitative-analysis files for the Streamlit application."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"

LABELS_BG = {
    "rephrase": "преформулиране",
    "delete": "изтриване",
    "ignore": "запазване",
    "split": "разделяне",
}

MODEL_SUMMARIES = {
    "Llama 3.1 без дообучаване": (
        "Създава свободни и често четими обяснения, но не следва устойчиво стила на примерните опростявания.",
        "Полезен е като отправна точка без обучение, но понякога добавя бележки, променя числа или въвежда нов смисъл.",
    ),
    "FLAN-T5 дообучен": (
        "Запазва добре съдържанието и формулировките от примерните опростявания, но често прави предпазливи промени.",
        "Високите BLEU и BERTScore показват близост до примерния текст, докато по-ниският SARI показва по-слабо действително опростяване.",
    ),
    "BioBART директен": (
        "Дава най-доброто практическо равновесие между опростяване и запазване на биомедицинския смисъл.",
        "Често съкращава добре, но понякога повтаря входа или оставя трудни медицински понятия непроменени.",
    ),
    "KG-BioBART първоначален граф": (
        "Първоначалният граф рядко променя полезно изхода и съдържа ограничен брой надеждни връзки.",
        "Когато не е открит подходящ термин, системата се държи почти като директния BioBART.",
    ),
    "KG-BioBART оптимизиран граф": (
        "По-чистият граф помага леко върху примерите с открити термини, но ниското покритие ограничава общия резултат.",
        "Дори при правилна връзка BioBART невинаги използва предложеното по-просто понятие.",
    ),
    "Класификатор + BioBART": (
        "Крайният резултат зависи силно от правилния избор на действие преди генерирането.",
        "Неправилното изтриване или запазване на изречение причинява по-голяма вреда от обикновена грешка при преформулиране.",
    ),
    "Подход с истински етикети": (
        "Истинските действия премахват грешките на класификатора, но не осигуряват убедително предимство пред директния BioBART.",
        "Опитът показва горната граница на многоетапната система, но не може да се използва върху нови данни.",
    ),
}

MODEL_NAMES_BG = {
    "Llama 3.1 8B via Ollama, zero-shot": "Llama 3.1 8B чрез Ollama, без дообучаване",
    "google/flan-t5-base fine-tuned": "google/flan-t5-base, дообучен",
    "GanjinZero/biobart-base fine-tuned": "GanjinZero/biobart-base, дообучен",
    "Optimized KG-BioBART, balanced graph": "KG-BioBART с оптимизиран балансиран граф",
    "Optimized KG-BioBART subset": "KG-BioBART върху подмножество",
    "Oracle gold-label action pipeline + BioBART": "Подход с истински етикети и BioBART",
    "PubMedBERT/BioBERT action classifier": "Класификатор на действия PubMedBERT/BioBERT",
    "Classifier + BioBART action pipeline": "Класификатор и BioBART",
}


def clean_comment(value: object) -> str:
    """Replace remaining English analysis phrases with Bulgarian wording."""
    text = "" if pd.isna(value) else str(value)
    replacements = {
        "добър fluent zero-shot изход, но по-дълъг от reference":
            "добър и четим изход без дообучаване, но по-дълъг от примерното опростяване",
        "добър изход без дообучаване, но по-дълъг от референтното изречение":
            "добър и четим изход без дообучаване, но по-дълъг от примерното опростяване",
        "mortality -> death": "„смъртност“ с „смърт“",
        "corticosteroids и mortality": "кортикостероидите и смъртността",
        "термин corticosteroids": "понятието за кортикостероиди",
        "терминът mortality": "понятието за смъртност",
        "mortality с deaths": "„смъртност“ с „смъртни случаи“",
        "при ignore пример": "при пример за запазване",
        "ignore label": "етикет за запазване",
        "split пример": "пример за разделяне",
        "DOAC е свързано с антибиотик":
            "съкращението за пряк перорален антикоагулант е погрешно свързано с антибиотик",
        "формулировка за DOAC": "формулировка за прекия перорален антикоагулант",
        "output": "изходът",
        "meta-commentary": "обяснение за начина на работа",
        "adverse effects": "нежелани ефекти",
        "mortality": "смъртност",
        "deaths": "смъртни случаи",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def clean_mapping_info(value: object) -> object:
    """Translate graph relations and action descriptions used in analysis tables."""
    if pd.isna(value):
        return value
    text = str(value)
    replacements = {
        "corticosteroids->steroids": "кортикостероиди → стероиди",
        "corticosteroids->steroid": "кортикостероиди → стероид",
        "mortality->death": "смъртност → смърт",
        "предсказан етикет: ignore": "предсказан етикет: запазване",
        "предсказан етикет: delete": "предсказан етикет: изтриване",
        "предсказан етикет: rephrase": "предсказан етикет: преформулиране",
        "действие: keep_original_sentence": "действие: запазване на изречението",
        "действие: remove_sentence": "действие: премахване на изречението",
        "действие: generate_with_biobart": "действие: генериране с BioBART",
        "истинско действие: delete": "истинско действие: изтриване",
        "истинско действие: ignore": "истинско действие: запазване",
        "истинско действие: rephrase": "истинско действие: преформулиране",
        "истинско действие: split": "истинско действие: разделяне",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def quote(text: object) -> str:
    """Format a possibly multiline example as a Markdown quotation."""
    value = "" if pd.isna(text) else str(text)
    return "\n".join(f"> {line}" if line else ">" for line in value.splitlines())


def metric_text(value: object, digits: int = 3) -> str:
    if pd.isna(value):
        return "—"
    return f"{float(value):.{digits}f}"


def update_analysis_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    llama_path = RESULTS_DIR / "llama_examples_for_documentation.csv"
    all_models_path = RESULTS_DIR / "all_models_examples_analysis.csv"

    llama_df = pd.read_csv(llama_path)
    llama_df["analysis_note_bg"] = llama_df["analysis_note_bg"].map(clean_comment)
    llama_df.to_csv(llama_path, index=False)

    all_models_df = pd.read_csv(all_models_path)
    all_models_df["коментар"] = all_models_df["коментар"].map(clean_comment)
    all_models_df["етикет"] = all_models_df["етикет"].map(
        lambda value: LABELS_BG.get(str(value), value)
    )
    all_models_df["открити връзки"] = all_models_df["открити връзки"].map(clean_mapping_info)
    all_models_df.to_csv(all_models_path, index=False)
    return llama_df, all_models_df


def write_llama_markdown(llama_df: pd.DataFrame) -> None:
    lines = [
        "# Анализ на примери от Llama 3.1 8B",
        "",
        "Файлът съдържа представителни примери от действителните изходи на Llama. "
        "Английският текст е запазен само в изходните изречения, примерните опростявания и резултатите на модела.",
        "",
        "## Обобщение",
        "",
        "- **Модел:** `llama3.1:8b`, стартиран чрез `Ollama`.",
        "- **Начин на работа:** без дообучаване върху набора от данни.",
        "- **Вход:** само сложното изречение, без съседни изречения или сведения за документа.",
        "- **Резултати:** SARI 28.25, BLEU 3.60 и BERTScore F1 0.897.",
        "- **Основно наблюдение:** моделът често създава четим текст, но понякога добавя обяснения, променя числа или не връща само опростеното изречение.",
        "",
    ]

    groups = [
        ("Успешни и полезни примери", llama_df.iloc[:10]),
        ("Проблемни примери", llama_df.iloc[10:14]),
        ("Кратък терминологичен пример", llama_df.iloc[14:]),
    ]
    for heading, group in groups:
        lines.extend([f"## {heading}", ""])
        for number, (_, row) in enumerate(group.iterrows(), start=1):
            label = LABELS_BG.get(str(row["label"]), row["label"])
            lines.extend(
                [
                    f"### Пример {number}",
                    "",
                    f"**Идентификатор:** двойка `{row['pair_id']}`, изречение `{row['sent_id']}`; **етикет:** {label}",
                    "",
                    f"**Коментар:** {clean_comment(row['analysis_note_bg'])}",
                    "",
                    "**Сложно изречение:**",
                    "",
                    quote(row["complex"]),
                    "",
                    "**Примерно опростяване:**",
                    "",
                    quote(row["simple"]),
                    "",
                    "**Изход на Llama:**",
                    "",
                    quote(row["prediction"]),
                    "",
                ]
            )

    lines.extend(
        [
            "## Извод",
            "",
            "Llama 3.1 8B показва какво може да постигне голям езиков модел без обучение върху конкретния корпус. "
            "Той често създава граматически правилни и разбираеми изречения, но отстъпва на дообучения BioBART. "
            "Основните затруднения са прекалено свободното преформулиране, добавянето на обяснения за начина на работа, "
            "неточното запазване на числата и непостоянното спазване на изискването за единствено опростено изречение.",
            "",
        ]
    )
    (RESULTS_DIR / "llama_examples_for_documentation.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def metric_table() -> list[str]:
    summary = pd.read_csv(RESULTS_DIR / "final_experiment_summary_for_analysis.csv")
    lines = [
        "| Опит | Модел | SARI | BLEU | BERTScore F1 | Точност | Усреднена F1 |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary.iterrows():
        model = MODEL_NAMES_BG.get(str(row["model"]), str(row["model"]))
        lines.append(
            f"| {row['experiment']} | {model} | {metric_text(row['SARI'])} | "
            f"{metric_text(row['BLEU'])} | {metric_text(row['BERTScore_F1'])} | "
            f"{metric_text(row['Accuracy'])} | {metric_text(row['F1_macro'])} |"
        )
    return lines


def write_all_models_markdown(all_models_df: pd.DataFrame) -> None:
    lines = [
        "# Анализ на примери от всички модели",
        "",
        "Анализът използва действителните изходи на системите. За всеки подход са показани еднакви полета: "
        "сложно изречение, примерно опростяване, изход на модела и кратък коментар.",
        "",
        "## Сравнение по показатели",
        "",
        *metric_table(),
        "",
    ]

    for model_name in all_models_df["модел"].drop_duplicates():
        model_rows = all_models_df[all_models_df["модел"].eq(model_name)]
        conclusion, detail = MODEL_SUMMARIES[model_name]
        lines.extend(
            [
                f"## {model_name}",
                "",
                conclusion,
                "",
                detail,
                "",
            ]
        )
        for number, (_, row) in enumerate(model_rows.iterrows(), start=1):
            pair = row["двойка"]
            sentence = row["изречение"]
            identifier = f"двойка `{pair}`, изречение `{sentence}`"
            if pd.isna(pair) or str(pair).strip() == "":
                identifier = f"ред `{sentence}`"
            lines.extend(
                [
                    f"### Пример {number}",
                    "",
                    f"**Идентификатор:** {identifier}; **етикет:** {row['етикет']}",
                    "",
                    f"**Коментар:** {clean_comment(row['коментар'])}",
                    "",
                ]
            )
            mappings = row.get("открити връзки")
            if not pd.isna(mappings) and str(mappings).strip() not in {"", "[]"}:
                lines.extend([f"**Открити връзки:** `{mappings}`", ""])
            lines.extend(
                [
                    "**Сложно изречение:**",
                    "",
                    quote(row["сложно изречение"]),
                    "",
                    "**Примерно опростяване:**",
                    "",
                    quote(row["примерно опростяване"]),
                    "",
                    "**Изход на модела:**",
                    "",
                    quote(row["изход на модела"]),
                    "",
                ]
            )

    lines.extend(
        [
            "## Общи изводи",
            "",
            "1. Директно дообученият BioBART предлага най-доброто практическо равновесие между опростяване и запазване на смисъла.",
            "2. FLAN-T5 остава близо до примерните формулировки, но извършва по-малко полезни промени.",
            "3. Llama създава четим текст, но без дообучаване допуска повече свободни и неподкрепени промени.",
            "4. Оптимизираният граф е по-чист, но малкото покритие не позволява подобрение върху целия изпитвателен набор.",
            "5. Многоетапният подход е чувствителен към грешките при избора на действие; истинските етикети помагат, но не надминават убедително директния BioBART.",
            "",
        ]
    )
    (RESULTS_DIR / "all_models_examples_analysis.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def main() -> None:
    llama_df, all_models_df = update_analysis_tables()
    write_llama_markdown(llama_df)
    write_all_models_markdown(all_models_df)
    print("Updated Bulgarian model analyses.")


if __name__ == "__main__":
    main()
