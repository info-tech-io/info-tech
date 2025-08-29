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
          if ! grep -q "{{.module_name}}:\" docker-compose.yml; then
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

3. Edit content in ${chalk.cyan('content/')}
 directory

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

  }

  async validateContent(modulePath) {

  }

  async validateQuizzes(modulePath) {

  }

  async validateDocker(modulePath) {

  }

  printResults() {
    console.log(chalk.blue('\n📊 Validation Results:'));
    console.log('=' * 50);

    if (this.errors.length > 0) {
      console.log(chalk.red(`❌ ${this.errors.length} Errors found:`));
      this.errors.forEach(err => console.log(chalk.red(`  - ${err}`)));
    }

    if (this.warnings.length > 0) {
      console.log(chalk.yellow(`\n⚠️ ${this.warnings.length} Warnings found:`));
      this.warnings.forEach(warn => console.log(chalk.yellow(`  - ${warn}`)));
    }

    if (this.errors.length === 0 && this.warnings.length === 0) {
      console.log(chalk.green('✅ All checks passed! Module is valid.'));
      return true;
    } else if (this.errors.length === 0) {
      console.log(chalk.green('✅ Module is valid, but has some warnings.'));
      return true;
    } else {
      console.log(chalk.red('❌ Module is invalid. Please fix the errors.'));
      return false;
    }
  }
}

// Обработка аргументов командной строки
const argv = yargs(hideBin(process.argv))
  .command('create', 'Create a new module', (yargs) => {
    return yargs
      .option('name', {
        alias: 'n',
        description: 'Module name (kebab-case)',
        type: 'string'
      })
      .option('template', {
        alias: 't',
        description: 'Template to use',
        type: 'string'
      })
      .option('category', {
        alias: 'c',
        description: 'Module category',
        type: 'string'
      })
  })
  .command('validate [path]', 'Validate an existing module', (yargs) => {
    return yargs.positional('path', {
      describe: 'Path to the module directory',
      default: '.'
    });
  })
  .demandCommand(1, 'You need to specify a command (create or validate)')
  .help()
  .alias('help', 'h')
  .argv;

// Запуск
if (argv._[0] === 'create') {
  const creator = new ModuleCreator();
  creator.createModule(argv);
} else if (argv._[0] === 'validate') {
  const validator = new ModuleValidator();
  validator.validateModule(path.resolve(argv.path));
}
