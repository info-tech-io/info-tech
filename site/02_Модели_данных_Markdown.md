# Модели данных для Markdown + YAML frontmatter

## Адаптация моделей Headless CMS

Существующие модели из `02_CONTENT_STRUCTURE.md` адаптированы для работы с Hugo и YAML frontmatter вместо Headless CMS.

## Структура файлов контента

### 1. Статья блога (Blog Post)

**Файл:** `content/blog/posts/[slug].md`

**YAML frontmatter:**
```yaml
---
title: "Заголовок статьи"
slug: "how-we-built-quiz-engine"
date: 2025-09-21T10:00:00Z
author: "author-slug"
cover_image: "/images/blog/quiz-engine-cover.jpg"
excerpt: "Краткая выдержка для превью статьи"
tags: ["hugo", "architecture", "javascript"]
draft: false
featured: false
---
```

**Содержимое:** Markdown контент статьи

**Примечания:**
- `author` ссылается на файл автора через slug
- `cover_image` - относительный путь к изображению
- `featured` - для отображения в featured секции

### 2. Новость (News Item)

**Файл:** `content/news/items/[slug].md`

**YAML frontmatter:**
```yaml
---
title: "Заголовок новости"
date: 2025-09-21T15:30:00Z
type: "release" # release, update, event, announcement
priority: "high" # high, medium, low
featured: true
---
```

**Содержимое:** Markdown контент новости

### 3. Автор (Author)

**Файл:** `content/authors/[slug].md`

**YAML frontmatter:**
```yaml
---
name: "Имя Фамилия"
avatar: "/images/authors/john-doe.jpg"
role: "Lead Developer"
bio: "Краткая биография автора"
social_links:
  github: "https://github.com/username"
  linkedin: "https://linkedin.com/in/username"
  twitter: "https://twitter.com/username"
weight: 1 # Для сортировки в команде
---
```

**Содержимое:** Подробная биография (Markdown)

### 4. Элемент дорожной карты (Roadmap Item)

**Файл:** `content/roadmap/items/[slug].md`

**YAML frontmatter:**
```yaml
---
title: "Запуск публичной бета-версии"
stage: "growth" # mvp, beta, growth, scale
status: "in-progress" # planned, in-progress, completed
priority: "high"
completion_date: 2025-12-31
team: ["core-team", "frontend-team"]
dependencies: ["quiz-engine-v2", "user-system"]
weight: 2 # Для сортировки
---
```

**Содержимое:** Детальное описание задачи (Markdown)

### 5. Продукт (Product)

**Файл:** `content/products/[slug].md`

**YAML frontmatter:**
```yaml
---
name: "ИНФОТЕКА"
short_name: "infotecha"
url: "https://infotecha.ru"
description: "Образовательная платформа для изучения IT-технологий"
short_description: "Интерактивное обучение с практическими заданиями"
cover_image: "/images/products/infotecha-cover.jpg"
logo: "/images/products/infotecha-logo.svg"
status: "active" # active, development, planned, archived
pricing_model: "free" # free, freemium, premium
target_audience: "Начинающие разработчики и IT-специалисты"
tech_stack: ["Hugo", "JavaScript", "Quiz Engine", "Apache2"]
github_repos:
  - name: "infotecha"
    url: "https://github.com/info-tech-io/infotecha"
  - name: "mod_linux_base"
    url: "https://github.com/info-tech-io/mod_linux_base"
metrics:
  users: 1000
  modules: 3
  completion_rate: 85
launched_date: 2025-08-31
weight: 1 # Для сортировки в каталоге
featured: true
---
```

**Содержимое:** Подробное описание продукта (Markdown)

### 6. Страница документации (Documentation Page)

**Файл:** `content/docs/[category]/[page].md`

**YAML frontmatter:**
```yaml
---
title: "Getting Started with Quiz Engine"
description: "Быстрый старт для разработчиков"
category: "quiz-engine" # для группировки
section: "getting-started" # для навигации
weight: 1 # Порядок в секции
toc: true # Показывать Table of Contents
api_reference: false
code_examples: true
last_updated: 2025-09-21T10:00:00Z
contributors: ["john-doe", "jane-smith"]
---
```

**Содержимое:** Техническая документация (Markdown)

### 7. Глобальные настройки сайта

**Файл:** `data/site.yaml`

```yaml
title: "InfoTech.io - Открытая экосистема IT-образования"
description: "Создаем качественные образовательные продукты с открытым исходным кодом"
keywords: ["образование", "IT", "open source", "hugo", "разработка"]
author: "InfoTech.io Organization"

# Социальные сети организации
social_links:
  github: "https://github.com/info-tech-io"
  linkedin: "https://linkedin.com/company/info-tech-io"
  telegram: "https://t.me/infotechgroup"
  email: "hello@info-tech.io"

# Настройки контента
content:
  posts_per_page: 10
  featured_posts_limit: 3
  recent_news_limit: 5
  featured_products_limit: 4

# Настройки навигации
navigation:
  main_menu:
    - name: "Продукты"
      url: "/products"
    - name: "Open Source"
      url: "/open-source"
    - name: "Блог"
      url: "/blog"
    - name: "О проекте"
      url: "/about"

  footer_menu:
    - name: "Документация"
      url: "/docs"
    - name: "Contributing"
      url: "/contributing"
    - name: "Roadmap"
      url: "/roadmap"

# SEO настройки
seo:
  google_analytics: "G-XXXXXXXXXX"
  google_search_console: "verification-code"
  schema_org_type: "Organization"
```

### 8. Конфигурация команды

**Файл:** `data/team.yaml`

```yaml
core_team:
  - slug: "founder"
    featured: true
    order: 1
  - slug: "lead-dev"
    featured: true
    order: 2

contributors:
  - slug: "contributor-1"
    contributions: ["frontend", "documentation"]
    since: "2025-08"
  - slug: "contributor-2"
    contributions: ["backend", "testing"]
    since: "2025-09"

# Статистика команды
stats:
  total_contributors: 15
  active_contributors: 8
  countries_represented: 5
  first_contribution_date: "2025-07-01"
```

## Технические особенности

### Hugo Taxonomies

```yaml
# В hugo.toml
[taxonomies]
  tag = "tags"
  author = "authors"
  category = "categories"
  product = "products"
  status = "statuses"
```

### Автоматическая генерация

**Списки и индексы:**
- `/blog/` - автоматический список всех статей
- `/news/` - автоматический список новостей
- `/products/` - каталог продуктов
- `/roadmap/` - визуальная дорожная карта
- `/team/` - страница команды

**RSS и Sitemap:**
- Автоматическая генерация RSS фидов
- XML Sitemap для SEO
- JSON Feed для современных читалок

### Валидация данных

**JSON Schema файлы:**
- `schemas/blog-post.json` - валидация статей блога
- `schemas/product.json` - валидация продуктов
- `schemas/author.json` - валидация авторов
- `schemas/roadmap-item.json` - валидация roadmap

**Pre-commit hooks:**
- Валидация YAML frontmatter
- Проверка обязательных полей
- Валидация ссылок и изображений

## Миграция из существующих моделей

### Соответствие моделей

| Headless CMS модель | Markdown эквивалент | Файл/директория |
|-------------------|-------------------|----------------|
| Blog Post | Blog Post | `content/blog/posts/` |
| News Item | News Item | `content/news/items/` |
| Author | Author | `content/authors/` |
| Roadmap Item | Roadmap Item | `content/roadmap/items/` |
| Educational Product | Product | `content/products/` |
| Global Settings | Site Data | `data/site.yaml` |

### Преимущества Markdown подхода

**Для разработчиков:**
- Весь контент в Git - полная история изменений
- Возможность Code Review для контента
- Простота локальной разработки
- Нет зависимости от внешних сервисов

**Для авторов:**
- Простой Markdown синтаксис
- Возможность работы в любом редакторе
- Предварительный просмотр в GitHub
- Совместная работа через Pull Requests

**Для архитектуры:**
- Единая экосистема с hugo-templates
- Автоматическая синхронизация
- Отсутствие Single Point of Failure
- Простота резервного копирования