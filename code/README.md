# Biomedical Text Simplification

Проект за опростяване на биомедицински текстове чрез класически NLP анализ, дообучени transformer модели и експерименти с biomedical knowledge graph. Работата е фокусирана върху сравнение между baseline подходи, BioBART варианти, action-classifier pipeline и knowledge-enhanced generation.

## Какво съдържа проектът

- `app.py` - Streamlit приложение за преглед на резултати, метрики и качествен анализ.
- `notebooks/` - експериментални notebooks за анализ на данните, обучение, inference и сравнение на моделите.
- `src/` - помощни Python модули за preprocessing, evaluation и генериране на анализи.
- `requirements.txt` - основните Python зависимости.

Допълнителната документация, презентацията и фигурите са оставени извън `code/`, в основната директория на проекта.

Локалните папки `data/`, `models/` и `results/` са игнорирани от Git, защото съдържат dataset-и, генерирани prediction файлове, метрики и/или моделни артефакти. При ново клониране те трябва да се възстановят локално или да се генерират чрез notebooks. Кодът може да чете тези папки както от `code/`, така и от основната директория.

## Инсталация

Препоръчително е да се използва отделна виртуална среда:

```bash
cd code
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Ако се използва Llama baseline през Ollama, настройте модела в `.env`:

```bash
cp .env.example .env
```

По подразбиране примерната конфигурация използва:

```env
OLLAMA_MODEL=llama3.1:8b
```

## Стартиране на приложението

Streamlit dashboard-ът се стартира от `code/` директорията:

```bash
cd code
streamlit run app.py
```

Приложението очаква локално налични файлове в `results/` и `data/knowledge_graph/`. Ако тези папки са в основната директория на проекта, приложението ще ги намери автоматично. Ако липсват, отделни секции ще останат празни, докато резултатите не бъдат генерирани от notebooks.

## Работен поток

1. Подготовка и анализ на данните: `notebooks/00_environment_setup.ipynb` и `notebooks/01_dataset_analysis.ipynb`.
2. Baseline експерименти: Llama и FLAN-T5 notebooks.
3. BioBART експерименти за sentence-level и document-level simplification.
4. Knowledge graph експерименти и KG-enhanced BioBART.
5. Action classification и pipeline подходи.
6. Обща оценка чрез `src/evaluation.py` и визуален преглед чрез `app.py`.

## Оценяване

Проектът използва общи evaluation функции за:

- SARI
- BLEU
- BERTScore
- Accuracy и macro/weighted F1 за action classification

Целта е всички модели и pipeline варианти да се сравняват с еднаква логика за оценяване.

## GitHub подготовка

В repository-то не трябва да се качват:

- `.env` файлове с локална конфигурация;
- виртуални среди като `.venv/`;
- dataset-и в `data/`;
- model checkpoints и weight файлове;
- генерирани резултати в `results/`;
- системни/cache файлове като `.DS_Store`, `.cache/` и `.ipynb_checkpoints/`.

Преди push е полезно да се провери:

```bash
git status --short
git ls-files -ci --exclude-standard
```

Втората команда трябва да не връща файлове. Ако върне файл, той е вече тракнат, въпреки че е в `.gitignore`, и трябва да бъде изваден от индекса с `git rm --cached <path>`.
