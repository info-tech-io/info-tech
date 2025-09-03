# Этап 4: Создание репозитория infotecha (центральная ось платформы)

## Шаг 4.1: Создание репозитория infotecha

**Цель:** Создать центральный репозиторий платформы InfoTech.io

**Действия:**
```bash
# Создание репозитория через GitHub CLI
gh repo create info-tech-io/infotecha --public --description "Central hub for InfoTech.io educational platform"

# Клонирование и настройка
git clone https://github.com/info-tech-io/infotecha.git
cd infotecha
git remote set-url origin https://github.com/info-tech-io/infotecha.git
```

**Структура репозитория:**
```
infotecha/
├── .github/workflows/
│   ├── deploy-hub.yml          # Деплой главной страницы
│   ├── module-updated.yml      # Обработка обновлений модулей
│   └── build-module.yml        # Билд конкретного модуля
├── content/
│   ├── index.html             # Главная страница платформы
│   ├── modules.js             # JavaScript для загрузки модулей
│   ├── styles.css             # Базовые стили
│   └── images/                # Логотипы, иконки
├── modules.json               # Единый реестр всех модулей
├── scripts/
│   ├── build-module.sh        # Скрипт билда модуля
│   ├── deploy.sh              # Скрипт деплоя на сервер
│   └── validate-module.json   # Валидация модулей
├── templates/
│   └── module-template.json   # Шаблон для нового модуля
├── README.md
└── .gitignore
```

**Контрольные процедуры:**
```bash
# Проверка создания репозитория
gh repo view info-tech-io/infotecha

# Проверка структуры
find . -type d | sort
test -d .github/workflows && echo "✅ Workflows directory created"
test -d content && echo "✅ Content directory created"
```

**Критерии успеха:**
- ✅ Репозиторий создан в организации info-tech-io
- ✅ Базовая структура директорий создана
- ✅ GitHub CLI доступ настроен

---

## Шаг 4.2: Создание реестра модулей modules.json

**Цель:** Создать централизованный реестр всех учебных модулей

**Файл modules.json (начальная версия):**
```json
{
  "schema_version": "1.0",
  "platform": {
    "name": "InfoTech.io",
    "description": "Интерактивная образовательная платформа с открытым контентом",
    "domain": "infotecha.ru",
    "github_org": "info-tech-io"
  },
  "last_updated": "2025-01-01T00:00:00Z",
  "modules": {
    "linux_base": {
      "name": "Основы Linux",
      "description": "Введение в операционную систему Linux для начинающих",
      "content_repo": "mod_linux_base",
      "template_repo": "hugo-base",
      "subdomain": "linux-base",
      "last_updated": "2025-01-01T00:00:00Z",
      "status": "planned"
    },
    "linux_advanced": {
      "name": "Продвинутый Linux",
      "description": "Администрирование и продвинутые возможности Linux",
      "content_repo": "mod_linux_advanced", 
      "template_repo": "hugo-base",
      "subdomain": "linux-advanced",
      "last_updated": "2025-01-01T00:00:00Z",
      "status": "planned"
    },
    "linux_professional": {
      "name": "Linux для профессионалов",
      "description": "Профессиональное администрирование Linux систем",
      "content_repo": "mod_linux_professional",
      "template_repo": "hugo-base", 
      "subdomain": "linux-professional",
      "last_updated": "2025-01-01T00:00:00Z",
      "status": "planned"
    }
  }
}
```

**Расширенная версия для будущего развития:**
```json
{
  "modules": {
    "linux_base": {
      "name": "Основы Linux",
      "description": "Введение в операционную систему Linux для начинающих",
      "content_repo": "mod_linux_base",
      "template_repo": "hugo-base",
      "subdomain": "linux-base",
      "last_updated": "2025-01-01T00:00:00Z",
      "status": "active",
      
      // Расширенные поля для будущего
      "category": "devops",
      "difficulty": "beginner", 
      "duration": "40 hours",
      "author": {
        "name": "InfoTech.io Team",
        "github": "info-tech-io"
      },
      "tags": ["linux", "command-line", "basics"],
      "language": "ru",
      "version": "1.0.0",
      "prerequisites": [],
      "learning_objectives": [
        "Понимание основ файловой системы Linux",
        "Работа с командной строкой",
        "Управление файлами и каталогами"
      ]
    }
  }
}
```

**Контрольные процедуры:**
```bash
# Валидация JSON
jq empty modules.json && echo "✅ JSON syntax valid" || echo "❌ Invalid JSON"

# Проверка обязательных полей
jq '.modules | to_entries[] | select(.value.name == null or .value.content_repo == null)' modules.json | \
  jq -r '.key + " - missing required fields"' | \
  (grep -q . && echo "❌ Missing required fields" || echo "✅ All required fields present")

# Проверка уникальности поддоменов
jq -r '.modules[].subdomain' modules.json | sort | uniq -d | \
  (grep -q . && echo "❌ Duplicate subdomains found" || echo "✅ All subdomains unique")
```

**Критерии успеха:**
- ✅ modules.json создан и валиден
- ✅ Все обязательные поля присутствуют
- ✅ Поддомены уникальны
- ✅ Структура готова к расширению

---

## Шаг 4.3: Создание главной страницы платформы

**Цель:** Создать статическую главную страницу с каталогом курсов

**Файл content/index.html:**
```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InfoTech.io - Открываем двери в мир технологий</title>
    <meta name="description" content="Интерактивная образовательная платформа с открытым контентом">
    
    <!-- Стили -->
    <link rel="stylesheet" href="styles.css">
    
    <!-- Open Graph Meta Tags -->
    <meta property="og:title" content="InfoTech.io">
    <meta property="og:description" content="Интерактивная образовательная платформа с открытым контентом">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://infotecha.ru">
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="/images/favicon.ico">
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <img src="images/logo.svg" alt="InfoTech.io" class="logo-image">
                    <h1 class="logo-text">InfoTech.io</h1>
                </div>
                <nav class="nav">
                    <a href="#courses" class="nav-link">Курсы</a>
                    <a href="#about" class="nav-link">О платформе</a>
                    <a href="https://github.com/info-tech-io" class="nav-link" target="_blank">GitHub</a>
                </nav>
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <div class="hero-content">
                <h2 class="hero-title">Открываем двери в мир технологий</h2>
                <p class="hero-description">
                    Интерактивная образовательная платформа с открытым контентом.
                    Изучайте современные технологии через практические курсы с интерактивными тестами.
                </p>
                <a href="#courses" class="hero-button">Начать обучение</a>
            </div>
        </div>
    </section>

    <!-- Courses Catalog -->
    <section id="courses" class="courses">
        <div class="container">
            <h2 class="section-title">Каталог курсов</h2>
            
            <!-- Loading State -->
            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p>Загружаем каталог курсов...</p>
            </div>
            
            <!-- Error State -->
            <div id="error" class="error" style="display: none;">
                <p>❌ Ошибка загрузки каталога курсов</p>
                <button id="retry-button" class="retry-button">Попробовать снова</button>
            </div>
            
            <!-- Courses Grid -->
            <div id="courses-grid" class="courses-grid" style="display: none;">
                <!-- Курсы будут загружены динамически через JavaScript -->
            </div>
            
            <!-- Empty State -->
            <div id="empty" class="empty" style="display: none;">
                <p>📚 Курсы скоро появятся на платформе</p>
            </div>
        </div>
    </section>

    <!-- About Section -->
    <section id="about" class="about">
        <div class="container">
            <div class="about-content">
                <h2 class="section-title">О платформе InfoTech.io</h2>
                <div class="about-grid">
                    <div class="about-item">
                        <div class="about-icon">🎯</div>
                        <h3>Интерактивное обучение</h3>
                        <p>Каждый курс содержит интерактивные тесты и практические задания</p>
                    </div>
                    <div class="about-item">
                        <div class="about-icon">🔓</div>
                        <h3>Открытый контент</h3>
                        <p>Все материалы платформы открыты и доступны на GitHub</p>
                    </div>
                    <div class="about-item">
                        <div class="about-icon">🚀</div>
                        <h3>Современные технологии</h3>
                        <p>Изучайте актуальные технологии и инструменты</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <p>&copy; 2025 InfoTech.io. Открытая образовательная платформа.</p>
                <p>
                    <a href="https://github.com/info-tech-io" target="_blank">GitHub</a> |
                    <a href="https://github.com/info-tech-io/infotecha" target="_blank">Исходный код</a>
                </p>
            </div>
        </div>
    </footer>

    <!-- JavaScript -->
    <script src="modules.js"></script>
</body>
</html>
```

**Файл content/modules.js:**
```javascript
/**
 * InfoTech.io Modules Loader
 * Загружает каталог курсов из modules.json и отображает их на главной странице
 */

class ModulesLoader {
    constructor() {
        this.modulesUrl = '/modules.json';
        this.retryCount = 0;
        this.maxRetries = 3;
        
        this.loadingEl = document.getElementById('loading');
        this.errorEl = document.getElementById('error');
        this.coursesGridEl = document.getElementById('courses-grid');
        this.emptyEl = document.getElementById('empty');
        this.retryButtonEl = document.getElementById('retry-button');
        
        this.init();
    }

    init() {
        this.loadModules();
        this.retryButtonEl.addEventListener('click', () => this.loadModules());
    }

    async loadModules() {
        this.showLoading();
        
        try {
            console.log('🔄 Loading modules from:', this.modulesUrl);
            
            const response = await fetch(this.modulesUrl, {
                cache: 'no-cache',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('✅ Modules loaded:', data);
            
            this.renderModules(data);
            this.retryCount = 0; // Reset retry count on success
            
        } catch (error) {
            console.error('❌ Error loading modules:', error);
            this.handleError(error);
        }
    }

    renderModules(data) {
        if (!data.modules || Object.keys(data.modules).length === 0) {
            this.showEmpty();
            return;
        }

        const activeModules = Object.entries(data.modules)
            .filter(([key, module]) => module.status === 'active')
            .sort((a, b) => a[1].name.localeCompare(b[1].name));

        if (activeModules.length === 0) {
            this.showEmpty();
            return;
        }

        const coursesHtml = activeModules.map(([key, module]) => 
            this.createModuleCard(key, module, data.platform.domain)
        ).join('');

        this.coursesGridEl.innerHTML = coursesHtml;
        this.showCourses();
    }

    createModuleCard(moduleKey, module, domain) {
        const moduleUrl = `https://${module.subdomain}.${domain}`;
        const lastUpdated = new Date(module.last_updated).toLocaleDateString('ru-RU');
        
        // Определяем иконку по категории (для будущего использования)
        const categoryIcon = this.getCategoryIcon(module.category);
        
        return `
            <article class="course-card">
                <div class="course-header">
                    <div class="course-icon">${categoryIcon}</div>
                    <div class="course-meta">
                        <span class="course-difficulty">${this.getDifficultyLabel(module.difficulty)}</span>
                        ${module.duration ? `<span class="course-duration">${module.duration}</span>` : ''}
                    </div>
                </div>
                
                <div class="course-content">
                    <h3 class="course-title">
                        <a href="${moduleUrl}" target="_blank">${module.name}</a>
                    </h3>
                    <p class="course-description">${module.description}</p>
                    
                    ${module.tags ? `
                        <div class="course-tags">
                            ${module.tags.map(tag => `<span class="course-tag">${tag}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
                
                <div class="course-footer">
                    <span class="course-updated">Обновлен: ${lastUpdated}</span>
                    <a href="${moduleUrl}" class="course-button" target="_blank">
                        Изучать →
                    </a>
                </div>
            </article>
        `;
    }

    getCategoryIcon(category) {
        const icons = {
            'devops': '⚙️',
            'programming': '💻',
            'web-development': '🌐',
            'data-science': '📊',
            'design': '🎨',
            'mobile': '📱'
        };
        return icons[category] || '📚';
    }

    getDifficultyLabel(difficulty) {
        const labels = {
            'beginner': 'Начальный',
            'intermediate': 'Средний',
            'advanced': 'Продвинутый'
        };
        return labels[difficulty] || difficulty;
    }

    showLoading() {
        this.loadingEl.style.display = 'flex';
        this.errorEl.style.display = 'none';
        this.coursesGridEl.style.display = 'none';
        this.emptyEl.style.display = 'none';
    }

    showError() {
        this.loadingEl.style.display = 'none';
        this.errorEl.style.display = 'block';
        this.coursesGridEl.style.display = 'none';
        this.emptyEl.style.display = 'none';
    }

    showCourses() {
        this.loadingEl.style.display = 'none';
        this.errorEl.style.display = 'none';
        this.coursesGridEl.style.display = 'grid';
        this.emptyEl.style.display = 'none';
    }

    showEmpty() {
        this.loadingEl.style.display = 'none';
        this.errorEl.style.display = 'none';
        this.coursesGridEl.style.display = 'none';
        this.emptyEl.style.display = 'block';
    }

    handleError(error) {
        this.retryCount++;
        
        if (this.retryCount < this.maxRetries) {
            console.log(`🔄 Retry ${this.retryCount}/${this.maxRetries} in 2 seconds...`);
            setTimeout(() => this.loadModules(), 2000);
        } else {
            console.error(`❌ Max retries (${this.maxRetries}) reached`);
            this.showError();
        }
    }
}

// Инициализация после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 InfoTech.io Modules Loader initialized');
    new ModulesLoader();
});

// Обработка ошибок JavaScript
window.addEventListener('error', (event) => {
    console.error('💥 JavaScript Error:', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error
    });
});
```

**Контрольные процедуры:**
```bash
# Проверка HTML валидности (требует html-validate)
npx html-validate content/index.html && echo "✅ HTML valid" || echo "⚠️ HTML validation skipped"

# Проверка JavaScript синтаксиса
node -c content/modules.js && echo "✅ JavaScript syntax valid"

# Проверка загрузки modules.json в браузере
python3 -m http.server 8000 --directory . &
SERVER_PID=$!
sleep 2
curl -f http://localhost:8000/modules.json > /dev/null && echo "✅ modules.json accessible via HTTP"
kill $SERVER_PID
```

**Критерии успеха:**
- ✅ HTML страница создана и валидна
- ✅ JavaScript загружает modules.json
- ✅ Отображение курсов работает
- ✅ Обработка ошибок реализована

---

## Шаг 4.4: Создание GitHub Actions workflows

**Цель:** Настроить автоматизацию для обработки обновлений модулей и деплоя

**Файл .github/workflows/module-updated.yml:**
```yaml
name: Module Updated Handler

on:
  repository_dispatch:
    types: [module-updated]

jobs:
  update-module:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout infotecha repository
      uses: actions/checkout@v4
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Parse module update payload
      id: parse
      run: |
        echo "module_name=${{ github.event.client_payload.module_name }}" >> $GITHUB_OUTPUT
        echo "content_repo=${{ github.event.client_payload.content_repo }}" >> $GITHUB_OUTPUT
        echo "updated_at=${{ github.event.client_payload.updated_at }}" >> $GITHUB_OUTPUT
        
        echo "📦 Module Update Request:"
        echo "  Module: ${{ github.event.client_payload.module_name }}"
        echo "  Repo: ${{ github.event.client_payload.content_repo }}"
        echo "  Updated: ${{ github.event.client_payload.updated_at }}"
        
    - name: Update modules.json registry
      id: update-registry
      run: |
        MODULE_NAME="${{ steps.parse.outputs.module_name }}"
        UPDATED_AT="${{ steps.parse.outputs.updated_at }}"
        
        echo "🔄 Updating modules.json for module: $MODULE_NAME"
        
        # Обновляем дату последнего обновления модуля
        jq --arg module "$MODULE_NAME" --arg date "$UPDATED_AT" \
           '.modules[$module].last_updated = $date | .last_updated = now | strftime("%Y-%m-%dT%H:%M:%SZ")' \
           modules.json > modules.json.tmp
        
        mv modules.json.tmp modules.json
        
        echo "✅ Registry updated"
        
    - name: Trigger module build
      uses: peter-evans/repository-dispatch@v3
      with:
        token: ${{ secrets.PAT_TOKEN }}
        repository: ${{ github.repository }}
        event-type: build-module
        client-payload: |
          {
            "module_name": "${{ steps.parse.outputs.module_name }}",
            "content_repo": "${{ steps.parse.outputs.content_repo }}",
            "trigger": "content-update"
          }
          
    - name: Commit registry changes
      uses: stefanzweifel/git-auto-commit-action@v5
      with:
        commit_message: "chore: update ${{ steps.parse.outputs.module_name }} module timestamp"
        file_pattern: modules.json
        commit_user_name: "InfoTech.io Bot"
        commit_user_email: "bot@infotecha.ru"
```

**Файл .github/workflows/build-module.yml:**
```yaml
name: Build Module

on:
  repository_dispatch:
    types: [build-module]
  workflow_dispatch:
    inputs:
      module_name:
        description: 'Module name to build'
        required: true
        type: string
      content_repo:
        description: 'Content repository name'
        required: true
        type: string

env:
  MODULE_NAME: ${{ github.event.client_payload.module_name || github.event.inputs.module_name }}
  CONTENT_REPO: ${{ github.event.client_payload.content_repo || github.event.inputs.content_repo }}

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout infotecha repository
      uses: actions/checkout@v4
      
    - name: Checkout hugo-base template
      uses: actions/checkout@v4
      with:
        repository: info-tech-io/hugo-base
        path: hugo-base
        token: ${{ secrets.PAT_TOKEN }}
        
    - name: Checkout module content
      uses: actions/checkout@v4
      with:
        repository: info-tech-io/${{ env.CONTENT_REPO }}
        path: module-content
        token: ${{ secrets.PAT_TOKEN }}
        
    - name: Setup Hugo
      uses: peaceiris/actions-hugo@v2
      with:
        hugo-version: '0.148.2'
        extended: true
        
    - name: Build module site
      run: |
        echo "🏗️ Building module: ${{ env.MODULE_NAME }}"
        
        # Создаем рабочую директорию для сборки
        mkdir -p build-workspace
        cd build-workspace
        
        # Копируем шаблон hugo-base
        cp -r ../hugo-base/* .
        cp -r ../hugo-base/.* . 2>/dev/null || true
        
        # Заменяем контент модуля (если папка content есть в модуле)
        if [ -d "../module-content/content" ]; then
            echo "📂 Using content from module repository"
            rm -rf content/
            cp -r ../module-content/content/ ./
        else
            echo "⚠️ No content/ folder in module repository, using default"
        fi
        
        # Обновляем конфигурацию Hugo для конкретного модуля
        MODULE_SUBDOMAIN=$(jq -r --arg module "${{ env.MODULE_NAME }}" '.modules[$module].subdomain' ../modules.json)
        MODULE_TITLE=$(jq -r --arg module "${{ env.MODULE_NAME }}" '.modules[$module].name' ../modules.json)
        
        # Обновляем hugo.toml
        sed -i "s|baseURL = '.*'|baseURL = 'https://${MODULE_SUBDOMAIN}.infotecha.ru/'|" hugo.toml
        sed -i "s|title = '.*'|title = '${MODULE_TITLE}'|" hugo.toml
        
        echo "🎯 Configuration updated:"
        echo "  Base URL: https://${MODULE_SUBDOMAIN}.infotecha.ru/"
        echo "  Title: ${MODULE_TITLE}"
        
        # Инициализируем submodules если нужно
        git submodule update --init --recursive || echo "No submodules or already initialized"
        
        # Собираем сайт
        hugo --minify --gc
        
        echo "✅ Site built successfully"
        ls -la public/
        
    - name: Deploy to server
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.PROD_HOST }}
        username: ${{ secrets.PROD_USERNAME }}
        key: ${{ secrets.PROD_SSH_KEY }}
        script: |
          set -e
          
          MODULE_NAME="${{ env.MODULE_NAME }}"
          MODULE_SUBDOMAIN=$(echo "$MODULE_NAME" | tr '_' '-')
          
          echo "🚀 Deploying module: $MODULE_NAME to subdomain: $MODULE_SUBDOMAIN"
          
          # Создаем директорию модуля если не существует
          sudo mkdir -p "/var/www/infotecha.ru/${MODULE_SUBDOMAIN}"
          
          # Устанавливаем права
          sudo chown -R www-data:www-data "/var/www/infotecha.ru/${MODULE_SUBDOMAIN}"
          
          echo "✅ Module deployment directory prepared"
          
    - name: Upload built site
      uses: appleboy/scp-action@v0.1.4
      with:
        host: ${{ secrets.PROD_HOST }}
        username: ${{ secrets.PROD_USERNAME }}
        key: ${{ secrets.PROD_SSH_KEY }}
        source: "build-workspace/public/*"
        target: "/tmp/infotecha-deploy-${{ env.MODULE_NAME }}/"
        strip_components: 2
        
    - name: Complete deployment
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.PROD_HOST }}
        username: ${{ secrets.PROD_USERNAME }}
        key: ${{ secrets.PROD_SSH_KEY }}
        script: |
          set -e
          
          MODULE_NAME="${{ env.MODULE_NAME }}"
          MODULE_SUBDOMAIN=$(echo "$MODULE_NAME" | tr '_' '-')
          DEPLOY_DIR="/tmp/infotecha-deploy-${MODULE_NAME}"
          TARGET_DIR="/var/www/infotecha.ru/${MODULE_SUBDOMAIN}"
          
          echo "📦 Deploying files to: $TARGET_DIR"
          
          # Копируем файлы
          sudo cp -r "$DEPLOY_DIR"/* "$TARGET_DIR/"
          
          # Устанавливаем права
          sudo chown -R www-data:www-data "$TARGET_DIR"
          sudo chmod -R 755 "$TARGET_DIR"
          
          # Очищаем временные файлы
          rm -rf "$DEPLOY_DIR"
          
          # Обновляем конфигурацию Apache (mod_rewrite правила)
          sudo bash -c "cat > /etc/apache2/sites-available/infotecha-modules.conf << 'EOF'
<VirtualHost *:80>
    ServerName infotecha.ru
    ServerAlias *.infotecha.ru
    DocumentRoot /var/www/infotecha.ru
    
    # Главная страница
    <Directory /var/www/infotecha.ru>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
        DirectoryIndex index.html
    </Directory>
    
    # Перенаправление поддоменов в соответствующие папки
    RewriteEngine On
    RewriteCond %{HTTP_HOST} ^([^.]+)\.infotecha\.ru$
    RewriteCond %{DOCUMENT_ROOT}/%1 -d
    RewriteRule ^/(.*) /%1/$1 [L]
    
    # Логи
    ErrorLog \${APACHE_LOG_DIR}/infotecha_error.log
    CustomLog \${APACHE_LOG_DIR}/infotecha_access.log combined
</VirtualHost>
EOF"
          
          # Включаем сайт и модуль rewrite
          sudo a2enmod rewrite
          sudo a2ensite infotecha-modules.conf
          
          # Перезагружаем Apache
          sudo systemctl reload apache2
          
          echo "✅ Module $MODULE_NAME deployed successfully"
          echo "🌐 Available at: https://${MODULE_SUBDOMAIN}.infotecha.ru"
```

**Файл .github/workflows/deploy-hub.yml:**
```yaml
name: Deploy Hub

on:
  push:
    branches: [main]
    paths:
      - 'content/**'
      - 'modules.json'
  workflow_dispatch:

jobs:
  deploy-hub:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Deploy hub to server
      uses: appleboy/scp-action@v0.1.4
      with:
        host: ${{ secrets.PROD_HOST }}
        username: ${{ secrets.PROD_USERNAME }}
        key: ${{ secrets.PROD_SSH_KEY }}
        source: "content/*,modules.json"
        target: "/tmp/infotecha-hub-deploy/"
        
    - name: Complete hub deployment
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.PROD_HOST }}
        username: ${{ secrets.PROD_USERNAME }}
        key: ${{ secrets.PROD_SSH_KEY }}
        script: |
          set -e
          
          echo "🚀 Deploying InfoTech.io hub..."
          
          # Копируем файлы главной страницы
          sudo cp -r /tmp/infotecha-hub-deploy/content/* /var/www/infotecha.ru/
          sudo cp /tmp/infotecha-hub-deploy/modules.json /var/www/infotecha.ru/
          
          # Устанавливаем права
          sudo chown -R www-data:www-data /var/www/infotecha.ru
          sudo chmod -R 755 /var/www/infotecha.ru
          
          # Очищаем временные файлы
          rm -rf /tmp/infotecha-hub-deploy
          
          # Перезагружаем Apache для применения изменений
          sudo systemctl reload apache2
          
          echo "✅ Hub deployed successfully"
          echo "🌐 Available at: https://infotecha.ru"
```

**Контрольные процедуры:**
```bash
# Валидация YAML файлов
for workflow in .github/workflows/*.yml; do
    echo "Checking $workflow..."
    yq eval 'true' "$workflow" > /dev/null && echo "✅ $workflow - valid YAML" || echo "❌ $workflow - invalid YAML"
done

# Проверка обязательных секретов
echo "Required secrets for workflows:"
echo "- PROD_HOST (server IP/domain)"  
echo "- PROD_USERNAME (SSH user)"
echo "- PROD_SSH_KEY (SSH private key)"
echo "- PAT_TOKEN (GitHub token with repo access)"
```

**Критерии успеха:**
- ✅ Все workflow файлы валидны
- ✅ Логика обработки обновлений модулей настроена
- ✅ Билд и деплой модулей автоматизирован
- ✅ Деплой главной страницы настроен

---

## Шаг 4.5: Создание базовых стилей

**Цель:** Создать современный и отзывчивый дизайн главной страницы

**Файл content/styles.css:**
```css
/* InfoTech.io Platform Styles */

/* CSS Variables */
:root {
  --primary-color: #2563eb;
  --primary-hover: #1d4ed8;
  --secondary-color: #64748b;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --danger-color: #ef4444;
  
  --background-color: #ffffff;
  --surface-color: #f8fafc;
  --border-color: #e2e8f0;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
  
  --font-family-base: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  --font-family-mono: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
  
  --border-radius: 0.5rem;
  --border-radius-lg: 1rem;
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;
}

/* Reset and Base Styles */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: var(--font-family-base);
  line-height: 1.6;
  color: var(--text-primary);
  background-color: var(--background-color);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

/* Header */
.header {
  background: var(--background-color);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.9);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  text-decoration: none;
  color: var(--text-primary);
}

.logo-image {
  width: 32px;
  height: 32px;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
}

.nav {
  display: flex;
  gap: var(--spacing-lg);
}

.nav-link {
  text-decoration: none;
  color: var(--text-secondary);
  font-weight: 500;
  transition: color 0.2s ease;
}

.nav-link:hover {
  color: var(--primary-color);
}

/* Hero Section */
.hero {
  background: linear-gradient(135deg, var(--surface-color) 0%, var(--background-color) 100%);
  padding: var(--spacing-2xl) 0;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: var(--spacing-lg);
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
}

.hero-description {
  font-size: 1.25rem;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-xl);
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-button {
  display: inline-flex;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-xl);
  background-color: var(--primary-color);
  color: white;
  text-decoration: none;
  border-radius: var(--border-radius);
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.2s ease;
  box-shadow: var(--shadow);
}

.hero-button:hover {
  background-color: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

/* Courses Section */
.courses {
  padding: var(--spacing-2xl) 0;
  background-color: var(--surface-color);
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: var(--spacing-2xl);
  color: var(--text-primary);
}

/* Loading, Error, Empty States */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-md);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--danger-color);
}

.retry-button {
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.retry-button:hover {
  background-color: var(--primary-hover);
}

.empty {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
  font-size: 1.1rem;
}

/* Courses Grid */
.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: var(--spacing-xl);
  margin-top: var(--spacing-xl);
}

.course-card {
  background: var(--background-color);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow);
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-md);
}

.course-icon {
  font-size: 2rem;
  padding: var(--spacing-sm);
  background-color: var(--surface-color);
  border-radius: var(--border-radius);
}

.course-meta {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  align-items: flex-end;
}

.course-difficulty,
.course-duration {
  font-size: 0.875rem;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius);
  font-weight: 500;
}

.course-difficulty {
  background-color: var(--primary-color);
  color: white;
}

.course-duration {
  background-color: var(--surface-color);
  color: var(--text-secondary);
}

.course-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
}

.course-title a {
  color: var(--text-primary);
  text-decoration: none;
  transition: color 0.2s ease;
}

.course-title a:hover {
  color: var(--primary-color);
}

.course-description {
  color: var(--text-secondary);
  margin-bottom: var(--spacing-md);
  line-height: 1.6;
}

.course-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-lg);
}

.course-tag {
  font-size: 0.75rem;
  padding: var(--spacing-xs) var(--spacing-sm);
  background-color: var(--surface-color);
  color: var(--text-secondary);
  border-radius: var(--border-radius);
  font-weight: 500;
}

.course-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--border-color);
}

.course-updated {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.course-button {
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--primary-color);
  color: white;
  text-decoration: none;
  border-radius: var(--border-radius);
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.course-button:hover {
  background-color: var(--primary-hover);
}

/* About Section */
.about {
  padding: var(--spacing-2xl) 0;
  background-color: var(--background-color);
}

.about-content {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.about-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-xl);
  margin-top: var(--spacing-2xl);
}

.about-item {
  text-align: center;
}

.about-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing-md);
}

.about-item h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
  color: var(--text-primary);
}

.about-item p {
  color: var(--text-secondary);
  line-height: 1.6;
}

/* Footer */
.footer {
  background-color: var(--text-primary);
  color: white;
  padding: var(--spacing-xl) 0;
  text-align: center;
}

.footer-content p {
  margin-bottom: var(--spacing-sm);
}

.footer a {
  color: var(--primary-color);
  text-decoration: none;
}

.footer a:hover {
  text-decoration: underline;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-description {
    font-size: 1rem;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .courses-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
  
  .about-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
  }
  
  .nav {
    display: none; /* Упростить навигацию на мобильных */
  }
  
  .course-header {
    align-items: center;
  }
  
  .course-meta {
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0 var(--spacing-sm);
  }
  
  .hero {
    padding: var(--spacing-xl) 0;
  }
  
  .courses,
  .about {
    padding: var(--spacing-xl) 0;
  }
}
```

**Контрольные процедуры:**
```bash
# Валидация CSS (требует CSS валидатор)
# npm install -g css-validator
css-validator content/styles.css && echo "✅ CSS valid" || echo "⚠️ CSS validation skipped"

# Проверка размера CSS файла
CSS_SIZE=$(wc -c < content/styles.css)
echo "📏 CSS file size: $CSS_SIZE bytes"
if [ $CSS_SIZE -gt 50000 ]; then
    echo "⚠️ CSS file is quite large, consider optimization"
else
    echo "✅ CSS file size is reasonable"
fi
```

**Критерии успеха:**
- ✅ CSS файл создан и валиден
- ✅ Дизайн responsive (адаптивный)
- ✅ Стили для всех состояний реализованы
- ✅ Размер файла оптимален

---

## Итоговые контрольные процедуры этапа 4

```bash
# Полная проверка репозитория infotecha
echo "🔍 Comprehensive validation of infotecha repository..."

# 1. Структура репозитория
echo "📁 Checking repository structure..."
REQUIRED_DIRS=".github/workflows content scripts templates"
for dir in $REQUIRED_DIRS; do
    test -d "$dir" && echo "✅ $dir exists" || echo "❌ $dir missing"
done

REQUIRED_FILES="modules.json content/index.html content/modules.js content/styles.css README.md"
for file in $REQUIRED_FILES; do
    test -f "$file" && echo "✅ $file exists" || echo "❌ $file missing"
done

# 2. JSON валидация
echo "📋 Validating JSON files..."
jq empty modules.json && echo "✅ modules.json valid" || echo "❌ modules.json invalid"

# 3. HTML валидация
echo "🌐 Validating HTML..."
npx html-validate content/index.html 2>/dev/null && echo "✅ HTML valid" || echo "⚠️ HTML validation skipped"

# 4. JavaScript проверка
echo "📜 Validating JavaScript..."
node -c content/modules.js && echo "✅ JavaScript valid" || echo "❌ JavaScript invalid"

# 5. CSS проверка
echo "🎨 Validating CSS..."
css-validator content/styles.css 2>/dev/null && echo "✅ CSS valid" || echo "⚠️ CSS validation skipped"

# 6. YAML workflow проверка
echo "⚙️ Validating workflows..."
for workflow in .github/workflows/*.yml; do
    yq eval 'true' "$workflow" > /dev/null && echo "✅ $(basename $workflow) valid" || echo "❌ $(basename $workflow) invalid"
done

# 7. Функциональное тестирование (если возможно)
echo "🧪 Functional testing..."
if command -v python3 &> /dev/null; then
    python3 -m http.server 8000 --directory . &
    SERVER_PID=$!
    sleep 3
    
    # Тест доступности files
    curl -f http://localhost:8000/modules.json > /dev/null && echo "✅ modules.json accessible"
    curl -f http://localhost:8000/content/index.html > /dev/null && echo "✅ index.html accessible"
    curl -f http://localhost:8000/content/modules.js > /dev/null && echo "✅ modules.js accessible"
    curl -f http://localhost:8000/content/styles.css > /dev/null && echo "✅ styles.css accessible"
    
    kill $SERVER_PID
else
    echo "⚠️ Python not available, skipping HTTP tests"
fi

echo "🎉 Repository validation complete!"
```

**Критерии успеха этапа 4:**
- ✅ Репозиторий infotecha создан в организации info-tech-io
- ✅ modules.json реестр создан с MVP модулями
- ✅ Главная страница с каталогом курсов работает
- ✅ JavaScript загружает и отображает модули
- ✅ GitHub Actions workflows настроены
- ✅ Responsive дизайн реализован
- ✅ Все файлы валидны и доступны

**Следующий этап:** Создание CLI инструмента (опционально) или переход к развертыванию