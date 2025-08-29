## Этап 5: Создание platform-hub (центральная ось)

### Шаг 5.1: Создание репозитория platform-hub

**Цель:** Создать центральный репозиторий для управления платформой

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
│   ├── update-registry.yml
│   ├── deploy-hub.yml
│   └── rebuild-modules.yml
├── landing-page/
│   ├── content/
│   ├── static/
│   └── hugo.toml
├── module-registry.json
├── nginx/
│   ├── platform.conf
│   └── snippets/
├── docker-compose.yml
├── Dockerfile
├── scripts/
│   ├── update-registry.js
│   ├── generate-nginx-config.js
│   └── deploy.sh
└── README.md
```

---

### Шаг 5.2: Создание реестра модулей

**Цель:** Создать централизованный реестр всех учебных модулей

**module-registry.json:**
```json
{
  "schema_version": "1.0",
  "last_updated": "2025-01-01T00:00:00Z",
  "modules": {
    "javascript-basics": {
      "name": "JavaScript Basics",
      "description": "Learn the fundamentals of JavaScript",
      "subdomain": "js-basics",
      "repository": "https://github.com/learning-platform-org/module-javascript-basics",
      "image": "ghcr.io/learning-platform-org/module-javascript-basics:latest",
      "image_digest": "sha256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "status": "active",
      "order": 1,
      "category": "programming",
      "difficulty": "beginner",
      "duration": "40 hours",
      "tags": ["javascript", "web", "frontend"],
      "last_updated": "2025-01-01T00:00:00Z"
    },
    "python-for-beginners": {
      "name": "Python for Beginners",
      "description": "Start your journey with Python",
      "subdomain": "python-basics",
      "repository": "https://github.com/learning-platform-org/module-python-for-beginners",
      "image": "ghcr.io/learning-platform-org/module-python-for-beginners:latest",
      "image_digest": "sha256:yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
      "status": "active",
      "order": 2,
      "category": "programming",
      "difficulty": "beginner",
      "duration": "50 hours",
      "tags": ["python", "backend", "data-science"],
      "last_updated": "2025-01-01T00:00:00Z"
    }
  }
}
```

**Скрипт для обновления реестра:**
```javascript
// scripts/update-registry.js
const fs = require('fs-extra');
const path = require('path');
const Ajv = require('ajv');

class ModuleRegistry {
  constructor(registryPath) {
    this.registryPath = registryPath;
    this.registry = fs.readJsonSync(this.registryPath);
    this.ajv = new Ajv();
    this.schema = {
      type: 'object',
      properties: {
        module_name: { type: 'string' },
        module_title: { type: 'string' },
        subdomain: { type: 'string' },
        category: { type: 'string' },
        difficulty: { type: 'string' },
        image_digest: { type: 'string' },
        updated_at: { type: 'string', format: 'date-time' }
      },
      required: ['module_name', 'module_title', 'subdomain', 'image_digest', 'updated_at']
    };
    this.validate = this.ajv.compile(this.schema);
  }

  updateModule(payload) {
    console.log('🔄 Updating module registry...');
    
    // Валидация payload
    if (!this.validate(payload)) {
      console.error('❌ Invalid payload:', this.validate.errors);
      throw new Error('Invalid payload for module update');
    }

    const { module_name, module_title, subdomain, category, difficulty, image_digest, updated_at } = payload;
    
    // Обновляем или добавляем модуль
    if (!this.registry.modules[module_name]) {
      console.log(`➕ Adding new module: ${module_name}`);
      this.registry.modules[module_name] = {
        order: Object.keys(this.registry.modules).length + 1,
        status: 'active'
      };
    } else {
      console.log(`✏️ Updating existing module: ${module_name}`);
    }

    this.registry.modules[module_name] = {
      ...this.registry.modules[module_name],
      name: module_title,
      subdomain: subdomain,
      repository: `https://github.com/${process.env.GITHUB_REPOSITORY_OWNER}/${module_name}`,
      image: `ghcr.io/${process.env.GITHUB_REPOSITORY_OWNER}/${module_name}:latest`,
      image_digest: image_digest,
      category: category,
      difficulty: difficulty,
      last_updated: updated_at
    };

    this.registry.last_updated = new Date().toISOString();
    
    // Сохраняем реестр
    fs.writeJsonSync(this.registryPath, this.registry, { spaces: 2 });
    console.log('✅ Module registry updated successfully');
  }
}

// Запуск
if (require.main === module) {
  const payload = process.env.CLIENT_PAYLOAD;
  if (!payload) {
    console.error('❌ CLIENT_PAYLOAD environment variable not set');
    process.exit(1);
  }

  try {
    const parsedPayload = JSON.parse(payload);
    const registry = new ModuleRegistry(path.join(__dirname, '../module-registry.json'));
    registry.updateModule(parsedPayload);
  } catch (error) {
    console.error('❌ Failed to update registry:', error.message);
    process.exit(1);
  }
}
```

**CI/CD для обновления реестра:**
```yaml
# .github/workflows/update-registry.yml
name: Update Module Registry

on:
  repository_dispatch:
    types: [module-updated]

jobs:
  update-registry:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        token: ${{ secrets.PAT_TOKEN }}
        
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        
    - name: Install dependencies
      run: npm install ajv fs-extra
      working-directory: scripts
      
    - name: Update registry
      env:
        CLIENT_PAYLOAD: ${{ toJSON(github.event.client_payload) }}
        GITHUB_REPOSITORY_OWNER: ${{ github.repository_owner }}
      run: node scripts/update-registry.js
      
    - name: Commit and push changes
      uses: stefanzweifel/git-auto-commit-action@v5
      with:
        commit_message: "chore: update module registry for ${{ github.event.client_payload.module_name }}"
        file_pattern: module-registry.json
        commit_user_name: "GitHub Actions"
        commit_user_email: "actions@github.com"
        
    - name: Trigger hub deployment
      uses: peter-evans/repository-dispatch@v3
      with:
        token: ${{ secrets.PAT_TOKEN }}
        repository: ${{ github.repository }}
        event-type: registry-updated
```

---

### Шаг 5.3: Создание лендинга (Hub)

**Цель:** Создать главный лендинг, который отображает список модулей

**hugo.toml для лендинга:**
```toml
# landing-page/hugo.toml
baseURL = "https://learn.example.com"
title = "Info-Tech.io: Открываем двери в мир технологий"
theme = "landing-theme"

[params]
  description = "Интерактивная образовательная платформа с открытым контентом"
  
[params.data]
  registry_path = "../module-registry.json"
```

**Шаблон для отображения модулей:**
```html
<!-- landing-page/themes/landing-theme/layouts/index.html -->
{{ define "main" }}
<section class="hero">
  <h1>{{ .Site.Title }}</h1>
  <p>{{ .Site.Params.description }}</p>
</section>

<section class="module-catalog">
  <h2>Каталог курсов</h2>
  <div class="module-grid">
    {{ $registry := getJSON .Site.Params.data.registry_path }}
    {{ range $key, $module := $registry.modules }}
      {{ if eq $module.status "active" }}
        <a href="https://{{ $module.subdomain }}.learn.example.com" class="module-card">
          <h3>{{ $module.name }}</h3>
          <p>{{ $module.description }}</p>
          <div class="module-meta">
            <span>{{ $module.difficulty }}</span>
            <span>{{ $module.duration }}</span>
          </div>
        </a>
      {{ end }}
    {{ end }}
  </div>
</section>
{{ end }}
```

**Dockerfile для лендинга:**
```dockerfile
# Dockerfile
FROM klakegg/hugo:ext-alpine AS builder
WORKDIR /src
COPY landing-page/ .
COPY module-registry.json .
RUN hugo --minify

FROM nginx:alpine
COPY --from=builder /src/public /usr/share/nginx/html
COPY nginx/platform.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

### Шаг 5.4: Настройка Nginx и Docker Compose

**Цель:** Настроить Nginx для маршрутизации и Docker Compose для деплоя

**Nginx конфигурация:**
```nginx
# nginx/platform.conf
server {
    listen 80 default_server;
    server_name _;
    
    location / {
        proxy_pass http://platform-hub:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Динамически генерируемая часть для модулей
# include /etc/nginx/modules.conf;
```

**Скрипт для генерации Nginx конфига:**
```javascript
// scripts/generate-nginx-config.js
const fs = require('fs-extra');
const path = require('path');

const registry = fs.readJsonSync(path.join(__dirname, '../module-registry.json'));
let nginxConfig = '';

for (const [key, module] of Object.entries(registry.modules)) {
  if (module.status === 'active') {
    nginxConfig += `
server {
    listen 80;
    server_name ${module.subdomain}.learn.example.com;
    
    location / {
        proxy_pass http://${key}:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
`;
  }
}

fs.writeFileSync(path.join(__dirname, '../nginx/modules.conf'), nginxConfig);
console.log('✅ Nginx config for modules generated');
```

**Docker Compose:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  nginx-proxy:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/platform.conf:/etc/nginx/conf.d/default.conf
      - ./nginx/modules.conf:/etc/nginx/conf.d/modules.conf
      - ./ssl:/etc/nginx/ssl
    networks:
      - learning-platform
    depends_on:
      - platform-hub
      # Динамически добавляемые модули

  platform-hub:
    image: ghcr.io/learning-platform-org/platform-hub:latest
    container_name: platform-hub
    networks:
      - learning-platform
      
# Динамически добавляемые сервисы модулей
# module-javascript-basics:
#   image: ghcr.io/learning-platform-org/module-javascript-basics:latest
#   container_name: module-javascript-basics
#   networks:
#     - learning-platform

networks:
  learning-platform:
    driver: bridge
```
