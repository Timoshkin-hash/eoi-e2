# Экономика информатизации — решение экзаменационной задачи №2

Репозиторий содержит воспроизводимое решение задачи **«Расчёт критической массы и ценности социальной сети»** для проекта «ГородСоцСеть».

## Содержание

| Путь | Назначение |
|---|---|
| `notebooks/task_02_social_network.ipynb` | Основной исполняемый Jupyter Notebook с расчётами, таблицами, графиками и динамическими выводами. |
| `data/task_02_social_network_config.json` | Единственный источник исходных параметров, сценариев и управленческих допущений. |
| `utils/calculations.py` | Параметризованные функции критической массы, пользовательской траектории, денежных потоков и NPV. |
| `reports/figures/` | Графики, созданные при выполнении Notebook. |
| `reports/task_02_report.html` | HTML-отчёт без отображения кода. |
| `reports/task_02_report.pdf` | PDF-версия отчёта. |
| `docs/methodology.md` | Описание расчётной модели, формул и ограничений. |
| `docs/glossary.md` | Глоссарий ключевых терминов. |
| `docs/json_parameters_guide.md` | Понятное описание всех параметров JSON и их влияния на расчёты. |
| `docs/model_review_task_02.md` | Методическая проверка формул, допущений и отличий от укрупнённого сценария. |
| `docs/profitability_roadmap_task_02.md` | Сценарии выхода в прибыль, сроки и ответы на вопрос «что если». |
| `docs/defense_notes_task_02.docx` | Материалы для устной защиты. |
| `requirements.txt` | Минимальные Python-зависимости. |

## Запуск

```bash
git clone https://github.com/Timoshkin-hash/eoi-e2.git
cd eoi-e2
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
jupyter lab
```

Откройте `notebooks/task_02_social_network.ipynb` и выполните все ячейки сверху вниз.

Для безинтерактивного запуска:

```bash
python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=180 notebooks/task_02_social_network.ipynb
```

Для формирования HTML:

```bash
python -m jupyter nbconvert --to html --no-input --output-dir reports --output task_02_report notebooks/task_02_social_network.ipynb
```

PDF можно получить из HTML через браузер: открыть `reports/task_02_report.html`, нажать `Ctrl + P` и выбрать сохранение в PDF.

## Важные особенности модели

- Все бизнес-параметры и сценарии загружаются из JSON.
- Исходные пользователи месяца 0 не считаются новым привлечением.
- Основной NPV рассчитывается по фактическим помесячным потокам.
- Укрупнённый NPV по блокам вынесен в отдельный контрольный сценарий.
- Если даже при CAC = 0 NPV остаётся отрицательным, Notebook рекомендует повышать ARPU, ускорять рост или снижать затраты на поддержание.
- Закон Мэткалфа используется как учебная оценка потенциальной сетевой ценности.

## Автор

Глазков Тимофей Владимирович, группа БИ ОЗФО5-1.
