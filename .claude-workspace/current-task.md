# Текущая задача

## Задача: Web Page to Markdown Parser (web2md)

### Цель
Создать Python CLI-утилиту для загрузки веб-страниц, извлечения основного контента (без навигации, рекламы, футеров) и конвертации в чистый Markdown-формат. Приоритет — стабильность и качество извлечения.

### Сложность: M (Medium)
### Количество шагов: 8
### Уровень риска: Низкий

### Область

**Входит в scope:**
- CLI утилита `web2md`
- Загрузка страницы по URL
- Multi-extractor стратегия для максимального качества
- Конвертация в Markdown
- Сохранение в файл или вывод в stdout

**Не входит в scope:**
- JavaScript-rendered страницы (SPA)
- Batch processing множества URL
- Кэширование
- Прокси поддержка

### Стратегия извлечения контента (Multi-Extractor)

**Обоснование:** Benchmark показывает что ensemble методы превосходят отдельные экстракторы.

| Extractor | F1 Score | Precision | Recall | Роль |
|-----------|----------|-----------|--------|------|
| Trafilatura | 0.958 | 0.938 | 0.978 | Primary |
| Readability-lxml | 0.922 | 0.913 | 0.931 | Fallback |

**Алгоритм:**
1. Предобработка HTML (BeautifulSoup): удаление script, style, nav, footer
2. Trafilatura с настройками качества (include_comments=False, include_tables=True)
3. Если результат < 100 символов или пустой → Readability fallback
4. Валидация: минимум 50 символов текста, не только whitespace

### Выбранные библиотеки

| Назначение | Библиотека | Версия | Почему |
|------------|------------|--------|--------|
| HTTP клиент | httpx | >=0.27.0 | Современный, HTTP/2, timeout handling |
| Предобработка | beautifulsoup4 + lxml | >=4.12.0 | Надёжная очистка HTML |
| Primary extractor | trafilatura | >=1.12.0 | Best F1 score (0.958) |
| Fallback extractor | readability-lxml | >=0.8.1 | High median score, predictable |
| HTML→Markdown | markdownify | >=0.13.1 | Простой, предсказуемый |

### Шаги реализации

1. [ ] **Step 1: Project Setup**
   - Файлы: `requirements.txt`, `requirements-dev.txt`
   - Изменения: Создать файлы зависимостей
   - Тесты: Нет (infrastructure)
   - Команды: `pip install -r requirements.txt -r requirements-dev.txt`

2. [ ] **Step 2: Create Package Structure**
   - Файлы: `src/web2md/__init__.py`, `src/web2md/py.typed`
   - Изменения: Создать пакет web2md
   - Тесты: Нет (structure only)

3. [ ] **Step 3: Implement Exceptions Module**
   - Файлы: `src/web2md/exceptions.py`, `tests/test_exceptions.py`
   - Изменения: Custom exceptions с понятными сообщениями
   - Классы: `Web2MdError`, `FetchError`, `ExtractionError`, `ConversionError`
   - Тесты: exception inheritance, messages

4. [ ] **Step 4: Implement Fetcher Module**
   - Файлы: `src/web2md/fetcher.py`, `tests/test_fetcher.py`
   - Изменения:
     - `fetch_page(url, timeout, user_agent) -> str`
     - Retry logic (2 attempts)
     - Proper User-Agent header
     - Encoding detection
   - Тесты: success, timeout, HTTP errors, invalid URL, retry

5. [ ] **Step 5: Implement Extractor Module (Multi-Extractor)**
   - Файлы: `src/web2md/extractor.py`, `tests/test_extractor.py`
   - Изменения:
     - `preprocess_html(html) -> str` — очистка через BeautifulSoup
     - `extract_with_trafilatura(html, url) -> ExtractedContent | None`
     - `extract_with_readability(html, url) -> ExtractedContent | None`
     - `extract_content(html, url) -> ExtractedContent` — orchestration
     - Dataclass `ExtractedContent`: title, content, author, date, source_url
     - Валидация результата (min length, not empty)
   - Тесты:
     - trafilatura success
     - trafilatura fail → readability fallback
     - both fail → ExtractionError
     - validation tests

6. [ ] **Step 6: Implement Converter Module**
   - Файлы: `src/web2md/converter.py`, `tests/test_converter.py`
   - Изменения:
     - `html_to_markdown(html) -> str`
     - `format_document(content: ExtractedContent, include_metadata: bool) -> str`
     - Опциональные метаданные в начале файла (YAML frontmatter)
   - Тесты: headers, lists, links, code blocks, images, frontmatter

7. [ ] **Step 7: Implement Core Pipeline**
   - Файлы: `src/web2md/core.py`, `tests/test_core.py`
   - Изменения:
     - `url_to_markdown(url, output_path, timeout, include_metadata) -> str`
     - Оркестрация: fetch → extract → convert → save
     - Логирование этапов
   - Тесты: full pipeline, file saving, error propagation

8. [ ] **Step 8: Implement CLI**
   - Файлы: `src/web2md/cli.py`, `tests/test_cli.py`, `src/web2md/__main__.py`
   - Изменения:
     - CLI с argparse
     - Args: URL, --output/-o, --timeout/-t, --metadata/-m, --verbose/-v
     - Exit codes: 0=success, 1=fetch error, 2=extraction error, 3=conversion error
     - `__main__.py` для `python -m web2md`
   - Тесты: argument parsing, stdout/file output, exit codes, verbose mode

### Файлы для создания

| Файл | Назначение |
|------|------------|
| `requirements.txt` | Production зависимости |
| `requirements-dev.txt` | Dev зависимости (pytest, ruff, mypy) |
| `src/web2md/__init__.py` | Package init, public API |
| `src/web2md/__main__.py` | Entry point для python -m web2md |
| `src/web2md/py.typed` | PEP 561 marker |
| `src/web2md/exceptions.py` | Custom exceptions |
| `src/web2md/fetcher.py` | HTTP fetching с retry |
| `src/web2md/extractor.py` | Multi-extractor (trafilatura + readability) |
| `src/web2md/converter.py` | HTML→Markdown (markdownify) |
| `src/web2md/core.py` | Pipeline orchestration |
| `src/web2md/cli.py` | CLI interface |
| `tests/conftest.py` | Pytest fixtures |
| `tests/test_exceptions.py` | Exception tests |
| `tests/test_fetcher.py` | Fetcher tests |
| `tests/test_extractor.py` | Extractor tests (важнейшие!) |
| `tests/test_converter.py` | Converter tests |
| `tests/test_core.py` | Integration tests |
| `tests/test_cli.py` | CLI tests |

### Зависимости

**requirements.txt:**
```
httpx>=0.27.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
trafilatura>=1.12.0
readability-lxml>=0.8.1
markdownify>=0.13.1
```

**requirements-dev.txt:**
```
-r requirements.txt
pytest>=8.0.0
pytest-cov>=4.1.0
pytest-httpx>=0.30.0
ruff>=0.5.0
mypy>=1.10.0
types-beautifulsoup4>=4.12.0
```

### Критерии успеха

- [ ] `python -m web2md https://example.com` выводит Markdown в stdout
- [ ] `python -m web2md https://example.com -o article.md` сохраняет в файл
- [ ] `python -m web2md URL --metadata` добавляет YAML frontmatter
- [ ] Навигация, сайдбары, футеры удаляются
- [ ] Multi-extractor: fallback работает корректно
- [ ] Заголовки, списки, ссылки, код-блоки корректно конвертируются
- [ ] Понятные сообщения об ошибках
- [ ] `pytest` — все тесты проходят
- [ ] `ruff check src/ tests/` — нет ошибок
- [ ] `mypy src/` — нет ошибок типов
- [ ] Coverage >= 80%

### Риски и митигации

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Оба экстрактора не справляются | Low | High | Вернуть очищенный HTML как fallback |
| JS-rendered контент | Medium | High | Документировать; можно добавить playwright позже |
| Encoding issues | Low | Medium | httpx auto-detect + charset из meta |
| Медленные сайты | Medium | Low | Configurable timeout, retry logic |

### Примеры использования

```bash
# Базовое использование — stdout
python -m web2md https://blog.example.com/article

# Сохранение в файл
python -m web2md https://blog.example.com/article -o article.md

# С метаданными (YAML frontmatter)
python -m web2md https://blog.example.com/article -o article.md --metadata

# С увеличенным таймаутом
python -m web2md https://slow-site.com/page --timeout 60

# Verbose режим (логи извлечения)
python -m web2md https://example.com -v
```

**Пример вывода с --metadata:**
```markdown
---
title: "Article Title"
author: "John Doe"
date: "2025-01-15"
source: "https://example.com/article"
extracted_at: "2025-12-07T21:30:00Z"
---

# Article Title

Content here...
```

```python
# Программное использование
from web2md import url_to_markdown

# Получить markdown
md = url_to_markdown("https://example.com/article")

# С сохранением
url_to_markdown("https://example.com/article", output_path="article.md")

# С метаданными
url_to_markdown("https://example.com/article", include_metadata=True)
```
