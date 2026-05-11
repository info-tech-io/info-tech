Текущая задача: Разработка мульти-шаблонной системы сборки hugo-templates с поддержкой множественных тем и гибкой конфигурации компонентов

## Описание задачи

### Контекст и проблематика
В настоящее время репозиторий `hugo-base` представляет собой монолитный шаблон для сборки статических сайтов образовательных модулей. Система работает по схеме "один шаблон - одна тема - одна конфигурация", что ограничивает гибкость и возможности кастомизации для различных типов образовательного контента.

Текущий pipeline сборки:
```
Модуль изменен → module-updated.yml → modules.json → build-module.yml → hugo-base → Deploy
```

### Цель задачи
Трансформировать `hugo-base` из монолитного шаблона в гибкую **мульти-шаблонную систему сборки** с поддержкой:
- Множественных тем (themes)
- Гибких конфигураций сборки (build templates) 
- Модульных компонентов (Quiz Engine, Analytics, Auth и др.)
- Параметризованной сборки через реестр модулей

### Архитектурные изменения

#### Переход от Monolithic к Multi-Template Architecture:

**БЫЛО (Monolithic):**
- 1 тема (compose)
- 1 конфиг (hugo.toml)
- Фиксированные компоненты (Quiz Engine обязателен)
- Статическая сборка

**СТАНЕТ (Multi-Template):**
- N тем (compose, academic, corporate, minimal)
- N build templates (default, minimal, enterprise, educational)
- Гибкие компоненты (Quiz Engine опционален)
- Параметризованная сборка

#### Целевая файловая структура hugo-templates:

```
hugo-templates/
├── README.md                        # Документация системы
├── build.sh                         # Параметризованный скрипт сборки
├── docker-compose.yml              # Обновленная композиция
├── Dockerfile                       # Мультистадийная сборка
│
├── templates/                       # Шаблоны сборки (Build Templates)
│   ├── default/                     # Стандартный шаблон (текущий функционал)
│   │   ├── hugo.toml               # Конфиг с Quiz Engine
│   │   ├── static/                 # Статические файлы
│   │   ├── components.yml          # Описание включенных компонентов
│   │   └── archetypes/            # Архетипы страниц
│   ├── minimal/                    # Минимальный шаблон без Quiz Engine
│   │   ├── hugo.toml              # Облегченный конфиг
│   │   ├── static/                # Базовые статические файлы
│   │   └── components.yml         # Минимальный набор компонентов
│   ├── academic/                   # Академический шаблон
│   │   ├── hugo.toml              # Расширенные академические настройки
│   │   ├── static/                # Академические ресурсы
│   │   └── components.yml         # Quiz + References + Citations
│   └── enterprise/                 # Корпоративный шаблон
│       ├── hugo.toml              # Корпоративные настройки
│       ├── static/                # Брендинг и корпоративные ресурсы
│       └── components.yml         # Quiz + Analytics + Auth + LMS Integration
│
├── themes/                         # Множественные темы (Git Submodules)
│   ├── compose/                   # Текущая тема (существующий submodule)
│   ├── academic/                  # Новая академическая тема
│   ├── corporate/                 # Корпоративная тема
│   └── minimal/                   # Минимальная тема для быстрой загрузки
│
├── components/                     # Модульные компоненты
│   ├── quiz-engine/               # Quiz Engine (Git Submodule)
│   ├── analytics/                 # Система аналитики
│   ├── auth/                      # Авторизация и профили
│   ├── progress-tracking/         # Отслеживание прогресса
│   ├── certificates/              # Система сертификатов
│   └── lms-integration/          # Интеграция с LMS
│
├── scripts/                       # Улучшенные скрипты
│   ├── build.sh                  # Главный скрипт параметризованной сборки
│   ├── test-template.sh          # Тестирование конкретного template
│   ├── validate-components.sh    # Валидация компонентов
│   ├── theme-switcher.sh         # Переключение тем
│   └── deploy.sh                 # Скрипт деплоя с параметрами
│
├── tests/                         # Расширенные тесты
│   ├── integration/              # Интеграционные тесты для каждого template
│   ├── templates/                # Тесты шаблонов сборки
│   ├── themes/                   # Тесты тем
│   └── components/               # Тесты компонентов
│
├── docs/                          # Документация
│   ├── USAGE.md                  # Руководство по использованию
│   ├── TEMPLATES.md              # Документация по templates
│   ├── THEMES.md                 # Документация по темам
│   ├── COMPONENTS.md             # Документация по компонентам
│   └── MIGRATION.md              # Миграция с hugo-base
│
└── .github/
    └── workflows/
        ├── test-all-templates.yml    # CI для всех templates
        ├── validate-pr.yml          # Валидация PR
        └── update-submodules.yml    # Обновление submodules
```

### Сквозные изменения в экосистеме

#### 1. Обновление реестра модулей (infotecha/modules.json):
```json
{
  "schema_version": "2.0",
  "modules": {
    "linux_base": {
      "name": "Основы Linux",
      "content_repo": "mod_linux_base",
      "template_repo": "hugo-templates",
      "build_template": "default",        // ← НОВОЕ: выбор шаблона сборки
      "theme": "compose",                 // ← НОВОЕ: выбор темы
      "components": ["quiz-engine"],      // ← НОВОЕ: список компонентов
      "subdomain": "linux-base",
      "status": "active"
    },
    "linux_advanced": {
      "build_template": "academic",       // ← другой template
      "theme": "academic",                // ← другая тема
      "components": ["quiz-engine", "analytics", "certificates"]
    },
    "corporate_training": {
      "build_template": "enterprise",     // ← корпоративный template
      "theme": "corporate",               // ← корпоративная тема
      "components": ["quiz-engine", "auth", "lms-integration", "progress-tracking"]
    }
  }
}
```

#### 2. Обновление CI/CD Pipeline (infotecha/.github/workflows/build-module.yml):
```yaml
# Определение какой репозиторий использовать (dual-repo поддержка)
env:
  TEMPLATE_REPO: ${{ steps.get-config.outputs.template_repo || 'hugo-base' }}
  BUILD_TEMPLATE: ${{ steps.get-config.outputs.build_template || 'legacy' }}
  THEME: ${{ steps.get-config.outputs.theme || 'compose' }}
  COMPONENTS: ${{ steps.get-config.outputs.components || 'quiz-engine' }}

jobs:
  build-and-deploy:
    steps:
    # Динамический checkout в зависимости от template_repo
    - name: Checkout template repository
      uses: actions/checkout@v4
      with:
        repository: info-tech-io/${{ env.TEMPLATE_REPO }}
        path: build-template
        token: ${{ secrets.PAT_TOKEN }}
        submodules: recursive

    # Условная сборка для new/legacy систем
    - name: Build with appropriate system
      run: |
        cd build-template
        if [ "${{ env.TEMPLATE_REPO }}" = "hugo-templates" ]; then
          # Новая мульти-шаблонная система
          ./build.sh \
            --template="${BUILD_TEMPLATE}" \
            --theme="${THEME}" \
            --components="${COMPONENTS}" \
            --content="../module-content" \
            --module="${MODULE_NAME}"
        else
          # Legacy hugo-base система
          # ... существующий код сборки
        fi
```

#### 3. Создание новых theme repositories:
- Fork `academic` theme → `info-tech-io/academic` 
- Fork `corporate` theme → `info-tech-io/corporate`
- Fork `minimal` theme → `info-tech-io/minimal`

#### 4. Модульная архитектура компонентов:
- Разделение Quiz Engine на отдельный опциональный компонент
- Создание системы компонентов с версионированием
- Автоматическое включение/исключение компонентов при сборке

### Стратегия развертывания

**Blue-Green Deployment:** Создание нового репозитория `hugo-templates` параллельно с сохранением работающего `hugo-base`

#### **Преимущества подхода:**
- ✅ **Zero downtime** - продакшн остается стабильным
- ✅ **Безопасная разработка** - возможность экспериментов
- ✅ **Плавная миграция** - постепенный переход модулей
- ✅ **Быстрый откат** - возврат к hugo-base в любой момент

### Этапы выполнения

#### **Фаза 1: Создание и базовая разработка (5 дней)**
1. **Создание нового репозитория hugo-templates** - инициализация с GitHub
2. **Базовая структура** - копирование foundation из hugo-base  
3. **Архитектурное планирование** - детальный план мульти-шаблонной системы
4. **Создание templates/** - разработка 4 шаблонов сборки
5. **Система themes/** - настройка множественных тем как submodules

#### **Фаза 2: Функциональная разработка (6 дней)**  
6. **Модульные components/** - разработка компонентной системы
7. **Параметризованная сборка** - scripts/build.sh с CLI параметрами
8. **Расширенное тестирование** - все комбинации template+theme+components
9. **Базовая документация** - README и основные руководства

#### **Фаза 3: Интеграция в экосистему (4 дня)**
10. **Расширение modules.json** - поддержка template_repo поля (v2.0)
11. **Обновление CI/CD** - поддержка dual-repo в build-module.yml
12. **Staging тестирование** - полная проверка на тестовом окружении
13. **Pilot deployment** - 1-2 новых модуля на hugo-templates

#### **Фаза 4: Production миграция (3 дня)**
14. **Постепенная миграция модулей** - по одному модулю с мониторингом
15. **Production валидация** - проверка всех мигрированных модулей
16. **Полная документация** - финальная документация системы

#### **Фаза 5: Завершение (2 дня)**
17. **Финальная миграция** - оставшиеся модули
18. **Архивирование hugo-base** - пометка как deprecated
19. **Очистка CI/CD** - удаление legacy кода  
20. **Celebration** - успешное завершение миграции 🎉

### Критерии успеха
- ✅ Поддержка множественных build templates (минимум 3)
- ✅ Поддержка множественных тем (минимум 3)
- ✅ Модульная система компонентов с возможностью включения/отключения
- ✅ Параметризованная сборка через build.sh
- ✅ Интеграция с обновленным modules.json (schema v2.0)
- ✅ Обратная совместимость с существующими модулями
- ✅ Полная документация и примеры использования
- ✅ Переименование репозитория с сохранением истории

### Ожидаемые результаты
- Гибкая система сборки вместо монолитного шаблона
- Возможность создания модулей с различным дизайном и функциональностью
- Упрощение добавления новых тем и компонентов
- Масштабируемая архитектура для будущих расширений
- Переименованный репозиторий `hugo-templates` отражающий новую роль 
