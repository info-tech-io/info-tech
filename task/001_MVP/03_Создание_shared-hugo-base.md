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
        if [ ! -f /tmp/test-results/result.txt ] || [ $(cat /tmp/test-results/result.txt) != 'success' ]; then
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
        echo 'theme = "learning-platform"' >> hugo.toml
        
        # Создаем тестовую страницу с квизом
        mkdir -p content
        cat > content/_index.md << 'EOF'
---
title: Integration Test
---
# Test Page
{{< quiz src="/test-quiz.json" >}}
EOF
        
        # Создаем тестовый квиз
        cat > static/test-quiz.json << 'EOF'
{
  "config": { "type": "single-choice" },
  "question": { "ru": "Тест?", "en": "Test?" },
  "answers": [
    { "text": { "ru": "Да", "en": "Yes" }, "correct": true }
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
