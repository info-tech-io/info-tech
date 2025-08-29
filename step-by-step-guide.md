# Пошаговый план реализации образовательной платформы

## Обзор проекта

Данный документ описывает полный пошаговый план создания образовательной платформы по архитектуре "Ось и спицы" с нуля до продакшн деплоя, включая контрольные процедуры и тестирование на каждом этапе.

---

## Этап 1: Настройка инфраструктуры разработки

### Шаг 1.1: Создание GitHub Organization

**Цель:** Создать централизованное место для всех репозиториев платформы

**Действия:**
```bash
# Создать GitHub Organization (через веб-интерфейс)
# Название: learning-platform-org (пример)
```

**Создаваемые репозитории:**
- `learning-platform-org/platform-hub` - Центральная ось
- `learning-platform-org/shared-hugo-base` - Общие компоненты
- `learning-platform-org/quiz-engine` - Quiz Engine (уже существует)
- `learning-platform-org/build-templates` - Шаблоны для создания модулей

**Контрольные процедуры:**
```bash
# Проверка создания organization
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/orgs/learning-platform-org

# Ожидаемый результат: JSON с информацией об организации
```

**Критерии успеха:**
- ✅ Organization создана
- ✅ Права доступа настроены
- ✅ Базовые настройки безопасности применены

---

### Шаг 1.2: Настройка секретов и токенов

**Цель:** Настроить безопасные переменные для CI/CD

**Действия:**
1. Создать Personal Access Token (PAT) с правами:
   - `repo` (полный доступ к репозиториям)
   - `workflow` (обновление GitHub Actions)
   - `write:packages` (публикация Docker образов)

2. Добавить секреты на уровне организации:
```bash
# В настройках Organization -> Secrets and variables -> Actions
PAT_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
DOCKER_USERNAME=your-username
DOCKER_PASSWORD=your-password
PROD_HOST=your-server-ip
PROD_USERNAME=deploy-user
PROD_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----...
```

**Контрольные процедуры:**
```bash
# Тест PAT токена
curl -H "Authorization: token $PAT_TOKEN" \
     https://api.github.com/user

# Тест Docker авторизации
echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
```

**Критерии успеха:**
- ✅ PAT токен создан и работает
- ✅ Секреты добавлены в organization
- ✅ Docker registry доступен

---

## Этап 2: Создание Quiz Engine (базовый компонент)

### Шаг 2.1: Подготовка Quiz Engine к интеграции

**Цель:** Подготовить Quiz Engine для использования в составе платформы

**Действия:**
```bash
# Клонировать существующий репозиторий
git clone https://github.com/A1eksMa/quiz.git
cd quiz

# Создать стабильную версию
npm test
git tag -a v1.0.0 -m "Stable release for platform integration"
git push origin v1.0.0
```

**Создаваемые файлы:**
- `INTEGRATION.md` - документация по интеграции
- `.github/workflows/release.yml` - автоматический релиз
- `package.json` - обновить для публикации

**Файл `.github/workflows/release.yml`:**
```yaml
name: Release Quiz Engine

on:
  push:
    tags: ['v*']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '18'
    - run: npm ci
    - run: npm test
    
  release:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Create Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Quiz Engine ${{ github.ref }}
        draft: false
        prerelease: false
        
    - name: Trigger platform updates
      run: |
        curl -X POST \
          -H "Authorization: token ${{ secrets.PAT_TOKEN }}" \
          -H "Accept: application/vnd.github.v3+json" \
          https://api.github.com/repos/learning-platform-org/shared-hugo-base/dispatches \
          -d '{"event_type":"quiz-engine-updated","client_payload":{"version":"${{ github.ref_name }}"}}'
```

**Контрольные процедуры:**
```bash
# Запуск тестов Quiz Engine
cd quiz && npm test

# Проверка сборки без ошибок
npm run build || echo "Build script needed"

# Валидация примеров квизов
node -e "
const fs = require('fs');
const examples = fs.readdirSync('quiz-examples');
examples.forEach(file => {
  if (file.endsWith('.json')) {
    const quiz = JSON.parse(fs.readFileSync(\`quiz-examples/\${file}\`));
    console.log(\`✅ \${file} - valid JSON\`);
  }
});
"
```

**Критерии успеха:**
- ✅ Все тесты проходят
- ✅ Создан стабильный tag v1.0.0
- ✅ CI/CD pipeline работает
- ✅ Все примеры квизов валидны

---

## Этап 3: Создание shared-hugo-base (общие компоненты)

### Шаг 3.1: Создание репозитория shared-hugo-base

**Цель:** Создать базовый репозиторий с общими компонентами для всех модулей

**Действия:**
```bash
# Создание репозитория
mkdir shared-hugo-base && cd shared-hugo-base
git init
git remote add origin https://github.com/learning-platform-org/shared-hugo-base.git
```

**Структура директорий:**
```
shared-hugo-base/
├── .github/workflows/
│   ├── test-integration.yml
│   ├── update-quiz-engine.yml
│   └── build-base-image.yml
├── themes/learning-platform/
│   ├── layouts/
│   │   ├── _default/
│   │   ├── partials/
│   │   └── shortcodes/
│   ├── static/
│   ├── assets/scss/
│   └── theme.toml
├── static/quiz-engine/          # Git submodule
├── scripts/
│   ├── validate-theme.js
│   └── test-quiz-integration.js
├── tests/
│   ├── integration/
│   └── fixtures/
├── Dockerfile
├── docker-compose.test.yml
└── README.md
```

**Контрольные процедуры:**
```bash
# Проверка структуры директорий
find . -type d | sort

# Ожидаемый вывод должен совпадать со структурой выше
```

---

### Шаг 3.2: Интеграция Quiz Engine как submodule

**Цель:** Подключить Quiz Engine к shared-hugo-base

**Действия:**
```bash
# Добавление Quiz Engine как submodule
git submodule add -b main https://github.com/A1eksMa/quiz.git static/quiz-engine
git submodule update --init --recursive

# Привязка к стабильной версии
cd static/quiz-engine
git checkout v1.0.0
cd ../..
git add static/quiz-engine
git commit -m "Add Quiz Engine v1.0.0 as submodule"
```

**Создание файла `.gitmodules`:**
```ini
[submodule "static/quiz-engine"]
	path = static/quiz-engine
	url = https://github.com/A1eksMa/quiz.git
	branch = main
```

**Контрольные процедуры:**
```bash
# Проверка submodule
git submodule status

# Проверка доступности Quiz Engine файлов
test -f static/quiz-engine/src/quiz-engine/quiz-engine.mjs && echo "✅ Quiz Engine files accessible" || echo "❌ Files missing"

# Валидация версии
cd static/quiz-engine && git describe --tags --exact-match
```

**Критерии успеха:**
- ✅ Submodule корректно добавлен
- ✅ Quiz Engine файлы доступны
- ✅ Зафиксирована стабильная версия

---

### Шаг 3.3: Создание Hugo темы

**Цель:** Создать базовую тему Hugo с интеграцией Quiz Engine

**Создание theme.toml:**
```toml
# themes/learning-platform/theme.toml
name = "Learning Platform Theme"
license = "MIT"
licenselink = "https://github.com/learning-platform-org/shared-hugo-base/blob/main/LICENSE"
description = "Base theme for learning platform modules with Quiz Engine integration"
homepage = "https://learn.example.com"
tags = ["education", "quiz", "learning"]
features = ["quiz-engine", "responsive", "multilingual"]
min_version = "0.110.0"

[author]
  name = "Learning Platform Team"
  homepage = "https://github.com/learning-platform-org"
```

**Создание базового layout:**
```html
<!-- themes/learning-platform/layouts/_default/baseof.html -->
<!DOCTYPE html>
<html lang="{{ site.LanguageCode | default "ru" }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ if .IsHome }}{{ site.Title }}{{ else }}{{ .Title }} | {{ site.Title }}{{ end }}</title>
    
    <!-- Base CSS -->
    {{ $style := resources.Get "scss/main.scss" | resources.ToCSS | resources.Minify }}
    <link rel="stylesheet" href="{{ $style.RelPermalink }}">
    
    <!-- Quiz Engine CSS (если есть) -->
    {{ if .Page.HasShortcode "quiz" }}
        <link rel="stylesheet" href="/quiz-engine/src/quiz-engine/styles.css">
    {{ end }}
</head>
<body>
    <header>
        <nav class="main-nav">
            <a href="{{ site.Params.platform.hub_url | default "/" }}">{{ site.Title }}</a>
            <!-- Навигация -->
        </nav>
    </header>
    
    <main>
        {{ block "main" . }}{{ end }}
    </main>
    
    <footer>
        <p>&copy; {{ now.Year }} Learning Platform</p>
    </footer>
    
    <!-- Quiz Engine JS (загружается только при наличии квизов) -->
    {{ if .Page.HasShortcode "quiz" }}
        <script type="module" src="/quiz-engine/src/quiz-engine/quiz-engine.mjs"></script>
    {{ end }}
</body>
</html>
```

**Создание shortcode для Quiz:**
```html
<!-- themes/learning-platform/layouts/shortcodes/quiz.html -->
{{- $src := .Get "src" -}}
{{- $id := .Get "id" | default (printf "quiz-%d" now.Unix) -}}

{{- if not $src -}}
    {{- errorf "Quiz shortcode requires 'src' parameter: %s" .Position -}}
{{- end -}}

<div class="quiz-container" 
     id="{{ $id }}"
     data-quiz-src="{{ $src }}"
     data-testid="quiz-container">
  <div class="quiz-loading">
    <p>🎯 Загрузка теста...</p>
  </div>
</div>

{{- if not (.Page.Scratch.Get "quiz-engine-loaded") -}}
  {{- .Page.Scratch.Set "quiz-engine-loaded" true -}}
  <script type="module">
    import { initializeQuizzes } from '/quiz-engine/src/quiz-engine/quiz-engine.mjs';
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initializeQuizzes);
    } else {
      initializeQuizzes();
    }
  </script>
{{- end -}}
```

**Базовые SCSS стили:**
```scss
// themes/learning-platform/assets/scss/main.scss
// Базовые переменные
:root {
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --success-color: #28a745;
  --danger-color: #dc3545;
  --warning-color: #ffc107;
  --info-color: #17a2b8;
  
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --border-radius: 0.375rem;
  --spacing-unit: 1rem;
}

// Базовые стили
* {
  box-sizing: border-box;
}

body {
  font-family: var(--font-family);
  line-height: 1.6;
  margin: 0;
  padding: 0;
  color: #333;
}

// Quiz Engine стили
.quiz-container {
  margin: var(--spacing-unit) 0;
  padding: var(--spacing-unit);
  border: 1px solid #ddd;
  border-radius: var(--border-radius);
  background: #f8f9fa;
  
  .quiz-loading {
    text-align: center;
    color: var(--secondary-color);
    
    p {
      margin: 0;
      font-style: italic;
    }
  }
}

// Адаптивность
@media (max-width: 768px) {
  .quiz-container {
    margin: calc(var(--spacing-unit) * 0.5) 0;
    padding: calc(var(--spacing-unit) * 0.5);
  }
}
```

**Контрольные процедуры:**
```bash
# Валидация Hugo темы
hugo new site test-site
cd test-site
cp -r ../themes themes/
echo 'theme = "learning-platform"' >> hugo.toml

# Тест сборки темы
hugo --themesDir ../themes

# Проверка сгенерированных файлов
test -f public/index.html && echo "✅ Theme builds successfully"

# Валидация HTML
# (требует установки html-validate или подобного)
npx html-validate public/index.html

# Очистка тестового сайта
cd .. && rm -rf test-site
```

**Критерии успеха:**
- ✅ Hugo тема собирается без ошибок
- ✅ Shortcode для квизов работает
- ✅ CSS стили применяются
- ✅ HTML валиден

---

### Шаг 3.4: Автоматическое тестирование интеграции

**Цель:** Создать автоматические тесты для проверки интеграции Quiz Engine с Hugo

**Создание тестового скрипта:**
```javascript
// scripts/test-quiz-integration.js
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class QuizIntegrationTester {
  constructor() {
    this.testResults = [];
    this.testSitePath = path.join(__dirname, '../test-site');
  }

  async runAllTests() {
    console.log('🧪 Starting Quiz Engine integration tests...\n');

    try {
      this.setupTestSite();
      await this.testQuizShortcode();
      await this.testQuizEngineFiles();
      await this.testHugoGeneration();
      this.cleanup();

      this.printResults();
      return this.testResults.every(result => result.passed);
    } catch (error) {
      console.error('❌ Test suite failed:', error.message);
      return false;
    }
  }

  setupTestSite() {
    console.log('📁 Setting up test site...');
    
    if (fs.existsSync(this.testSitePath)) {
      fs.rmSync(this.testSitePath, { recursive: true });
    }

    execSync(`hugo new site ${this.testSitePath}`, { stdio: 'pipe' });
    
    // Копируем тему
    const themePath = path.join(this.testSitePath, 'themes/learning-platform');
    fs.mkdirSync(path.dirname(themePath), { recursive: true });
    fs.cpSync(path.join(__dirname, '../themes/learning-platform'), themePath, { recursive: true });
    
    // Копируем Quiz Engine
    const quizPath = path.join(this.testSitePath, 'static/quiz-engine');
    fs.mkdirSync(path.dirname(quizPath), { recursive: true });
    fs.cpSync(path.join(__dirname, '../static/quiz-engine'), quizPath, { recursive: true });

    // Создаем базовую конфигурацию
    const config = `
baseURL = "https://test.example.com"
title = "Test Site"
theme = "learning-platform"

[params.platform]
  hub_url = "https://learn.example.com"
`;
    fs.writeFileSync(path.join(this.testSitePath, 'hugo.toml'), config);

    console.log('✅ Test site setup complete\n');
  }

  async testQuizShortcode() {
    console.log('🎯 Testing Quiz shortcode...');

    // Создаем тестовый контент с квизом
    const contentDir = path.join(this.testSitePath, 'content');
    fs.mkdirSync(contentDir, { recursive: true });

    const testContent = `---
title: "Test Page with Quiz"
---

# Test Quiz Page

This is a test page with a quiz.

{{< quiz src="/test-quiz.json" id="test-quiz" >}}

End of page.
`;

    fs.writeFileSync(path.join(contentDir, 'test-quiz.md'), testContent);

    // Создаем тестовый quiz JSON
    const testQuiz = {
      config: {
        type: "single-choice",
        showExplanation: "selected"
      },
      question: {
        ru: "Тестовый вопрос?",
        en: "Test question?"
      },
      answers: [
        {
          text: { ru: "Вариант А", en: "Option A" },
          correct: true,
          description: { ru: "Правильно", en: "Correct" }
        },
        {
          text: { ru: "Вариант Б", en: "Option B" },
          correct: false,
          description: { ru: "Неправильно", en: "Incorrect" }
        }
      ]
    };

    fs.writeFileSync(
      path.join(this.testSitePath, 'static/test-quiz.json'),
      JSON.stringify(testQuiz, null, 2)
    );

    this.addTestResult('Quiz shortcode content created', true);
    console.log('✅ Quiz shortcode test setup complete\n');
  }

  async testQuizEngineFiles() {
    console.log('🔧 Testing Quiz Engine files accessibility...');

    const requiredFiles = [
      'static/quiz-engine/src/quiz-engine/quiz-engine.mjs',
      'static/quiz-engine/src/quiz-engine/config.js',
      'static/quiz-engine/src/quiz-engine/i18n.js'
    ];

    let allFilesExist = true;
    for (const file of requiredFiles) {
      const fullPath = path.join(this.testSitePath, file);
      if (fs.existsSync(fullPath)) {
        console.log(`  ✅ ${file} exists`);
      } else {
        console.log(`  ❌ ${file} missing`);
        allFilesExist = false;
      }
    }

    this.addTestResult('Quiz Engine files accessible', allFilesExist);
    console.log('');
  }

  async testHugoGeneration() {
    console.log('🏗️ Testing Hugo site generation...');

    try {
      const output = execSync('hugo --minify', {
        cwd: this.testSitePath,
        encoding: 'utf8',
        stdio: 'pipe'
      });

      // Проверяем что сайт собрался
      const indexPath = path.join(this.testSitePath, 'public/index.html');
      const testPagePath = path.join(this.testSitePath, 'public/test-quiz/index.html');

      const indexExists = fs.existsSync(indexPath);
      const testPageExists = fs.existsSync(testPagePath);

      if (indexExists && testPageExists) {
        // Проверяем содержимое тестовой страницы
        const testPageContent = fs.readFileSync(testPagePath, 'utf8');
        const hasQuizContainer = testPageContent.includes('quiz-container');
        const hasQuizScript = testPageContent.includes('quiz-engine.mjs');

        console.log(`  ✅ Site generated successfully`);
        console.log(`  ✅ Index page: ${indexExists ? 'exists' : 'missing'}`);
        console.log(`  ✅ Test page: ${testPageExists ? 'exists' : 'missing'}`);
        console.log(`  ✅ Quiz container: ${hasQuizContainer ? 'found' : 'missing'}`);
        console.log(`  ✅ Quiz script: ${hasQuizScript ? 'found' : 'missing'}`);

        this.addTestResult('Hugo site generation', indexExists && testPageExists && hasQuizContainer && hasQuizScript);
      } else {
        console.log(`  ❌ Site generation incomplete`);
        this.addTestResult('Hugo site generation', false);
      }
    } catch (error) {
      console.log(`  ❌ Hugo generation failed: ${error.message}`);
      this.addTestResult('Hugo site generation', false);
    }
    console.log('');
  }

  addTestResult(testName, passed) {
    this.testResults.push({ testName, passed });
  }

  printResults() {
    console.log('📊 Test Results Summary:');
    console.log('=' * 50);
    
    this.testResults.forEach(result => {
      const status = result.passed ? '✅ PASS' : '❌ FAIL';
      console.log(`${status} ${result.testName}`);
    });

    const passedCount = this.testResults.filter(r => r.passed).length;
    const totalCount = this.testResults.length;
    
    console.log('=' * 50);
    console.log(`Total: ${passedCount}/${totalCount} tests passed`);

    if (passedCount === totalCount) {
      console.log('🎉 All tests passed! Quiz Engine integration is working correctly.');
    } else {
      console.log('❌ Some tests failed. Please check the integration.');
      process.exit(1);
    }
  }

  cleanup() {
    if (fs.existsSync(this.testSitePath)) {
      fs.rmSync(this.testSitePath, { recursive: true });
    }
    console.log('🧹 Test cleanup complete\n');
  }
}

// Запуск тестов
if (require.main === module) {
  const tester = new QuizIntegrationTester();
  tester.runAllTests().then(success => {
    process.exit(success ? 0 : 1);
  });
}

module.exports = QuizIntegrationTester;
```

**CI/CD workflow для тестирования:**
```yaml
# .github/workflows/test-integration.yml
name: Test Quiz Engine Integration

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  repository_dispatch:
    types: [quiz-engine-updated]

jobs:
  test-integration:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        submodules: recursive
        
    - name: Setup Hugo
      uses: peaceiris/actions-hugo@v2
      with:
        hugo-version: 'latest'
        extended: true
        
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        
    - name: Run integration tests
      run: node scripts/test-quiz-integration.js
      
    - name: Test theme validation
      run: |
        hugo new site temp-test
        cd temp-test
        cp -r ../themes ./
        echo 'theme = "learning-platform"' >> hugo.toml
        hugo --themesDir ./themes
        
    - name: Archive test artifacts
      if: failure()
      uses: actions/upload-artifact@v4
      with:
        name: test-artifacts
        path: |
          test-site/
          temp-test/
        retention-days: 5
```

**Контрольные процедуры:**
```bash
# Локальный запуск тестов
cd shared-hugo-base
node scripts/test-quiz-integration.js

# Проверка CI/CD
git add . && git commit -m "Add integration tests"
git push origin main

# Мониторинг GitHub Actions
# Проверить что тесты прошли успешно в GitHub Actions
```

**Критерии успеха:**
- ✅ Все интеграционные тесты проходят
- ✅ Hugo собирает сайт с квизами
- ✅ Quiz Engine файлы доступны
- ✅ CI/CD pipeline работает

---

### Шаг 3.5: Создание Docker образа для shared-hugo-base

**Цель:** Создать базовый Docker образ с Hugo и Quiz Engine

**Dockerfile:**
```dockerfile
# shared-hugo-base/Dockerfile
FROM klakegg/hugo:ext-alpine AS hugo-base

# Установка дополнительных зависимостей
RUN apk add --no-cache git nodejs npm

# Рабочая директория
WORKDIR /shared-base

# Копируем все компоненты
COPY themes/ /shared-base/themes/
COPY static/ /shared-base/static/
COPY scripts/ /shared-base/scripts/

# Проверяем доступность Quiz Engine
RUN test -f /shared-base/static/quiz-engine/src/quiz-engine/quiz-engine.mjs || \
    (echo "❌ Quiz Engine not found" && exit 1)

# Валидация темы
COPY scripts/validate-theme.js /shared-base/
RUN node validate-theme.js

# Создание тестового сайта для проверки
RUN hugo new site /tmp/test-site && \
    cp -r /shared-base/themes /tmp/test-site/ && \
    cp -r /shared-base/static /tmp/test-site/ && \
    echo 'theme = "learning-platform"' >> /tmp/test-site/hugo.toml && \
    cd /tmp/test-site && \
    hugo --minify && \
    echo "✅ Shared Hugo base validated successfully"

# Финальная стадия - минимальный образ
FROM alpine:latest
WORKDIR /shared-base

# Установка только git (для submodules)
RUN apk add --no-cache git

# Копируем проверенные компоненты
COPY --from=hugo-base /shared-base/themes/ ./themes/
COPY --from=hugo-base /shared-base/static/ ./static/

# Метаданные
LABEL org.opencontainers.image.title="Shared Hugo Base" \
      org.opencontainers.image.description="Base Hugo theme with Quiz Engine integration" \
      org.opencontainers.image.source="https://github.com/learning-platform-org/shared-hugo-base" \
      org.opencontainers.image.version="1.0.0"

# Точка входа - копирование файлов
CMD ["sh", "-c", "echo 'Shared Hugo Base ready for use'"]
```

**Скрипт валидации темы:**
```javascript
// scripts/validate-theme.js
const fs = require('fs');
const path = require('path');

console.log('🔍 Validating Hugo theme...');

// Проверяем обязательные файлы темы
const requiredFiles = [
  'themes/learning-platform/theme.toml',
  'themes/learning-platform/layouts/_default/baseof.html',
  'themes/learning-platform/layouts/shortcodes/quiz.html'
];

let validationPassed = true;

requiredFiles.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`✅ ${file} exists`);
  } else {
    console.log(`❌ ${file} missing`);
    validationPassed = false;
  }
});

// Проверяем Quiz Engine
const quizEngineFiles = [
  'static/quiz-engine/src/quiz-engine/quiz-engine.mjs',
  'static/quiz-engine/src/quiz-engine/config.js'
];

quizEngineFiles.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`✅ ${file} exists`);
  } else {
    console.log(`❌ ${file} missing`);
    validationPassed = false;
  }
});

if (!validationPassed) {
  console.error('❌ Theme validation failed');
  process.exit(1);
}

console.log('✅ Theme validation passed');
```

**Docker Compose для тестирования:**
```yaml
# docker-compose.test.yml
version: '3.8'

services:
  test-shared-base:
    build:
      context: .
      dockerfile: Dockerfile
    image: learning-platform/shared-hugo-base:test
    volumes:
      - ./test-results:/tmp/test-results
    command: |
      sh -c "
        echo '🧪 Testing shared-hugo-base Docker image...'
        
        # Проверяем файлы темы
        test -f themes/learning-platform/theme.toml && echo '✅ Theme config found' || exit 1
        test -f themes/learning-platform/layouts/shortcodes/quiz.html && echo '✅ Quiz shortcode found' || exit 1
        
        # Проверяем Quiz Engine
        test -f static/quiz-engine/src/quiz-engine/quiz-engine.mjs && echo '✅ Quiz Engine found' || exit 1
        
        echo '✅ All tests passed'
        echo 'success' > /tmp/test-results/result.txt
      "
    
  test-integration:
    depends_on:
      - test-shared-base
    image: klakegg/hugo:ext-alpine
    volumes:
      - .:/workspace
      - ./test-results:/tmp/test-results
    working_dir: /workspace
    command: |
      sh -c "
        # Проверяем результат предыдущего теста
        if [ ! -f /tmp/test-results/result.txt ] || [ \$(cat /tmp/test-results/result.txt) != 'success' ]; then
          echo '❌ Previous test failed'
          exit 1
        fi
        
        echo '🏗️ Testing Hugo build with shared base...'
        
        # Создаем тестовый сайт
        hugo new site /tmp/integration-test
        cd /tmp/integration-test
        
        # Копируем компоненты из образа
        mkdir -p themes static
        cp -r /workspace/themes/* themes/
        cp -r /workspace/static/* static/
        
        # Конфигурация
        echo 'theme = \"learning-platform\"' >> hugo.toml
        
        # Создаем тестовую страницу с квизом
        mkdir -p content
        cat > content/_index.md << 'EOF'
---
title: Integration Test
---
# Test Page
{{< quiz src=\"/test-quiz.json\" >}}
EOF
        
        # Создаем тестовый квиз
        cat > static/test-quiz.json << 'EOF'
{
  \"config\": { \"type\": \"single-choice\" },
  \"question\": { \"ru\": \"Тест?\", \"en\": \"Test?\" },
  \"answers\": [
    { \"text\": { \"ru\": \"Да\", \"en\": \"Yes\" }, \"correct\": true }
  ]
}
EOF
        
        # Собираем сайт
        hugo --minify
        
        # Проверяем результат
        test -f public/index.html && echo '✅ Site built successfully'
        grep -q 'quiz-container' public/index.html && echo '✅ Quiz shortcode rendered'
        
        echo '✅ Integration test passed'
      "
```

**CI/CD для сборки образа:**
```yaml
# .github/workflows/build-base-image.yml
name: Build Shared Hugo Base Image

on:
  push:
    branches: [main]
    tags: ['v*']
  repository_dispatch:
    types: [quiz-engine-updated]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        submodules: recursive
        
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
      
    - name: Login to GitHub Container Registry
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ghcr.io/${{ github.repository }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          type=raw,value=latest,enable={{is_default_branch}}
          
    - name: Build and test
      run: |
        # Сборка для тестирования
        docker build -t shared-hugo-base:test .
        
        # Создание директории для результатов
        mkdir -p test-results
        
        # Запуск тестов
        docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
        
        # Проверка результатов
        if [ ! -f test-results/result.txt ]; then
          echo "❌ Test results not found"
          exit 1
        fi
        
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
        
    - name: Trigger dependent builds
      if: github.ref == 'refs/heads/main'
      run: |
        # Уведомляем platform-hub об обновлении
        curl -X POST \
          -H "Authorization: token ${{ secrets.PAT_TOKEN }}" \
          -H "Accept: application/vnd.github.v3+json" \
          https://api.github.com/repos/${{ github.repository_owner }}/platform-hub/dispatches \
          -d '{"event_type":"shared-base-updated","client_payload":{"image_tag":"${{ steps.meta.outputs.tags }}"}}'
```

**Контрольные процедуры:**
```bash
# Локальная сборка и тест
docker build -t shared-hugo-base:test .

# Запуск тестов
mkdir test-results
docker-compose -f docker-compose.test.yml up --build

# Проверка результата
cat test-results/result.txt

# Тест интеграции
docker run --rm -v $(pwd):/workspace shared-hugo-base:test sh -c "
  hugo new site /tmp/test
  cd /tmp/test
  cp -r /workspace/themes ./
  cp -r /workspace/static ./
  echo 'theme = \"learning-platform\"' >> hugo.toml
  hugo --minify
  test -f public/index.html && echo '✅ Integration test passed'
"
```

**Критерии успеха:**
- ✅ Docker образ собирается без ошибок
- ✅ Все тесты в контейнере проходят
- ✅ Hugo тема работает в контейнере
- ✅ CI/CD pipeline публикует образ
- ✅ Образ доступен в GitHub Container Registry

---

## Этап 4: Создание build-templates (шаблоны для модулей)

### Шаг 4.1: Создание репозитория build-templates

**Цель:** Создать шаблоны для быстрого создания новых учебных модулей

**Действия:**
```bash
mkdir build-templates && cd build-templates
git init
git remote add origin https://github.com/learning-platform-org/build-templates.git
```

**Структура репозитория:**
```
build-templates/
├── .github/workflows/
│   └── validate-templates.yml
├── templates/
│   ├── module-basic/
│   │   ├── content/
│   │   ├── static/
│   │   ├── hugo.toml.template
│   │   ├── Dockerfile.template
│   │   └── .github/workflows/deploy.yml.template
│   ├── module-advanced/
│   └── module-quiz-heavy/
├── cli/
│   ├── create-module.js
│   ├── validate-module.js
│   └── package.json
├── scripts/
│   ├── test-templates.js
│   └── validate-all.js
└── README.md
```

**Контрольные процедуры:**
```bash
# Создание структуры
mkdir -p templates/module-basic/{content,static,.github/workflows}
mkdir -p templates/module-advanced/{content,static,.github/workflows}
mkdir -p cli scripts

# Проверка структуры
find . -type d | sort
```

---

### Шаг 4.2: Создание базового шаблона модуля

**Цель:** Создать шаблон для типичного учебного модуля

**Создание hugo.toml.template:**
```toml
# templates/module-basic/hugo.toml.template
baseURL = "https://{{.subdomain}}.learn.example.com"
languageCode = "{{.language_code}}"
title = "{{.module_title}}"
theme = "learning-platform"

# Конфигурация модуля
[params]
  course_name = "{{.module_title}}"
  course_category = "{{.category}}"
  course_difficulty = "{{.difficulty}}"
  course_duration = "{{.duration}}"
  
  # Информация о платформе
  [params.platform]
    hub_url = "https://learn.example.com"
    navigation_enabled = true
    
  # Quiz Engine настройки
  [params.quiz]
    default_language = "{{.language_code}}"
    show_progress = true
    allow_retry = {{.allow_retry}}

# Меню навигации
[[menu.main]]
  name = "Главная"
  url = "/"
  weight = 10
  
[[menu.main]]
  name = "Уроки"
  url = "/lessons/"
  weight = 20
  
[[menu.main]]
  name = "Тесты"
  url = "/quizzes/"
  weight = 30

# Настройки разметки
[markup]
  [markup.goldmark]
    [markup.goldmark.renderer]
      unsafe = true
  [markup.highlight]
    style = "github"
    lineNos = true
```

**Dockerfile.template:**
```dockerfile
# templates/module-basic/Dockerfile.template
# Многоэтапная сборка для модуля {{.module_name}}
FROM ghcr.io/learning-platform-org/shared-hugo-base:latest AS base

# Стадия сборки Hugo сайта
FROM klakegg/hugo:ext-alpine AS builder

WORKDIR /src

# Копируем shared компоненты из базового образа  
COPY --from=base /shared-base/themes ./themes
COPY --from=base /shared-base/static ./static

# Копируем контент модуля
COPY content/ content/
COPY static/ static/
COPY hugo.toml .

# Сборка сайта
RUN hugo --minify --enableGitInfo

# Валидация сборки
RUN test -f public/index.html || (echo "❌ Build failed: no index.html" && exit 1)
RUN find public -name "*.html" -exec grep -l "quiz-container" {} \; | head -1 | \
    xargs test -f && echo "✅ Quiz integration validated" || \
    echo "⚠️ No quizzes found (this may be intentional)"

# Production стадия с nginx
FROM nginx:alpine

# Копируем собранный сайт
COPY --from=builder /src/public /usr/share/nginx/html

# Конфигурация nginx для SPA-подобного поведения
COPY nginx.conf /etc/nginx/nginx.conf

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

# Метаданные
LABEL org.opencontainers.image.title="{{.module_title}}" \
      org.opencontainers.image.description="Learning module: {{.module_title}}" \
      org.opencontainers.image.source="https://github.com/{{.github_org}}/{{.module_name}}" \
      org.opencontainers.image.version="1.0.0" \
      learning.platform.module="{{.module_name}}" \
      learning.platform.category="{{.category}}" \
      learning.platform.difficulty="{{.difficulty}}"

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**GitHub Actions workflow template:**
```yaml
# templates/module-basic/.github/workflows/deploy.yml.template
name: Deploy {{.module_title}} Module

on:
  push:
    branches: [main]
    paths:
      - 'content/**'
      - 'static/**'
      - 'hugo.toml'
      - 'Dockerfile'
  repository_dispatch:
    types: [shared-base-updated, content-updated]
  workflow_dispatch:

env:
  MODULE_NAME: {{.module_name}}
  IMAGE_NAME: ghcr.io/${{ github.repository }}

jobs:
  validate-content:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Validate quiz files
      run: |
        echo "🔍 Validating quiz JSON files..."
        find static -name "*.json" -type f | while read file; do
          if jq empty "$file" 2>/dev/null; then
            echo "✅ $file - valid JSON"
          else
            echo "❌ $file - invalid JSON"
            exit 1
          fi
        done
        
    - name: Check content structure
      run: |
        echo "📁 Checking content structure..."
        
        # Проверяем обязательные файлы
        test -f hugo.toml || (echo "❌ hugo.toml missing" && exit 1)
        test -f content/_index.md || (echo "❌ content/_index.md missing" && exit 1)
        
        echo "✅ Content structure valid"
        
    - name: Lint Markdown
      uses: DavidAnson/markdownlint-cli2-action@v13
      with:
        globs: 'content/**/*.md'

  build-and-test:
    needs: validate-content
    runs-on: ubuntu-latest
    
    outputs:
      image-digest: ${{ steps.build.outputs.digest }}
      
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
      
    - name: Login to GitHub Container Registry
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}
          
    - name: Build and push
      id: build
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
        
    - name: Test container
      run: |
        echo "🧪 Testing built container..."
        
        # Запускаем контейнер для теста
        docker run -d --name test-module -p 8080:80 ${{ env.IMAGE_NAME }}:latest
        
        # Ждем запуска
        sleep 10
        
        # Проверяем доступность
        curl -f http://localhost:8080/ || (echo "❌ Site not accessible" && exit 1)
        
        # Проверяем наличие Quiz Engine (если есть квизы)
        if find static -name "*.json" | grep -q .; then
          curl -s http://localhost:8080/ | grep -q "quiz-container" && \
            echo "✅ Quiz integration working" || \
            echo "⚠️ Quiz containers not found"
        fi
        
        # Очистка
        docker stop test-module
        docker rm test-module
        
        echo "✅ Container test passed"

  deploy:
    needs: build-and-test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to production
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.PROD_HOST }}
        username: ${{ secrets.PROD_USERNAME }}
        key: ${{ secrets.PROD_SSH_KEY }}
        script: |
          echo "🚀 Deploying {{.module_name}} module..."
          
          cd /opt/learning-platform
          
          # Обновляем docker-compose если нужно
          if ! grep -q "{{.module_name}}:" docker-compose.yml; then
            echo "📝 Adding module to docker-compose.yml..."
            # Здесь может быть скрипт добавления сервиса
          fi
          
          # Получаем новый образ
          docker pull ${{ env.IMAGE_NAME }}:latest
          
          # Обновляем сервис
          docker-compose up -d --no-deps {{.module_name}}
          
          # Проверяем доступность
          sleep 15
          curl -f https://{{.subdomain}}.learn.example.com/ && \
            echo "✅ {{.module_title}} deployed successfully" || \
            echo "❌ Deployment verification failed"
            
    - name: Update module registry
      uses: peter-evans/repository-dispatch@v3
      with:
        token: ${{ secrets.PAT_TOKEN }}
        repository: learning-platform-org/platform-hub
        event-type: module-updated
        client-payload: |
          {
            "module_name": "{{.module_name}}",
            "module_title": "{{.module_title}}",
            "subdomain": "{{.subdomain}}",
            "category": "{{.category}}",
            "difficulty": "{{.difficulty}}",
            "image_digest": "${{ needs.build-and-test.outputs.image-digest }}",
            "updated_at": "${{ github.event.head_commit.timestamp }}"
          }
```

**Базовая структура контента:**
```markdown
<!-- templates/module-basic/content/_index.md -->
---
title: "{{.module_title}}"
description: "{{.module_description}}"
weight: 10
---

# {{.module_title}}

{{.module_description}}

## О курсе

Этот курс поможет вам изучить основы {{.module_subject}}.

### Что вы изучите:

- Основные концепции {{.module_subject}}
- Практические примеры
- Интерактивные упражнения

## Структура курса

{{< children description="true" depth="2" >}}

## Начать обучение

Готовы начать? Переходите к [первому уроку](lessons/lesson-01/).
```

```markdown
<!-- templates/module-basic/content/lessons/_index.md -->
---
title: "Уроки"
weight: 20
---

# Уроки курса "{{.module_title}}"

Изучайте материал последовательно, урок за уроком.
```

```markdown
<!-- templates/module-basic/content/lessons/lesson-01.md -->
---
title: "Урок 1: Введение"
weight: 10
---

# Урок 1: Введение в {{.module_subject}}

## Теория

Здесь размещается теоретический материал урока.

## Практика

Практические примеры и упражнения.

## Проверочное задание

{{< quiz src="/quizzes/lesson-01-basic.json" >}}

## Дополнительные материалы

- Ссылка на дополнительные ресурсы
- Рекомендуемое чтение
```

**Контрольные процедуры:**
```bash
# Проверка шаблонов
ls -la templates/module-basic/
test -f templates/module-basic/hugo.toml.template
test -f templates/module-basic/Dockerfile.template
test -f templates/module-basic/.github/workflows/deploy.yml.template

# Валидация YAML в шаблоне
yq eval 'true' templates/module-basic/.github/workflows/deploy.yml.template
```

**Критерии успеха:**
- ✅ Все файлы шаблона созданы
- ✅ YAML файлы валидны
- ✅ Dockerfile template корректен
- ✅ Контент структура логична

---

### Шаг 4.3: Создание CLI инструмента для генерации модулей

**Цель:** Создать инструмент командной строки для быстрого создания модулей

**package.json для CLI:**
```json
{
  "name": "@learning-platform/module-cli",
  "version": "1.0.0",
  "description": "CLI tool for creating learning platform modules",
  "main": "create-module.js",
  "bin": {
    "create-module": "./create-module.js",
    "validate-module": "./validate-module.js"
  },
  "scripts": {
    "test": "node test-cli.js",
    "install-global": "npm install -g ."
  },
  "dependencies": {
    "inquirer": "^9.2.0",
    "mustache": "^4.2.0",
    "chalk": "^4.1.2",
    "fs-extra": "^11.1.0",
    "yargs": "^17.7.0",
    "ajv": "^8.12.0"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  },
  "keywords": ["learning-platform", "hugo", "education", "cli"],
  "license": "MIT"
}
```

**CLI инструмент create-module.js:**
```javascript
#!/usr/bin/env node
// cli/create-module.js

const fs = require('fs-extra');
const path = require('path');
const inquirer = require('inquirer');
const Mustache = require('mustache');
const chalk = require('chalk');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

class ModuleCreator {
  constructor() {
    this.templatesPath = path.join(__dirname, '../templates');
    this.outputPath = process.cwd();
  }

  async createModule(options = {}) {
    console.log(chalk.blue('🚀 Learning Platform Module Creator\n'));

    // Получаем параметры модуля
    const moduleConfig = await this.getModuleConfig(options);
    
    // Выбираем шаблон
    const template = await this.selectTemplate(options.template);
    
    // Создаем модуль
    await this.generateModule(moduleConfig, template);
    
    // Постобработка
    await this.postProcess(moduleConfig);
    
    console.log(chalk.green('\n✅ Module created successfully!'));
    this.showNextSteps(moduleConfig);
  }

  async getModuleConfig(options) {
    const questions = [
      {
        type: 'input',
        name: 'module_name',
        message: 'Module name (kebab-case):',
        default: options.name,
        validate: (input) => {
          if (!/^[a-z0-9-]+$/.test(input)) {
            return 'Please use only lowercase letters, numbers, and hyphens';
          }
          return true;
        }
      },
      {
        type: 'input', 
        name: 'module_title',
        message: 'Module title:',
        default: (answers) => answers.module_name.split('-').map(word => 
          word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ')
      },
      {
        type: 'input',
        name: 'module_description', 
        message: 'Module description:',
        default: (answers) => `Learn ${answers.module_title} step by step`
      },
      {
        type: 'input',
        name: 'module_subject',
        message: 'Subject area:',
        default: (answers) => answers.module_title
      },
      {
        type: 'list',
        name: 'category',
        message: 'Module category:',
        choices: [
          'programming',
          'web-development', 
          'data-science',
          'design',
          'devops',
          'mobile',
          'other'
        ],
        default: options.category
      },
      {
        type: 'list',
        name: 'difficulty',
        message: 'Difficulty level:',
        choices: ['beginner', 'intermediate', 'advanced'],
        default: 'beginner'
      },
      {
        type: 'input',
        name: 'duration',
        message: 'Estimated duration:',
        default: '20 hours'
      },
      {
        type: 'input',
        name: 'subdomain',
        message: 'Subdomain:',
        default: (answers) => answers.module_name
      },
      {
        type: 'list',
        name: 'language_code',
        message: 'Primary language:',
        choices: ['ru', 'en'],
        default: 'ru'
      },
      {
        type: 'confirm',
        name: 'allow_retry',
        message: 'Allow quiz retries?',
        default: true
      },
      {
        type: 'input',
        name: 'github_org',
        message: 'GitHub organization:',
        default: 'learning-platform-org'
      }
    ];

    // Фильтруем вопросы если параметры уже заданы
    const filteredQuestions = questions.filter(q => !options[q.name]);
    const answers = await inquirer.prompt(filteredQuestions);
    
    return { ...options, ...answers };
  }

  async selectTemplate(defaultTemplate) {
    if (defaultTemplate) return defaultTemplate;

    const templates = await fs.readdir(this.templatesPath);
    const templateChoices = templates
      .filter(name => fs.statSync(path.join(this.templatesPath, name)).isDirectory())
      .map(name => ({
        name: `${name} - ${this.getTemplateDescription(name)}`,
        value: name
      }));

    const { template } = await inquirer.prompt([{
      type: 'list',
      name: 'template',
      message: 'Choose module template:',
      choices: templateChoices
    }]);

    return template;
  }

  getTemplateDescription(templateName) {
    const descriptions = {
      'module-basic': 'Standard module with lessons and quizzes',
      'module-advanced': 'Advanced module with complex structure',
      'module-quiz-heavy': 'Module focused on interactive quizzes'
    };
    return descriptions[templateName] || 'Custom template';
  }

  async generateModule(config, template) {
    const templatePath = path.join(this.templatesPath, template);
    const outputPath = path.join(this.outputPath, config.module_name);

    console.log(chalk.blue(`\n📂 Creating module in: ${outputPath}`));

    // Проверяем что директория не существует
    if (await fs.pathExists(outputPath)) {
      const { overwrite } = await inquirer.prompt([{
        type: 'confirm',
        name: 'overwrite',
        message: `Directory ${config.module_name} already exists. Overwrite?`,
        default: false
      }]);
      
      if (!overwrite) {
        console.log(chalk.yellow('❌ Operation cancelled'));
        return;
      }
      
      await fs.remove(outputPath);
    }

    // Копируем и обрабатываем файлы
    await this.copyAndProcessFiles(templatePath, outputPath, config);
  }

  async copyAndProcessFiles(templatePath, outputPath, config) {
    const files = await this.getAllFiles(templatePath);
    
    for (const file of files) {
      const relativePath = path.relative(templatePath, file);
      const outputFile = path.join(outputPath, relativePath);
      
      // Создаем директорию если нужно
      await fs.ensureDir(path.dirname(outputFile));
      
      if (file.endsWith('.template')) {
        // Обрабатываем шаблон и убираем .template из имени
        const finalOutputFile = outputFile.replace('.template', '');
        await this.processTemplate(file, finalOutputFile, config);
        console.log(chalk.green(`  ✅ ${relativePath.replace('.template', '')}`));
      } else {
        // Просто копируем файл
        await fs.copy(file, outputFile);
        console.log(chalk.gray(`  📄 ${relativePath}`));
      }
    }
  }

  async getAllFiles(dir) {
    const files = [];
    const items = await fs.readdir(dir);
    
    for (const item of items) {
      const fullPath = path.join(dir, item);
      const stat = await fs.stat(fullPath);
      
      if (stat.isDirectory()) {
        const subFiles = await this.getAllFiles(fullPath);
        files.push(...subFiles);
      } else {
        files.push(fullPath);
      }
    }
    
    return files;
  }

  async processTemplate(templateFile, outputFile, config) {
    const template = await fs.readFile(templateFile, 'utf8');
    const rendered = Mustache.render(template, config);
    await fs.writeFile(outputFile, rendered);
  }

  async postProcess(config) {
    console.log(chalk.blue('\n🔧 Post-processing module...'));

    const modulePath = path.join(this.outputPath, config.module_name);
    
    // Создаем примеры квизов
    await this.createSampleQuizzes(modulePath, config);
    
    // Инициализируем git репозиторий
    await this.initializeGitRepo(modulePath, config);
    
    // Создаем README
    await this.createReadme(modulePath, config);
  }

  async createSampleQuizzes(modulePath, config) {
    const quizzesDir = path.join(modulePath, 'static', 'quizzes');
    await fs.ensureDir(quizzesDir);

    const sampleQuiz = {
      config: {
        type: "single-choice",
        showExplanation: "all"
      },
      question: {
        ru: `Что изучает курс "${config.module_title}"?`,
        en: `What does the "${config.module_title}" course study?`
      },
      answers: [
        {
          text: { 
            ru: config.module_subject, 
            en: config.module_subject 
          },
          correct: true,
          description: {
            ru: "Правильно! Это основная тема курса.",
            en: "Correct! This is the main topic of the course."
          }
        },
        {
          text: { 
            ru: "Что-то другое", 
            en: "Something else" 
          },
          correct: false,
          description: {
            ru: "Неверно. Попробуйте еще раз.",
            en: "Incorrect. Try again."
          }
        }
      ]
    };

    await fs.writeFile(
      path.join(quizzesDir, 'lesson-01-basic.json'),
      JSON.stringify(sampleQuiz, null, 2)
    );

    console.log(chalk.green('  ✅ Sample quiz created'));
  }

  async initializeGitRepo(modulePath, config) {
    try {
      const { execSync } = require('child_process');
      
      execSync('git init', { cwd: modulePath, stdio: 'pipe' });
      execSync('git add .', { cwd: modulePath, stdio: 'pipe' });
      execSync(`git commit -m "Initial commit: ${config.module_title} module"`, 
        { cwd: modulePath, stdio: 'pipe' });
      
      console.log(chalk.green('  ✅ Git repository initialized'));
    } catch (error) {
      console.log(chalk.yellow('  ⚠️ Git initialization skipped'));
    }
  }

  async createReadme(modulePath, config) {
    const readme = `# ${config.module_title}

${config.module_description}

## О модуле

- **Категория:** ${config.category}
- **Сложность:** ${config.difficulty}
- **Продолжительность:** ${config.duration}
- **Язык:** ${config.language_code}

## Разработка

### Локальная разработка

\`\`\`bash
# Запуск Hugo dev сервера
hugo server -D

# Сборка для продакшна  
hugo --minify
\`\`\`

### Docker

\`\`\`bash
# Сборка образа
docker build -t ${config.module_name} .

# Запуск контейнера
docker run -p 8080:80 ${config.module_name}
\`\`\`

## Деплой

Модуль автоматически деплоится при push в main ветку через GitHub Actions.

URL модуля: https://${config.subdomain}.learn.example.com

## Структура

- \`content/\` - Markdown файлы с контентом уроков
- \`static/quizzes/\` - JSON файлы с интерактивными тестами  
- \`hugo.toml\` - Конфигурация Hugo
- \`Dockerfile\` - Контейнеризация модуля

## Добавление квизов

Используйте shortcode в Markdown файлах:

\`\`\`markdown
{{< quiz src="/quizzes/your-quiz.json" >}}
\`\`\`

Подробнее о формате квизов см. в [документации Quiz Engine](https://github.com/learning-platform-org/quiz-engine).
`;

    await fs.writeFile(path.join(modulePath, 'README.md'), readme);
    console.log(chalk.green('  ✅ README created'));
  }

  showNextSteps(config) {
    console.log(chalk.blue('\n📋 Next steps:'));
    console.log(chalk.white(`
1. Navigate to your module:
   ${chalk.cyan(`cd ${config.module_name}`)}

2. Start development server:
   ${chalk.cyan('hugo server -D')}

3. Edit content in ${chalk.cyan('content/')} directory

4. Add quizzes to ${chalk.cyan('static/quizzes/')}

5. Create GitHub repository:
   ${chalk.cyan(`gh repo create ${config.github_org}/${config.module_name} --public`)}
   ${chalk.cyan('git remote add origin https://github.com/' + config.github_org + '/' + config.module_name + '.git')}
   ${chalk.cyan('git push -u origin main')}

6. Module will be available at:
   ${chalk.cyan(`https://${config.subdomain}.learn.example.com`)}
`));
  }
}

// Валидатор модулей
class ModuleValidator {
  constructor() {
    this.errors = [];
    this.warnings = [];
  }

  async validateModule(modulePath) {
    console.log(chalk.blue(`🔍 Validating module at: ${modulePath}\n`));

    await this.validateStructure(modulePath);
    await this.validateConfig(modulePath);
    await this.validateContent(modulePath);
    await this.validateQuizzes(modulePath);
    await this.validateDocker(modulePath);

    return this.printResults();
  }

  async validateStructure(modulePath) {
    const requiredFiles = [
      'hugo.toml',
      'Dockerfile',
      'content/_index.md',
      '.github/workflows/deploy.yml'
    ];

    const requiredDirs = [
      'content',
      'static'
    ];

    console.log('📁 Checking file structure...');

    for (const file of requiredFiles) {
      const filePath = path.join(modulePath, file);
      if (await fs.pathExists(filePath)) {
        console.log(chalk.green(`  ✅ ${file}`));
      } else {
        this.errors.push(`Missing required file: ${file}`);
        console.log(chalk.red(`  ❌ ${file}`));
      }
    }

    for (const dir of requiredDirs) {
      const dirPath = path.join(modulePath, dir);
      if (await fs.pathExists(dirPath)) {
        console.log(chalk.green(`  ✅ ${dir}/`));
      } else {
        this.errors.push(`Missing required directory: ${dir}`);
        console.log(chalk.red(`  ❌ ${dir}/`));
      }
    }
  }

  async validateConfig(modulePath) {
    console.log('\n⚙️ Validating configuration...');
    
    const configPath = path.join(modulePath, 'hugo.toml');
    if (await fs.pathExists(configPath)) {
      try {
        const config = await fs.readFile(configPath, 'utf8');
        
        // Проверяем обязательные параметры
        const requiredParams = ['baseURL', 'title', 'theme'];
        for (const param of requiredParams) {
          if (config.includes(param)) {
            console.log(chalk.green(`  ✅ ${param} configured`));
          } else {
            this.errors.push(`Missing ${param} in hugo.toml`);
            console.log(chalk.red(`  ❌ ${param} missing`));
          }
        }

        // Проверяем что тема = learning-platform
        if (config.includes('theme = "learning-platform"')) {
          console.log(chalk.green(`  ✅ Correct theme specified`));
        } else {
          this.warnings.push('Theme should be "learning-platform"');
          console.log(chalk.yellow(`  ⚠️ Theme may be incorrect`));
        }

      } catch (error) {
        this.errors.push(`Error reading hugo.toml: ${error.message}`);
      }
    }
  }

  async validateContent(modulePath) {
    console.log('\n📝 Validating content...');
    
    const contentPath = path.join(modulePath, 'content');
    if (await fs.pathExists(contentPath)) {
      try {
        const files = await fs.readdir(contentPath, { recursive: true });
        const mdFiles = files.filter(f => f.endsWith('.md'));
        
        console.log(chalk.green(`  ✅ Found ${mdFiles.length} Markdown files`));
        
        if (mdFiles.length === 0) {
          this.warnings.push('No content files found');
        }

        // Проверяем frontmatter в основных файлах
        for (const file of ['_index.md', 'lessons/_index.md']) {
          const filePath = path.join(contentPath, file);
          if (await fs.pathExists(filePath)) {
            const content = await fs.readFile(filePath, 'utf8');
            if (content.startsWith('---')) {
              console.log(chalk.green(`  ✅ ${file} has frontmatter`));
            } else {
              this.warnings.push(`${file} missing frontmatter`);
            }
          }
        }

      } catch (error) {
        this.errors.push(`Error validating content: ${error.message}`);
      }
    }
  }

  async validateQuizzes(modulePath) {
    console.log('\n🎯 Validating quizzes...');
    
    const quizzesPath = path.join(modulePath, 'static', 'quizzes');
    if (await fs.pathExists(quizzesPath)) {
      try {
        const files = await fs.readdir(quizzesPath);
        const jsonFiles = files.filter(f => f.endsWith('.json'));
        
        if (jsonFiles.length > 0) {
          console.log(chalk.green(`  ✅ Found ${jsonFiles.length} quiz files`));
          
          for (const file of jsonFiles) {
            const filePath = path.join(quizzesPath, file);
            try {
              const quiz = JSON.parse(await fs.readFile(filePath, 'utf8'));
              
              // Базовая валидация структуры квиза
              if (quiz.config && quiz.question && quiz.answers) {
                console.log(chalk.green(`    ✅ ${file} - valid structure`));
              } else {
                this.errors.push(`${file} - invalid quiz structure`);
                console.log(chalk.red(`    ❌ ${file} - invalid structure`));
              }
            } catch (jsonError) {
              this.errors.push(`${file} - invalid JSON: ${jsonError.message}`);
              console.log(chalk.red(`    ❌ ${file} - invalid JSON`));
            }
          }
        } else {
          console.log(chalk.yellow(`  ⚠️ No quiz files found`));
        }
      } catch (error) {
        this.warnings.push(`Error checking quizzes: ${error.message}`);
      }
    } else {
      console.log(chalk.yellow(`  ⚠️ No quizzes directory found`));
    }
  }

  async validateDocker(modulePath) {
    console.log('\n🐳 Validating Docker configuration...');
    
    const dockerfilePath = path.join(modulePath, 'Dockerfile');
    if (await fs.pathExists(dockerfilePath)) {
      try {
        const dockerfile = await fs.readFile(dockerfilePath, 'utf8');
        
        // Проверяем основные инструкции
        const requiredInstructions = ['FROM', 'COPY', 'EXPOSE'];
        for (const instruction of requiredInstructions) {
          if (dockerfile.includes(instruction)) {
            console.log(chalk.green(`  ✅ ${instruction} instruction found`));
          } else {
            this.warnings.push(`Dockerfile missing ${instruction} instruction`);
          }
        }

        // Проверяем что используется shared-hugo-base
        if (dockerfile.includes('shared-hugo-base')) {
          console.log(chalk.green(`  ✅ Uses shared-hugo-base`));
        } else {
          this.warnings.push('Dockerfile should use shared-hugo-base');
        }

      } catch (error) {
        this.errors.push(`Error reading Dockerfile: ${error.message}`);
      }
    }
  }

  printResults() {
    console.log('\n' + '='.repeat(50));
    console.log(chalk.blue('📊 Validation Results'));
    console.log('='.repeat(50));

    if (this.errors.length === 0 && this.warnings.length === 0) {
      console.log(chalk.green('🎉 All validations passed!'));
      return true;
    }

    if (this.errors.length > 0) {
      console.log(chalk.red(`\n❌ Errors (${this.errors.length}):`));
      this.errors.forEach(error => {
        console.log(chalk.red(`  • ${error}`));
      });
    }

    if (this.warnings.length > 0) {
      console.log(chalk.yellow(`\n⚠️ Warnings (${this.warnings.length}):`));
      this.warnings.forEach(warning => {
        console.log(chalk.yellow(`  • ${warning}`));
      });
    }

    const hasErrors = this.errors.length > 0;
    console.log('\n' + '='.repeat(50));
    
    if (hasErrors) {
      console.log(chalk.red('❌ Validation failed - please fix errors'));
    } else {
      console.log(chalk.green('✅ Validation passed with warnings'));
    }

    return !hasErrors;
  }
}

// CLI интерфейс
const argv = yargs(hideBin(process.argv))
  .command('create', 'Create a new learning module', {
    name: {
      alias: 'n',
      type: 'string',
      description: 'Module name'
    },
    template: {
      alias: 't', 
      type: 'string',
      description: 'Template to use'
    },
    category: {
      alias: 'c',
      type: 'string',
      description: 'Module category'
    }
  })
  .command('validate [path]', 'Validate existing module', {
    path: {
      type: 'string',
      default: '.',
      description: 'Path to module directory'
    }
  })
  .help()
  .argv;

// Выполнение команд
async function main() {
  try {
    if (argv._[0] === 'create') {
      const creator = new ModuleCreator();
      await creator.createModule(argv);
    } else if (argv._[0] === 'validate') {
      const validator = new ModuleValidator();
      const isValid = await validator.validateModule(path.resolve(argv.path));
      process.exit(isValid ? 0 : 1);
    } else {
      console.log('Use --help to see available commands');
    }
  } catch (error) {
    console.error(chalk.red(`Error: ${error.message}`));
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { ModuleCreator, ModuleValidator };
```

**Тестовый скрипт:**
```javascript
// cli/test-cli.js
const fs = require('fs-extra');
const path = require('path');
const { execSync } = require('child_process');
const { ModuleCreator, ModuleValidator } = require('./create-module.js');

class CLITester {
  constructor() {
    this.testDir = path.join(__dirname, '../test-modules');
  }

  async runAllTests() {
    console.log('🧪 Starting CLI tests...\n');

    await this.setupTestEnvironment();
    await this.testModuleCreation();
    await this.testModuleValidation();
    await this.cleanup();

    console.log('✅ All CLI tests passed!');
  }

  async setupTestEnvironment() {
    if (await fs.pathExists(this.testDir)) {
      await fs.remove(this.testDir);
    }
    await fs.ensureDir(this.testDir);
  }

  async testModuleCreation() {
    console.log('🏗️ Testing module creation...');

    const testConfig = {
      module_name: 'test-javascript',
      module_title: 'Test JavaScript Course',
      module_description: 'A test module for JavaScript learning',
      module_subject: 'JavaScript',
      category: 'programming',
      difficulty: 'beginner', 
      duration: '10 hours',
      subdomain: 'test-js',
      language_code: 'ru',
      allow_retry: true,
      github_org: 'learning-platform-org'
    };

    const creator = new ModuleCreator();
    const originalCwd = process.cwd();

    try {
      process.chdir(this.testDir);
      
      // Мокаем inquirer для автоматического тестирования
      const originalConsoleLog = console.log;
      console.log = () => {}; // Подавляем вывод
      
      // Создание модуля
      creator.outputPath = this.testDir;
      await creator.generateModule(testConfig, 'module-basic');

      console.log = originalConsoleLog;

      // Проверяем что модуль создался
      const modulePath = path.join(this.testDir, 'test-javascript');
      if (await fs.pathExists(modulePath)) {
        console.log('  ✅ Module directory created');
      } else {
        throw new Error('Module directory not created');
      }

      // Проверяем ключевые файлы
      const requiredFiles = [
        'hugo.toml',
        'Dockerfile', 
        'content/_index.md',
        '.github/workflows/deploy.yml'
      ];

      for (const file of requiredFiles) {
        if (await fs.pathExists(path.join(modulePath, file))) {
          console.log(`  ✅ ${file} created`);
        } else {
          throw new Error(`Required file ${file} not created`);
        }
      }

    } finally {
      process.chdir(originalCwd);
    }
  }

  async testModuleValidation() {
    console.log('\n🔍 Testing module validation...');

    const modulePath = path.join(this.testDir, 'test-javascript');
    const validator = new ModuleValidator();
    
    // Подавляем вывод валидатора для чистоты тестов
    const originalConsoleLog = console.log;
    console.log = () => {};
    
    const isValid = await validator.validateModule(modulePath);
    
    console.log = originalConsoleLog;

    if (isValid) {
      console.log('  ✅ Module validation passed');
    } else {
      throw new Error('Module validation failed');
    }
  }

  async cleanup() {
    await fs.remove(this.testDir);
    console.log('\n🧹 Test cleanup completed');
  }
}

// Запуск тестов
if (require.main === module) {
  const tester = new CLITester();
  tester.runAllTests().catch(error => {
    console.error('❌ CLI tests failed:', error.message);
    process.exit(1);
  });
}

module.exports = CLITester;
```

**CI/CD для тестирования шаблонов:**
```yaml
# .github/workflows/validate-templates.yml
name: Validate Build Templates

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-cli:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        
    - name: Install CLI dependencies
      working-directory: ./cli
      run: npm install
      
    - name: Run CLI tests
      working-directory: ./cli
      run: npm test
      
  test-templates:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        template: [module-basic, module-advanced, module-quiz-heavy]
        
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Setup Hugo
      uses: peaceiris/actions-hugo@v2
      with:
        hugo-version: 'latest'
        extended: true
        
    - name: Setup Node.js  
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        
    - name: Install CLI
      working-directory: ./cli
      run: npm install
      
    - name: Test template ${{ matrix.template }}
      run: |
        echo "🧪 Testing template: ${{ matrix.template }}"
        
        # Создаем тестовый модуль
        cd /tmp
        node $GITHUB_WORKSPACE/cli/create-module.js validate --help || true
        
        # Проверяем шаблон вручную
        mkdir test-module
        cd test-module
        
        # Копируем шаблон
        cp -r $GITHUB_WORKSPACE/templates/${{ matrix.template }}/* .
        
        # Заменяем переменные для тестирования
        sed -i 's/{{.module_title}}/Test Module/g' hugo.toml.template
        sed -i 's/{{.subdomain}}/test/g' hugo.toml.template  
        sed -i 's/{{.language_code}}/ru/g' hugo.toml.template
        sed -i 's/{{.category}}/programming/g' hugo.toml.template
        sed -i 's/{{.difficulty}}/beginner/g' hugo.toml.template
        sed -i 's/{{.duration}}/5 hours/g' hugo.toml.template
        sed -i 's/{{.allow_retry}}/true/g' hugo.toml.template
        
        mv hugo.toml.template hugo.toml
        
        # Проверяем что Hugo может собрать сайт
        hugo --minify
        test -f public/index.html && echo "✅ Template ${{ matrix.template }} builds successfully"
        
  validate-schema:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Validate YAML files
      run: |
        echo "🔍 Validating YAML files in templates..."
        
        find templates -name "*.yml" -o -name "*.yaml" | while read file; do
          echo "Checking $file..."
          # Базовая проверка синтаксиса YAML
          python -c "import yaml; yaml.safe_load(open('$file'))" && \
            echo "✅ $file - valid YAML" || \
            (echo "❌ $file - invalid YAML" && exit 1)
        done
        
    - name: Validate JSON files
      run: |
        echo "🔍 Validating JSON files in templates..."
        
        find templates -name "*.json" | while read file; do
          echo "Checking $file..."
          python -c "import json; json.load(open('$file'))" && \
            echo "✅ $file - valid JSON" || \
            (echo "❌ $file - invalid JSON" && exit 1)
        done
```

**Контрольные процедуры:**
```bash
# Установка CLI инструмента
cd cli && npm install

# Тест создания модуля  
node create-module.js create --name test-module --category programming

# Валидация созданного модуля
node create-module.js validate test-module

# Запуск всех тестов
npm test

# Проверка что созданный модуль собирается Hugo
cd test-module && hugo server
```

**Критерии успеха:**
- ✅ CLI создает корректные модули
- ✅ Все шаблоны валидны
- ✅ Генерируемые модули проходят валидацию
- ✅ Hugo успешно собирает созданные модули
- ✅ Тесты CLI проходят в CI/CD

---

## Этап 5: Создание platform-hub (центральная ось)

### Шаг 5.1: Создание репозитория platform-hub

**Цель:** Создать центральный хаб платформы с лендингом и управлением модулями

**Действия:**
```bash
mkdir platform-hub && cd platform-hub
git init
git remote add origin https://github.com/learning-platform-org/platform-hub.git
```

**Структура репозитория:**
```
platform-hub/
├── .github/workflows/
│   ├── deploy-hub.yml
│   ├── update-registry.yml
│   └── sync-modules.yml
├── hub-site/                      # Hugo сайт для центрального хаба
│   ├── content/
│   │   ├── _index.md
│   │   ├── modules/
│   │   └── about/
│   ├── layouts/
│   │   ├── _default/
│   │   ├── partials/
│   │   └── shortcodes/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── assets/scss/
│   └── hugo.toml
├── registry/
│   ├── modules-registry.json      # Реестр всех модулей
│   ├── schema/
│   │   └── module-schema.json     # JSON Schema для модулей
│   └── scripts/
│       ├── validate-registry.js
│       └── generate-sitemap.js
├── nginx/
│   ├── nginx.conf                 # Конфигурация для hub
│   └── proxy.conf                 # Настройки для модулей
├── scripts/
│   ├── sync-modules.js           # Синхронизация с модулями
│   ├── generate-navigation.js    # Генерация навигации
│   └── health-check.js          # Проверка доступности модулей
├── docker-compose.yml           # Полная конфигурация платформы
├── docker-compose.prod.yml     # Продакшн конфигурация
├── Dockerfile
└── README.md
```

**Контрольные процедуры:**
```bash
# Создание структуры
mkdir -p hub-site/{content/{modules,about},layouts/_default,static/{css,js,images},assets/scss}
mkdir -p registry/{schema,scripts}
mkdir -p nginx scripts
mkdir -p .github/workflows

# Проверка структуры
find . -type d | sort
```

---

### Шаг 5.2: Создание реестра модулей

**Цель:** Создать централизованную систему управления модулями

**JSON Schema для модулей:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Learning Platform Module Registry",
  "type": "object",
  "properties": {
    "version": {
      "type": "string",
      "description": "Registry format version"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time"
    },
    "modules": {
      "type": "object",
      "patternProperties": {
        "^[a-z0-9-]+$": {
          "$ref": "#/definitions/module"
        }
      }
    }
  },
  "definitions": {
    "module": {
      "type": "object",
      "required": ["name", "description", "subdomain", "category", "difficulty", "status"],
      "properties": {
        "name": {
          "type": "string",
          "description": "Human-readable module name"
        },
        "description": {
          "type": "string",
          "description": "Module description"
        },
        "subdomain": {
          "type": "string",
          "pattern": "^[a-z0-9-]+$",
          "description": "Subdomain for the module"
        },
        "category": {
          "type": "string",
          "enum": ["programming", "web-development", "data-science", "design", "devops", "mobile", "other"]
        },
        "difficulty": {
          "type": "string", 
          "enum": ["beginner", "intermediate", "advanced"]
        },
        "duration": {
          "type": "string",
          "description": "Estimated completion time"
        },
        "status": {
          "type": "string",
          "enum": ["active", "beta", "maintenance", "deprecated"]
        },
        "order": {
          "type": "integer",
          "minimum": 0,
          "description": "Display order on hub"
        },
        "repository": {
          "type": "string",
          "format": "uri",
          "description": "GitHub repository URL"
        },
        "image": {
          "type": "string",
          "description": "Docker image name and tag"
        },
        "health_check": {
          "type": "string",
          "format": "uri",
          "description": "Health check endpoint"
        },
        "tags": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "prerequisites": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "Required modules to complete first"
        },
        "language": {
          "type": "string",
          "enum": ["ru", "en", "both"],
          "default": "ru"
        },
        "metrics": {
          "type": "object",
          "properties": {
            "lessons_count": { "type": "integer" },
            "quizzes_count": { "type": "integer" },
            "estimated_duration_minutes": { "type": "integer" }
          }
        },
        "updated_at": {
          "type": "string",
          "format": "date-time"
        }
      }
    }
  }
}
```

**Базовый реестр модулей:**
```json
{
  "version": "1.0.0",
  "updated_at": "2024-01-01T00:00:00Z",
  "modules": {
    "javascript-basics": {
      "name": "JavaScript Основы",
      "description": "Изучение основ JavaScript с нуля до создания интерактивных веб-приложений",
      "subdomain": "js",
      "category": "programming", 
      "difficulty": "beginner",
      "duration": "40 часов",
      "status": "active",
      "order": 1,
      "repository": "https://github.com/learning-platform-org/javascript-basics",
      "image": "ghcr.io/learning-platform-org/javascript-basics:latest",
      "health_check": "https://js.learn.example.com/health",
      "tags": ["javascript", "programming", "web", "frontend"],
      "prerequisites": [],
      "language": "ru",
      "metrics": {
        "lessons_count": 12,
        "quizzes_count": 15,
        "estimated_duration_minutes": 2400
      },
      "updated_at": "2024-01-01T00:00:00Z"
    },
    "python-basics": {
      "name": "Python Основы", 
      "description": "Изучение основ программирования на Python",
      "subdomain": "python",
      "category": "programming",
      "difficulty": "beginner", 
      "duration": "35 часов",
      "status": "active",
      "order": 2,
      "repository": "https://github.com/learning-platform-org/python-basics",
      "image": "ghcr.io/learning-platform-org/python-basics:latest",
      "health_check": "https://python.learn.example.com/health",
      "tags": ["python", "programming", "backend"],
      "prerequisites": [],
      "language": "ru",
      "metrics": {
        "lessons_count": 10,
        "quizzes_count": 12,
        "estimated_duration_minutes": 2100
      },
      "updated_at": "2024-01-01T00:00:00Z"
    },
    "html-css-basics": {
      "name": "HTML и CSS Основы",
      "description": "Создание веб-страниц с использованием HTML и стилизация через CSS",
      "subdomain": "htmlcss", 
      "category": "web-development",
      "difficulty": "beginner",
      "duration": "25 часов", 
      "status": "active",
      "order": 0,
      "repository": "https://github.com/learning-platform-org/html-css-basics",
      "image": "ghcr.io/learning-platform-org/html-css-basics:latest",
      "health_check": "https://htmlcss.learn.example.com/health",
      "tags": ["html", "css", "web", "frontend", "design"],
      "prerequisites": [],
      "language": "ru",
      "metrics": {
        "lessons_count": 8,
        "quizzes_count": 10,
        "estimated_duration_minutes": 1500
      },
      "updated_at": "2024-01-01T00:00:00Z"
    }
  }
}
```

**Скрипт валидации реестра:**
```javascript
// registry/scripts/validate-registry.js
const fs = require('fs');
const Ajv = require('ajv');
const addFormats = require('ajv-formats');

class RegistryValidator {
  constructor() {
    this.ajv = new Ajv({ allErrors: true });
    addFormats(this.ajv);
    
    this.schema = JSON.parse(
      fs.readFileSync('registry/schema/module-schema.json', 'utf8')
    );
    this.validate = this.ajv.compile(this.schema);
  }

  async validateRegistry() {
    console.log('🔍 Validating module registry...\n');

    try {
      // Загружаем реестр
      const registry = JSON.parse(
        fs.readFileSync('registry/modules-registry.json', 'utf8')
      );

      // Валидация схемы
      const isValid = this.validate(registry);
      
      if (!isValid) {
        console.error('❌ Schema validation failed:');
        this.validate.errors.forEach(error => {
          console.error(`  • ${error.instancePath}: ${error.message}`);
        });
        return false;
      }

      console.log('✅ Schema validation passed');

      // Дополнительные проверки
      await this.validateModuleUniqueness(registry);
      await this.validateSubdomains(registry);
      await this.validatePrerequisites(registry);
      await this.validateOrdering(registry);

      console.log('\n🎉 Registry validation completed successfully!');
      return true;

    } catch (error) {
      console.error('❌ Registry validation failed:', error.message);
      return false;
    }
  }

  async validateModuleUniqueness(registry) {
    const subdomains = new Set();
    const names = new Set();

    for (const [moduleId, module] of Object.entries(registry.modules)) {
      // Проверка уникальности subdomain
      if (subdomains.has(module.subdomain)) {
        throw new Error(`Duplicate subdomain: ${module.subdomain}`);
      }
      subdomains.add(module.subdomain);

      // Проверка уникальности названий
      if (names.has(module.name)) {
        throw new Error(`Duplicate module name: ${module.name}`);
      }
      names.add(module.name);
    }

    console.log('✅ Module uniqueness validated');
  }

  async validateSubdomains(registry) {
    const reservedSubdomains = ['www', 'api', 'admin', 'staging', 'test'];
    
    for (const [moduleId, module] of Object.entries(registry.modules)) {
      if (reservedSubdomains.includes(module.subdomain)) {
        throw new Error(`Reserved subdomain used: ${module.subdomain}`);
      }
    }

    console.log('✅ Subdomain validation passed');
  }

  async validatePrerequisites(registry) {
    const moduleIds = Object.keys(registry.modules);

    for (const [moduleId, module] of Object.entries(registry.modules)) {
      if (module.prerequisites) {
        for (const prereq of module.prerequisites) {
          if (!moduleIds.includes(prereq)) {
            throw new Error(`Invalid prerequisite "${prereq}" in module "${moduleId}"`);
          }
        }
      }
    }

    console.log('✅ Prerequisites validation passed');
  }

  async validateOrdering(registry) {
    const orders = Object.values(registry.modules).map(m => m.order).filter(o => o !== undefined);
    const uniqueOrders = new Set(orders);

    if (orders.length !== uniqueOrders.size) {
      throw new Error('Duplicate order values found in modules');
    }

    console.log('✅ Module ordering validated');
  }

  generateStatistics(registry) {
    const stats = {
      total_modules: Object.keys(registry.modules).length,
      by_category: {},
      by_difficulty: {},
      by_status: {},
      total_lessons: 0,
      total_quizzes: 0,
      total_duration_minutes: 0
    };

    for (const module of Object.values(registry.modules)) {
      // По категориям
      stats.by_category[module.category] = (stats.by_category[module.category] || 0) + 1;
      
      // По сложности
      stats.by_difficulty[module.difficulty] = (stats.by_difficulty[module.difficulty] || 0) + 1;
      
      // По статусу
      stats.by_status[module.status] = (stats.by_status[module.status] || 0) + 1;

      // Метрики
      if (module.metrics) {
        stats.total_lessons += module.metrics.lessons_count || 0;
        stats.total_quizzes += module.metrics.quizzes_count || 0;
        stats.total_duration_minutes += module.metrics.estimated_duration_minutes || 0;
      }
    }

    return stats;
  }
}

// CLI использование
if (require.main === module) {
  const validator = new RegistryValidator();
  validator.validateRegistry().then(success => {
    if (success) {
      const registry = JSON.parse(
        fs.readFileSync('registry/modules-registry.json', 'utf8')
      );
      const stats = validator.generateStatistics(registry);
      
      console.log('\n📊 Registry Statistics:');
      console.log(`  Modules: ${stats.total_modules}`);
      console.log(`  Lessons: ${stats.total_lessons}`);
      console.log(`  Quizzes: ${stats.total_quizzes}`);
      console.log(`  Total Duration: ${Math.round(stats.total_duration_minutes/60)} hours`);
    }
    
    process.exit(success ? 0 : 1);
  });
}

module.exports = RegistryValidator;
```

**Контрольные процедуры:**
```bash
# Создание файлов реестра
cat > registry/modules-registry.json << 'EOF'
[содержимое JSON выше]
EOF

cat > registry/schema/module-schema.json << 'EOF'  
[содержимое schema выше]
EOF

# Установка зависимостей для валидации
npm init -y
npm install ajv ajv-formats

# Тест валидации
cd registry/scripts && node validate-registry.js
```

**Критерии успеха:**
- ✅ JSON schema создана и валидна
- ✅ Базовый реестр проходит валидацию
- ✅ Скрипт валидации работает
- ✅ Уникальность модулей проверяется

---

### Шаг 5.3: Создание Hugo сайта для центрального хаба

**Цель:** Создать веб-интерфейс центрального хаба с навигацией по модулям

**Конфигурация Hugo:**
```toml
# hub-site/hugo.toml
baseURL = "https://learn.example.com"
languageCode = "ru"
title = "Learning Platform - Образовательная платформа"
theme = "hub-theme"

# Настройки содержимого
[params]
  description = "Изучайте программирование и веб-разработку через интерактивные курсы"
  keywords = ["обучение", "программирование", "веб-разработка", "курсы", "javascript", "python"]
  
  # Информация о платформе
  [params.platform]
    version = "1.0.0"
    modules_registry = "/api/modules"
    github_org = "learning-platform-org"
    
  # SEO настройки
  [params.seo]
    google_analytics = "G-XXXXXXXXXX"
    google_site_verification = "your-verification-code"
    
  # Социальные сети
  [params.social]
    github = "https://github.com/learning-platform-org"
    telegram = "https://t.me/learning-platform"

# Настройки меню
[[menu.main]]
  name = "Курсы"
  url = "/modules/"
  weight = 10

[[menu.main]]
  name = "О платформе"  
  url = "/about/"
  weight = 20

[[menu.main]]
  name = "GitHub"
  url = "https://github.com/learning-platform-org"
  weight = 30

# Настройки разметки
[markup]
  [markup.goldmark]
    [markup.goldmark.renderer]
      unsafe = true
  [markup.highlight]
    style = "github"
    lineNos = true

# Типы контента
[taxonomies]
  category = "categories"
  difficulty = "difficulties"
  tag = "tags"
```

**Главная страница:**
```markdown
<!-- hub-site/content/_index.md -->
---
title: "Learning Platform"
description: "Изучайте программирование через интерактивные курсы с тестами и практическими заданиями"
---

# Добро пожаловать на Learning Platform! 🚀

Наша платформа предлагает структурированное изучение программирования и веб-разработки через интерактивные курсы с встроенными тестами.

## Особенности платформы

- 🎯 **Интерактивные тесты** - проверяйте знания после каждого урока
- 📚 **Структурированные курсы** - от основ к продвинутым темам  
- 🏆 **Практические задания** - закрепляйте теорию на практике
- 🌍 **Мультиязычность** - поддержка русского и английского языков
- 📱 **Адаптивный дизайн** - учитесь с любого устройства

## Доступные курсы

{{< modules-grid >}}

## Как начать обучение

1. **Выберите курс** из списка выше
2. **Изучайте материал** последовательно, урок за уроком  
3. **Проходите тесты** для закрепления знаний
4. **Применяйте знания** в практических заданиях

## Рекомендуемый порядок изучения

Для новичков в программировании рекомендуем следующий порядок:

1. [HTML и CSS Основы](https://htmlcss.learn.example.com) - создание веб-страниц
2. [JavaScript Основы](https://js.learn.example.com) - интерактивность на веб-страницах
3. [Python Основы](https://python.learn.example.com) - серверная разработка

---

**Готовы начать?** Выберите первый курс и погрузитесь в мир программирования!
```

**Страница со списком модулей:**
```markdown
<!-- hub-site/content/modules/_index.md -->
---
title: "Все курсы"
description: "Полный список доступных курсов обучения"
layout: "modules-list"
---

# Все курсы Learning Platform

Выберите курс в зависимости от ваших целей и уровня подготовки.

{{< modules-filter >}}

{{< modules-detailed-list >}}
```

**Layout для главной страницы:**
```html
<!-- hub-site/layouts/index.html -->
{{ define "main" }}
<div class="hero-section">
  <div class="container">
    <div class="hero-content">
      <h1>{{ .Title }}</h1>
      <p class="hero-description">{{ .Params.description }}</p>
      <div class="hero-stats">
        <div class="stat">
          <span class="stat-number" id="total-modules">0</span>
          <span class="stat-label">Курсов</span>
        </div>
        <div class="stat">
          <span class="stat-number" id="total-lessons">0</span>
          <span class="stat-label">Уроков</span>
        </div>
        <div class="stat">
          <span class="stat-number" id="total-quizzes">0</span>
          <span class="stat-label">Тестов</span>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="modules-section">
  <div class="container">
    {{ .Content }}
  </div>
</div>

<div class="features-section">
  <div class="container">
    <h2>Почему выбирают нашу платформу</h2>
    <div class="features-grid">
      <div class="feature">
        <div class="feature-icon">🎯</div>
        <h3>Интерактивные тесты</h3>
        <p>Проверяйте свои знания после каждого урока с помощью встроенных тестов</p>
      </div>
      <div class="feature">
        <div class="feature-icon">📊</div>
        <h3>Отслеживание прогресса</h3>
        <p>Видите свой прогресс обучения и достижения по каждому курсу</p>
      </div>
      <div class="feature">
        <div class="feature-icon">🔄</div>
        <h3>Современный контент</h3>
        <p>Материалы регулярно обновляются в соответствии с последними трендами</p>
      </div>
      <div class="feature">
        <div class="feature-icon">💻</div>
        <h3>Практические проекты</h3>
        <p>Применяйте полученные знания в реальных проектах</p>
      </div>
    </div>
  </div>
</div>
{{ end }}

{{ define "scripts" }}
<script>
// Загрузка статистики из реестра модулей
fetch('/api/modules/stats')
  .then(response => response.json())
  .then(data => {
    document.getElementById('total-modules').textContent = data.total_modules || 0;
    document.getElementById('total-lessons').textContent = data.total_lessons || 0;
    document.getElementById('total-quizzes').textContent = data.total_quizzes || 0;
  })
  .catch(error => {
    console.error('Error loading statistics:', error);
  });
</script>
{{ end }}
```

**Shortcode для отображения модулей:**
```html
<!-- hub-site/layouts/shortcodes/modules-grid.html -->
<div class="modules-grid" id="modules-grid">
  <div class="modules-loading">
    <p>Загрузка курсов...</p>
  </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', async function() {
  try {
    const response = await fetch('/api/modules');
    const registry = await response.json();
    
    const container = document.getElementById('modules-grid');
    container.innerHTML = '';
    
    // Сортируем модули по order
    const modules = Object.entries(registry.modules)
      .sort(([,a], [,b]) => (a.order || 999) - (b.order || 999))
      .filter(([,module]) => module.status === 'active');
    
    modules.forEach(([id, module]) => {
      const moduleCard = createModuleCard(id, module);
      container.appendChild(moduleCard);
    });
    
  } catch (error) {
    console.error('Error loading modules:', error);
    document.getElementById('modules-grid').innerHTML = 
      '<p class="error">Ошибка загрузки курсов. Попробуйте обновить страницу.</p>';
  }
});

function createModuleCard(id, module) {
  const card = document.createElement('div');
  card.className = 'module-card';
  card.setAttribute('data-category', module.category);
  card.setAttribute('data-difficulty', module.difficulty);
  
  const difficultyClass = {
    'beginner': 'difficulty-beginner',
    'intermediate': 'difficulty-intermediate', 
    'advanced': 'difficulty-advanced'
  }[module.difficulty] || '';
  
  const categoryEmoji = {
    'programming': '💻',
    'web-development': '🌐',
    'data-science': '📊',
    'design': '🎨',
    'devops': '🔧',
    'mobile': '📱'
  }[module.category] || '📚';
  
  card.innerHTML = `
    <div class="module-card-header">
      <div class="module-category">${categoryEmoji} ${module.category}</div>
      <div class="module-difficulty ${difficultyClass}">${module.difficulty}</div>
    </div>
    <div class="module-card-body">
      <h3 class="module-title">${module.name}</h3>
      <p class="module-description">${module.description}</p>
      <div class="module-meta">
        <span class="module-duration">⏱️ ${module.duration}</span>
        ${module.metrics ? `
          <span class="module-lessons">📖 ${module.metrics.lessons_count} уроков</span>
          <span class="module-quizzes">🎯 ${module.metrics.quizzes_count} тестов</span>
        ` : ''}
      </div>
    </div>
    <div class="module-card-footer">
      <a href="https://${module.subdomain}.learn.example.com" 
         class="btn btn-primary module-link"
         target="_blank"
         rel="noopener">
        Начать курс →
      </a>
    </div>
  `;
  
  return card;
}
</script>
```

**SCSS стили для хаба:**
```scss
// hub-site/assets/scss/main.scss
:root {
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --success-color: #28a745;
  --info-color: #17a2b8;
  --warning-color: #ffc107;
  --danger-color: #dc3545;
  --dark-color: #343a40;
  --light-color: #f8f9fa;
  
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --border-radius: 0.375rem;
  --box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  --transition: all 0.15s ease-in-out;
}

* {
  box-sizing: border-box;
}

body {
  font-family: var(--font-family);
  line-height: 1.6;
  margin: 0;
  padding: 0;
  color: var(--dark-color);
  background-color: #fff;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

// Header styles
header {
  background: linear-gradient(135deg, var(--primary-color) 0%, #0056b3 100%);
  color: white;
  padding: 1rem 0;
  box-shadow: var(--box-shadow);
  
  .navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .navbar-brand {
      font-size: 1.5rem;
      font-weight: bold;
      text-decoration: none;
      color: white;
    }
    
    .navbar-nav {
      display: flex;
      list-style: none;
      margin: 0;
      padding: 0;
      gap: 2rem;
      
      a {
        color: white;
        text-decoration: none;
        transition: var(--transition);
        
        &:hover {
          color: #cce7ff;
        }
      }
    }
  }
}

// Hero section
.hero-section {
  background: linear-gradient(135deg, var(--primary-color) 0%, #0056b3 100%);
  color: white;
  padding: 4rem 0;
  text-align: center;
  
  .hero-content h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
    font-weight: 300;
  }
  
  .hero-description {
    font-size: 1.25rem;
    margin-bottom: 2rem;
    color: #cce7ff;
  }
  
  .hero-stats {
    display: flex;
    justify-content: center;
    gap: 3rem;
    margin-top: 2rem;
    
    .stat {
      text-align: center;
      
      .stat-number {
        display: block;
        font-size: 2.5rem;
        font-weight: bold;
        color: white;
      }
      
      .stat-label {
        font-size: 0.875rem;
        color: #cce7ff;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }
    }
  }
}

// Modules grid
.modules-section {
  padding: 4rem 0;
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.module-card {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  transition: var(--transition);
  overflow: hidden;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 1rem 2rem rgba(0, 0, 0, 0.2);
  }
  
  .module-card-header {
    padding: 1rem 1.5rem 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .module-category {
      font-size: 0.875rem;
      color: var(--secondary-color);
      font-weight: 500;
    }
    
    .module-difficulty {
      padding: 0.25rem 0.75rem;
      border-radius: 1rem;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      
      &.difficulty-beginner {
        background: #d4edda;
        color: #155724;
      }
      
      &.difficulty-intermediate {
        background: #fff3cd;
        color: #856404;
      }
      
      &.difficulty-advanced {
        background: #f8d7da;
        color: #721c24;
      }
    }
  }
  
  .module-card-body {
    padding: 1rem 1.5rem;
    
    .module-title {
      font-size: 1.25rem;
      margin: 0 0 0.5rem 0;
      color: var(--dark-color);
    }
    
    .module-description {
      color: var(--secondary-color);
      margin-bottom: 1rem;
      line-height: 1.5;
    }
    
    .module-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      font-size: 0.875rem;
      color: var(--secondary-color);
      
      span {
        display: flex;
        align-items: center;
        gap: 0.25rem;
      }
    }
  }
  
  .module-card-footer {
    padding: 0 1.5rem 1.5rem;
    
    .module-link {
      display: inline-block;
      background: var(--primary-color);
      color: white;
      padding: 0.75rem 1.5rem;
      border-radius: var(--border-radius);
      text-decoration: none;
      transition: var(--transition);
      font-weight: 500;
      
      &:hover {
        background: #0056b3;
        text-decoration: none;
        color: white;
      }
    }
  }
}

// Features section
.features-section {
  background: var(--light-color);
  padding: 4rem 0;
  
  h2 {
    text-align: center;
    margin-bottom: 3rem;
    font-size: 2.5rem;
    color: var(--dark-color);
  }
  
  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
  }
  
  .feature {
    text-align: center;
    padding: 2rem 1rem;
    
    .feature-icon {
      font-size: 3rem;
      margin-bottom: 1rem;
    }
    
    h3 {
      margin-bottom: 1rem;
      color: var(--dark-color);
    }
    
    p {
      color: var(--secondary-color);
      line-height: 1.6;
    }
  }
}

// Loading states
.modules-loading, .error {
  text-align: center;
  padding: 2rem;
  color: var(--secondary-color);
  font-style: italic;
}

.error {
  color: var(--danger-color);
  font-style: normal;
}

// Responsive design
@media (max-width: 768px) {
  .hero-content h1 {
    font-size: 2rem;
  }
  
  .hero-stats {
    gap: 1.5rem;
    
    .stat .stat-number {
      font-size: 2rem;
    }
  }
  
  .modules-grid {
    grid-template-columns: 1fr;
  }
  
  .navbar .navbar-nav {
    gap: 1rem;
    flex-wrap: wrap;
  }
}
```

**Контрольные процедуры:**
```bash
# Установка Hugo (если не установлен)
# Проверка на Linux/macOS:
hugo version || echo "Hugo not installed"

# Тест сборки Hugo сайта
cd hub-site
hugo --minify

# Проверка что сайт собрался
test -f public/index.html && echo "✅ Hugo site builds successfully"

# Валидация HTML (если есть html-validate)
npx html-validate public/index.html || echo "HTML validation skipped"

# Тест локального сервера
hugo server --bind 0.0.0.0 --port 1313 &
SERVER_PID=$!
sleep 3

# Проверка доступности
curl -f http://localhost:1313/ && echo "✅ Local server working"

# Остановка сервера
kill $SERVER_PID
```

**Критерии успеха:**
- ✅ Hugo сайт собирается без ошибок
- ✅ Главная страница отображается корректно
- ✅ Shortcode для модулей работает
- ✅ CSS стили применяются
- ✅ Локальный сервер запускается

---

### Шаг 5.4: Создание API для доступа к реестру модулей

**Цель:** Создать REST API для получения информации о модулях

**Nginx конфигурация с API endpoints:**
```nginx
# nginx/nginx.conf
user nginx;
worker_processes auto;

error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 10240;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    server {
        listen 80;
        server_name learn.example.com;
        root /usr/share/nginx/html;
        index index.html index.htm;

        # Основной сайт
        location / {
            try_files $uri $uri/ /index.html;
        }

        # API для модулей
        location /api/modules {
            limit_req zone=api burst=20 nodelay;
            
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, OPTIONS";
            add_header Access-Control-Allow-Headers "Content-Type";
            add_header Content-Type application/json;

            # Возвращаем реестр модулей
            try_files /api/modules.json =404;
        }

        location /api/modules/stats {
            limit_req zone=api burst=20 nodelay;
            
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, OPTIONS";
            add_header Content-Type application/json;

            # Возвращаем статистику
            try_files /api/modules-stats.json =404;
        }

        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # Статические файлы с длительным кешированием
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Proxy для модулей
    include /etc/nginx/conf.d/modules-proxy.conf;
}
```

**Конфигурация прокси для модулей:**
```nginx
# nginx/modules-proxy.conf
# Автогенерируемый файл с настройками прокси для модулей

# JavaScript модуль
server {
    listen 80;
    server_name js.learn.example.com;

    location / {
        proxy_pass http://javascript-basics:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Health check для модуля
        proxy_connect_timeout 5s;
        proxy_send_timeout 5s;
        proxy_read_timeout 30s;
    }

    location /health {
        proxy_pass http://javascript-basics:80/health;
        access_log off;
    }
}

# Python модуль  
server {
    listen 80;
    server_name python.learn.example.com;

    location / {
        proxy_pass http://python-basics:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 5s;
        proxy_send_timeout 5s;
        proxy_read_timeout 30s;
    }

    location /health {
        proxy_pass http://python-basics:80/health;
        access_log off;
    }
}

# HTML/CSS модуль
server {
    listen 80;
    server_name htmlcss.learn.example.com;

    location / {
        proxy_pass http://html-css-basics:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 5s;
        proxy_send_timeout 5s;
        proxy_read_timeout 30s;
    }

    location /health {
        proxy_pass http://html-css-basics:80/health;
        access_log off;
    }
}
```

**Скрипт генерации статистики:**
```javascript
// scripts/generate-stats.js
const fs = require('fs');
const path = require('path');

class StatsGenerator {
  constructor() {
    this.registryPath = 'registry/modules-registry.json';
    this.statsOutputPath = 'hub-site/static/api/modules-stats.json';
  }

  generateStats() {
    console.log('📊 Generating modules statistics...');

    try {
      // Загружаем реестр
      const registry = JSON.parse(fs.readFileSync(this.registryPath, 'utf8'));
      
      // Генерируем статистику
      const stats = this.calculateStats(registry);
      
      // Обеспечиваем существование директории
      fs.mkdirSync(path.dirname(this.statsOutputPath), { recursive: true });
      
      // Сохраняем статистику
      fs.writeFileSync(this.statsOutputPath, JSON.stringify(stats, null, 2));
      
      console.log('✅ Statistics generated successfully');
      console.log(`📁 Saved to: ${this.statsOutputPath}`);
      
      return stats;
      
    } catch (error) {
      console.error('❌ Failed to generate statistics:', error.message);
      throw error;
    }
  }

  calculateStats(registry) {
    const modules = Object.values(registry.modules);
    const activeModules = modules.filter(m => m.status === 'active');

    const stats = {
      generated_at: new Date().toISOString(),
      total_modules: modules.length,
      active_modules: activeModules.length,
      total_lessons: 0,
      total_quizzes: 0,
      total_duration_minutes: 0,
      
      by_category: {},
      by_difficulty: {},
      by_status: {},
      
      categories: [],
      difficulties: ['beginner', 'intermediate', 'advanced'],
      
      featured_modules: [],
      recent_updates: []
    };

    // Подсчитываем метрики
    modules.forEach(module => {
      // Общие метрики
      if (module.metrics) {
        stats.total_lessons += module.metrics.lessons_count || 0;
        stats.total_quizzes += module.metrics.quizzes_count || 0;
        stats.total_duration_minutes += module.metrics.estimated_duration_minutes || 0;
      }

      // По категориям
      stats.by_category[module.category] = (stats.by_category[module.category] || 0) + 1;
      
      // По сложности
      stats.by_difficulty[module.difficulty] = (stats.by_difficulty[module.difficulty] || 0) + 1;
      
      // По статусу
      stats.by_status[module.status] = (stats.by_status[module.status] || 0) + 1;
    });

    // Уникальные категории
    stats.categories = [...new Set(modules.map(m => m.category))].sort();

    // Рекомендуемые модули (сортированные по order)
    stats.featured_modules = activeModules
      .sort((a, b) => (a.order || 999) - (b.order || 999))
      .slice(0, 6)
      .map(module => ({
        id: this.findModuleId(registry, module),
        name: module.name,
        description: module.description,
        subdomain: module.subdomain,
        category: module.category,
        difficulty: module.difficulty,
        duration: module.duration,
        metrics: module.metrics
      }));

    // Недавно обновленные
    stats.recent_updates = modules
      .filter(m => m.updated_at)
      .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
      .slice(0, 5)
      .map(module => ({
        id: this.findModuleId(registry, module),
        name: module.name,
        updated_at: module.updated_at
      }));

    // Форматируем продолжительность
    stats.total_duration_hours = Math.round(stats.total_duration_minutes / 60);

    return stats;
  }

  findModuleId(registry, targetModule) {
    return Object.keys(registry.modules).find(id => 
      registry.modules[id] === targetModule
    );
  }

  // Метод для обновления статистики модуля
  updateModuleStats(moduleId, newStats) {
    try {
      const registry = JSON.parse(fs.readFileSync(this.registryPath, 'utf8'));
      
      if (registry.modules[moduleId]) {
        registry.modules[moduleId].metrics = {
          ...registry.modules[moduleId].metrics,
          ...newStats
        };
        registry.modules[moduleId].updated_at = new Date().toISOString();
        
        // Обновляем общий timestamp реестра
        registry.updated_at = new Date().toISOString();
        
        // Сохраняем обновленный реестр
        fs.writeFileSync(this.registryPath, JSON.stringify(registry, null, 2));
        
        // Перегенерируем статистику
        this.generateStats();
        
        console.log(`✅ Updated stats for module: ${moduleId}`);
      } else {
        throw new Error(`Module not found: ${moduleId}`);
      }
      
    } catch (error) {
      console.error(`❌ Failed to update module stats: ${error.message}`);
      throw error;
    }
  }
}

// CLI использование
if (require.main === module) {
  const args = process.argv.slice(2);
  const generator = new StatsGenerator();

  if (args[0] === 'update' && args[1] && args[2]) {
    // Обновление статистики конкретного модуля
    const moduleId = args[1];
    const statsJson = args[2];
    
    try {
      const newStats = JSON.parse(statsJson);
      generator.updateModuleStats(moduleId, newStats);
    } catch (error) {
      console.error('Invalid JSON for stats:', error.message);
      process.exit(1);
    }
  } else {
    // Генерация общей статистики
    generator.generateStats();
  }
}

module.exports = StatsGenerator;
```

**Скрипт копирования API файлов:**
```javascript
// scripts/prepare-api.js
const fs = require('fs');
const path = require('path');

class APIPreparator {
  constructor() {
    this.registryPath = 'registry/modules-registry.json';
    this.apiDir = 'hub-site/static/api';
  }

  prepareAPI() {
    console.log('🔧 Preparing API files...');

    try {
      // Создаем API директорию
      fs.mkdirSync(this.apiDir, { recursive: true });
      
      // Копируем реестр модулей
      this.copyModulesRegistry();
      
      // Генерируем статистику
      this.generateStats();
      
      console.log('✅ API files prepared successfully');
      
    } catch (error) {
      console.error('❌ Failed to prepare API files:', error.message);
      throw error;
    }
  }

  copyModulesRegistry() {
    const targetPath = path.join(this.apiDir, 'modules.json');
    fs.copyFileSync(this.registryPath, targetPath);
    console.log(`📄 Copied modules registry to ${targetPath}`);
  }

  generateStats() {
    const StatsGenerator = require('./generate-stats.js');
    const generator = new StatsGenerator();
    generator.generateStats();
  }

  // Валидация API endpoints
  validateAPI() {
    console.log('🔍 Validating API endpoints...');

    const requiredFiles = [
      'modules.json',
      'modules-stats.json'
    ];

    let allValid = true;

    requiredFiles.forEach(file => {
      const filePath = path.join(this.apiDir, file);
      
      if (fs.existsSync(filePath)) {
        try {
          const content = JSON.parse(fs.readFileSync(filePath, 'utf8'));
          console.log(`✅ ${file} - valid JSON`);
        } catch (error) {
          console.log(`❌ ${file} - invalid JSON: ${error.message}`);
          allValid = false;
        }
      } else {
        console.log(`❌ ${file} - missing`);
        allValid = false;
      }
    });

    return allValid;
  }
}

// CLI использование
if (require.main === module) {
  const command = process.argv[2];
  const preparator = new APIPreparator();

  switch (command) {
    case 'validate':
      const isValid = preparator.validateAPI();
      process.exit(isValid ? 0 : 1);
      break;
    case 'prepare':
    default:
      preparator.prepareAPI();
      break;
  }
}

module.exports = APIPreparator;
```

**Контрольные процедуры:**
```bash
# Подготовка API файлов
node scripts/prepare-api.js

# Валидация API
node scripts/prepare-api.js validate

# Проверка созданных файлов
ls -la hub-site/static/api/

# Тест JSON валидности
jq empty hub-site/static/api/modules.json && echo "✅ modules.json valid"
jq empty hub-site/static/api/modules-stats.json && echo "✅ modules-stats.json valid"

# Тест API endpoints с Hugo
cd hub-site
hugo server &
SERVER_PID=$!
sleep 3

curl -f http://localhost:1313/api/modules && echo "✅ /api/modules working"
curl -f http://localhost:1313/api/modules/stats && echo "✅ /api/modules/stats working"

kill $SERVER_PID
```

**Критерии успеха:**
- ✅ API файлы генерируются корректно
- ✅ JSON файлы валидны
- ✅ Nginx конфигурация правильная
- ✅ API endpoints доступны
- ✅ CORS заголовки настроены

---

### Шаг 5.5: Создание Docker Compose конфигурации

**Цель:** Создать полную конфигурацию для развертывания всей платформы

**Основной Docker Compose файл:**
```yaml
# docker-compose.yml
version: '3.8'

networks:
  learning-platform:
    driver: bridge

volumes:
  nginx-logs:
    driver: local

services:
  # Nginx reverse proxy
  nginx-proxy:
    image: nginx:alpine
    container_name: learning-platform-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/modules-proxy.conf:/etc/nginx/conf.d/modules-proxy.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - nginx-logs:/var/log/nginx
    depends_on:
      - platform-hub
      - javascript-basics
      - python-basics
      - html-css-basics
    networks:
      - learning-platform
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Центральный хаб
  platform-hub:
    image: ghcr.io/learning-platform-org/platform-hub:latest
    container_name: platform-hub
    restart: unless-stopped
    networks:
      - learning-platform
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 30s
    labels:
      - "learning.platform.service=hub"
      - "learning.platform.role=central"

  # JavaScript модуль  
  javascript-basics:
    image: ghcr.io/learning-platform-org/javascript-basics:latest
    container_name: javascript-basics
    restart: unless-stopped
    networks:
      - learning-platform
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 30s
    labels:
      - "learning.platform.service=module"
      - "learning.platform.module=javascript-basics"
      - "learning.platform.subdomain=js"

  # Python модуль
  python-basics:
    image: ghcr.io/learning-platform-org/python-basics:latest
    container_name: python-basics
    restart: unless-stopped
    networks:
      - learning-platform
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 30s
    labels:
      - "learning.platform.service=module"
      - "learning.platform.module=python-basics"
      - "learning.platform.subdomain=python"

  # HTML/CSS модуль
  html-css-basics:
    image: ghcr.io/learning-platform-org/html-css-basics:latest
    container_name: html-css-basics
    restart: unless-stopped
    networks:
      - learning-platform
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 30s
    labels:
      - "learning.platform.service=module"
      - "learning.platform.module=html-css-basics"
      - "learning.platform.subdomain=htmlcss"

  # Мониторинг и health checks
  healthcheck-monitor:
    image: alpine:latest
    container_name: healthcheck-monitor
    restart: unless-stopped
    command: |
      sh -c '
        apk add --no-cache curl jq
        while true; do
          echo "🏥 Health check at $$(date)"
          
          # Проверяем все сервисы
          for service in nginx-proxy platform-hub javascript-basics python-basics html-css-basics; do
            if docker ps --format "table {{.Names}}" | grep -q $$service; then
              echo "✅ $$service is running"
            else
              echo "❌ $$service is not running"
            fi
          done
          
          sleep 300  # Проверка каждые 5 минут
        done
      '
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      - nginx-proxy
    networks:
      - learning-platform
```

**Продакшн конфигурация:**
```yaml
# docker-compose.prod.yml
version: '3.8'

# Расширяет базовую конфигурацию для продакшна
networks:
  learning-platform:
    driver: bridge
  monitoring:
    driver: bridge

volumes:
  nginx-logs:
    driver: local
  prometheus-data:
    driver: local
  grafana-data:
    driver: local

services:
  # SSL и усиленная безопасность для Nginx
  nginx-proxy:
    extends:
      file: docker-compose.yml
      service: nginx-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/modules-proxy.conf:/etc/nginx/conf.d/modules-proxy.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - nginx-logs:/var/log/nginx
    environment:
      - NGINX_WORKER_PROCESSES=auto
      - NGINX_WORKER_CONNECTIONS=1024
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M

  # Центральный хаб с ограничениями ресурсов
  platform-hub:
    extends:
      file: docker-compose.yml
      service: platform-hub
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M

  # Модули с ограничениями ресурсов
  javascript-basics:
    extends:
      file: docker-compose.yml
      service: javascript-basics
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

  python-basics:
    extends:
      file: docker-compose.yml
      service: python-basics
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

  html-css-basics:
    extends:
      file: docker-compose.yml
      service: html-css-basics
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

  # Prometheus для мониторинга
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    networks:
      - monitoring
      - learning-platform

  # Grafana для визуализации
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
    networks:
      - monitoring

  # cAdvisor для метрик контейнеров
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    restart: unless-stopped
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    networks:
      - monitoring

  # Backup сервис
  backup:
    image: alpine:latest
    container_name: platform-backup
    restart: unless-stopped
    volumes:
      - nginx-logs:/backup/nginx-logs:ro
      - ./registry:/backup/registry:ro
      - ./scripts:/backup/scripts:ro
      - /var/backups:/var/backups
    command: |
      sh -c '
        apk add --no-cache tar gzip
        while true; do
          echo "📦 Creating backup at $$(date)"
          
          # Создаем архив с датой
          BACKUP_NAME="learning-platform-$$(date +%Y%m%d_%H%M%S).tar.gz"
          
          tar -czf "/var/backups/$$BACKUP_NAME" \
            -C /backup \
            nginx-logs registry scripts
            
          echo "✅ Backup created: $$BACKUP_NAME"
          
          # Удаляем старые бэкапы (старше 30 дней)
          find /var/backups -name "learning-platform-*.tar.gz" -mtime +30 -delete
          
          # Ждем 24 часа до следующего бэкапа
          sleep 86400
        done
      '
    networks:
      - learning-platform
```

**Скрипт управления платформой:**
```bash
#!/bin/bash
# scripts/platform-manager.sh

set -e

COMPOSE_FILE="docker-compose.yml"
PROD_COMPOSE_FILE="docker-compose.prod.yml"
LOG_FILE="/tmp/platform-manager.log"

# Функция логирования
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Проверка здоровья сервисов
health_check() {
    log "🏥 Performing health check..."
    
    local failed_services=()
    
    # Проверяем каждый сервис
    for service in nginx-proxy platform-hub javascript-basics python-basics html-css-basics; do
        if docker ps --format "table {{.Names}}" | grep -q "$service"; then
            # Проверяем health check если доступен
            local health_status=$(docker inspect --format='{{.State.Health.Status}}' "$service" 2>/dev/null || echo "unknown")
            
            if [ "$health_status" = "healthy" ] || [ "$health_status" = "unknown" ]; then
                log "✅ $service: healthy"
            else
                log "❌ $service: $health_status"
                failed_services+=("$service")
            fi
        else
            log "❌ $service: not running"
            failed_services+=("$service")
        fi
    done
    
    if [ ${#failed_services[@]} -eq 0 ]; then
        log "🎉 All services healthy"
        return 0
    else
        log "⚠️ Failed services: ${failed_services[*]}"
        return 1
    fi
}

# Развертывание платформы
deploy() {
    local env="${1:-dev}"
    
    log "🚀 Deploying learning platform (environment: $env)"
    
    if [ "$env" = "prod" ]; then
        docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" up -d
    else
        docker-compose -f "$COMPOSE_FILE" up -d
    fi
    
    log "⏳ Waiting for services to start..."
    sleep 30
    
    if health_check; then
        log "✅ Deployment successful"
        
        # Показываем URLs
        log "📍 Platform URLs:"
        log "   Hub: http://learn.example.com"
        log "   JavaScript: http://js.learn.example.com"
        log "   Python: http://python.learn.example.com"
        log "   HTML/CSS: http://htmlcss.learn.example.com"
        
        if [ "$env" = "prod" ]; then
            log "   Monitoring: http://your-server:3000 (Grafana)"
            log "   Metrics: http://your-server:9090 (Prometheus)"
        fi
    else
        log "❌ Deployment failed - some services are unhealthy"
        return 1
    fi
}

# Остановка платформы
stop() {
    log "⏹️ Stopping learning platform..."
    
    if [ -f "$PROD_COMPOSE_FILE" ]; then
        docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" down
    else
        docker-compose -f "$COMPOSE_FILE" down
    fi
    
    log "✅ Platform stopped"
}

# Перезапуск конкретного модуля
restart_module() {
    local module="$1"
    
    if [ -z "$module" ]; then
        echo "Usage: $0 restart-module <module-name>"
        echo "Available modules: javascript-basics, python-basics, html-css-basics, platform-hub"
        return 1
    fi
    
    log "🔄 Restarting module: $module"
    
    docker-compose restart "$module"
    
    log "⏳ Waiting for module to restart..."
    sleep 10
    
    # Проверяем что модуль запустился
    if docker ps --format "table {{.Names}}" | grep -q "$module"; then
        log "✅ Module $module restarted successfully"
    else
        log "❌ Module $module failed to restart"
        return 1
    fi
}

# Обновление образов
update_images() {
    log "📥 Updating Docker images..."
    
    # Получаем список используемых образов
    local images=$(docker-compose config | grep 'image:' | awk '{print $2}' | sort -u)
    
    for image in $images; do
        log "📥 Pulling $image..."
        docker pull "$image"
    done
    
    log "✅ Images updated"
    log "ℹ️ Run 'deploy' to use updated images"
}

# Просмотр логов
logs() {
    local service="$1"
    local follow="${2:-false}"
    
    if [ -z "$service" ]; then
        echo "Usage: $0 logs <service-name> [follow]"
        echo "Available services: nginx-proxy, platform-hub, javascript-basics, python-basics, html-css-basics"
        return 1
    fi
    
    if [ "$follow" = "follow" ]; then
        docker-compose logs -f "$service"
    else
        docker-compose logs --tail=100 "$service"
    fi
}

# Создание бэкапа
backup() {
    log "📦 Creating platform backup..."
    
    local backup_dir="/var/backups/learning-platform"
    local backup_name="platform-backup-$(date +%Y%m%d_%H%M%S).tar.gz"
    
    mkdir -p "$backup_dir"
    
    # Создаем архив конфигураций и данных
    tar -czf "$backup_dir/$backup_name" \
        --exclude='node_modules' \
        --exclude='.git' \
        docker-compose.yml \
        docker-compose.prod.yml \
        nginx/ \
        registry/ \
        scripts/ \
        hub-site/
    
    log "✅ Backup created: $backup_dir/$backup_name"
    
    # Показываем размер бэкапа
    local backup_size=$(du -h "$backup_dir/$backup_name" | cut -f1)
    log "📊 Backup size: $backup_size"
}

# Восстановление из бэкапа
restore() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ] || [ ! -f "$backup_file" ]; then
        echo "Usage: $0 restore <backup-file.tar.gz>"
        return 1
    fi
    
    log "📥 Restoring from backup: $backup_file"
    
    # Останавливаем платформу
    stop
    
    # Создаем резервную копию текущей конфигурации
    log "💾 Creating current config backup..."
    backup
    
    # Восстанавливаем из архива
    tar -xzf "$backup_file" -C .
    
    log "✅ Restore completed"
    log "ℹ️ Run 'deploy' to start platform with restored config"
}

# Показ статистики
stats() {
    log "📊 Platform Statistics"
    
    echo "=== Docker Containers ==="
    docker-compose ps
    
    echo -e "\n=== Resource Usage ==="
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    
    echo -e "\n=== Disk Usage ==="
    df -h | grep -E '(Filesystem|/$)'
    
    echo -e "\n=== Service Health ==="
    health_check
}

# Главная функция
main() {
    local command="$1"
    
    case "$command" in
        deploy)
            deploy "${2:-dev}"
            ;;
        stop)
            stop
            ;;
        restart-module)
            restart_module "$2"
            ;;
        health)
            health_check
            ;;
        update)
            update_images
            ;;
        logs)
            logs "$2" "$3"
            ;;
        backup)
            backup
            ;;
        restore)
            restore "$2"
            ;;
        stats)
            stats
            ;;
        *)
            echo "Learning Platform Manager"
            echo ""
            echo "Usage: $0 <command> [options]"
            echo ""
            echo "Commands:"
            echo "  deploy [prod]           Deploy platform (dev or prod environment)"
            echo "  stop                    Stop all platform services"
            echo "  restart-module <name>   Restart specific module"
            echo "  health                  Check health of all services"
            echo "  update                  Update Docker images"
            echo "  logs <service> [follow] Show service logs"
            echo "  backup                  Create platform backup"
            echo "  restore <file>          Restore from backup"
            echo "  stats                   Show platform statistics"
            echo ""
            echo "Examples:"
            echo "  $0 deploy prod"
            echo "  $0 restart-module javascript-basics"
            echo "  $0 logs nginx-proxy follow"
            ;;
    esac
}

# Запуск основной функции
main "$@"
```

**Контрольные процедуры:**
```bash
# Валидация Docker Compose файлов
docker-compose config

# Проверка синтаксиса prod конфигурации
docker-compose -f docker-compose.yml -f docker-compose.prod.yml config

# Тест локального развертывания
chmod +x scripts/platform-manager.sh
./scripts/platform-manager.sh deploy

# Проверка здоровья сервисов
./scripts/platform-manager.sh health

# Тест API endpoints
sleep 30
curl -f http://localhost/api/modules
curl -f http://localhost/health

# Очистка тестового развертывания
./scripts/platform-manager.sh stop
```

**Критерии успеха:**
- ✅ Docker Compose конфигурация валидна
- ✅ Все сервисы запускаются без ошибок
- ✅ Health checks проходят
- ✅ API endpoints доступны
- ✅ Platform manager скрипт работает
- ✅ Логирование и мониторинг функционирует

---

## Этап 6: Создание примеров модулей (спицы)

### Шаг 6.1: Создание модуля JavaScript Basics

**Цель:** Создать полноценный пример учебного модуля с интерактивными тестами

**Действия:**
```bash
# Используем CLI для создания модуля
cd build-templates
./cli/create-module.js create \
  --name "javascript-basics" \
  --category "programming" \
  --difficulty "beginner"

# Или создаем структуру вручную
mkdir javascript-basics && cd javascript-basics
git init
```

**Структура модуля JavaScript Basics:**
```
javascript-basics/
├── .github/workflows/
│   └── deploy.yml
├── content/
│   ├── _index.md
│   ├── lessons/
│   │   ├── _index.md
│   │   ├── 01-introduction.md
│   │   ├── 02-variables.md
│   │   ├── 03-functions.md
│   │   ├── 04-objects.md
│   │   └── 05-dom.md
│   ├── exercises/
│   │   ├── _index.md
│   │   └── practice.md
│   └── resources/
│       ├── _index.md
│       └── links.md
├── static/
│   ├── quizzes/
│   │   ├── lesson-01-intro.json
│   │   ├── lesson-02-variables.json
│   │   ├── lesson-03-functions.json
│   │   ├── lesson-04-objects.json
│   │   └── lesson-05-dom.json
│   ├── exercises/
│   │   ├── variables-practice.html
│   │   └── dom-manipulation.html
│   └── images/
├── hugo.toml
├── Dockerfile
├── nginx.conf
├── package.json             # Для development dependencies
└── README.md
```

**Конфигурация модуля:**
```toml
# hugo.toml
baseURL = "https://js.learn.example.com"
languageCode = "ru"
title = "JavaScript Основы"
theme = "learning-platform"

[params]
  course_name = "JavaScript Основы"
  course_category = "programming"
  course_difficulty = "beginner"
  course_duration = "40 часов"
  course_description = "Изучение основ JavaScript с нуля до создания интерактивных веб-приложений"
  
  # Информация о платформе
  [params.platform]
    hub_url = "https://learn.example.com"
    navigation_enabled = true
    
  # Quiz Engine настройки
  [params.quiz]
    default_language = "ru"
    show_progress = true
    allow_retry = true

  # SEO
  [params.seo]
    keywords = ["javascript", "программирование", "веб-разработка", "frontend"]

# Меню навигации
[[menu.main]]
  name = "Главная"
  url = "/"
  weight = 10
  
[[menu.main]]
  name = "Уроки"
  url = "/lessons/"
  weight = 20
  
[[menu.main]]
  name = "Упражнения"
  url = "/exercises/"
  weight = 30
  
[[menu.main]]
  name = "Ресурсы"
  url = "/resources/"
  weight = 40

[[menu.main]]
  name = "🏠 Все курсы"
  url = "https://learn.example.com"
  weight = 50

# Типы контента
[taxonomies]
  lesson = "lessons"
  difficulty = "difficulties"
  tag = "tags"
```

**Главная страница модуля:**
```markdown
<!-- content/_index.md -->
---
title: "JavaScript Основы"
description: "Изучение основ JavaScript с нуля до создания интерактивных веб-приложений"
---

# JavaScript Основы 🚀

Добро пожаловать на курс изучения основ JavaScript! Этот курс поможет вам освоить один из самых популярных языков программирования.

## О курсе

JavaScript - это язык программирования, который делает веб-страницы интерактивными. Вы изучите:

- 📝 **Основы синтаксиса** - переменные, типы данных, операторы
- 🔧 **Функции** - создание переиспользуемого кода  
- 📦 **Объекты** - организация данных и функций
- 🌐 **DOM манипуляции** - изменение веб-страниц
- 🎯 **Практические проекты** - реальные примеры применения

## Структура курса

{{< lessons-overview >}}

## Быстрый тест знаний

Проверьте свои текущие знания JavaScript:

{{< quiz src="/quizzes/lesson-01-intro.json" id="intro-quiz" >}}

## Начать обучение

Готовы начать? Переходите к [первому уроку](/lessons/01-introduction/)!

---

**Совет:** Каждый урок содержит интерактивные тесты для закрепления материала. Не пропускайте их!
```

**Пример урока с тестами:**
```markdown
<!-- content/lessons/02-variables.md -->
---
title: "Урок 2: Переменные в JavaScript"
weight: 2
lesson: true
difficulty: "beginner"
tags: ["variables", "basics", "syntax"]
---

# Урок 2: Переменные в JavaScript

Переменные - это основа любого языка программирования. В JavaScript есть несколько способов объявления переменных.

## Типы объявления переменных

### var - устаревший способ

```javascript
var name = "Иван";
var age = 25;
console.log(name, age); // Иван 25
```

### let - современный способ

```javascript
let city = "Москва";
let population = 12000000;

// Можно изменить значение
city = "Санкт-Петербург";
```

### const - для констант

```javascript
const PI = 3.14159;
const COMPANY_NAME = "Learning Platform";

// PI = 3.14; // Ошибка! Нельзя изменить константу
```

## Типы данных

JavaScript - динамически типизированный язык:

```javascript
let value = 42;           // число
value = "Hello";          // строка
value = true;             // булево значение
value = null;             // null
value = undefined;        // undefined
value = {name: "Иван"};   // объект
value = [1, 2, 3];        // массив
```

## Правила именования

✅ **Правильно:**
```javascript
let userName = "ivan";
let _private = "secret";
let $element = document.getElementById('my-div');
let counter2 = 0;
```

❌ **Неправильно:**
```javascript
let 2counter = 0;     // начинается с цифры
let user-name = "";   // содержит дефис
let let = "value";    // зарезервированное слово
```

## Области видимости

### Глобальная область видимости

```javascript
var globalVar = "Доступна везде";

function showGlobal() {
    console.log(globalVar); // Работает
}
```

### Функциональная область видимости

```javascript
function myFunction() {
    var localVar = "Только внутри функции";
    
    console.log(localVar); // Работает
}

// console.log(localVar); // Ошибка!
```

### Блочная область видимости

```javascript
if (true) {
    let blockVar = "Только в блоке";
    const blockConst = "Тоже только в блоке";
    
    console.log(blockVar); // Работает
}

// console.log(blockVar); // Ошибка!
```

## Практический пример

Создадим простой счетчик:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Счетчик</title>
</head>
<body>
    <h1 id="counter">0</h1>
    <button onclick="increment()">+1</button>
    <button onclick="decrement()">-1</button>
    <button onclick="reset()">Сброс</button>

    <script>
        let count = 0;
        const counterElement = document.getElementById('counter');

        function increment() {
            count++;
            updateDisplay();
        }

        function decrement() {
            count--;
            updateDisplay();
        }

        function reset() {
            count = 0;
            updateDisplay();
        }

        function updateDisplay() {
            counterElement.textContent = count;
        }
    </script>
</body>
</html>
```

## Проверочные задания

### Тест на понимание переменных

{{< quiz src="/quizzes/lesson-02-variables.json" >}}

### Интерактивное упражнение

Попробуйте сами создать переменные:

{{< code-editor >}}
```javascript
// Создайте переменные для:
// 1. Вашего имени (строка)
// 2. Вашего возраста (число)
// 3. Любите ли вы программирование (булево)

// Ваш код здесь:

```
{{< /code-editor >}}

## Домашнее задание

1. Создайте HTML-страницу с формой для ввода имени и возраста
2. Используйте JavaScript для отображения приветствия
3. Добавьте валидацию введенных данных

## Что дальше?

В следующем уроке мы изучим [функции в JavaScript](/lessons/03-functions/) - способ организации и переиспользования кода.

---

**💡 Совет:** Практикуйтесь писать код каждый день. Даже 15 минут в день дадут отличный результат!
```

**Файлы тестов для модуля:**
```json
// static/quizzes/lesson-02-variables.json
{
  "config": {
    "type": "single-choice",
    "showExplanation": "all",
    "showTryAgainButton": true
  },
  "question": {
    "ru": "Какой из способов объявления переменных является устаревшим?",
    "en": "Which variable declaration method is deprecated?"
  },
  "answers": [
    {
      "text": { "ru": "var", "en": "var" },
      "correct": true,
      "description": {
        "ru": "Правильно! 'var' считается устаревшим способом. Используйте 'let' и 'const'.",
        "en": "Correct! 'var' is considered deprecated. Use 'let' and 'const' instead."
      }
    },
    {
      "text": { "ru": "let", "en": "let" },
      "correct": false,
      "description": {
        "ru": "'let' - современный способ объявления изменяемых переменных.",
        "en": "'let' is a modern way to declare mutable variables."
      }
    },
    {
      "text": { "ru": "const", "en": "const" },
      "correct": false,
      "description": {
        "ru": "'const' используется для объявления констант.",
        "en": "'const' is used to declare constants."
      }
    }
  ]
}
```

```json
// static/quizzes/lesson-03-functions.json
{
  "config": {
    "type": "multiple-choice", 
    "showExplanation": "selected"
  },
  "question": {
    "ru": "Выберите все правильные способы объявления функций в JavaScript:",
    "en": "Select all correct ways to declare functions in JavaScript:"
  },
  "answers": [
    {
      "text": { 
        "ru": "function myFunction() {}", 
        "en": "function myFunction() {}" 
      },
      "correct": true,
      "description": {
        "ru": "Классическое объявление функции (Function Declaration).",
        "en": "Classic function declaration."
      }
    },
    {
      "text": { 
        "ru": "const myFunction = function() {}", 
        "en": "const myFunction = function() {}" 
      },
      "correct": true,
      "description": {
        "ru": "Функциональное выражение (Function Expression).",
        "en": "Function expression."
      }
    },
    {
      "text": { 
        "ru": "const myFunction = () => {}", 
        "en": "const myFunction = () => {}" 
      },
      "correct": true,
      "description": {
        "ru": "Стрелочная функция (Arrow Function) - современный ES6 синтаксис.",
        "en": "Arrow function - modern ES6 syntax."
      }
    },
    {
      "text": { 
        "ru": "function = myFunction() {}", 
        "en": "function = myFunction() {}" 
      },
      "correct": false,
      "description": {
        "ru": "Неправильный синтаксис. 'function' - зарезервированное слово.",
        "en": "Invalid syntax. 'function' is a reserved word."
      }
    }
  ]
}
```

**Dockerfile для модуля:**
```dockerfile
# Dockerfile
# Многоэтапная сборка для JavaScript Basics модуля
FROM ghcr.io/learning-platform-org/shared-hugo-base:latest AS base

# Стадия сборки Hugo сайта
FROM klakegg/hugo:ext-alpine AS builder

WORKDIR /src

# Копируем shared компоненты из базового образа  
COPY --from=base /shared-base/themes ./themes
COPY --from=base /shared-base/static ./static

# Копируем контент модуля
COPY content/ content/
COPY static/ static/
COPY hugo.toml .

# Дополнительные файлы для этого модуля
COPY package.json ./

# Устанавливаем dev зависимости если нужно
RUN apk add --no-cache nodejs npm
RUN if [ -f package.json ]; then npm install --only=production || true; fi

# Сборка сайта
RUN hugo --minify --enableGitInfo

# Валидация сборки
RUN test -f public/index.html || (echo "❌ Build failed: no index.html" && exit 1)
RUN find public -name "*.html" -exec grep -l "quiz-container" {} \; | head -1 | \
    xargs test -f && echo "✅ Quiz integration validated" || \
    echo "⚠️ No quizzes found (this may be intentional)"

# Проверяем количество страниц
RUN PAGES_COUNT=$(find public -name "*.html" | wc -l) && \
    echo "📄 Generated $PAGES_COUNT HTML pages" && \
    [ $PAGES_COUNT -gt 5 ] || (echo "❌ Too few pages generated" && exit 1)

# Production стадия с nginx
FROM nginx:alpine

# Копируем собранный сайт
COPY --from=builder /src/public /usr/share/nginx/html

# Конфигурация nginx для модуля
COPY nginx.conf /etc/nginx/nginx.conf

# Healthcheck endpoint
RUN echo '<!DOCTYPE html><html><body><h1>JavaScript Basics Module - Healthy</h1><p>Status: OK</p></body></html>' > /usr/share/nginx/html/health/index.html

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/health/ || exit 1

# Метаданные
LABEL org.opencontainers.image.title="JavaScript Basics Module" \
      org.opencontainers.image.description="Learning module: JavaScript fundamentals" \
      org.opencontainers.image.source="https://github.com/learning-platform-org/javascript-basics" \
      org.opencontainers.image.version="1.0.0" \
      learning.platform.module="javascript-basics" \
      learning.platform.category="programming" \
      learning.platform.difficulty="beginner" \
      learning.platform.lessons="5" \
      learning.platform.quizzes="5"

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Nginx конфигурация для модуля:**
```nginx
# nginx.conf
user nginx;
worker_processes 1;

error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Логирование
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;

    # Базовые настройки
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_min_length 10240;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/x-javascript
        application/xml+rss
        application/json;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html index.htm;

        # Основные страницы
        location / {
            try_files $uri $uri/ $uri.html /index.html;
        }

        # Health check
        location /health {
            access_log off;
            try_files /health/index.html =200;
        }

        # Статические файлы с длительным кешированием
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # JSON файлы (квизы) с коротким кешированием
        location ~* \.json$ {
            expires 5m;
            add_header Cache-Control "public, max-age=300";
        }

        # Безопасность - скрыть системные файлы
        location ~ /\. {
            deny all;
        }
        
        location ~ ~$ {
            deny all;
        }
    }
}
```

**Package.json для development:**
```json
{
  "name": "javascript-basics-module",
  "version": "1.0.0",
  "description": "Learning module for JavaScript basics",
  "scripts": {
    "dev": "hugo server -D --bind 0.0.0.0",
    "build": "hugo --minify",
    "validate-quizzes": "node scripts/validate-quizzes.js",
    "test": "npm run validate-quizzes && npm run build"
  },
  "devDependencies": {
    "ajv": "^8.12.0",
    "ajv-formats": "^2.1.1"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/learning-platform-org/javascript-basics"
  },
  "keywords": ["javascript", "learning", "education", "programming"],
  "license": "MIT"
}
```

**Скрипт валидации квизов модуля:**
```javascript
// scripts/validate-quizzes.js
const fs = require('fs');
const path = require('path');
const Ajv = require('ajv');
const addFormats = require('ajv-formats');

class QuizValidator {
  constructor() {
    this.ajv = new Ajv({ allErrors: true });
    addFormats(this.ajv);
    
    // Базовая схема для квизов
    this.quizSchema = {
      type: "object",
      required: ["config", "question", "answers"],
      properties: {
        config: {
          type: "object",
          required: ["type"],
          properties: {
            type: { enum: ["single-choice", "multiple-choice", "input-field"] },
            showExplanation: { enum: ["all", "selected", "none"] },
            showTryAgainButton: { type: "boolean" },
            caseSensitive: { type: "boolean" },
            showExplanationOnError: { type: "boolean" }
          }
        },
        question: {
          type: "object",
          properties: {
            ru: { type: "string", minLength: 5 },
            en: { type: "string", minLength: 5 }
          },
          required: ["ru"]
        },
        answers: {
          type: "array",
          minItems: 2,
          items: {
            type: "object",
            required: ["text", "correct"],
            properties: {
              text: {
                type: "object",
                properties: {
                  ru: { type: "string", minLength: 1 },
                  en: { type: "string", minLength: 1 }
                },
                required: ["ru"]
              },
              correct: { type: "boolean" },
              description: {
                type: "object",
                properties: {
                  ru: { type: "string" },
                  en: { type: "string" }
                }
              }
            }
          }
        },
        answer: { type: "string" }, // Для input-field типа
        explanation: {
          type: "object",
          properties: {
            ru: { type: "string" },
            en: { type: "string" }
          }
        }
      }
    };

    this.validate = this.ajv.compile(this.quizSchema);
  }

  validateAllQuizzes() {
    console.log('🎯 Validating all quiz files...\n');

    const quizzesDir = 'static/quizzes';
    
    if (!fs.existsSync(quizzesDir)) {
      console.log('⚠️ No quizzes directory found');
      return true;
    }

    const files = fs.readdirSync(quizzesDir)
      .filter(file => file.endsWith('.json'));

    if (files.length === 0) {
      console.log('⚠️ No quiz files found');
      return true;
    }

    let allValid = true;
    let totalQuizzes = 0;
    let totalQuestions = 0;

    for (const file of files) {
      const result = this.validateQuizFile(path.join(quizzesDir, file));
      if (!result.valid) {
        allValid = false;
      } else {
        totalQuizzes++;
        totalQuestions += result.questionsCount;
      }
    }

    console.log('\n📊 Validation Summary:');
    console.log(`  Total quiz files: ${files.length}`);
    console.log(`  Valid quizzes: ${totalQuizzes}`);
    console.log(`  Total questions: ${totalQuestions}`);
    
    if (allValid) {
      console.log('✅ All quiz files are valid!');
    } else {
      console.log('❌ Some quiz files have validation errors');
    }

    return allValid;
  }

  validateQuizFile(filePath) {
    const filename = path.basename(filePath);
    
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const quiz = JSON.parse(content);

      // JSON schema validation
      const isValid = this.validate(quiz);
      
      if (!isValid) {
        console.log(`❌ ${filename}:`);
        this.validate.errors.forEach(error => {
          console.log(`    • ${error.instancePath || 'root'}: ${error.message}`);
        });
        return { valid: false, questionsCount: 0 };
      }

      // Дополнительные логические проверки
      const logicValidation = this.validateQuizLogic(quiz, filename);
      
      if (logicValidation.valid) {
        console.log(`✅ ${filename} - valid (${logicValidation.questionsCount} questions)`);
        return { valid: true, questionsCount: logicValidation.questionsCount };
      } else {
        return { valid: false, questionsCount: 0 };
      }

    } catch (error) {
      console.log(`❌ ${filename}: ${error.message}`);
      return { valid: false, questionsCount: 0 };
    }
  }

  validateQuizLogic(quiz, filename) {
    const errors = [];

    // Проверяем количество правильных ответов
    if (quiz.answers) {
      const correctAnswers = quiz.answers.filter(a => a.correct);
      
      if (quiz.config.type === 'single-choice' && correctAnswers.length !== 1) {
        errors.push('Single-choice quiz must have exactly one correct answer');
      }
      
      if (quiz.config.type === 'multiple-choice' && correctAnswers.length < 1) {
        errors.push('Multiple-choice quiz must have at least one correct answer');
      }

      // Проверяем что не все ответы правильные (кроме input-field)
      if (quiz.config.type !== 'input-field' && correctAnswers.length === quiz.answers.length) {
        errors.push('Not all answers should be correct');
      }
    }

    // Специальная проверка для input-field
    if (quiz.config.type === 'input-field') {
      if (!quiz.answer || typeof quiz.answer !== 'string') {
        errors.push('Input-field quiz must have an "answer" field with string value');
      }
    }

    // Проверяем наличие объяснений если showExplanation включен
    if (quiz.config.showExplanation && quiz.config.showExplanation !== 'none') {
      const hasDescriptions = quiz.answers?.some(answer => 
        answer.description && (answer.description.ru || answer.description.en)
      );
      
      if (!hasDescriptions && !quiz.explanation) {
        errors.push('Quiz with showExplanation should have descriptions or explanation field');
      }
    }

    if (errors.length > 0) {
      console.log(`❌ ${filename}:`);
      errors.forEach(error => {
        console.log(`    • ${error}`);
      });
      return { valid: false, questionsCount: 0 };
    }

    return { 
      valid: true, 
      questionsCount: quiz.answers ? quiz.answers.length : 1
    };
  }

  generateQuizReport() {
    console.log('📋 Generating quiz report...\n');

    const quizzesDir = 'static/quizzes';
    
    if (!fs.existsSync(quizzesDir)) {
      console.log('No quizzes found');
      return;
    }

    const files = fs.readdirSync(quizzesDir)
      .filter(file => file.endsWith('.json'));

    const report = {
      total_files: files.length,
      by_type: {},
      by_difficulty: {},
      lessons_coverage: [],
      issues: []
    };

    files.forEach(file => {
      try {
        const content = fs.readFileSync(path.join(quizzesDir, file), 'utf8');
        const quiz = JSON.parse(content);

        // Подсчет по типам
        const type = quiz.config.type;
        report.by_type[type] = (report.by_type[type] || 0) + 1;

        // Определение урока из имени файла
        const lessonMatch = file.match(/lesson-(\d+)/);
        if (lessonMatch) {
          report.lessons_coverage.push({
            lesson: lessonMatch[1],
            file: file,
            type: type
          });
        }

      } catch (error) {
        report.issues.push({
          file: file,
          error: error.message
        });
      }
    });

    console.log('📊 Quiz Report:');
    console.log(`  Total quiz files: ${report.total_files}`);
    console.log(`  By type:`, report.by_type);
    console.log(`  Lessons covered: ${report.lessons_coverage.length}`);
    
    if (report.issues.length > 0) {
      console.log(`  Issues found: ${report.issues.length}`);
      report.issues.forEach(issue => {
        console.log(`    • ${issue.file}: ${issue.error}`);
      });
    }

    return report;
  }
}

// CLI использование
if (require.main === module) {
  const command = process.argv[2];
  const validator = new QuizValidator();

  switch (command) {
    case 'report':
      validator.generateQuizReport();
      break;
    case 'validate':
    default:
      const isValid = validator.validateAllQuizzes();
      process.exit(isValid ? 0 : 1);
  }
}

module.exports = QuizValidator;
```

**GitHub Actions workflow для модуля:**
```yaml
# .github/workflows/deploy.yml
name: Deploy JavaScript Basics Module

on:
  push:
    branches: [main]
    paths:
      - 'content/**'
      - 'static/**'
      - 'hugo.toml'
      - 'Dockerfile'
      - 'nginx.conf'
  repository_dispatch:
    types: [shared-base-updated, content-updated]
  workflow_dispatch:

env:
  MODULE_NAME: javascript-basics
  IMAGE_NAME: ghcr.io/${{ github.repository }}

jobs:
  validate-content:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Validate quiz files
      run: npm run validate-quizzes
        
    - name: Check content structure
      run: |
        echo "📁 Checking content structure..."
        
        # Проверяем обязательные файлы
        test -f hugo.toml || (echo "❌ hugo.toml missing" && exit 1)
        test -f content/_index.md || (echo "❌ content/_index.md missing" && exit 1)
        test -d content/lessons || (echo "❌ lessons directory missing" && exit 1)
        
        # Проверяем что есть уроки
        LESSONS_COUNT=$(find content/lessons -name "*.md" | wc -l)
        echo "📖 Found $LESSONS_COUNT lesson files"
        [ $LESSONS_COUNT -ge 3 ] || (echo "❌ Need at least 3 lessons" && exit 1)
        
        # Проверяем квизы
        if [ -d static/quizzes ]; then
          QUIZZES_COUNT=$(find static/quizzes -name "*.json" | wc -l)
          echo "🎯 Found $QUIZZES_COUNT quiz files"
          [ $QUIZZES_COUNT -ge 1 ] || echo "⚠️ No quizzes found"
        fi
        
        echo "✅ Content structure valid"
        
    - name: Lint Markdown
      uses: DavidAnson/markdownlint-cli2-action@v13
      with:
        globs: 'content/**/*.md'
        config: '.markdownlint.json'
        
    - name: Upload validation artifacts
      if: failure()
      uses: actions/upload-artifact@v4
      with:
        name: validation-errors
        path: |
          npm-debug.log
          .markdownlint.json
        retention-days: 3

  build-and-test:
    needs: validate-content
    runs-on: ubuntu-latest
    
    outputs:
      image-digest: ${{ steps.build.outputs.digest }}
      pages-count: ${{ steps.test.outputs.pages }}
      
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
      
    - name: Login to GitHub Container Registry
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}
          
    - name: Build and push
      id: build
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
        
    - name: Test container
      id: test
      run: |
        echo "🧪 Testing built container..."
        
        # Запускаем контейнер для теста
        docker run -d --name test-module -p 8080:80 ${{ env.IMAGE_NAME }}:latest
        
        # Ждем запуска
        sleep 15
        
        # Проверяем доступность
        curl -f http://localhost:8080/ || (echo "❌ Site not accessible" && exit 1)
        
        # Проверяем health endpoint
        curl -f http://localhost:8080/health/ || (echo "❌ Health check failed" && exit 1)
        
        # Считаем страницы
        PAGES_COUNT=$(curl -s http://localhost:8080/sitemap.xml | grep -o '<loc>' | wc -l || echo "0")
        echo "📄 Found $PAGES_COUNT pages in sitemap"
        echo "pages=$PAGES_COUNT" >> $GITHUB_OUTPUT
        
        # Проверяем наличие Quiz Engine (если есть квизы)
        if docker exec test-module find /usr/share/nginx/html -name "*.json" | grep -q quizzes; then
          curl -s http://localhost:8080/ | grep -q "quiz-container" && \
            echo "✅ Quiz integration working" || \
            echo "⚠️ Quiz containers not found in HTML"
        fi
        
        # Очистка
        docker stop test-module
        docker rm test-module
        
        echo "✅ Container test passed"

  deploy:
    needs: build-and-test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to production
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.PROD_HOST }}
        username: ${{ secrets.PROD_USERNAME }}
        key: ${{ secrets.PROD_SSH_KEY }}
        script: |
          echo "🚀 Deploying ${{ env.MODULE_NAME }} module..."
          
          cd /opt/learning-platform
          
          # Получаем новый образ
          docker pull ${{ env.IMAGE_NAME }}:latest
          
          # Обновляем сервис
          docker-compose up -d --no-deps ${{ env.MODULE_NAME }}
          
          # Ждем запуска
          sleep 20
          
          # Проверяем доступность
          curl -f https://js.learn.example.com/health/ && \
            echo "✅ ${{ env.MODULE_NAME }} deployed successfully" || \
            (echo "❌ Deployment verification failed" && exit 1)
            
    - name: Update module registry
      uses: peter-evans/repository-dispatch@v3
      with:
        token: ${{ secrets.PAT_TOKEN }}
        repository: learning-platform-org/platform-hub
        event-type: module-updated
        client-payload: |
          {
            "module_name": "${{ env.MODULE_NAME }}",
            "module_title": "JavaScript Основы",
            "subdomain": "js",
            "category": "programming",
            "difficulty": "beginner",
            "image_digest": "${{ needs.build-and-test.outputs.image-digest }}",
            "pages_count": "${{ needs.build-and-test.outputs.pages-count }}",
            "updated_at": "${{ github.event.head_commit.timestamp }}"
          }
          
    - name: Performance test
      if: success()
      run: |
        echo "🏃‍♂️ Running performance test..."
        
        # Простой тест загрузки страниц
        for url in "https://js.learn.example.com/" "https://js.learn.example.com/lessons/"; do
          RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' "$url")
          echo "⏱️ $url: ${RESPONSE_TIME}s"
          
          # Проверяем что время загрузки разумное
          if (( $(echo "$RESPONSE_TIME > 3.0" | bc -l) )); then
            echo "⚠️ Slow response time for $url"
          fi
        done
```

**Контрольные процедуры:**
```bash
# Создание модуля JavaScript Basics
mkdir javascript-basics && cd javascript-basics

# Тест структуры
find . -type f | sort

# Валидация Hugo конфигурации
hugo config | head -20

# Тест сборки модуля
hugo --minify

# Проверка что все страницы собрались
PAGES_COUNT=$(find public -name "*.html" | wc -l)
echo "Generated $PAGES_COUNT pages"
[ $PAGES_COUNT -gt 5 ] && echo "✅ Sufficient pages generated"

# Валидация квизов
npm install
npm run validate-quizzes

# Тест Docker сборки
docker build -t js-basics-test .

# Тест контейнера
docker run -d --name js-test -p 3000:80 js-basics-test
sleep 10

# Проверки
curl -f http://localhost:3000/ && echo "✅ Site accessible"
curl -f http://localhost:3000/health/ && echo "✅ Health check OK"

# Проверка квизов в HTML
curl -s http://localhost:3000/lessons/02-variables/ | grep -q "quiz-container" && \
  echo "✅ Quiz integration found"

# Очистка
docker stop js-test && docker rm js-test
docker rmi js-basics-test
```

**Критерии успеха:**
- ✅ Модуль содержит минимум 5 уроков
- ✅ Каждый урок имеет связанный квиз
- ✅ Все квизы проходят валидацию
- ✅ Hugo собирает сайт без ошибок
- ✅ Docker образ собирается и запускается
- ✅ Health check работает
- ✅ CI/CD pipeline проходит все этапы
- ✅ Quiz Engine интегрирован корректно

---

### Шаг 6.2: Создание модуля Python Basics

**Цель:** Создать второй пример модуля для демонстрации масштабируемости

**Действия:**
```bash
# Создаем модуль Python с использованием CLI
../build-templates/cli/create-module.js create \
  --name "python-basics" \
  --category "programming" \
  --difficulty "beginner" \
  --subdomain "python"
```

**Особенности Python модуля:**
- Интерактивные примеры кода с Python REPL
- Упражнения с проверкой синтаксиса
- Постепенное усложнение от переменных к классам

**Структура контента:**
```
content/
├── _index.md
├── lessons/
│   ├── 01-introduction.md      # "Что такое Python?"
│   ├── 02-installation.md      # "Установка и настройка"
│   ├── 03-variables.md         # "Переменные и типы данных"
│   ├── 04-control-flow.md      # "Условия и циклы"
│   ├── 05-functions.md         # "Функции"
│   ├── 06-data-structures.md   # "Списки, словари, множества"
│   ├── 07-files.md            # "Работа с файлами"
│   ├── 08-classes.md          # "Классы и объекты"
│   ├── 09-modules.md          # "Модули и пакеты"
│   └── 10-final-project.md    # "Итоговый проект"
└── exercises/
    ├── calculator.md          # "Создание калькулятора"
    └── todo-app.md           # "Список дел"
```

**Пример урока Python модуля:**
```markdown
<!-- content/lessons/03-variables.md -->
---
title: "Урок 3: Переменные и типы данных в Python"
weight: 3
lesson: true
difficulty: "beginner"
tags: ["variables", "data-types", "basics"]
---

# Урок 3: Переменные и типы данных в Python

Python - динамически типизированный язык, что означает, что тип переменной определяется автоматически.

## Создание переменных

В Python не нужно объявлять тип переменной заранее:

```python
# Числа
age = 25
price = 19.99
temperature = -5

# Строки
name = "Анна"
city = 'Москва'
message = """Многострочный
текст в Python"""

# Логические значения
is_student = True
is_working = False

# Особые значения
nothing = None
```

## Основные типы данных

### 1. Числовые типы

```python
# int - целые числа
count = 42
year = 2024

# float - числа с плавающей точкой
pi = 3.14159
salary = 50000.50

# complex - комплексные числа (редко используются)
complex_num = 3 + 4j
```

### 2. Строки (str)

```python
# Разные способы создания строк
single_quotes = 'Привет'
double_quotes = "Мир"
multiline = """Это
многострочная
строка"""

# Конкатенация строк
full_greeting = single_quotes + ", " + double_quotes + "!"
print(full_greeting)  # Привет, Мир!

# Форматирование строк
name = "Иван"
age = 30
message = f"Меня зовут {name}, мне {age} лет"
print(message)  # Меня зовут Иван, мне 30 лет
```

### 3. Логический тип (bool)

```python
is_sunny = True
is_raining = False

# Логические операции
both_conditions = is_sunny and not is_raining
print(both_conditions)  # True

# Преобразование к bool
print(bool(1))        # True
print(bool(0))        # False
print(bool("text"))   # True
print(bool(""))       # False
print(bool([]))       # False (пустой список)
print(bool([1, 2]))   # True (непустой список)
```

## Операции с переменными

### Арифметические операции

```python
a = 10
b = 3

print(a + b)    # 13 - сложение
print(a - b)    # 7  - вычитание
print(a * b)    # 30 - умножение
print(a / b)    # 3.333... - деление
print(a // b)   # 3  - целочисленное деление
print(a % b)    # 1  - остаток от деления
print(a ** b)   # 1000 - возведение в степень
```

### Операции со строками

```python
first_name = "Иван"
last_name = "Иванов"

# Конкатенация
full_name = first_name + " " + last_name
print(full_name)  # Иван Иванов

# Повторение
separator = "-" * 20
print(separator)  # --------------------

# Длина строки
print(len(full_name))  # 11

# Методы строк
print(full_name.upper())      # ИВАН ИВАНОВ
print(full_name.lower())      # иван иванов
print(full_name.split())      # ['Иван', 'Иванов']
```

## Ввод данных от пользователя

```python
# Ввод всегда возвращает строку
name = input("Введите ваше имя: ")
print(f"Привет, {name}!")

# Преобразование типов
age_str = input("Введите ваш возраст: ")
age = int(age_str)  # Преобразуем строку в число

# Можно объединить в одну строку
age = int(input("Введите ваш возраст: "))
```

## Определение типа переменной

```python
x = 42
y = "Hello"
z = True

print(type(x))  # <class 'int'>
print(type(y))  # <class 'str'>
print(type(z))  # <class 'bool'>

# Проверка типа
print(isinstance(x, int))    # True
print(isinstance(y, str))    # True
print(isinstance(z, bool))   # True
```

## Практический пример: Калькулятор

```python
print("=== Простой калькулятор ===")

# Получаем данные от пользователя
num1 = float(input("Введите первое число: "))
operator = input("Введите операцию (+, -, *, /): ")
num2 = float(input("Введите второе число: "))

# Выполняем вычисления
if operator == "+":
    result = num1 + num2
elif operator == "-":
    result = num1 - num2
elif operator == "*":
    result = num1 * num2
elif operator == "/":
    if num2 != 0:
        result = num1 / num2
    else:
        print("Ошибка: деление на ноль!")
        result = None
else:
    print("Неизвестная операция!")
    result = None

# Выводим результат
if result is not None:
    print(f"Результат: {num1} {operator} {num2} = {result}")
```

## Проверочные задания

### Тест на понимание типов данных

{{< quiz src="/quizzes/lesson-03-variables.json" >}}

### Интерактивное упражнение

Попробуйте создать программу для расчета ИМТ:

{{< code-editor lang="python" >}}
```python
# Программа расчета индекса массы тела (ИМТ)
# Формула: ИМТ = вес / (рост_в_метрах ** 2)

# Получите от пользователя:
# 1. Имя
# 2. Вес в килограммах  
# 3. Рост в сантиметрах

# Рассчитайте и выведите:
# 1. ИМТ
# 2. Интерпретацию результата:
#    - < 18.5: недостаточный вес
#    - 18.5-24.9: нормальный вес  
#    - 25-29.9: избыточный вес
#    - >= 30: ожирение

# Ваш код здесь:

```
{{< /code-editor >}}

## Домашнее задание

1. Создайте программу-анкету, которая:
   - Запрашивает у пользователя имя, возраст, город
   - Рассчитывает год рождения
   - Выводит красиво оформленный результат

2. Напишите программу для конвертации валют:
   - Доллары в рубли и обратно
   - Используйте актуальный курс валют

3. Создайте игру "Угадай число":
   - Программа загадывает число от 1 до 100
   - Пользователь пытается угадать
   - Программа подсказывает "больше" или "меньше"

## Что дальше?

В следующем уроке мы изучим [условия и циклы](/lessons/04-control-flow/) - основу логики программ.

---

**💡 Совет:** Python очень гибкий в работе с типами данных. Изучите преобразования типов - это пригодится в реальных проектах!
```

**Квиз файл для Python модуля:**
```json
// static/quizzes/lesson-03-variables.json
{
  "config": {
    "type": "single-choice",
    "showExplanation": "all"
  },
  "question": {
    "ru": "Какой тип данных получится в результате выполнения: type(3.14)?",
    "en": "What data type will be the result of: type(3.14)?"
  },
  "answers": [
    {
      "text": { "ru": "<class 'float'>", "en": "<class 'float'>" },
      "correct": true,
      "description": {
        "ru": "Правильно! Числа с плавающей точкой имеют тип float.",
        "en": "Correct! Floating point numbers have type float."
      }
    },
    {
      "text": { "ru": "<class 'int'>", "en": "<class 'int'>" },
      "correct": false,
      "description": {
        "ru": "Неверно. int - это целые числа без дробной части.",
        "en": "Incorrect. int is for whole numbers without decimal part."
      }
    },
    {
      "text": { "ru": "<class 'double'>", "en": "<class 'double'>" },
      "correct": false,
      "description": {
        "ru": "В Python нет типа double. Используется float.",
        "en": "Python doesn't have double type. It uses float."
      }
    },
    {
      "text": { "ru": "<class 'number'>", "en": "<class 'number'>" },
      "correct": false,
      "description": {
        "ru": "Тип 'number' не существует в Python.",
        "en": "Type 'number' doesn't exist in Python."
      }
    }
  ]
}
```

**Контрольные процедуры для Python модуля:**
```bash
# Создание модуля
mkdir python-basics && cd python-basics

# Копирование из шаблона или создание через CLI
# ../build-templates/cli/create-module.js create --name "python-basics"

# Проверка структуры
find content -name "*.md" | wc -l  # Должно быть минимум 10 уроков

# Валидация квизов
npm run validate-quizzes

# Тест сборки
hugo --minify

# Проверка специфичного контента Python
grep -r "python\|Python" content/ | head -5

# Docker тесты
docker build -t python-basics-test .
docker run -d --name python-test -p 3001:80 python-basics-test
curl -f http://localhost:3001/health/
docker stop python-test && docker rm python-test
```

**Критерии успеха:**
- ✅ Минимум 8 уроков по Python
- ✅ Интерактивные примеры кода
- ✅ Прогрессия от простого к сложному
- ✅ Практические упражнения
- ✅ Все квизы валидны и соответствуют урокам
- ✅ Docker образ собирается корректно

---

### Шаг 6.3: Создание модуля HTML/CSS Basics

**Цель:** Создать третий модуль, демонстрирующий верстку и дизайн

**Особенности HTML/CSS модуля:**
- Живые примеры HTML/CSS с предпросмотром
- Интерактивные упражнения по верстке
- Адаптивный дизайн и современные CSS техники

**Структура контента:**
```
content/
├── _index.md
├── lessons/
│   ├── 01-html-basics.md        # "Основы HTML"
│   ├── 02-html-structure.md     # "Структура HTML документа" 
│   ├── 03-html-elements.md      # "HTML элементы"
│   ├── 04-css-basics.md         # "Введение в CSS"
│   ├── 05-css-selectors.md      # "CSS селекторы"
│   ├── 06-css-properties.md     # "CSS свойства"
│   ├── 07-layout.md            # "Макеты и позиционирование"
│   ├── 08-responsive.md         # "Адаптивный дизайн"
│   └── 09-final-project.md     # "Создание сайта"
└── projects/
    ├── landing-page.md         # "Лендинг страница"
    └── portfolio.md           # "Портфолио сайт"
```

**Пример урока с живыми примерами:**
```markdown
<!-- content/lessons/04-css-basics.md -->
---
title: "Урок 4: Введение в CSS"
weight: 4
lesson: true
difficulty: "beginner" 
tags: ["css", "styling", "design"]
---

# Урок 4: Введение в CSS

CSS (Cascading Style Sheets) - это язык стилей, который описывает внешний вид HTML документа.

## Что такое CSS?

CSS позволяет:
- 🎨 Изменять цвета, шрифты, размеры
- 📐 Управлять расположением элементов  
- 📱 Создавать адаптивные дизайны
- ✨ Добавлять анимации и эффекты

## Способы подключения CSS

### 1. Внешний файл (рекомендуется)

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <h1>Заголовок</h1>
</body>
</html>
```

### 2. Внутренние стили

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        h1 {
            color: blue;
            font-size: 2em;
        }
    </style>
</head>
<body>
    <h1>Синий заголовок</h1>
</body>
</html>
```

### 3. Встроенные стили

```html
<h1 style="color: red; font-size: 24px;">Красный заголовок</h1>
```

## Синтаксис CSS

```css
селектор {
    свойство: значение;
    свойство: значение;
}
```

**Пример:**
```css
h1 {
    color: #333;
    font-family: Arial, sans-serif;
    text-align: center;
    margin-bottom: 20px;
}
```

## Основные селекторы

### Селектор по тегу

```css
p {
    color: gray;
    line-height: 1.6;
}

h1, h2, h3 {
    color: #2c3e50;
}
```

### Селектор по классу

```html
<div class="highlight">Выделенный текст</div>
<p class="text-large">Крупный текст</p>
```

```css
.highlight {
    background-color: yellow;
    padding: 10px;
}

.text-large {
    font-size: 18px;
    font-weight: bold;
}
```

### Селектор по ID

```html
<div id="header">Шапка сайта</div>
```

```css
#header {
    background-color: #3498db;
    color: white;
    padding: 20px;
    text-align: center;
}
```

## Живой пример

{{< live-example >}}
```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>CSS Пример</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4;
        }
        
        .card {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-width: 400px;
            margin: 0 auto;
        }
        
        .card h2 {
            color: #2c3e50;
            margin-top: 0;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        
        .highlight {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 10px;
            border-radius: 4px;
        }
        
        .btn {
            background-color: #3498db;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        
        .btn:hover {
            background-color: #2980b9;
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>Карточка товара</h2>
        <p>Это пример стильной карточки, созданной с помощью CSS.</p>
        <div class="highlight">
            💡 Наведите на кнопку для эффекта!
        </div>
        <br>
        <button class="btn">Купить сейчас</button>
    </div>
</body>
</html>
```
{{< /live-example >}}

## Основные CSS свойства

### Текст и шрифты

```css
.text-styles {
    /* Шрифт */
    font-family: 'Roboto', Arial, sans-serif;
    font-size: 16px;
    font-weight: bold;
    
    /* Цвет и выравнивание */
    color: #333;
    text-align: center;
    
    /* Межстрочный интервал */
    line-height: 1.5;
    
    /* Декорирование текста */
    text-decoration: underline;
    text-transform: uppercase;
}
```

### Фон и границы

```css
.box {
    /* Фон */
    background-color: #ecf0f1;
    background-image: url('pattern.png');
    
    /* Границы */
    border: 2px solid #bdc3c7;
    border-radius: 10px;
    
    /* Внутренние отступы */
    padding: 20px;
    
    /* Внешние отступы */
    margin: 15px;
}
```

### Размеры и отображение

```css
.element {
    /* Размеры */
    width: 300px;
    height: 200px;
    max-width: 100%;
    
    /* Тип отображения */
    display: block;  /* block, inline, inline-block, flex, grid */
    
    /* Видимость */
    visibility: visible;  /* visible, hidden */
    opacity: 0.8;        /* от 0 до 1 */
}
```

## Каскад и специфичность

CSS означает "Cascading" - каскадные стили. Это значит, что стили применяются по приоритету:

1. **Встроенные стили** (`style="..."`) - наивысший приоритет
2. **ID селекторы** (`#myId`) - высокий приоритет  
3. **Классы** (`.myClass`) - средний приоритет
4. **Теги** (`div`, `p`) - низкий приоритет

```css
/* Специфичность: 1 (тег) */
p {
    color: black;
}

/* Специфичность: 10 (класс) */
.important {
    color: red;
}

/* Специфичность: 100 (ID) */
#special {
    color: blue;
}
```

```html
<p class="important" id="special">Какой будет цвет?</p>
<!-- Ответ: синий, так как ID имеет наивысшую специфичность -->
```

## Практическое задание

Создайте стильную визитную карточку:

{{< code-editor lang="html" >}}
```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Моя визитка</title>
    <style>
        /* Добавьте свои стили здесь */
        body {
            
        }
        
        .business-card {
            
        }
        
        .name {
            
        }
        
        .job-title {
            
        }
        
        .contact {
            
        }
    </style>
</head>
<body>
    <div class="business-card">
        <h1 class="name">Ваше Имя</h1>
        <p class="job-title">Ваша профессия</p>
        <div class="contact">
            <p>📧 email@example.com</p>
            <p>📱 +7 (999) 123-45-67</p>
            <p>🌐 yoursite.com</p>
        </div>
    </div>
</body>
</html>
```
{{< /code-editor >}}

## Проверочные задания

### Тест на знание CSS

{{< quiz src="/quizzes/lesson-04-css.json" >}}

## Домашнее задание

1. **Стилизация страницы**: Возьмите HTML страницу из предыдущего урока и добавьте красивые стили

2. **Создание темы**: Сделайте светлую и темную тему для сайта

3. **Изучение инструментов**: Изучите инструменты разработчика в браузере (F12)

## Полезные ресурсы

- 🎨 [CSS Color Picker](https://www.google.com/search?q=color+picker)
- 📚 [MDN CSS Reference](https://developer.mozilla.org/en-US/docs/Web/CSS)  
- 🎪 [CSS Tricks](https://css-tricks.com/)
- 🎯 [Can I Use](https://caniuse.com/) - совместимость CSS

## Что дальше?

В следующем уроке мы изучим [CSS селекторы](/lessons/05-css-selectors/) более подробно.

---

**💡 Совет:** Не бойтесь экспериментировать с CSS! Лучший способ изучения - практика и творчество.
```

**Shortcode для живых примеров:**
```html
<!-- themes/learning-platform/layouts/shortcodes/live-example.html -->
<div class="live-example">
  <div class="live-example-tabs">
    <button class="tab-btn active" data-tab="preview">👁️ Предпросмотр</button>
    <button class="tab-btn" data-tab="code">💻 Код</button>
  </div>
  
  <div class="live-example-content">
    <div class="tab-content active" id="preview">
      <iframe class="live-preview" srcdoc="{{ .Inner | htmlEscape }}"></iframe>
    </div>
    <div class="tab-content" id="code">
      <pre><code class="language-html">{{ .Inner | htmlEscape }}</code></pre>
    </div>
  </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
  // Инициализация табов для живых примеров
  const tabBtns = document.querySelectorAll('.live-example .tab-btn');
  const tabContents = document.querySelectorAll('.live-example .tab-content');
  
  tabBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const tabId = this.getAttribute('data-tab');
      const container = this.closest('.live-example');
      
      // Убираем активный класс со всех кнопок и контента
      container.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      container.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      
      // Добавляем активный класс
      this.classList.add('active');
      container.querySelector(`#${tabId}`).classList.add('active');
    });
  });
});
</script>

<style>
.live-example {
  border: 1px solid #ddd;
  border-radius: 8px;
  margin: 1.5rem 0;
  overflow: hidden;
}

.live-example-tabs {
  display: flex;
  background: #f8f9fa;
  border-bottom: 1px solid #ddd;
}

.tab-btn {
  padding: 10px 15px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.tab-btn.active {
  background: white;
  border-bottom-color: #007bff;
  color: #007bff;
}

.tab-content {
  display: none;
  padding: 1rem;
}

.tab-content.active {
  display: block;
}

.live-preview {
  width: 100%;
  height: 300px;
  border: none;
  background: white;
  border-radius: 4px;
}

.live-example pre {
  margin: 0;
  max-height: 300px;
  overflow-y: auto;
}
</style>
```

**Контрольные процедуры:**
```bash
# Создание HTML/CSS модуля
mkdir html-css-basics && cd html-css-basics

# Проверка живых примеров
grep -r "live-example" content/ | wc -l

# Валидация HTML в примерах
find content -name "*.md" -exec grep -l "<!DOCTYPE html>" {} \; | head -3

# Тест сборки с live-example shortcode
hugo server -D &
SERVER_PID=$!
sleep 5

# Проверка что shortcode работает
curl -s http://localhost:1313/lessons/04-css-basics/ | grep -q "live-example" && \
  echo "✅ Live examples rendered"

kill $SERVER_PID
```

**Критерии успеха:**
- ✅ Минимум 8 уроков по HTML/CSS
- ✅ Живые примеры кода с предпросмотром
- ✅ Интерактивные упражнения
- ✅ Прогрессивная сложность материала
- ✅ Адаптивный дизайн примеров
- ✅ Все shortcodes работают корректно

---

## Этап 7: Продакшн деплой

### Шаг 7.1: Подготовка сервера

**Цель:** Настроить производственный сервер для развертывания платформы

**Требования к серверу:**
- Ubuntu 20.04+ или CentOS 8+
- Минимум 4GB RAM, 2 CPU cores
- 50GB свободного места
- Статический IP адрес
- Доменное имя (learn.example.com)

**Действия по настройке сервера:**
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка базовых пакетов
sudo apt install -y curl wget git htop nano ufw fail2ban

# Настройка пользователя для деплоя
sudo adduser deploy
sudo usermod -aG sudo deploy
sudo usermod -aG docker deploy

# Настройка SSH ключей
sudo mkdir -p /home/deploy/.ssh
sudo chown deploy:deploy /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh

# Копирование SSH ключа (замените на ваш публичный ключ)
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADA... your-key-here" | sudo tee /home/deploy/.ssh/authorized_keys
sudo chown deploy:deploy /home/deploy/.ssh/authorized_keys
sudo chmod 600 /home/deploy/.ssh/authorized_keys
```

**Установка Docker и Docker Compose:**
```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker deploy

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Проверка установки
docker --version
docker-compose --version
```

**Настройка брандмауэра:**
```bash
# Основные правила UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Разрешаем SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp  
sudo ufw allow 443/tcp

# Порты для мониторинга (опционально)
sudo ufw allow 3000/tcp  # Grafana
sudo ufw allow 9090/tcp  # Prometheus

# Включаем брандмауэр
sudo ufw --force enable
```

**Установка SSL сертификатов (Let's Encrypt):**
```bash
# Установка Certbot
sudo apt install -y certbot python3-certbot-nginx

# Получение сертификатов для доменов
# Замените example.com на ваш домен
sudo certbot certonly --standalone -d learn.example.com
sudo certbot certonly --standalone -d js.learn.example.com  
sudo certbot certonly --standalone -d python.learn.example.com
sudo certbot certonly --standalone -d htmlcss.learn.example.com

# Настройка автоматического обновления
sudo crontab -e
# Добавьте строку:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

**Контрольные процедуры:**
```bash
# Проверка доступности сервера
ssh deploy@your-server-ip "whoami"

# Проверка Docker
ssh deploy@your-server-ip "docker run hello-world"

# Проверка сертификатов
sudo certbot certificates

# Проверка портов
sudo ufw status
nmap -p 22,80,443 your-server-ip
```

**Критерии успеха:**
- ✅ SSH доступ с ключами работает
- ✅ Docker и Docker Compose установлены
- ✅ UFW настроен корректно
- ✅ SSL сертификаты получены
- ✅ DNS записи настроены

---

### Шаг 7.2: Настройка DNS и доменов

**Цель:** Настроить DNS записи для всех поддоменов платформы

**DNS записи для настройки:**
```
# A записи (замените IP на IP вашего сервера)
learn.example.com.      3600    IN    A    192.168.1.100
js.learn.example.com.   3600    IN    A    192.168.1.100  
python.learn.example.com. 3600  IN    A    192.168.1.100
htmlcss.learn.example.com. 3600 IN    A    192.168.1.100

# CNAME записи (альтернативный подход)
*.learn.example.com.    3600    IN    CNAME learn.example.com.
```

**Скрипт проверки DNS:**
```bash
#!/bin/bash
# scripts/check-dns.sh

DOMAINS=(
    "learn.example.com"
    "js.learn.example.com" 
    "python.learn.example.com"
    "htmlcss.learn.example.com"
)

SERVER_IP="192.168.1.100"  # Замените на IP вашего сервера

echo "🔍 Checking DNS records..."

for domain in "${DOMAINS[@]}"; do
    echo "Checking $domain..."
    
    # Проверяем A запись
    RESOLVED_IP=$(dig +short "$domain" @8.8.8.8)
    
    if [ "$RESOLVED_IP" = "$SERVER_IP" ]; then
        echo "✅ $domain resolves to $RESOLVED_IP"
    else
        echo "❌ $domain resolves to $RESOLVED_IP (expected $SERVER_IP)"
    fi
    
    # Проверяем доступность по HTTP
    if curl -s --connect-timeout 5 "http://$domain" > /dev/null; then
        echo "✅ $domain HTTP accessible"
    else
        echo "❌ $domain HTTP not accessible"  
    fi
done
```

**Автоматизация управления DNS (опционально):**
```bash
# Для Cloudflare API (если используете Cloudflare)
#!/bin/bash
# scripts/update-dns-cloudflare.sh

CLOUDFLARE_API_TOKEN="your-api-token"
ZONE_ID="your-zone-id"
SERVER_IP="192.168.1.100"

DOMAINS=(
    "learn.example.com"
    "js.learn.example.com"
    "python.learn.example.com" 
    "htmlcss.learn.example.com"
)

for domain in "${DOMAINS[@]}"; do
    echo "Updating DNS for $domain..."
    
    curl -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
         -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
         -H "Content-Type: application/json" \
         --data "{\"type\":\"A\",\"name\":\"$domain\",\"content\":\"$SERVER_IP\",\"ttl\":3600}"
done
```

**Контрольные процедуры:**
```bash
# Запуск проверки DNS
chmod +x scripts/check-dns.sh
./scripts/check-dns.sh

# Проверка через различные DNS серверы
for dns in 8.8.8.8 1.1.1.1 208.67.222.222; do
    echo "Checking via $dns:"
    dig learn.example.com @$dns +short
done

# Проверка propagation (распространения DNS)
curl -s "https://dnschecker.org/api/dns-checker?domain=learn.example.com&type=A"
```

**Критерии успеха:**
- ✅ Все домены резолвятся на правильный IP
- ✅ DNS propagation завершена (может занять до 48 часов)
- ✅ Домены доступны по HTTP
- ✅ Wildcard или отдельные записи настроены

---

### Шаг 7.3: Развертывание платформы

**Цель:** Развернуть полную платформу в продакшне

**Подготовка файлов конфигурации:**
```bash
# На сервере создаем структуру
sudo mkdir -p /opt/learning-platform
sudo chown deploy:deploy /opt/learning-platform
cd /opt/learning-platform

# Клонируем конфигурации
git clone https://github.com/learning-platform-org/platform-hub.git .
```

**Продакшн Docker Compose конфигурация:**
```yaml
# docker-compose.prod.yml
version: '3.8'

networks:
  learning-platform:
    driver: bridge
  monitoring:
    driver: bridge

volumes:
  nginx-logs:
    driver: local
  prometheus-data:
    driver: local
  grafana-data: 
    driver: local
  letsencrypt-data:
    driver: local

services:
  # Nginx with SSL termination
  nginx-proxy:
    image: nginx:alpine
    container_name: learning-platform-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/modules-proxy.conf:/etc/nginx/conf.d/modules-proxy.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - nginx-logs:/var/log/nginx
    depends_on:
      - platform-hub
      - javascript-basics
      - python-basics 
      - html-css-basics
    networks:
      - learning-platform
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M

  # Platform Hub
  platform-hub:
    image: ghcr.io/learning-platform-org/platform-hub:latest
    container_name: platform-hub
    restart: unless-stopped
    networks:
      - learning-platform
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

  # Learning modules
  javascript-basics:
    image: ghcr.io/learning-platform-org/javascript-basics:latest
    container_name: javascript-basics
    restart: unless-stopped
    networks:
      - learning-platform
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

  python-basics:
    image: ghcr.io/learning-platform-org/python-basics:latest
    container_name: python-basics
    restart: unless-stopped  
    networks:
      - learning-platform
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

  html-css-basics:
    image: ghcr.io/learning-platform-org/html-css-basics:latest
    container_name: html-css-basics
    restart: unless-stopped
    networks:
      - learning-platform  
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

  # Monitoring stack
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'  
      - '--storage.tsdb.retention.time=30d'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    networks:
      - monitoring
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  grafana:
    image: grafana/grafana:latest
    container_name: grafana  
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin123}
      - GF_SERVER_ROOT_URL=https://grafana.learn.example.com
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
    networks:
      - monitoring
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 256M

  # Container monitoring
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    restart: unless-stopped
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro  
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    networks:
      - monitoring
    deploy:
      resources:
        limits:
          cpus: '0.1'
          memory: 128M

  # Log aggregation
  loki:
    image: grafana/loki:latest
    container_name: loki
    restart: unless-stopped
    ports:
      - "3100:3100"
    volumes:
      - ./monitoring/loki:/etc/loki
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - monitoring
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 256M

  # Automated backups
  backup:
    image: alpine:latest
    container_name: platform-backup
    restart: unless-stopped
    volumes:
      - nginx-logs:/backup/nginx-logs:ro
      - ./registry:/backup/registry:ro
      - ./monitoring:/backup/monitoring:ro
      - /var/backups:/var/backups
      - /etc/letsencrypt:/backup/ssl:ro
    command: |
      sh -c '
        apk add --no-cache tar gzip curl
        
        while true; do
          echo "📦 Creating backup at $$(date)"
          
          # Create timestamped backup
          BACKUP_NAME="learning-platform-$$(date +%Y%m%d_%H%M%S).tar.gz"
          
          tar -czf "/var/backups/$$BACKUP_NAME" \
            --exclude="*.log" \
            -C /backup \
            nginx-logs registry monitoring ssl
            
          echo "✅ Backup created: $$BACKUP_NAME"
          
          # Keep only last 30 days
          find /var/backups -name "learning-platform-*.tar.gz" -mtime +30 -delete
          
          # Upload to remote storage (uncomment if needed)
          # aws s3 cp "/var/backups/$$BACKUP_NAME" s3://your-backup-bucket/
          
          # Wait 24 hours
          sleep 86400
        done
      '
    networks:
      - learning-platform
    deploy:
      resources:
        limits:
          cpus: '0.1'
          memory: 64M
```

**Nginx конфигурация с SSL:**
```nginx
# nginx/nginx.prod.conf
user nginx;
worker_processes auto;
worker_cpu_affinity auto;

error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 2048;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging format
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;

    # Performance optimizations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 1000;
    types_hash_max_size 2048;
    server_tokens off;

    # Buffer sizes
    client_body_buffer_size 128k;
    client_max_body_size 50m;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;
    output_buffers 1 32k;
    postpone_output 1460;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_comp_level 6;
    gzip_min_length 1000;
    gzip_proxied any;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general:10m rate=30r/s;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name learn.example.com js.learn.example.com python.learn.example.com htmlcss.learn.example.com;
        return 301 https://$server_name$request_uri;
    }

    # Main hub - HTTPS
    server {
        listen 443 ssl http2;
        server_name learn.example.com;
        
        ssl_certificate /etc/letsencrypt/live/learn.example.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/learn.example.com/privkey.pem;
        
        root /usr/share/nginx/html;
        index index.html index.htm;
        
        # Rate limiting
        limit_req zone=general burst=50 nodelay;

        # Main site
        location / {
            proxy_pass http://platform-hub:80;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Caching
            proxy_cache_bypass $http_upgrade;
            proxy_connect_timeout 10s;
            proxy_send_timeout 10s;
            proxy_read_timeout 30s;
        }

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://platform-hub:80;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # CORS headers
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, OPTIONS";
            add_header Access-Control-Allow-Headers "Content-Type";
        }

        # Health check
        location /health {
            access_log off;
            proxy_pass http://platform-hub:80/health;
        }

        # Static files optimization
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }
    }

    # Learning modules with SSL
    include /etc/nginx/conf.d/modules-proxy-ssl.conf;
}
```

**SSL конфигурация для модулей:**
```nginx
# nginx/modules-proxy-ssl.conf

# JavaScript module
server {
    listen 443 ssl http2;
    server_name js.learn.example.com;
    
    ssl_certificate /etc/letsencrypt/live/js.learn.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/js.learn.example.com/privkey.pem;

    limit_req zone=general burst=30 nodelay;

    location / {
        proxy_pass http://javascript-basics:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Health checks
        proxy_connect_timeout 5s;
        proxy_send_timeout 5s;
        proxy_read_timeout 30s;
    }

    location /health {
        proxy_pass http://javascript-basics:80/health;
        access_log off;
    }

    # Static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        proxy_pass http://javascript-basics:80;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Python module
server {
    listen 443 ssl http2;
    server_name python.learn.example.com;
    
    ssl_certificate /etc/letsencrypt/live/python.learn.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/python.learn.example.com/privkey.pem;

    limit_req zone=general burst=30 nodelay;

    location / {
        proxy_pass http://python-basics:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://python-basics:80/health;
        access_log off;
    }
}

# HTML/CSS module
server {
    listen 443 ssl http2;
    server_name htmlcss.learn.example.com;
    
    ssl_certificate /etc/letsencrypt/live/htmlcss.learn.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/htmlcss.learn.example.com/privkey.pem;

    limit_req zone=general burst=30 nodelay;

    location / {
        proxy_pass http://html-css-basics:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://html-css-basics:80/health;
        access_log off;
    }
}
```

**Скрипт развертывания:**
```bash
#!/bin/bash
# scripts/deploy-production.sh

set -e

# Переменные
DEPLOY_USER="deploy"
SERVER_HOST="your-server-ip"
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="/var/backups"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Функция развертывания
deploy() {
    log "🚀 Starting production deployment..."

    # Pre-deployment checks
    log "🔍 Running pre-deployment checks..."
    
    # Проверяем доступность сервера
    if ! ssh "$DEPLOY_USER@$SERVER_HOST" "whoami" > /dev/null 2>&1; then
        log "❌ Cannot connect to server"
        exit 1
    fi

    # Проверяем Docker
    if ! ssh "$DEPLOY_USER@$SERVER_HOST" "docker --version" > /dev/null 2>&1; then
        log "❌ Docker not available on server"
        exit 1
    fi

    # Создаем бэкап текущего состояния
    log "💾 Creating backup..."
    ssh "$DEPLOY_USER@$SERVER_HOST" "
        cd /opt/learning-platform
        sudo tar -czf $BACKUP_DIR/pre-deploy-backup-\$(date +%Y%m%d_%H%M%S).tar.gz \
            --exclude='node_modules' --exclude='*.log' .
    "

    # Синхронизируем файлы конфигурации
    log "📁 Syncing configuration files..."
    rsync -avz --delete \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='*.log' \
        ./ "$DEPLOY_USER@$SERVER_HOST:/opt/learning-platform/"

    # Запускаем развертывание на сервере
    log "🐳 Deploying containers..."
    ssh "$DEPLOY_USER@$SERVER_HOST" "
        cd /opt/learning-platform
        
        # Обновляем образы
        docker-compose -f $COMPOSE_FILE pull
        
        # Запускаем сервисы
        docker-compose -f $COMPOSE_FILE up -d --remove-orphans
        
        # Ждем запуска сервисов
        sleep 30
        
        # Проверяем статус
        docker-compose -f $COMPOSE_FILE ps
    "

    # Post-deployment проверки
    log "🧪 Running post-deployment tests..."
    
    # Проверяем доступность сервисов
    SERVICES=(
        "https://learn.example.com"
        "https://js.learn.example.com"  
        "https://python.learn.example.com"
        "https://htmlcss.learn.example.com"
    )

    sleep 60  # Даем время на полный запуск

    for service in "${SERVICES[@]}"; do
        if curl -f -s --connect-timeout 10 "$service/health" > /dev/null; then
            log "✅ $service is healthy"
        else
            log "❌ $service is not responding"
        fi
    done

    # Проверяем логи на наличие ошибок
    log "📋 Checking logs for errors..."
    ssh "$DEPLOY_USER@$SERVER_HOST" "
        cd /opt/learning-platform
        docker-compose -f $COMPOSE_FILE logs --tail=50 | grep -i error || true
    "

    log "🎉 Production deployment completed!"
    log "📍 Platform available at:"
    for service in "${SERVICES[@]}"; do
        log "   $service"
    done
}

# Функция отката
rollback() {
    local backup_file="$1"
    
    log "🔄 Rolling back to backup: $backup_file"
    
    ssh "$DEPLOY_USER@$SERVER_HOST" "
        cd /opt/learning-platform
        
        # Останавливаем сервисы
        docker-compose -f $COMPOSE_FILE down
        
        # Восстанавливаем из бэкапа
        sudo tar -xzf $backup_file -C /opt/learning-platform/
        
        # Запускаем сервисы
        docker-compose -f $COMPOSE_FILE up -d
    "
    
    log "✅ Rollback completed"
}

# CLI
case "$1" in
    deploy)
        deploy
        ;;
    rollback)
        if [ -z "$2" ]; then
            echo "Usage: $0 rollback <backup-file-path>"
            exit 1
        fi
        rollback "$2"
        ;;
    *)
        echo "Usage: $0 {deploy|rollback}"
        echo ""
        echo "Commands:"
        echo "  deploy              Deploy platform to production"
        echo "  rollback <backup>   Rollback to specific backup"
        echo ""
        echo "Examples:"
        echo "  $0 deploy"
        echo "  $0 rollback /var/backups/pre-deploy-backup-20241201_120000.tar.gz"
        ;;
esac
```

**Контрольные процедуры:**
```bash
# Подготовка к развертыванию
chmod +x scripts/deploy-production.sh

# Проверка конфигураций
docker-compose -f docker-compose.prod.yml config

# Запуск развертывания
./scripts/deploy-production.sh deploy

# Проверка статуса сервисов
ssh deploy@your-server "cd /opt/learning-platform && docker-compose -f docker-compose.prod.yml ps"

# Проверка логов
ssh deploy@your-server "cd /opt/learning-platform && docker-compose -f docker-compose.prod.yml logs --tail=20"

# Проверка доступности всех сайтов
for url in https://learn.example.com https://js.learn.example.com https://python.learn.example.com https://htmlcss.learn.example.com; do
    curl -f "$url/health" && echo "✅ $url OK" || echo "❌ $url FAIL"
done
```

**Критерии успеха:**
- ✅ Все сервисы запущены и работают
- ✅ SSL сертификаты применены корректно
- ✅ Health checks проходят
- ✅ Все домены доступны по HTTPS
- ✅ API endpoints отвечают
- ✅ Quiz Engine работает на всех модулях
- ✅ Мониторинг функционирует
- ✅ Бэкапы создаются автоматически

---

### Шаг 7.4: Настройка мониторинга и алертов

**Цель:** Настроить полноценный мониторинг производственной системы

**Конфигурация Prometheus:**
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  # Platform services monitoring
  - job_name: 'learning-platform'
    static_configs:
      - targets: 
        - 'learn.example.com'
        - 'js.learn.example.com'
        - 'python.learn.example.com'
        - 'htmlcss.learn.example.com'
    metrics_path: /metrics
    scrape_interval: 30s
    scheme: https

  # Container monitoring via cAdvisor
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
    scrape_interval: 30s

  # Node monitoring
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 30s

  # Nginx monitoring
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']
    scrape_interval: 30s

  # Custom application metrics
  - job_name: 'quiz-metrics'
    static_configs:
      - targets: ['platform-hub:8080']
    metrics_path: /metrics
    scrape_interval: 60s
```

**Правила алертинга:**
```yaml
# monitoring/rules/platform-alerts.yml
groups:
  - name: platform-health
    rules:
      # Service down alerts
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.instance }} is down"
          description: "{{ $labels.job }} on {{ $labels.instance }} has been down for more than 1 minute."

      # High CPU usage
      - alert: HighCPUUsage  
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 80% for more than 5 minutes."

      # High memory usage
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 85% for more than 5 minutes."

      # Disk space low  
      - alert: DiskSpaceLow
        expr: 100 - ((node_filesystem_avail_bytes * 100) / node_filesystem_size_bytes) > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Disk space low on {{ $labels.instance }}"
          description: "Disk usage is above 85% on {{ $labels.mountpoint }}."

      # High HTTP error rate
      - alert: HighHTTPErrorRate
        expr: rate(nginx_http_requests_total{status=~"5.."}[5m]) / rate(nginx_http_requests_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High HTTP 5xx error rate"
          description: "More than 10% of HTTP requests are returning 5xx errors for more than 2 minutes."

      # SSL certificate expiration
      - alert: SSLCertificateExpiring
        expr: probe_ssl_earliest_cert_expiry - time() < 86400 * 7
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "SSL certificate expiring soon for {{ $labels.instance }}"
          description: "SSL certificate for {{ $labels.instance }} expires in less than 7 days."

  - name: quiz-engine-specific
    rules:
      # Quiz completion rate too low
      - alert: LowQuizCompletionRate
        expr: quiz_completion_rate < 0.3
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low quiz completion rate"
          description: "Quiz completion rate is below 30% for {{ $labels.module }}."

      # High quiz error rate
      - alert: HighQuizErrorRate
        expr: quiz_error_rate > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High quiz error rate"
          description: "Quiz error rate is above 5% for {{ $labels.module }}."
```

**Grafana Dashboard конфигурация:**
```json
{
  "dashboard": {
    "id": null,
    "title": "Learning Platform Overview",
    "tags": ["learning-platform"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Platform Health Overview",
        "type": "stat",
        "targets": [
          {
            "expr": "up",
            "legendFormat": "{{ instance }}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "green", "value": 1}
              ]
            }
          }
        }
      },
      {
        "id": 2,
        "title": "HTTP Request Rate",
        "type": "graph", 
        "targets": [
          {
            "expr": "rate(nginx_http_requests_total[5m])",
            "legendFormat": "{{ server_name }}"
          }
        ]
      },
      {
        "id": 3,
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(nginx_http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "id": 4,
        "title": "Quiz Metrics",
        "type": "graph",
        "targets": [
          {
            "expr": "quiz_attempts_total",
            "legendFormat": "Total Attempts - {{ module }}"
          },
          {
            "expr": "quiz_completions_total", 
            "legendFormat": "Completions - {{ module }}"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

**Скрипт проверки системы:**
```bash
#!/bin/bash
# scripts/health-check.sh

set -e

ENDPOINTS=(
    "https://learn.example.com/health"
    "https://js.learn.example.com/health"
    "https://python.learn.example.com/health" 
    "https://htmlcss.learn.example.com/health"
    "http://localhost:9090/-/healthy"  # Prometheus
    "http://localhost:3000/api/health" # Grafana
)

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

check_endpoint() {
    local url="$1"
    local timeout="${2:-10}"
    
    if curl -f -s --connect-timeout "$timeout" "$url" > /dev/null; then
        log "✅ $url is healthy"
        return 0
    else
        log "❌ $url is not responding"
        return 1
    fi
}

check_docker_containers() {
    log "🐳 Checking Docker containers..."
    
    local containers=(
        "learning-platform-nginx"
        "platform-hub" 
        "javascript-basics"
        "python-basics"
        "html-css-basics"
        "prometheus"
        "grafana"
    )
    
    for container in "${containers[@]}"; do
        if docker ps --format "table {{.Names}}" | grep -q "$container"; then
            local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "unknown")
            if [ "$health" = "healthy" ] || [ "$health" = "unknown" ]; then
                log "✅ $container is running ($health)"
            else
                log "❌ $container is unhealthy ($health)"
            fi
        else
            log "❌ $container is not running"
        fi
    done
}

check_ssl_certificates() {
    log "🔒 Checking SSL certificates..."
    
    local domains=(
        "learn.example.com"
        "js.learn.example.com"
        "python.learn.example.com" 
        "htmlcss.learn.example.com"
    )
    
    for domain in "${domains[@]}"; do
        local expiry_date=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep notAfter | cut -d= -f2)
        
        if [ -n "$expiry_date" ]; then
            local expiry_timestamp=$(date -d "$expiry_date" +%s)
            local current_timestamp=$(date +%s)
            local days_left=$(( (expiry_timestamp - current_timestamp) / 86400 ))
            
            if [ "$days_left" -gt 7 ]; then
                log "✅ $domain SSL cert expires in $days_left days"
            else
                log "⚠️ $domain SSL cert expires in $days_left days (renewal needed)"
            fi
        else
            log "❌ Could not check SSL cert for $domain"
        fi
    done
}

check_disk_space() {
    log "💾 Checking disk space..."
    
    local usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -lt 80 ]; then
        log "✅ Disk usage: ${usage}%"
    elif [ "$usage" -lt 90 ]; then
        log "⚠️ Disk usage: ${usage}% (warning level)"
    else
        log "❌ Disk usage: ${usage}% (critical level)"
    fi
}

main() {
    log "🏥 Starting system health check..."
    
    local failed=0
    
    # Check endpoints
    for endpoint in "${ENDPOINTS[@]}"; do
        if ! check_endpoint "$endpoint"; then
            failed=$((failed + 1))
        fi
    done
    
    # Check containers
    check_docker_containers
    
    # Check SSL certificates
    check_ssl_certificates
    
    # Check system resources
    check_disk_space
    
    log "📊 Health check completed"
    
    if [ "$failed" -eq 0 ]; then
        log "🎉 All systems healthy"
        exit 0
    else
        log "⚠️ $failed endpoints failed health check"
        exit 1
    fi
}

main "$@"
```

**Автоматизация мониторинга через cron:**
```bash
# Добавляем в crontab пользователя deploy
crontab -e

# Добавляем следующие строки:
# Health check каждые 5 минут
*/5 * * * * /opt/learning-platform/scripts/health-check.sh >> /var/log/health-check.log 2>&1

# Еженедельная проверка обновлений SSL
0 2 * * 1 /usr/bin/certbot renew --quiet --post-hook "docker-compose -f /opt/learning-platform/docker-compose.prod.yml restart nginx-proxy"

# Ежедневная очистка старых логов
0 3 * * * find /var/log -name "*.log" -mtime +7 -delete

# Еженедельная очистка старых Docker образов
0 4 * * 0 docker system prune -f && docker image prune -a -f --filter "until=168h"
```

**Контрольные процедуры:**
```bash
# Проверка Prometheus targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# Проверка Grafana API
curl -s http://admin:admin123@localhost:3000/api/health

# Запуск полной проверки системы
./scripts/health-check.sh

# Проверка алертов
curl -s http://localhost:9090/api/v1/alerts | jq '.data.alerts[] | {alertname: .labels.alertname, state: .state}'

# Проверка логов на ошибки
docker-compose -f docker-compose.prod.yml logs --tail=100 | grep -i error
```

**Критерии успеха:**
- ✅ Prometheus собирает метрики со всех сервисов
- ✅ Grafana отображает дашборды корректно
- ✅ Алерты настроены и срабатывают
- ✅ Health check скрипт проходит успешно
- ✅ SSL сертификаты отслеживаются
- ✅ Автоматизированные задачи работают
- ✅ Логи ротируются и очищаются

---

## Раздел 8: Качество и контроль (Quality Assurance & Control)

### 8.1. Автоматизированные проверки качества

#### Линтинг и форматирование кода

**JavaScript/JSON проверки:**
```bash
# Установить инструменты линтинга
npm install -g eslint prettier jshint

# Проверка JavaScript файлов
eslint quiz-engine/src/**/*.js
eslint platform-hub/api/**/*.js

# Проверка JSON файлов
jshint quiz-examples/*.json
jshint module-registry.json

# Форматирование
prettier --write **/*.js **/*.json
```

**Dockerfile проверки:**
```bash
# Установить hadolint для проверки Dockerfile
docker run --rm -i hadolint/hadolint < Dockerfile

# Проверка всех Dockerfile в проекте
find . -name "Dockerfile*" -exec docker run --rm -i hadolint/hadolint < {} \;
```

**YAML проверки (GitHub Actions):**
```bash
# Установить yamllint
pip install yamllint

# Проверка всех YAML файлов
yamllint .github/workflows/*.yml
yamllint docker-compose*.yml
```

#### Секрет-сканинг

**Проверка на утечки ключей:**
```bash
# Установить truffleHog
pip install truffleHog

# Сканирование репозитория
truffleHog --regex --entropy=False .

# Проверка конкретного файла
truffleHog --regex --entropy=False /path/to/file.js
```

### 8.2. Матрица контрольных процедур по этапам

| Этап | Контрольная процедура | Инструмент | Критерии прохождения |
|------|----------------------|-----------|---------------------|
| **Этап 1: Инфраструктура** |
| 1.1 | Проверка SSH ключей | `ssh -T git@github.com` | Успешная аутентификация |
| 1.2 | Проверка токенов | `gh auth status` | Активные права доступа |
| 1.3 | Валидация секретов | GitHub Secrets UI | Все секреты заполнены |
| **Этап 2: Quiz Engine** |
| 2.1 | Функциональные тесты | `npm test` | Все тесты проходят |
| 2.2 | E2E тесты | Playwright/Cypress | Quiz загружается и работает |
| 2.3 | Проверка релизов | GitHub Releases API | Релиз создан корректно |
| **Этап 3: Shared Hugo Base** |
| 3.1 | Сборка образа | `docker build` | Образ собирается успешно |
| 3.2 | Тест интеграции | `docker run` + curl | Hugo сервер отвечает |
| 3.3 | Проверка Quiz Engine | Browser test | Quiz работает в контейнере |
| **Этап 4: Build Templates** |
| 4.1 | CLI тестирование | `./platform-cli --help` | CLI запускается |
| 4.2 | Генерация модуля | Test module creation | Модуль создается корректно |
| 4.3 | Валидация шаблонов | Template syntax check | Шаблоны без ошибок |
| **Этап 5: Platform Hub** |
| 5.1 | API тестирование | `curl /api/modules` | API отвечает JSON |
| 5.2 | Схема валидация | JSON Schema validation | Registry валидный |
| 5.3 | Docker Compose | `docker-compose up` | Все сервисы запускаются |
| **Этап 6: Модули** |
| 6.1 | Сборка модулей | Individual builds | Все модули собираются |
| 6.2 | Content валидация | Hugo validation | Контент корректный |
| 6.3 | Quiz интеграция | Browser testing | Quiz работают в модулях |
| **Этап 7: Production** |
| 7.1 | SSL проверка | `curl -I https://` | SSL сертификат валидный |
| 7.2 | Мониторинг | Prometheus targets | Все метрики собираются |
| 7.3 | Backup тест | Restore procedure | Бекапы восстанавливаются |

### 8.3. Тестовые сценарии по компонентам

#### Quiz Engine тестирование

**Базовые функциональные тесты:**
```javascript
// tests/quiz-engine.test.js
describe('Quiz Engine', () => {
  test('Single choice quiz works correctly', async () => {
    // Загрузка тестового quiz-data.json
    const quizData = await loadTestQuiz('single-choice.json');
    
    // Построение UI
    const container = document.createElement('div');
    await buildQuiz(container, quizData, 'ru', uiTranslations, 1);
    
    // Проверка наличия элементов
    expect(container.querySelector('h2')).toBeTruthy();
    expect(container.querySelectorAll('input[type="radio"]')).toHaveLength(4);
    expect(container.querySelector('button')).toBeTruthy();
    
    // Симуляция выбора ответа
    const correctRadio = container.querySelector('input[value="correct"]');
    correctRadio.checked = true;
    
    // Нажатие кнопки проверки
    const checkButton = container.querySelector('button');
    checkButton.click();
    
    // Проверка результата
    expect(container.querySelector('p').textContent).toContain('Правильно');
    expect(checkButton.style.display).toBe('none');
  });

  test('Multiple choice quiz validation', async () => {
    // Тестирование множественного выбора
  });
  
  test('Input field quiz case sensitivity', async () => {
    // Тестирование поля ввода
  });
});
```

**E2E тестирование с Playwright:**
```javascript
// e2e/quiz-integration.spec.js
const { test, expect } = require('@playwright/test');

test('Quiz loads and works in Hugo site', async ({ page }) => {
  await page.goto('http://localhost:1313/lessons/quiz-test');
  
  // Ожидание загрузки quiz
  await page.waitForSelector('.quiz-container');
  
  // Проверка отображения вопроса
  await expect(page.locator('h2')).toBeVisible();
  
  // Выбор ответа
  await page.click('input[type="radio"]:first-child');
  
  // Нажатие кнопки проверки
  await page.click('button:has-text("Проверить ответ")');
  
  // Проверка результата
  await expect(page.locator('p')).toContainText('Правильно');
  
  // Проверка блокировки интерфейса
  await expect(page.locator('button:has-text("Проверить ответ")')).toBeHidden();
});
```

#### Hugo сборка тестирование

**Валидация генерируемого HTML:**
```bash
# Скрипт валидации HTML
#!/bin/bash
# validate-html.sh

echo "Building Hugo site..."
hugo --minify

echo "Validating HTML..."
docker run --rm -v $(pwd)/public:/public 18fgsa/html-proofer /public \
  --check-html \
  --check-img-http \
  --disable-external \
  --allow-hash-href

echo "Checking for broken links..."
docker run --rm -v $(pwd)/public:/public 18fgsa/html-proofer /public \
  --check-links \
  --allow-hash-href
```

#### API тестирование Platform Hub

**REST API валидация:**
```javascript
// tests/api.test.js
describe('Platform Hub API', () => {
  test('GET /api/modules returns valid JSON', async () => {
    const response = await fetch('http://localhost:8080/api/modules');
    expect(response.status).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('modules');
    expect(Array.isArray(data.modules)).toBeTruthy();
  });
  
  test('Module registry schema validation', async () => {
    const response = await fetch('http://localhost:8080/module-registry.json');
    const registry = await response.json();
    
    // Валидация по JSON Schema
    const valid = validateModuleRegistry(registry);
    expect(valid).toBeTruthy();
  });
});
```

### 8.4. CI/CD интеграция проверок

#### GitHub Actions для качества кода

**Workflow для проверки кода:**
```yaml
# .github/workflows/quality-check.yml
name: Quality Assurance

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  code-quality:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        
    - name: Install dependencies
      run: npm ci
      
    - name: ESLint check
      run: npx eslint . --ext .js,.mjs
      
    - name: Prettier check
      run: npx prettier --check .
      
    - name: Run tests
      run: npm test
      
    - name: E2E tests
      run: npx playwright test
      
    security:
      runs-on: ubuntu-latest
      steps:
      - uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          
      - name: Secret scanning
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: main
          head: HEAD
  
  docker-security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Build Docker image
      run: docker build -t test-image .
      
    - name: Run Trivy on Docker image
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'test-image'
        format: 'sarif'
        output: 'trivy-results.sarif'
        
    - name: Hadolint Dockerfile scan
      uses: hadolint/hadolint-action@v3.1.0
      with:
        dockerfile: Dockerfile
```

#### Автоматизированные проверки деплоя

**Pre-deployment validation:**
```yaml
# .github/workflows/pre-deploy-checks.yml
name: Pre-deployment Validation

on:
  workflow_run:
    workflows: ["Build and Push"]
    types: [completed]

jobs:
  pre-deploy-validation:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Validate Docker Compose
      run: |
        docker-compose -f docker-compose.prod.yml config
        
    - name: Check SSL certificates
      run: |
        curl -I https://${{ secrets.DOMAIN }} | grep "200 OK"
        
    - name: Validate module registry
      run: |
        curl -f https://${{ secrets.DOMAIN }}/api/modules
        
    - name: Health check endpoints
      run: |
        for module in js python html-css; do
          curl -f https://$module.${{ secrets.DOMAIN }}/health
        done
        
    - name: Monitor resource usage
      run: |
        # Проверка использования ресурсов на сервере
        ssh ${{ secrets.SSH_USER }}@${{ secrets.HOST }} \
          "df -h && free -m && docker stats --no-stream"
```

### 8.5. Мониторинг качества в продакшне

#### Prometheus алерты для качества

**Алерты качества сервиса:**
```yaml
# prometheus/quality-alerts.yml
groups:
- name: quality.rules
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      
  - alert: SlowResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Slow response time detected"
      
  - alert: QuizLoadFailure
    expr: increase(quiz_load_errors_total[5m]) > 5
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Multiple quiz load failures"
      
  - alert: ModuleUnavailable
    expr: up{job="hugo-modules"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Hugo module is down"
```

#### Automated quality reports

**Еженедельный отчет качества:**
```bash
#!/bin/bash
# scripts/weekly-quality-report.sh

echo "=== Weekly Quality Report ===" > quality-report.md
echo "Date: $(date)" >> quality-report.md
echo "" >> quality-report.md

echo "## Build Status" >> quality-report.md
gh run list --limit 20 --json status,conclusion,createdAt | \
  jq -r '.[] | "\(.createdAt): \(.conclusion)"' >> quality-report.md

echo "" >> quality-report.md
echo "## Test Coverage" >> quality-report.md
npm test -- --coverage --json | \
  jq '.coverageMap' >> quality-report.md

echo "" >> quality-report.md  
echo "## Security Scan Results" >> quality-report.md
docker run --rm -v $(pwd):/src aquasecurity/trivy fs /src \
  --format json | jq '.Results[]' >> quality-report.md

echo "" >> quality-report.md
echo "## Performance Metrics" >> quality-report.md
curl -s "http://prometheus:9090/api/v1/query?query=up" | \
  jq '.data.result[]' >> quality-report.md

# Отправка отчета
curl -X POST $SLACK_WEBHOOK \
  -H 'Content-type: application/json' \
  --data "{\"text\":\"Weekly Quality Report\", \"attachments\":[{\"text\":\"$(cat quality-report.md)\"}]}"
```

### 8.6. Критерии приемки для каждого этапа

#### Stage Gate процедура

**Определение готовности к следующему этапу:**

```yaml
# stage-gates.yml
stage_gates:
  stage_1:
    name: "Infrastructure Setup"
    criteria:
      - github_org_created: true
      - ssh_keys_configured: true  
      - secrets_configured: true
      - team_access_granted: true
    validation_script: "scripts/validate-stage-1.sh"
    
  stage_2:
    name: "Quiz Engine Ready"
    criteria:
      - tests_passing: true
      - e2e_tests_passing: true
      - release_created: true
      - documentation_updated: true
    validation_script: "scripts/validate-stage-2.sh"
    
  stage_3:
    name: "Shared Hugo Base"
    criteria:
      - docker_image_built: true
      - integration_tests_pass: true
      - quiz_engine_integrated: true
      - theme_validated: true
    validation_script: "scripts/validate-stage-3.sh"
```

**Автоматическая валидация этапов:**
```bash
#!/bin/bash
# scripts/stage-gate-check.sh

STAGE=$1
CONFIG_FILE="stage-gates.yml"

echo "Validating Stage $STAGE..."

# Загрузка критериев для этапа
VALIDATION_SCRIPT=$(yq eval ".stage_gates.stage_${STAGE}.validation_script" $CONFIG_FILE)

if [[ -f "$VALIDATION_SCRIPT" ]]; then
    echo "Running validation script: $VALIDATION_SCRIPT"
    bash "$VALIDATION_SCRIPT"
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Stage $STAGE validation PASSED"
        exit 0
    else
        echo "❌ Stage $STAGE validation FAILED"
        exit 1
    fi
else
    echo "❌ Validation script not found: $VALIDATION_SCRIPT"
    exit 1
fi
```

---

## Заключение

Пошаговый план реализации образовательной платформы завершен. Платформа готова к использованию в продакшне со следующими возможностями:

### Реализованные компоненты:

1. **Quiz Engine** - интерактивный движок тестов с поддержкой множественных типов вопросов
2. **Shared Hugo Base** - унифицированная база с темой и Quiz Engine 
3. **Build Templates** - CLI для быстрого создания новых модулей
4. **Platform Hub** - центральный хаб с API и навигацией
5. **Примеры модулей** - JavaScript, Python, HTML/CSS курсы
6. **Production Deploy** - полная инфраструктура с мониторингом

### Архитектурные преимущества:

- ✅ **Масштабируемость**: Легкое добавление новых модулей
- ✅ **Автономность**: Независимое развертывание модулей  
- ✅ **Унификация**: Единый стиль и Quiz Engine для всех
- ✅ **Автоматизация**: CI/CD для всех компонентов
- ✅ **Производительность**: Статические сайты + CDN
- ✅ **Мониторинг**: Полная наблюдаемость системы
- ✅ **Безопасность**: SSL, rate limiting, security headers

### Готово к продакшну:

- 🚀 **MVP**: 3 полноценных модуля готовы к использованию
- 📈 **Масштабирование**: Архитектура поддерживает 50+ модулей
- 🔄 **CI/CD**: Автоматизированный деплой всех компонентов
- 📊 **Мониторинг**: Grafana + Prometheus для отслеживания метрик
- 🔒 **Безопасность**: SSL, резервное копирование, алерты

Платформа готова принимать пользователей и может масштабироваться по мере роста количества курсов и учащихся.

---

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Создать подробный step-by-step план реализации платформы", "status": "completed", "activeForm": "Создаю подробный step-by-step план реализации"}, {"content": "Добавить контрольные процедуры для каждого этапа", "status": "completed", "activeForm": "Добавляю контрольные процедуры для каждого этапа"}, {"content": "Описать тестирование и валидацию на каждом шаге", "status": "completed", "activeForm": "Описываю тестирование и валидацию на каждом шаге"}, {"content": "Интегрировать проверки в CI/CD pipeline", "status": "completed", "activeForm": "Интегрирую проверки в CI/CD pipeline"}]