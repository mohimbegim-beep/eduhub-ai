# 🎯 ПОЛНЫЙ ПЛАН И НАСТРОЙКА GOOGLE SEARCH ADS (ПОИСКОВАЯ РЕКЛАМА) ДЛЯ EDUHUB AI

Данный документ содержит готовую конфигурацию поисковой рекламной кампании в **Google Ads**, настроенную для привлечения студентов и кандидатов IELTS с горячим поисковым намерением (*High-Intent Buyers*), без использования социальных сетей.

---

## 1. Параметры кампании (Campaign Settings)

| Параметр | Значение | Почему именно так |
| :--- | :--- | :--- |
| **Тип кампании** | **Search (Поисковая сеть)** | Только люди, которые сами вбивают запрос в строку поиска Google. |
| **Сети (Networks)** | ❌ Отключить **Display Network (КМС)**<br>❌ Отключить **Google Search Partners** | **Критично!** Предотвращает слив бюджета на баннеры и сторонние сайты-партнеры. |
| **Цель** | **Leads / Website Traffic** (или «Создать кампанию без подсказок цели») | Даёт полный ручной контроль над ставками и ключевыми словами. |
| **Геотаргетинг** | **Узбекистан, Казахстан, Азербайджан, Кыргызстан** (+ опционально Турция, ОАЭ) | Рынки с огромной плотностью сдающих IELTS и высокой конверсией в оплату. |
| **Языки** | **Английский, Русский** | Охватывает как студентов, ищущих на английском, так и на русском. |
| **Стратегия ставок** | **Maximize Clicks (Максимум кликов)**<br>с ограничением: **Max CPC Limit = $0.20** | Защищает от переплаты за клик (клики будут идти по \$0.08–\$0.18). |
| **Дневной бюджет** | **$5.00 – $10.00 / день** на старте | Достаточно для получения 30–60 целевых переходов в день. |

---

## 2. Группы объявлений и ключевые слова (Ad Groups & Keywords)

Мы используем типы соответствия:
- `"фразовое соответствие"` (в кавычках) — показ по запросу и его близким вариациям.
- `[точное соответствие]` (в квадратных скобках) — показ строго по этому запросу.

### Группа 1: IELTS Writing Task 2 (English Search)
*Целевая аудитория: студенты, ищущие проверку на английском языке.*

```text
"ielts writing task 2 checker"
"check my ielts essay"
"check ielts essay online"
"ielts essay band score calculator"
"ielts essay evaluation online"
"ielts writing correction service"
"cambridge ielts essay checker"
"rate my ielts essay"
[ielts writing checker]
[ielts essay checker]
[check ielts writing online]
[ielts band score checker writing]
[ielts writing task 2 evaluation]
```

### Группа 2: IELTS Writing (Russian Search / CIS)
*Целевая аудитория: студенты из СНГ, формулирующие запрос на русском.*

```text
"проверить эссе ielts"
"проверка эссе ielts онлайн"
"оценка эссе ielts writing"
"ielts writing task 2 проверка"
"проверить эссе по критериям кембридж"
"разбор эссе ielts онлайн"
[проверить эссе ielts]
[проверка эссе ielts онлайн]
[оценка эссе ielts]
[проверка writing task 2]
```

---

## 3. Список минус-слов (Negative Keywords) — Защита бюджета

> [!IMPORTANT]
> Добавьте эти минус-слова на уровне кампании. Они экономят до 40% бюджета, отсекая тех, кто ищет бесплатные книги, торренты или работу репетитором.

```text
free download
pdf book
torrent
cambridge book
book 16 pdf
book 17 pdf
book 18 pdf
book 19 pdf
скачать бесплатно
торрент
учебник
книга
скачать pdf
слив
вакансии
работа
job
vacancy
salary
зарплата
курсы оффлайн
адрес
телефон
экзаменационный центр
дата экзамена
расписание
british council address
idp office
сколько стоит сдать экзамен
регистрация на экзамен
listening practice
reading test
speaking simulator
```

---

## 4. Готовые тексты объявлений (Responsive Search Ads)

В Google Ads вставьте эти заголовки и описания в форму создания объявления:

### Группа 1 (English):
**Final URL (с UTM):**
```text
https://eduhub-ai.onrender.com/ielts-checker?utm_source=google&utm_medium=cpc&utm_campaign=ielts_search_en&utm_content=rsa_task2
```

**Заголовки (Headlines — до 30 символов каждый):**
1. `IELTS Writing Task 2 Checker`
2. `Instant Cambridge Band Score`
3. `Check Your Essay In 10 Sec`
4. `Band 8.5+ Model Rewrites`
5. `Senior Examiner Evaluation`
6. `Try 3-Day Pass For Just $1`
7. `Full TR, CC, LR, GRA Report`
8. `Photo & Handwritten OCR`
9. `1-Click Anki Deck Export`
10. `EduHub AI — IELTS Grader`
11. `Official Cambridge Rubrics`
12. `Accurate Band Diagnostic`
13. `Fix Grammar & Lexical Gaps`
14. `Improve Your Writing Band`
15. `Test Your Essay Now`

**Описания (Descriptions — до 90 символов каждое):**
1. `Instant Cambridge senior examiner evaluation. Get TR, CC, LR & GRA breakdown in 10 sec.`
2. `Upload your draft or handwriting photo. Get side-by-side Band 8.5+ rewrite for just $1.`
3. `Discover why examiners mark down your essay. High-yield vocabulary & full rubric scoring.`
4. `100% standardized Cambridge grading. Try full 3-day unlimited pass today for only $1.00.`

---

### Группа 2 (Russian):
**Final URL (с UTM):**
```text
https://eduhub-ai.onrender.com/ielts-checker?utm_source=google&utm_medium=cpc&utm_campaign=ielts_search_ru&utm_content=rsa_task2&lang=ru
```

**Заголовки (Headlines — до 30 символов каждый):**
1. `Проверка эссе IELTS за 10 сек`
2. `Оценка по шкале Cambridge`
3. `Разбор критериев TR CC LR GRA`
4. `Рерайт эссе на Band 8.5+`
5. `Тест-драйв за $1.00 на 3 дня`
6. `Проверь эссе Task 2 онлайн`
7. `Распознавание фото черновика`
8. `Словарь в Anki за 1 клик`
9. `EduHub AI — Оценка эссе`
10. `Узнай реальный балл IELTS`
11. `Академический рерайт текста`
12. `Точный кембриджский аудит`
13. `Исправление ошибок эссе`
14. `Твой путь к IELTS 7.5+`
15. `Проверь эссе прямо сейчас`

**Описания (Descriptions — до 90 символов каждое):**
1. `Мгновенная диагностика эссе по 4 критериям Cambridge. Разбор ошибок и рерайт на Band 8.5.`
2. `Загрузи текст или фото рукописного черновика. Получи полный аудит эксперта за $1.00.`
3. `Узнай, за что экзаменаторы снижают балл. Готовые академические связки и экспорт в Anki.`
4. `Стандарты Cambridge IELTS. Попробуй неограниченный 3-дневный доступ всего за $1.`

---

## 5. Расширения объявлений (Ad Assets / Extensions)

Добавьте расширения для увеличения размера объявления в выдаче и роста CTR на 15–20%:

1. **Быстрые ссылки (Sitelinks):**
   - **Sitelink 1:** *Критерии Cambridge* $\to$ Описание: *Диагностика TR, CC, LR, GRA за 10 сек*. URL: `https://eduhub-ai.onrender.com/ielts-checker#rubrics`
   - **Sitelink 2:** *Рерайт на Band 8.5* $\to$ Описание: *Академические обороты и связки*. URL: `https://eduhub-ai.onrender.com/ielts-checker#rewrite`
   - **Sitelink 3:** *Экспорт в Anki* $\to$ Описание: *Словарь для запоминания за 1 клик*. URL: `https://eduhub-ai.onrender.com/ielts-checker#anki`
   - **Sitelink 4:** *Тариф $1.00* $\to$ Описание: *3-дневный пробный доступ ко всем функциям*. URL: `https://eduhub-ai.onrender.com/ielts-checker#pricing`

2. **Уточнения (Callout Extensions):**
   - `Кембриджские стандарты`
   - `Разбор за 10 секунд`
   - `Фото рукописного эссе`
   - `Отмена в 1 клик`
   - `Band 8.5 Рерайт`

3. **Цены (Price Extension):**
   - Заголовок: *3-Day Pass* — Цена: *$1.00 USD*
   - Заголовок: *Pro Max Monthly* — Цена: *$19.00 USD / month*

---

## 6. Прогноз экономики и конверсии

| Метрика | Значение при бюджете $10/день |
| :--- | :--- |
| **Средняя цена клика (CPC)** | \$0.12 – \$0.18 |
| **Кликов в день** | **55 – 80 целевых переходов** |
| **Конверсия в $1 триал на сайте** | ~4% – 6% |
| **Оплат триала в день** | **2 – 4 новых платящих пользователя ($1)** |
| **Конверсия из триала в подписку ($19/мес)** | ~40% (1–2 активные подписки каждые 1–2 дня) |
| **Прирост регулярного дохода (MRR)** | **+\$250 – \$450 / месяц** |

---

## 7. Пошаговый чек-лист запуска (за 15 минут):

1. Зайдите на [ads.google.com](https://ads.google.com).
2. Нажмите **«+ Новая кампания»** $\to$ выберите **«Трафик веб-сайта»** $\to$ тип **«Поисковая сеть»**.
3. Снимите галочки с КМС и Поисковых партнеров.
4. Укажите страны (Узбекистан, Казахстан и др.).
5. Назначьте стратегию ставок **«Максимум кликов»** с пределом \$0.20.
6. Вставьте ключевые слова из Раздела 2.
7. Добавьте минус-слова из Раздела 3.
8. Скопируйте готовые заголовки и описания из Раздела 4.
9. Установите дневной бюджет \$5–\$10 и нажмите **«Опубликовать»**.
