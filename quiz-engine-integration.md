# Интеграция Quiz Engine в образовательную платформу

## Обзор

Данный документ описывает различные подходы к интеграции Quiz Engine в архитектуру образовательной платформы "Ось и спицы", включая рекомендуемое решение и альтернативные варианты.

## Рекомендуемый подход: Git Submodule

### Архитектура интеграции

Quiz Engine интегрируется в платформу как ключевой компонент для создания интерактивных проверочных заданий:

```
shared-hugo-base/
├── layouts/shortcodes/
│   └── quiz.html              # Hugo shortcode для встраивания тестов
├── static/quiz-engine/        # Git submodule с Quiz Engine
│   ├── src/quiz-engine/
│   │   ├── quiz-engine.mjs    # Основной модуль
│   │   ├── config.js          # Конфигурация
│   │   ├── i18n.js           # Интернационализация
│   │   └── quiz-types/       # Типы вопросов
│   └── quiz-examples/         # Примеры тестов
└── assets/scss/
    └── quiz-theme.scss        # Стили для интеграции с темой
```

### Принцип работы

1. **Git Submodule**: Quiz Engine подключается как submodule в `shared-hugo-base`
2. **Hugo Shortcode**: Простое встраивание через `{{< quiz src="/path/to/quiz.json" >}}`
3. **Автоматические обновления**: CI/CD pipeline отслеживает новые версии Quiz Engine
4. **Версионирование**: Контролируемые обновления через Git tags

### Использование в модулях

**В Markdown контенте:**
```markdown
# Урок: JavaScript Переменные

## Теория
Переменные в JavaScript используются для...

## Проверочное задание
{{< quiz src="/quizzes/variables-basic.json" >}}

## Дополнительное задание  
{{< quiz src="/quizzes/variables-advanced.json" id="advanced-quiz" >}}
```

**Структура тестов в модуле:**
```
module-javascript/
├── content/lessons/
├── static/quizzes/
│   ├── variables-basic.json
│   ├── functions-intro.json
│   └── objects-advanced.json
└── hugo.toml
```

### Hugo Shortcode

**layouts/shortcodes/quiz.html:**
```html
{{- $src := .Get "src" -}}
{{- $id := .Get "id" | default (printf "quiz-%d" now.Unix) -}}

<div class="quiz-container" 
     id="{{ $id }}"
     data-quiz-src="{{ $src }}">
  <p>Загрузка теста...</p>
</div>

{{- if not (.Page.Scratch.Get "quiz-engine-loaded") -}}
  {{- .Page.Scratch.Set "quiz-engine-loaded" true -}}
  <script type="module">
    import { initializeQuizzes } from '/quiz-engine/src/quiz-engine/quiz-engine.mjs';
    document.addEventListener('DOMContentLoaded', initializeQuizzes);
  </script>
{{- end -}}
```

### Конфигурация теста (quiz-data.json)

```json
{
  "config": {
    "type": "single-choice",
    "showExplanation": "all",
    "showTryAgainButton": true
  },
  "question": {
    "ru": "Какой тег является самым важным для SEO?",
    "en": "Which tag is most important for SEO?"
  },
  "answers": [
    {
      "text": { "ru": "<h1>", "en": "<h1>" },
      "correct": true,
      "description": {
        "ru": "Верно! H1 - основной заголовок страницы.",
        "en": "Correct! H1 is the main page heading."
      }
    },
    {
      "text": { "ru": "<h2>", "en": "<h2>" },
      "correct": false,
      "description": {
        "ru": "H2 - подзаголовок, менее важен для SEO.",
        "en": "H2 is a subheading, less important for SEO."
      }
    }
  ]
}
```

### Автоматическое обновление Quiz Engine

**GitHub Actions для shared-hugo-base:**
```yaml
name: Update Quiz Engine
on:
  repository_dispatch:
    types: [quiz-engine-updated]
  schedule:
    - cron: '0 2 * * 1' # Weekly check

jobs:
  update-submodule:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
      with:
        submodules: recursive
        token: ${{ secrets.PAT_TOKEN }}
    
    - name: Update Quiz Engine submodule
      run: |
        cd static/quiz-engine
        git fetch origin
        git checkout $(git describe --tags --abbrev=0)
        cd ../..
        git add static/quiz-engine
        git commit -m "chore: update Quiz Engine to $(cd static/quiz-engine && git describe --tags --abbrev=0)" || exit 0
        git push

    - name: Trigger module rebuilds
      run: |
        curl -X POST \
          -H "Authorization: token ${{ secrets.PAT_TOKEN }}" \
          -H "Accept: application/vnd.github.v3+json" \
          https://api.github.com/repos/yourorg/platform-hub/dispatches \
          -d '{"event_type":"shared-base-updated"}'
```

### Dockerfile для модулей с Quiz Engine

```dockerfile
# Многоэтапная сборка
FROM klakegg/hugo:ext-alpine AS builder
WORKDIR /src

# Копируем shared-hugo-base (включая Quiz Engine)
COPY --from=ghcr.io/yourorg/shared-hugo-base:latest /themes ./themes
COPY --from=ghcr.io/yourorg/shared-hugo-base:latest /layouts ./layouts
COPY --from=ghcr.io/yourorg/shared-hugo-base:latest /static ./static

# Копируем контент модуля
COPY content/ content/
COPY static/ static/
COPY hugo.toml .

RUN hugo --minify

# Production образ
FROM nginx:alpine
COPY --from=builder /src/public /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Преимущества подхода Git Submodule

- ✅ **Централизованность**: Все модули используют одну версию Quiz Engine
- ✅ **Версионирование**: Контролируемые обновления через Git tags
- ✅ **Простота использования**: Один shortcode в Markdown
- ✅ **Автоматизация**: Обновления Quiz Engine происходят автоматически
- ✅ **Производительность**: Статическая сборка включает все ресурсы
- ✅ **Кеширование**: CDN может кешировать Quiz Engine ресурсы
- ✅ **Отсутствие внешних зависимостей**: Не требует NPM registry или внешних CDN

### Недостатки подхода Git Submodule

- ⚠️ **Сложность для новичков**: Git submodule требует понимания специфичных команд
- ⚠️ **Синхронизация**: Необходимость координации обновлений между репозиториями
- ⚠️ **CI/CD complexity**: Усложнение пайплайнов сборки

## Альтернативный подход 1: NPM пакет

### Архитектура

Quiz Engine публикуется как NPM пакет и устанавливается в каждом модуле отдельно или в shared-hugo-base.

```
shared-hugo-base/
├── package.json               # Зависимость @yourorg/quiz-engine
├── node_modules/
│   └── @yourorg/quiz-engine/
├── layouts/shortcodes/
│   └── quiz.html
└── build-scripts/
    └── copy-quiz-assets.js    # Копирование из node_modules
```

### Пошаговая реализация

**1. Подготовка Quiz Engine для публикации:**
```json
// quiz/package.json
{
  "name": "@yourorg/quiz-engine",
  "version": "1.0.0",
  "main": "src/quiz-engine/quiz-engine.mjs",
  "files": [
    "src/",
    "quiz-examples/",
    "README.md"
  ],
  "scripts": {
    "prepublishOnly": "npm test"
  }
}
```

**2. Публикация пакета:**
```bash
cd quiz/
npm login
npm publish --access public
```

**3. Интеграция в shared-hugo-base:**
```json
// shared-hugo-base/package.json
{
  "name": "shared-hugo-base",
  "dependencies": {
    "@yourorg/quiz-engine": "^1.0.0"
  },
  "scripts": {
    "build": "node build-scripts/copy-quiz-assets.js && hugo"
  }
}
```

**4. Скрипт копирования ресурсов:**
```javascript
// build-scripts/copy-quiz-assets.js
const fs = require('fs');
const path = require('path');

const sourceDir = 'node_modules/@yourorg/quiz-engine';
const targetDir = 'static/quiz-engine';

// Копируем Quiz Engine в static папку
fs.cpSync(sourceDir, targetDir, { recursive: true });
console.log('Quiz Engine assets copied successfully');
```

**5. Dockerfile с NPM интеграцией:**
```dockerfile
FROM node:alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM klakegg/hugo:ext-alpine AS builder
WORKDIR /src

# Копируем Node.js зависимости
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/package*.json ./

# Копируем исходники
COPY . .

# Копируем Quiz Engine и собираем
RUN npm run build

FROM nginx:alpine
COPY --from=builder /src/public /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Преимущества NPM подхода

- ✅ **Стандартность**: Использование стандартного NPM workflow
- ✅ **Семантическое версионирование**: Четкие правила версионирования
- ✅ **Простота установки**: `npm install @yourorg/quiz-engine`
- ✅ **Dependency management**: NPM автоматически управляет зависимостями
- ✅ **Простота обновления**: `npm update @yourorg/quiz-engine`

### Недостатки NPM подхода

- ⚠️ **Публичная зависимость**: Требует публикации в NPM registry
- ⚠️ **Дополнительный этап сборки**: Необходимость копирования из node_modules
- ⚠️ **Node.js dependency**: Добавляет Node.js как зависимость в Docker образ
- ⚠️ **Registry dependency**: Зависимость от доступности NPM registry

## Альтернативный подход 2: Docker Multi-stage Copy

### Архитектура

Quiz Engine собирается в отдельном Docker образе и копируется на этапе сборки модулей.

```
quiz-engine/
├── Dockerfile                 # Сборка Quiz Engine в образ
└── src/

shared-hugo-base/
├── Dockerfile                 # Базовый образ с Quiz Engine
└── themes/

module/
├── Dockerfile                 # Копирует из shared-hugo-base
└── content/
```

### Реализация

**1. Dockerfile для Quiz Engine:**
```dockerfile
# quiz/Dockerfile
FROM alpine:latest
WORKDIR /quiz-engine
COPY src/ ./src/
COPY quiz-examples/ ./quiz-examples/
COPY package.json README.md ./

# Тесты и валидация
FROM node:alpine AS test
COPY . /app
WORKDIR /app
RUN npm test

# Финальный образ
FROM alpine:latest
WORKDIR /quiz-engine
COPY --from=0 /quiz-engine ./
```

**2. Базовый образ shared-hugo-base:**
```dockerfile
FROM ghcr.io/yourorg/quiz-engine:latest AS quiz
FROM klakegg/hugo:ext-alpine

# Копируем Quiz Engine
COPY --from=quiz /quiz-engine /quiz-engine

# Копируем темы и layouts
COPY themes/ /themes/
COPY layouts/ /layouts/
COPY static/ /static/

# Копируем Quiz Engine в static
RUN cp -r /quiz-engine /static/quiz-engine
```

**3. Dockerfile модуля:**
```dockerfile
FROM ghcr.io/yourorg/shared-hugo-base:latest AS base

WORKDIR /src
COPY content/ content/
COPY static/ static/
COPY hugo.toml .

RUN hugo --minify

FROM nginx:alpine
COPY --from=base /src/public /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### CI/CD для Docker подхода

```yaml
# quiz/.github/workflows/docker-build.yml
name: Build Quiz Engine Docker Image

on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: |
          ghcr.io/yourorg/quiz-engine:latest
          ghcr.io/yourorg/quiz-engine:${{ github.ref_name }}
        
    - name: Trigger shared-hugo-base rebuild
      run: |
        curl -X POST \
          -H "Authorization: token ${{ secrets.PAT_TOKEN }}" \
          https://api.github.com/repos/yourorg/shared-hugo-base/dispatches \
          -d '{"event_type":"quiz-engine-updated"}'
```

### Преимущества Docker Copy подхода

- ✅ **Полная изоляция**: Каждый модуль имеет зафиксированную версию Quiz Engine
- ✅ **Простота деплоя**: Один Docker образ содержит все зависимости
- ✅ **Нет external dependencies**: Не зависит от Git submodules или NPM
- ✅ **Кеширование слоев**: Docker кеширует неизменные слои
- ✅ **Rollback capability**: Простой откат к предыдущим версиям

### Недостатки Docker Copy подхода

- ⚠️ **Размер образов**: Дублирование Quiz Engine в каждом образе модуля
- ⚠️ **Сложность обновлений**: Требует пересборки всех модулей при обновлении
- ⚠️ **Registry dependency**: Зависимость от доступности Docker registry
- ⚠️ **Версионирование**: Сложнее отследить версии Quiz Engine в модулях

## Сравнительная таблица подходов

| Критерий | Git Submodule | NPM пакет | Docker Copy |
|----------|---------------|-----------|-------------|
| **Простота реализации** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Версионирование** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Обновления** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Размер билдов** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Независимость** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **CI/CD простота** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Отладка** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

## Рекомендации по выбору подхода

### Выберите Git Submodule, если:
- ✅ Команда знакома с Git submodules
- ✅ Нужна полная автономность (без внешних registry)
- ✅ Важна производительность (минимальный размер образов)
- ✅ Проект находится в стадии активной разработки

### Выберите NPM пакет, если:
- ✅ Команда предпочитает стандартные JavaScript инструменты
- ✅ Планируется использование Quiz Engine в других проектах
- ✅ Важно простое управление версиями
- ✅ Есть готовая инфраструктура NPM

### Выберите Docker Copy, если:
- ✅ Нужна максимальная изоляция компонентов
- ✅ Критична простота деплоя
- ✅ Команда имеет опыт с Docker multi-stage builds
- ✅ Размер образов не критичен

## Заключение

Для архитектуры образовательной платформы "Ось и спицы" **рекомендуется подход Git Submodule** как оптимальное сочетание производительности, контроля версий и автономности. Однако выбор конкретного подхода должен учитывать специфику команды разработки и требования проекта.

Все три подхода успешно решают задачу интеграции Quiz Engine в платформу и могут быть реализованы с учетом описанных преимуществ и недостатков.