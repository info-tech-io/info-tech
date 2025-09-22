# Стандартная структура docs/ для продуктов

## Обзор

Каждый продукт в экосистеме info-tech.io должен иметь стандартизированную структуру документации, обеспечивающую единообразный опыт для пользователей и упрощающую поддержку.

## Базовая структура

### Файловая организация

```
[product-repo]/
├── docs/                           # Корневая папка документации
│   ├── module.json                 # Конфигурация сборки документации
│   ├── content/                    # Контент документации
│   │   ├── _index.md              # Главная страница документации
│   │   ├── overview/              # Обзор продукта
│   │   │   ├── _index.md          # Что это и зачем
│   │   │   ├── features.md        # Ключевые возможности
│   │   │   ├── use-cases.md       # Сценарии использования
│   │   │   └── roadmap.md         # Планы развития
│   │   ├── getting-started/       # Быстрый старт
│   │   │   ├── _index.md          # Введение
│   │   │   ├── installation.md    # Установка
│   │   │   ├── configuration.md   # Базовая настройка
│   │   │   └── first-steps.md     # Первые шаги
│   │   ├── user-guide/           # Руководство пользователя
│   │   │   ├── _index.md          # Обзор возможностей
│   │   │   ├── basic-usage.md     # Основное использование
│   │   │   ├── advanced-features.md # Продвинутые возможности
│   │   │   ├── best-practices.md  # Лучшие практики
│   │   │   └── troubleshooting.md # Решение проблем
│   │   ├── developer/            # Для разработчиков
│   │   │   ├── _index.md          # Обзор для разработчиков
│   │   │   ├── api-reference.md   # Справочник API
│   │   │   ├── integration.md     # Интеграция
│   │   │   ├── examples/          # Примеры кода
│   │   │   │   ├── _index.md      # Список примеров
│   │   │   │   ├── basic-example.md
│   │   │   │   └── advanced-example.md
│   │   │   └── architecture.md    # Архитектура
│   │   ├── contributing/         # Руководство контрибьютора
│   │   │   ├── _index.md          # Как участвовать
│   │   │   ├── development.md     # Настройка среды разработки
│   │   │   ├── guidelines.md      # Руководящие принципы
│   │   │   ├── code-style.md      # Стиль кода
│   │   │   └── review-process.md  # Процесс ревью
│   │   └── reference/            # Справочная информация
│   │       ├── _index.md          # Справочники
│   │       ├── cli.md             # Команды CLI (если есть)
│   │       ├── configuration.md   # Справочник конфигурации
│   │       └── glossary.md        # Глоссарий терминов
│   ├── static/                   # Статические файлы
│   │   ├── images/               # Изображения для документации
│   │   │   ├── screenshots/      # Скриншоты интерфейса
│   │   │   ├── diagrams/         # Диаграммы и схемы
│   │   │   └── icons/            # Иконки и логотипы
│   │   └── files/                # Файлы для скачивания
│   └── .github/                  # GitHub конфигурация
       └── workflows/
           └── build-docs.yml     # CI/CD для документации
```

## Шаблоны файлов

### module.json (обязательный)

```json
{
  "name": "product-name-docs",
  "type": "documentation",
  "template": "documentation",
  "theme": "docs-theme",
  "title": "Product Name Documentation",
  "description": "Comprehensive documentation for Product Name",
  "url": "product.info-tech.io",
  "version": "1.0.0",
  "product": {
    "name": "Product Name",
    "repository": "https://github.com/info-tech-io/product-name",
    "website": "https://product.info-tech.io",
    "demo": "https://demo.product.info-tech.io"
  },
  "hugo": {
    "baseURL": "https://product.info-tech.io",
    "languageCode": "en",
    "title": "Product Name Docs",
    "params": {
      "version": "1.0.0",
      "edit_page": true,
      "search": true,
      "github_repo": "https://github.com/info-tech-io/product-name",
      "github_branch": "main",
      "github_subdir": "docs"
    }
  },
  "components": [
    "search",
    "table-of-contents",
    "edit-on-github",
    "last-modified",
    "version-selector"
  ],
  "navigation": {
    "main": [
      {"name": "Overview", "url": "/overview/", "weight": 10},
      {"name": "Getting Started", "url": "/getting-started/", "weight": 20},
      {"name": "User Guide", "url": "/user-guide/", "weight": 30},
      {"name": "Developer", "url": "/developer/", "weight": 40},
      {"name": "Contributing", "url": "/contributing/", "weight": 50},
      {"name": "Reference", "url": "/reference/", "weight": 60}
    ],
    "footer": [
      {"name": "GitHub", "url": "https://github.com/info-tech-io/product-name"},
      {"name": "info-tech.io", "url": "https://info-tech.io"},
      {"name": "Issues", "url": "https://github.com/info-tech-io/product-name/issues"}
    ]
  },
  "seo": {
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "author": "InfoTech.io",
    "robots": "index, follow"
  }
}
```

### content/_index.md (главная страница)

```markdown
---
title: "Product Name Documentation"
description: "Learn how to use and contribute to Product Name"
weight: 1
---

# Product Name Documentation

Welcome to the comprehensive documentation for Product Name, an open-source [brief description of what the product does].

## Quick Navigation

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">

### 🚀 [Getting Started](/getting-started/)
New to Product Name? Start here to get up and running quickly.

### 📖 [User Guide](/user-guide/)
Comprehensive guide for using all features of Product Name.

### 👩‍💻 [Developer Guide](/developer/)
API reference, integration guides, and examples for developers.

### 🤝 [Contributing](/contributing/)
Join our community and help improve Product Name.

### 📚 [Reference](/reference/)
Complete reference documentation and glossary.

### 🗺️ [Overview](/overview/)
Learn about Product Name's features and use cases.

</div>

## What is Product Name?

[2-3 paragraph description of the product, its purpose, and key benefits]

## Key Features

- **Feature 1**: Description of key feature
- **Feature 2**: Description of key feature
- **Feature 3**: Description of key feature

## Quick Example

[Brief code example or usage example]

```javascript
// Example usage
const example = new ProductName({
  option: 'value'
});
```

## Need Help?

- 📖 Check our [User Guide](/user-guide/) for detailed instructions
- 🐛 [Report a bug](https://github.com/info-tech-io/product-name/issues)
- 💬 [Join discussions](https://github.com/info-tech-io/product-name/discussions)
- 📧 [Contact us](mailto:hello@info-tech.io)

## Community

Product Name is developed by [info-tech.io](https://info-tech.io) and maintained by our amazing community of contributors.

- ⭐ [Star us on GitHub](https://github.com/info-tech-io/product-name)
- 🍴 [Fork and contribute](https://github.com/info-tech-io/product-name/fork)
- 📢 [Follow @infotechgroup](https://t.me/infotechgroup)
```

### overview/_index.md (обзор продукта)

```markdown
---
title: "Overview"
description: "Learn what Product Name is and why you should use it"
weight: 10
---

# Product Name Overview

## What is Product Name?

[Detailed explanation of what the product is, its purpose, and the problems it solves]

## Why Product Name?

### Problem Statement
[Description of the problem this product solves]

### Our Solution
[How Product Name addresses the problem]

### Key Benefits
- **Benefit 1**: Detailed explanation
- **Benefit 2**: Detailed explanation
- **Benefit 3**: Detailed explanation

## Core Features

### Feature 1
[Detailed description with examples]

### Feature 2
[Detailed description with examples]

### Feature 3
[Detailed description with examples]

## Use Cases

### Use Case 1: [Title]
[Description of who would use this and how]

### Use Case 2: [Title]
[Description of who would use this and how]

### Use Case 3: [Title]
[Description of who would use this and how]

## Architecture Overview

[High-level architecture diagram and explanation]

## Comparison with Alternatives

| Feature | Product Name | Alternative 1 | Alternative 2 |
|---------|--------------|---------------|---------------|
| Feature A | ✅ Yes | ❌ No | ⚠️ Limited |
| Feature B | ✅ Yes | ✅ Yes | ❌ No |

## Next Steps

- [Get started with installation](/getting-started/)
- [Explore the user guide](/user-guide/)
- [Check out examples](/developer/examples/)
```

### .github/workflows/build-docs.yml

```yaml
name: Build and Deploy Documentation

on:
  push:
    paths: ['docs/**']
    branches: [main]
  pull_request:
    paths: ['docs/**']

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install hugo-templates CLI
        run: npm install -g @info-tech-io/hugo-templates

      - name: Validate module.json
        run: hugo-templates validate docs/module.json

      - name: Build documentation
        run: hugo-templates build docs/

      - name: Deploy to GitHub Pages (staging)
        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
          destination_dir: docs

      - name: Deploy to production
        if: github.ref == 'refs/heads/main'
        run: |
          # Sync to production server
          rsync -avz --delete ./public/ user@server:/var/www/info-tech.io/product-subdomain/
          # Reload Apache
          ssh user@server 'sudo systemctl reload apache2'
        env:
          SSH_KEY: ${{ secrets.DEPLOY_SSH_KEY }}

      - name: Notify hub repository
        if: github.ref == 'refs/heads/main'
        run: |
          curl -X POST \
            -H "Authorization: token ${{ secrets.PAT_TOKEN }}" \
            -H "Accept: application/vnd.github.v3+json" \
            https://api.github.com/repos/info-tech-io/infotecha/dispatches \
            -d '{"event_type":"docs-updated","client_payload":{"product":"product-name","url":"https://product.info-tech.io"}}'
```

## CLI инструмент для инициализации

### Команда создания структуры

```bash
# В hugo-templates CLI
hugo-templates init-docs [product-name] [options]

# Опции:
--type=product          # Тип документации (product, tool, framework)
--language=en           # Основной язык (en, ru, multi)
--with-examples         # Включить секцию с примерами
--api-docs              # Включить API документацию
--cli-docs              # Включить CLI документацию
```

### Автоматические генерации

**При инициализации:**
- Создание базовой структуры папок
- Генерация module.json с базовыми настройками
- Создание шаблонов основных страниц
- Настройка GitHub workflow

**При сборке:**
- Валидация структуры и контента
- Генерация navigation меню
- Создание sitemap.xml
- Обновление "last modified" дат

## Валидация и контроль качества

### Pre-commit hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: validate-docs-structure
        name: Validate docs structure
        entry: hugo-templates validate-structure docs/
        language: system

      - id: markdown-lint
        name: Markdown lint
        entry: markdownlint docs/content/
        language: system

      - id: spell-check
        name: Spell check
        entry: cspell "docs/content/**/*.md"
        language: system

      - id: link-check
        name: Check links
        entry: markdown-link-check docs/content/
        language: system
```

### Автоматические проверки

**При каждом PR:**
- Структура соответствует стандарту
- Все обязательные файлы присутствуют
- Markdown синтаксис корректен
- Ссылки работают
- Орфография проверена

**При merge в main:**
- Полная сборка документации
- Деплой на staging (GitHub Pages)
- Деплой на production (поддомен)
- Уведомление hub репозитория

## Миграция существующих проектов

### Checklist для migration

- [ ] Создать структуру docs/ согласно стандарту
- [ ] Создать module.json с корректными настройками
- [ ] Мигрировать существующую документацию в новую структуру
- [ ] Настроить GitHub workflow для автоматической сборки
- [ ] Протестировать сборку локально
- [ ] Создать PR с новой документацией
- [ ] Настроить поддомен после merge

### Поддерживаемые форматы миграции

- **README.md** → overview/_index.md + getting-started/_index.md
- **Wiki страницы** → соответствующие разделы user-guide/
- **API документация** → developer/api-reference.md
- **Существующие docs/** → реструктуризация по новому стандарту