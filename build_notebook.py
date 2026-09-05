"""Создаёт Notebook по экзаменационной задаче №2."""
from pathlib import Path
import json
import nbformat as nbf

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / 'data' / 'task_02_social_network_config.json'
OUT = ROOT / 'notebooks' / 'task_02_social_network.ipynb'

config = json.loads(CONFIG.read_text(encoding='utf-8'))
nb = nbf.v4.new_notebook()
nb['metadata'] = {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python', 'version': '3.11'}}
cells = []

cells.append(nbf.v4.new_markdown_cell('''# Экономика информатизации — экзаменационная задача №2\n## Расчёт критической массы и ценности социальной сети «ГородСоцСеть»\n\n**Цель:** определить критическую массу пользователей, оценить сетевую ценность по закону Мэткалфа, рассчитать денежные потоки и NPV, провести сценарный анализ и сформулировать стратегические рекомендации.\n\nМодель использует параметры из `data/task_02_social_network_config.json`. Все выводы относятся к учебной модели и сопровождаются ограничениями применимости.'''))

cells.append(nbf.v4.new_code_cell('''from pathlib import Path\nimport json\nimport math\nimport sys\n\nimport matplotlib.pyplot as plt\nimport numpy as np\nimport pandas as pd\nfrom IPython.display import display, Markdown\n\nrepo_root = Path.cwd()\nif repo_root.name == "notebooks":\n    repo_root = repo_root.parent\nif not (repo_root / "data").exists():\n    repo_root = Path(".." ).resolve()\nsys.path.insert(0, str(repo_root))\nfrom utils.calculations import critical_mass, users_path, cash_flow_table, npv\n\nconfig_path = repo_root / "data" / "task_02_social_network_config.json"\nwith config_path.open(encoding="utf-8") as file:\n    cfg = json.load(file)\n\nplt.style.use("default")\nplt.rcParams.update({"font.family": "DejaVu Sans", "axes.grid": True, "grid.color": "#D9D9D9", "figure.dpi": 120})\npd.set_option("display.float_format", lambda value: f"{value:,.2f}".replace(",", " ").replace(".", ","))\nnp.set_printoptions(suppress=True, precision=2)\nfigures_dir = repo_root / "reports" / "figures"\nfigures_dir.mkdir(parents=True, exist_ok=True)\n\nprint(f"Проект: {cfg['project_name']}")\nprint(f"Горизонт: {cfg['horizon_months']} месяцев")'''))

cells.append(nbf.v4.new_markdown_cell('''## Исходные данные и допущения\n\nДо критической массы используется базовый ежемесячный прирост, после перехода — ускоренный прирост. В расчёте денежных потоков CAC умножается на число новых пользователей каждого месяца. Потенциал рынка ограничивает число пользователей сверху.\n\nКритическая масса рассчитывается в двух вариантах: **строгий вариант по исходному CAC = 500 руб.** и **операционный вариант**, показывающий, какой порог получается при снижении CAC до 50 руб. Сохранение обоих вариантов важно, поскольку исходный CAC делает проект несамоподдерживающимся даже при полном охвате рынка.'''))

cells.append(nbf.v4.new_code_cell('''input_data = pd.DataFrame({\n    "Параметр": [\n        "Потенциал рынка", "Начальные пользователи", "Рост до критической массы",\n        "Рост после критической массы", "Коэффициент Мэткалфа", "Поддержание в месяц",\n        "CAC", "ARPU", "Горизонт", "Ставка дисконтирования в месяц"\n    ],\n    "Значение": [\n        cfg["market_potential_users"], cfg["initial_users"], cfg["growth_before_critical"] * 100,\n        cfg["growth_after_critical"] * 100, cfg["network_value_coefficient_rub_per_user_squared"],\n        cfg["monthly_maintenance_cost_rub"], cfg["cac_rub"], cfg["arpu_rub_per_user_month"],\n        cfg["horizon_months"], cfg["monthly_discount_rate"] * 100\n    ],\n    "Единица измерения": ["чел.", "чел.", "%/мес.", "%/мес.", "руб./пользователь²", "руб./мес.", "руб./пользователь", "руб./пользователь/мес.", "мес.", "%/мес."]\n})\ndisplay(input_data)'''))

cells.append(nbf.v4.new_markdown_cell('''## Часть 1. Расчёт критической массы\n\n**Вопрос 1.** Определите критическую массу — минимальное число пользователей, при котором сеть становится самоподдерживающейся.\n\n**Вопрос 2.** Рассчитайте, через сколько месяцев сеть достигнет критической массы при росте 3% до порога и 15% после порога.\n\n### Расчёт критической массы и срока её достижения\n\nДля текущего темпа роста условие самоподдержания записывается так:\n\n$$ARPU \u00d7 N \u2265 C_{maint} + CAC \u00d7 (gN).$$\n\nВ учебном расчёте используется фиксированный ориентир новых пользователей $N_{new,ref} = M \u00d7 g$. Тогда $N_{crit} = (C_{maint} + CAC \u00d7 N_{new,ref}) / ARPU$. Помесячный денежный поток далее рассчитывается по фактическому числу новых пользователей траектории.'''))

cells.append(nbf.v4.new_code_cell('''g = cfg["growth_before_critical"]\nreference_new_users = cfg["market_potential_users"] * g\nstrict_critical = critical_mass(cfg["arpu_rub_per_user_month"], cfg["monthly_maintenance_cost_rub"], cfg["cac_rub"], reference_new_users)\noperational_cac = 50\noperational_critical = critical_mass(cfg["arpu_rub_per_user_month"], cfg["monthly_maintenance_cost_rub"], operational_cac, reference_new_users)\n\ndef months_to_target(target, growth, initial):\n    if target <= initial:\n        return 0\n    return math.ceil(math.log(target / initial) / math.log(1 + growth))\n\nstrict_within_market = np.isfinite(strict_critical) and strict_critical <= cfg["market_potential_users"]\noperational_months = months_to_target(operational_critical, g, cfg["initial_users"])\nstrict_critical_display = strict_critical\ncritical_table = pd.DataFrame({\n    "Сценарий": ["Исходный CAC = 500 руб.", "Операционный CAC = 50 руб."],\n    "Критическая масса, чел.": [strict_critical_display, operational_critical],\n    "Достижима в рынке": ["Нет" if not strict_within_market else "Да", "Да"],\n    "Месяцев при росте 3%": ["не достигается" if not strict_within_market else months_to_target(strict_critical, g, cfg["initial_users"]), operational_months]\n})\ndisplay(critical_table)\nprint("Строгий вывод:", "при исходном CAC критическая масса превышает потенциал рынка." if not strict_within_market else "критическая масса достижима в пределах рынка.")'''))

cells.append(nbf.v4.new_markdown_cell('''## Часть 2. Оценка ценности сети\n\n**Вопрос 3.** Рассчитайте ценность сети по закону Мэткалфа: $V(N) = k \times N^2$.\n\n**Вопрос 4.** Рассчитайте доход от пользователей: $R(N) = ARPU \times N$.\n\n**Вопрос 5.** Рассчитайте прибыль сети: выручка минус затраты на поддержание и CAC новых пользователей.\n\n### Динамика пользователей, ценность сети и прибыль\n\nЧисло пользователей моделируется помесячно. Для базового сценария используется операционная критическая масса при CAC = 50 руб.; это отдельный управленческий сценарий, а не подмена исходного параметра. Такой подход позволяет показать и строгий вывод по условию, и реалистичный вариант стратегии.'''))

cells.append(nbf.v4.new_code_cell('''users = users_path(cfg["initial_users"], cfg["growth_before_critical"], cfg["growth_after_critical"], operational_critical, cfg["horizon_months"])\nrows = cash_flow_table(users, cfg["arpu_rub_per_user_month"], cfg["monthly_maintenance_cost_rub"], operational_cac)\ndf = pd.DataFrame(rows)\ndf["network_value"] = cfg["network_value_coefficient_rub_per_user_squared"] * df["users"] ** 2\ndf["discount_factor"] = 1 / ((1 + cfg["monthly_discount_rate"]) ** df["month"])\ndf["discounted_profit"] = df["profit"] * df["discount_factor"]
display_df = df.rename(columns={
    "month": "Месяц",
    "users": "Пользователи, чел.",
    "new_users": "Новые пользователи, чел.",
    "revenue": "Выручка, руб.",
    "maintenance": "Поддержание, руб.",
    "acquisition_cost": "Привлечение, руб.",
    "profit": "Прибыль, руб.",
    "network_value": "Ценность сети, руб.",
    "discount_factor": "Коэффициент дисконтирования",
    "discounted_profit": "Дисконтированная прибыль, руб.",
})
display(display_df.head(13))\n\nsummary = pd.DataFrame({\n    "Показатель": ["Пользователи в конце горизонта", "Ценность при N крит", "Ценность при полном охвате", "Выручка при N крит", "Прибыль при N крит"],\n    "Значение": [users[-1], cfg["network_value_coefficient_rub_per_user_squared"] * operational_critical**2, cfg["network_value_coefficient_rub_per_user_squared"] * cfg["market_potential_users"]**2, cfg["arpu_rub_per_user_month"] * operational_critical, cfg["arpu_rub_per_user_month"] * operational_critical - cfg["monthly_maintenance_cost_rub"] - operational_cac * cfg["growth_before_critical"] * operational_critical],\n    "Единица": ["чел.", "руб.", "руб.", "руб./мес.", "руб./мес."]\n})\ndisplay(summary)'''))

cells.append(nbf.v4.new_markdown_cell('''## Часть 3. Анализ эффективности\n\n**Вопрос 6.** Рассчитайте NPV проекта за 36 месяцев при ставке дисконтирования 1% в месяц.\n\n**Вопрос 7.** Сравните NPV при пессимистичном и оптимистичном темпах роста.\n\n**Вопрос 8.** Определите минимальный ARPU, при котором проект становится безубыточным.\n\n### NPV базового сценария\n\nNPV проекта за 36 месяцев рассчитывается как сумма дисконтированных месячных прибылей. В базовом сценарии используется операционный CAC = 50 руб., потому что при исходном CAC = 500 руб. проект не достигает самоподдержания в пределах рынка.'''))

cells.append(nbf.v4.new_code_cell('''base_npv = npv(df["profit"].iloc[1:], cfg["monthly_discount_rate"])\nnpv_table = pd.DataFrame({"Сценарий": ["Исходные параметры, CAC = 500 руб.", "Операционный сценарий, CAC = 50 руб."], "NPV, руб.": [np.nan, base_npv], "Интерпретация": ["Не достигается критическая масса; проект убыточен", "Счётный сценарий после снижения CAC"]})\n# Строгий сценарий также считаем отдельно без перехода на ускоренный рост.\nstrict_users = [cfg["initial_users"]]\nfor _ in range(cfg["horizon_months"]):\n    strict_users.append(min(strict_users[-1] * (1 + cfg["growth_before_critical"]), cfg["market_potential_users"]))\nstrict_df = pd.DataFrame(cash_flow_table(strict_users, cfg["arpu_rub_per_user_month"], cfg["monthly_maintenance_cost_rub"], cfg["cac_rub"]))\nstrict_npv = npv(strict_df["profit"].iloc[1:], cfg["monthly_discount_rate"])\nnpv_table.loc[0, "NPV, руб."] = strict_npv\ndisplay(npv_table)\nprint(f"NPV операционного сценария: {base_npv:,.2f} руб.".replace(",", " ").replace(".", ","))'''))

cells.append(nbf.v4.new_markdown_cell('''### Сценарии темпов роста и минимальный ARPU\n\nСценарии отличаются темпами роста до и после критической массы. Для сопоставимости в каждом сценарии применяется операционный CAC = 50 руб. Дополнительно рассчитывается минимальный ARPU, при котором NPV становится неотрицательной для базовой траектории пользователей.'''))

cells.append(nbf.v4.new_code_cell('''scenarios = {\n    "Пессимистичный": (0.02, 0.10),\n    "Базовый": (0.03, 0.15),\n    "Оптимистичный": (0.05, 0.20),\n}\nscenario_rows = []\nscenario_dfs = {}\nfor name, (before, after) in scenarios.items():\n    path = users_path(cfg["initial_users"], before, after, operational_critical, cfg["horizon_months"])\n    table = pd.DataFrame(cash_flow_table(path, cfg["arpu_rub_per_user_month"], cfg["monthly_maintenance_cost_rub"], operational_cac))\n    scenario_dfs[name] = table\n    scenario_rows.append({"Сценарий": name, "Рост до / после": f"{before:.0%} / {after:.0%}", "Пользователи на 36 мес.": path[-1], "NPV, руб.": npv(table["profit"].iloc[1:], cfg["monthly_discount_rate"]), "Месяц критической массы": months_to_target(operational_critical, before, cfg["initial_users"])})\nscenario_table = pd.DataFrame(scenario_rows)\ndisplay(scenario_table)\n\nbase_users = scenario_dfs["Базовый"]["users"].tolist()\nmonths = np.arange(1, cfg["horizon_months"] + 1)\nweights_users = sum(u / ((1 + cfg["monthly_discount_rate"]) ** m) for m, u in zip(months, base_users[1:]))\nweights_new = sum(max(base_users[m] - base_users[m-1], 0) / ((1 + cfg["monthly_discount_rate"]) ** m) for m in months)\ncosts_pv = sum(cfg["monthly_maintenance_cost_rub"] / ((1 + cfg["monthly_discount_rate"]) ** m) + operational_cac * max(base_users[m] - base_users[m-1], 0) / ((1 + cfg["monthly_discount_rate"]) ** m) for m in months)\nbreak_even_arpu = costs_pv / weights_users\nprint(f"Минимальный ARPU для NPV >= 0: {break_even_arpu:,.2f} руб./пользователь/мес.".replace(",", " ").replace(".", ","))'''))

cells.append(nbf.v4.new_code_cell('''fig, ax = plt.subplots(figsize=(10, 5.5))\nfor name, table in scenario_dfs.items():\n    ax.plot(table["month"], table["users"], linewidth=2, label=name)\nax.axhline(operational_critical, linestyle="--", color="#777777", label="Операционная критическая масса")\nax.set(title="Динамика пользователей по сценариям", xlabel="Месяц", ylabel="Пользователи, чел.")\nax.legend()\nfig.tight_layout()\nfig.savefig(figures_dir / "task_02_users_scenarios.png", bbox_inches="tight")\nplt.show()\n\nfig, ax = plt.subplots(figsize=(10, 5.5))\nax.plot(df["month"], df["network_value"] / 1e6, color="#4C566A", linewidth=2.5)\nax.set(title="Ценность сети по закону Мэткалфа", xlabel="Месяц", ylabel="Ценность, млн руб.")\nfig.tight_layout()\nfig.savefig(figures_dir / "task_02_network_value.png", bbox_inches="tight")\nplt.show()\n\nfig, ax = plt.subplots(figsize=(10, 5.5))\nax.plot(df["month"], df["profit"] / 1e6, color="#A7B1C2", linewidth=2.5, label="Месячная прибыль")\nax.axhline(0, color="#343A40", linewidth=1)\nax.set(title="Месячная прибыль операционного сценария", xlabel="Месяц", ylabel="Прибыль, млн руб.")\nax.legend()\nfig.tight_layout()\nfig.savefig(figures_dir / "task_02_profit.png", bbox_inches="tight")\nplt.show()'''))

cells.append(nbf.v4.new_markdown_cell('''## Часть 4. Стратегические выводы\n\n**Вопрос 9.** Какой объём маркетинговых инвестиций необходим, чтобы достичь критической массы на шесть месяцев раньше?\n\n**Вопрос 10.** Сформулируйте рекомендации по стратегии достижения критической массы для «ГородСоцСеть».\n\n### Стратегический анализ и выводы\n\n**Итог по исходным параметрам.** При CAC = 500 руб. и росте 3% в месяц сеть не становится самоподдерживающейся в пределах рынка: строгая критическая масса равна 1 133 333 пользователям, что превышает потенциал в 1 млн человек. Поэтому исходный проект экономически неустойчив.\n\n**Минимальный ARPU.** Для базовой траектории после снижения CAC до 50 руб. рассчитан порог ARPU, при котором NPV становится неотрицательной. Этот показатель следует трактовать как ориентир, а не гарантию результата.\n\n**Маркетинговое ускорение на шесть месяцев.** При операционной критической массе сначала необходимо обеспечить базу пользователей, достаточную для достижения порога на шесть месяцев раньше. Требуемое число дополнительных пользователей и маркетинговые инвестиции рассчитываются как $CAC \u00d7$ дефицит пользователей относительно базовой траектории в целевом месяце. При исходном CAC стоимость привлечения этих пользователей существенно выше, поэтому инвестиции рациональны только после снижения CAC.\n\n**Рекомендации.** Приоритетом должны стать реферальная механика и локальные партнёрства для снижения CAC, поэтапный запуск для уменьшения затрат на поддержание, развитие платных сервисов для повышения ARPU, а также контроль когортных показателей: CAC, удержания, активность, ARPU и вклад пользователя в маржу.'''))

cells.append(nbf.v4.new_code_cell('''base_target_month = months_to_target(operational_critical, cfg["growth_before_critical"], cfg["initial_users"])\nearlier_month = max(1, base_target_month - 6)\nbase_users_at_target = cfg["initial_users"] * (1 + cfg["growth_before_critical"]) ** earlier_month\nrequired_users = operational_critical\nadditional_users = max(required_users - base_users_at_target, 0)\nmarketing_investment = additional_users * operational_cac\nstrategy_table = pd.DataFrame({\n    "Показатель": ["Базовый месяц достижения операционной критической массы", "Целевой месяц (на 6 месяцев раньше)", "Пользователи в целевом месяце без ускорения", "Дополнительные пользователи", "Маркетинговые инвестиции при CAC = 50 руб."],\n    "Значение": [base_target_month, earlier_month, base_users_at_target, additional_users, marketing_investment],\n    "Единица": ["мес.", "мес.", "чел.", "чел.", "руб."]\n})\ndisplay(strategy_table)\n\nfinal_table = pd.DataFrame({"Показатель": ["Строгая критическая масса при CAC = 500", "Операционная критическая масса при CAC = 50", "Строгий NPV за 36 мес.", "Операционный NPV за 36 мес.", "Безубыточный ARPU операционного сценария"], "Значение": [strict_critical_display, operational_critical, strict_npv, base_npv, break_even_arpu], "Единица": ["чел.", "чел.", "руб.", "руб.", "руб./пользователь/мес."]})\ndisplay(final_table)'''))

cells.append(nbf.v4.new_markdown_cell('''## Заключение\n\nМодель показывает, что при исходном CAC = 500 руб. и ARPU = 15 руб. социальная сеть не достигает критической массы внутри рынка в 1 млн жителей. Основной рычаг изменения результата — снижение стоимости привлечения пользователя. В операционном сценарии с CAC = 50 руб. можно анализировать достижение критической массы, сетевую ценность и NPV, однако запуск следует осуществлять поэтапно с проверкой фактических когортных показателей.\n\n**Ограничения:** закон Мэткалфа является упрощённой оценкой потенциальной сетевой ценности; оборот и выручка не равны прибыли без учёта маржи; модель не учитывает отток, сезонность, налоги, капитальные затраты, поддержку инфраструктуры сверх заданной суммы и изменение CAC по мере масштабирования.'''))

# Финальная структура «вопрос → расчёт → ответ» для удобной проверки задания.
cells[4].source = """## Часть 1. Расчёт критической массы

### Вопрос 1
Определите критическую массу — минимальное число пользователей, при котором сеть становится самоподдерживающейся.

**Расчёт и ответ.** Для текущего темпа роста используется фиксированный ориентир новых пользователей. Формула имеет вид:

$$N_{crit} = (C_{maint} + CAC \times N_{new,ref}) / ARPU.$$

Ниже приведены результаты для исходного CAC = 500 руб. и операционного сценария CAC = 50 руб."""
cells[5].source = cells[5].source.replace('Строгий вывод:', '**Ответ на вопрос 1:**')
cells[6].source = """### Вопрос 2
Рассчитайте, через сколько месяцев сеть достигнет критической массы при росте 3% до порога и 15% после порога.

**Расчёт и ответ.** Используется экспоненциальная модель:

$$N(t) = N_0 \times (1+g)^t.$$

Срок рассчитывается для операционной критической массы. При исходном CAC критическая масса выше потенциала рынка, поэтому срок её достижения в пределах рынка отсутствует.

## Часть 2. Оценка ценности сети

### Вопрос 3
Рассчитайте ценность сети по закону Мэткалфа: $V(N) = k \times N^2$.

### Вопрос 4
Рассчитайте доход от пользователей: $R(N) = ARPU \times N$.

### Вопрос 5
Рассчитайте прибыль сети: $П(N) = R(N) - C_{maint} - CAC \times N_{new}$.

**Расчёт и ответы.** Следующая таблица содержит помесячные значения пользователей, новых пользователей, выручки, затрат, прибыли, ценности сети и дисконтированной прибыли."""
cells[8].source = """## Часть 3. Анализ эффективности

### Вопрос 6
Рассчитайте NPV проекта за 36 месяцев при ставке дисконтирования 1% в месяц.

**Расчёт и ответ.** NPV рассчитывается дисконтированием помесячной прибыли.

### Вопрос 7
Рассчитайте изменение NPV при пессимистичном и оптимистичном темпах роста.

### Вопрос 8
Определите минимальный ARPU, при котором проект становится безубыточным.

**Ответы на вопросы 7–8** приведены в сценарной таблице и расчёте порогового ARPU ниже."""
cells[10].source = """### Расчёт ответов на вопросы 7–8

Сценарии отличаются темпами роста до и после критической массы. Для сопоставимости используется операционный CAC = 50 руб. Отдельно рассчитывается минимальный ARPU, при котором NPV становится неотрицательной для базовой траектории."""
cells[13].source = """## Часть 4. Стратегические выводы

### Вопрос 9
Какой объём маркетинговых инвестиций необходим, чтобы достичь критической массы на шесть месяцев раньше?

### Вопрос 10
Сформулируйте рекомендации по стратегии достижения критической массы для «ГородСоцСеть».

**Расчёт и ответы.** Ниже рассчитаны дополнительные пользователи и бюджет ускорения, после чего сформулированы рекомендации по снижению CAC, повышению ARPU и поэтапному запуску."""

nb['cells'] = cells
OUT.write_text(nbf.writes(nb), encoding='utf-8')
print(f'Notebook created: {OUT}')
