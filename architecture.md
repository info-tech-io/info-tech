# Архитектурные решения

## Обзор проекта

Данный документ описывает архитектурное решение для создания образовательной платформы, состоящей из федерации статических учебных модулей, объединенных по принципу "Ось и спицы" (Hub and Spoke).

## Функциональные требования

1. **Федеративная структура**: Создание учебной платформы из нескольких десятков независимых учебных модулей
2. **Архитектура "Ось и спицы"**: 
   - Центральный домен с единым лендингом (ось)
   - Отдельные поддомены для каждого учебного модуля (спицы)
3. **Компонентная структура**: Каждый модуль состоит из:
   - Hugo framework для сборки статических сайтов
   - Тема оформления Compose
   - Шаблонный сайт с пользовательскими настройками
   - Отдельный репозиторий с контентом (Markdown файлы)
4. **Унификация**: Все модули должны использовать единый стиль оформления, одинаковые настройки темы и унифицированный процесс сборки
5. **Автоматизированный деплой**: Автоматическое развертывание при изменении контента модулей

## Технические требования

1. **Контейнеризация**: Использование Docker с многоэтапной сборкой
2. **CI/CD**: GitHub Actions для автоматизации
3. **Инфраструктура**: Docker Compose для развертывания на удаленном сервере
4. **Веб-сервер**: Nginx или Apache для обслуживания статического контента

## Общая архитектура "Ось и спицы"

```
learning-platform/
├── platform-hub/              # ЦЕНТРАЛЬНАЯ ОСЬ
│   ├── landing-page/          # Главный лендинг
│   ├── module-registry.json   # Реестр всех модулей
│   ├── shared-hugo-base/      # Единая тема + Quiz Engine
│   └── nginx-proxy/           # Reverse proxy конфигурация
│
├── shared-hugo-base/          # ОБЩИЕ КОМПОНЕНТЫ
│   ├── themes/learning-platform/  # Базовая тема Hugo
│   ├── layouts/shortcodes/    # Hugo shortcodes (включая quiz.html)
│   ├── static/quiz-engine/    # Quiz Engine как Git submodule
│   └── assets/scss/          # Общие стили
│
├── build-templates/           # ШАБЛОНЫ СБОРКИ
│   ├── Dockerfile.template    # Базовый Dockerfile
│   ├── github-workflow.template
│   └── docker-compose.template
│
└── modules/                   # УЧЕБНЫЕ МОДУЛИ (спицы)
    ├── module_1/              # content repo
    ├── module_2/
    └── module_3/
```

## Доменная структура

```
learn.example.com              # Главный лендинг (ОСЬ)
├── module_1.learn.example.com   # Модуль 1
├── module_2.learn.example.com   # Модуль 2
├── module_3.learn.example.com   # Модуль 3
└── ...
```

## Реестр модулей

Централизованный файл `module-registry.json` содержит метаданные всех модулей:

```json
{
  "modules": {
    "javascript": {
      "name": "JavaScript Fundamentals",
      "description": "Learn JavaScript from basics",
      "subdomain": "js",
      "repository": "github.com/user/module-javascript",
      "status": "active",
      "order": 1,
      "category": "programming",
      "difficulty": "beginner",
      "duration": "40 hours"
    }
  }
}
```

## Docker-контейнеризация

### Многоэтапная сборка (Dockerfile)

```dockerfile
# Этап 1: Сборка Hugo сайта
FROM klakegg/hugo:ext-alpine AS builder
WORKDIR /src
COPY hugo.toml .
COPY themes/ themes/
COPY content/ content/
RUN hugo --minify

# Этап 2: Production образ с nginx
FROM nginx:alpine
COPY --from=builder /src/public /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Базовый образ для унификации

```dockerfile
# Создание shared-hugo-base image
FROM klakegg/hugo:ext-alpine AS hugo-base
COPY shared-theme/ /themes/learning-platform/
COPY base-config/ /config/

# Остальные модули наследуют от этого образа
FROM ghcr.io/yourorg/shared-hugo-base:latest AS builder
```

## GitHub Actions CI/CD Pipeline

### Workflow для отдельного модуля

```yaml
name: Build and Deploy Hugo Site
on:
  repository_dispatch:
    types: [content-updated]
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout main repo
      uses: actions/checkout@v4
      with:
        submodules: recursive
        
    - name: Checkout content repo
      uses: actions/checkout@v4
      with:
        repository: user/content-repo
        path: content
        token: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ghcr.io/${{ github.repository }}:latest
        
    - name: Deploy to server
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /opt/website
          docker-compose pull
          docker-compose up -d --remove-orphans
```

### Централизованный Platform Hub Workflow

```yaml
name: Deploy Learning Platform Federation
on:
  repository_dispatch:
    types: [module-updated, theme-updated]
  schedule:
    - cron: '0 2 * * *'  # Nightly rebuilds

jobs:
  identify-changes:
    # Логика определения измененных модулей
  
  rebuild-modules:
    # Пересборка только измененных модулей
  
  update-platform-registry:
    # Обновление реестра модулей
```

## Docker Compose для производственной среды

```yaml
version: '3.8'
services:
  nginx-proxy:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/platform.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - platform-hub
      - module-javascript
      - module-python
    networks:
      - learning-platform

  platform-hub:
    image: ghcr.io/yourorg/platform-hub:latest
    container_name: platform-hub
    networks:
      - learning-platform

  module-javascript:
    image: ghcr.io/yourorg/module-javascript:latest
    container_name: module-javascript
    networks:
      - learning-platform
```

## Унификация через шаблоны

### Шаблон конфигурации Hugo

```yaml
# build-templates/hugo.yaml.template
baseURL: "https://{{ .Subdomain }}.learn.example.com"
title: "{{ .ModuleName }}"
theme: "learning-platform"

params:
  course:
    name: "{{ .ModuleName }}"
    category: "{{ .Category }}"
    difficulty: "{{ .Difficulty }}"
  platform:
    hub_url: "https://learn.example.com"
    navigation_enabled: true
```

## Централизованное управление

### GitHub Organization структура

```
your-org/
├── platform-hub              # Главный репозиторий (ОСЬ)
├── shared-hugo-base          # Общая тема + базовая конфигурация
├── build-templates           # Шаблоны для автогенерации
├── module_1                  # Content репозиторий
├── module_2                  # Content репозиторий
└── module_3                  # Content репозиторий
```

### CLI инструмент для управления

```bash
# Создание нового модуля
./platform-cli create-module \
  --name "React Advanced" \
  --subdomain "react-advanced" \
  --category "frameworks" \
  --difficulty "advanced"

# Массовое обновление темы
./platform-cli update-theme --all-modules
```

## Процесс развертывания

### Рабочий процесс

```
1. Изменение контента модуля → 
2. Webhook в platform-hub → 
3. Пересборка конкретного модуля → 
4. Обновление module-registry.json → 
5. Частичный деплой только измененного модуля → 
6. Обновление nginx конфигурации → 
7. Zero-downtime switch
```

### Первичная настройка

1. **Создание основного репозитория** с Dockerfile и конфигурациями
2. **Добавление темы как submodule**:
   ```bash
   git submodule add https://github.com/user/compose-theme themes/compose
   ```
3. **Настройка GitHub Secrets**:
   - `HOST` - IP сервера
   - `USERNAME` - пользователь для SSH  
   - `SSH_KEY` - приватный SSH ключ
   - `PAT_TOKEN` - Personal Access Token для webhooks
4. **Развертывание на сервере**:
   ```bash
   mkdir /opt/website && cd /opt/website
   docker-compose up -d
   ```

## Преимущества архитектуры

### Для управления проектом

- ✅ **Centralized control**: Все модули управляются из одного места через platform-hub
- ✅ **Consistent branding**: Единый стиль оформления всех модулей благодаря shared-theme
- ✅ **Easy scaling**: Добавление нового модуля занимает минуты благодаря шаблонам
- ✅ **Version control**: Отслеживание версий каждого модуля через Docker tags
- ✅ **Centralized registry**: Единый реестр всех модулей с метаданными

### Для разработки

- ✅ **DRY principle**: Исключение дублирования конфигураций через наследование
- ✅ **Template-based**: Все новые модули создаются из готовых шаблонов
- ✅ **Independent development**: Команды могут работать над модулями независимо
- ✅ **A/B testing**: Возможность тестирования разных версий модулей
- ✅ **Code reuse**: Максимальное переиспользование компонентов

### Для производственной среды

- ✅ **Selective updates**: Обновляются только измененные модули, не вся платформа
- ✅ **Rollback capability**: Простой откат к предыдущим версиям через Docker tags
- ✅ **Load balancing**: Модули могут масштабироваться независимо друг от друга
- ✅ **CDN optimization**: Каждый модуль может иметь свою CDN конфигурацию
- ✅ **Zero downtime**: Развертывание без простоя благодаря контейнеризации
- ✅ **Resource optimization**: Многоэтапная сборка минимизирует размер образов

### Для пользователей

- ✅ **Consistent UX**: Единообразный пользовательский опыт на всех модулях
- ✅ **Fast loading**: Оптимизированные статические сайты загружаются быстро
- ✅ **Cross-module navigation**: Удобная навигация между модулями через hub
- ✅ **Mobile optimization**: Единая responsive тема для всех устройств

## Потенциальные недостатки и риски

### Технические риски

- ⚠️ **Single point of failure**: Platform-hub является критической точкой отказа
- ⚠️ **Theme coupling**: Сильная связанность всех модулей с единой темой
- ⚠️ **Complexity overhead**: Усложнение архитектуры для простых проектов
- ⚠️ **Docker dependency**: Зависимость от контейнеризации может усложнить отладку

### Операционные риски

- ⚠️ **DNS management**: Необходимость управления множеством поддоменов
- ⚠️ **SSL certificates**: Сложность управления сертификатами для всех поддоменов
- ⚠️ **Monitoring complexity**: Необходимость мониторинга множества сервисов
- ⚠️ **Backup strategy**: Усложнение стратегии резервного копирования

### Масштабирование

- ⚠️ **Resource consumption**: Каждый модуль потребляет отдельные ресурсы
- ⚠️ **Build time**: С ростом числа модулей увеличивается время полной пересборки
- ⚠️ **Registry management**: Module-registry может стать узким местом при большом количестве модулей

### Команда разработки

- ⚠️ **Learning curve**: Необходимость изучения Docker, Hugo, и специфичной архитектуры
- ⚠️ **Debugging complexity**: Отладка может быть сложнее из-за контейнеризации
- ⚠️ **Dependency management**: Необходимость координации обновлений shared-theme

## Стратегии митигации рисков

### Высокая доступность

1. **Load balancing**: Использование нескольких инстансов nginx-proxy
2. **Health checks**: Реализация проверок состояния всех сервисов
3. **Graceful degradation**: Резервные статические страницы при отказе модулей

### Мониторинг и наблюдаемость

1. **Centralized logging**: ELK stack для агрегации логов всех модулей
2. **Metrics collection**: Prometheus + Grafana для мониторинга метрик
3. **Uptime monitoring**: Внешние сервисы мониторинга доступности

### Автоматизация управления

1. **Infrastructure as Code**: Terraform для управления инфраструктурой
2. **Automated backups**: Регулярное резервное копирование всех данных
3. **Disaster recovery**: План восстановления после сбоев

## Рекомендации по развитию

### Краткосрочные улучшения

1. **Search functionality**: Глобальный поиск по всем модулям
2. **User analytics**: Единая система аналитики пользователей
3. **Content management**: Web-интерфейс для управления контентом

### Долгосрочная стратегия

1. **Microservices evolution**: Возможный переход к микросервисной архитектуре
2. **API gateway**: Добавление API шлюза для внешних интеграций
3. **Personalization**: Персонализированные траектории обучения
4. **Multi-language support**: Поддержка множественных языков

## Заключение

Предложенная архитектура федерации учебных модулей по принципу "Ось и спицы" оптимально решает поставленные задачи создания масштабируемой образовательной платформы. Архитектура обеспечивает:

- **Унификацию** через централизованное управление темами и конфигурациями
- **Масштабируемость** через контейнеризацию и независимое развертывание модулей
- **Автоматизацию** через CI/CD пайплайны и инфраструктуру как код
- **Производительность** через статическую генерацию контента и оптимизированную доставку

При правильной реализации и учете описанных рисков данная архитектура способна эффективно поддерживать десятки учебных модулей с минимальными операционными затратами и высоким качеством пользовательского опыта.
