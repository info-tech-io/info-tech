# Прогресс этапа 5: Интеграция с modules.json v2.0 и обновление CI/CD

## Статус: ⏳ Не начат (ожидает завершения этапа 4)

**Запланированный старт:** После завершения этапа 4  
**Запланированное завершение:** TBD (2 дня)  
**Фактический прогресс:** 0%

## План выполнения

- [ ] Шаг 5.1: Расширение схемы modules.json до v2.0
- [ ] Шаг 5.2: Обновление CI/CD pipeline в infotecha
- [ ] Шаг 5.3: Система конфигурации модулей
- [ ] Шаг 5.4: Тестирование dual-repo архитектуры
- [ ] Шаг 5.5: Документация и инструменты

## Текущая задача
Этап ожидает завершения этапа 4

## Контрольные точки (не выполнены)

### 📋 Запланированные проверки:

#### 1. Schema modules.json v2.0 работает
- [ ] Новые поля корректно парсятся и валидируются
- [ ] Обратная совместимость с v1.0 полностью сохранена
- [ ] Валидация reject некорректные конфигурации  
- [ ] JSON Schema документирует все поля и их использование

#### 2. Dual-repo CI/CD функционирует
- [ ] `build-module.yml` корректно выбирает репозиторий (hugo-base vs hugo-templates)
- [ ] Параметры template/theme/components передаются в hugo-templates  
- [ ] Legacy модули продолжают работать с hugo-base без изменений
- [ ] Новые модули корректно собираются с hugo-templates

#### 3. Система миграции модулей готова
- [ ] `update-module-config.sh` может обновить конфигурацию любого модуля
- [ ] Автоматическое определение оптимального template работает
- [ ] Валидация совместимости предотвращает некорректные конфигурации
- [ ] Rollback механизм позволяет вернуть старую конфигурацию

#### 4. End-to-end тестирование проходит
- [ ] Существующие модули (linux_base, linux_advanced, linux_professional) работают без изменений
- [ ] Тестовые модули с новой конфигурацией собираются корректно
- [ ] CI/CD pipeline обрабатывает оба типа модулей
- [ ] Deploy процесс работает для обеих систем

#### 5. Инструментарий и документация готовы
- [ ] CLI инструменты для управления модулями созданы
- [ ] Документация обновлена и отражает новые возможности
- [ ] План миграции детализирован и готов к исполнению
- [ ] Troubleshooting guide создан

## Способы верификации (готовы к использованию)

### 🔍 Проверка modules.json v2.0

#### Валидация схемы
```bash
cd infotecha/
# Проверка существующих модулей (должны работать как v1.0)
python3 scripts/validate-modules.py modules.json --version=auto
echo $?  # = 0

# Добавление тестового модуля с новой схемой
cat >> modules.json << 'EOF'
  "test_module": {
    "name": "Test Module",
    "content_repo": "mod_test", 
    "template_repo": "hugo-templates",
    "build_template": "minimal",
    "theme": "compose",
    "components": ["navigation"],
    "subdomain": "test",
    "status": "active"
  }
EOF

# Валидация расширенной схемы
python3 scripts/validate-modules.py modules.json --version=2.0
echo $?  # = 0
```

#### Тест обратной совместимости
```bash
# Существующие модули должны работать без template_repo (= hugo-base)
jq -r '.modules.linux_base | has("template_repo")' modules.json  # false
jq -r '.modules.linux_base.status' modules.json  # "active" 

# Проверка defaults
python3 -c "
import json
with open('modules.json') as f:
    data = json.load(f)
    linux_base = data['modules']['linux_base']
    print('template_repo:', linux_base.get('template_repo', 'hugo-base'))  # hugo-base
    print('build_template:', linux_base.get('build_template', 'legacy'))   # legacy
"
```

### 🔍 Проверка CI/CD dual-repo

#### Тест выбора репозитория
```bash
# Эмуляция workflow запуска для legacy модуля
cd infotecha/.github/workflows/
python3 -c "
import yaml, json
# Эмулируем получение конфигурации для linux_base
module_config = {'content_repo': 'mod_linux_base'}  # без template_repo
template_repo = module_config.get('template_repo', 'hugo-base')
print(f'Selected repo: {template_repo}')  # hugo-base
"

# Эмуляция для нового модуля  
python3 -c "
module_config = {
    'content_repo': 'mod_test',
    'template_repo': 'hugo-templates',
    'build_template': 'minimal',
    'theme': 'compose'
}
template_repo = module_config.get('template_repo', 'hugo-base')
print(f'Selected repo: {template_repo}')  # hugo-templates
"
```

### 🔍 Проверка инструментов миграции
```bash
# Тест обновления конфигурации модуля
cd infotecha/scripts/
./update-module-config.sh linux_base --template-repo=hugo-templates --build-template=default --theme=compose --components=quiz-engine --dry-run

# Проверка автоматического определения template
./auto-detect-template.sh mod_linux_base  # Должен предложить 'default'
./auto-detect-template.sh mod_documentation  # Должен предложить 'minimal'

# Тест валидации совместимости
./validate-combination.sh --template=academic --theme=corporate --components=quiz-engine
echo $?  # != 0 (несовместимая комбинация)

./validate-combination.sh --template=minimal --theme=compose --components=navigation  
echo $?  # = 0 (совместимая комбинация)
```

### 🔍 End-to-end тестирование
```bash
# Настройка staging окружения
cd /tmp/staging-test/
git clone https://github.com/info-tech-io/infotecha.git
git clone https://github.com/info-tech-io/hugo-templates.git
git clone https://github.com/info-tech-io/mod_linux_base.git

# Эмуляция CI/CD для legacy модуля
cd infotecha/
MODULE_NAME=linux_base TEMPLATE_REPO=hugo-base .github/workflows/test-build-module.sh

# Эмуляция CI/CD для нового модуля  
MODULE_NAME=test_module TEMPLATE_REPO=hugo-templates BUILD_TEMPLATE=minimal THEME=compose COMPONENTS=navigation .github/workflows/test-build-module.sh
```

## Риски для отслеживания

### 🔴 Высокие риски:
- **Нарушение работы существующих модулей** - изменения в CI/CD могут сломать работающие модули
- **Сложность dual-repo логики** - условная логика в CI/CD может быть источником bugs  

### 🟡 Средние риски:
- **Миграция данных modules.json** - некорректное обновление может сделать модули недоступными
- **Performance overhead dual-repo** - дополнительные проверки могут замедлить CI/CD

## Планируемые результаты
- ✅ **modules.json v2.0 schema** - расширенная схема с полной обратной совместимостью (100% готов)
- ✅ **Dual-repo CI/CD** - обновленный pipeline с поддержкой обеих систем (100% готов)
- ✅ **Migration toolkit** - инструменты для безопасной миграции модулей (100% готов)
- ✅ **End-to-end tests** - проверка работоспособности всей цепочки (100% готов)
- ✅ **Updated documentation** - обновленная документация реестра и CI/CD (100% готов)

### Примеры конфигураций после этапа

#### Legacy модуль (без изменений)
```json
"linux_base": {
  "name": "Основы Linux",
  "content_repo": "mod_linux_base", 
  "subdomain": "linux-base",
  "status": "active"
  // template_repo отсутствует = использовать hugo-base
}
```

#### Новый модуль с hugo-templates
```json
"python_basics": {
  "name": "Основы Python",
  "content_repo": "mod_python_basics",
  "template_repo": "hugo-templates",
  "build_template": "minimal", 
  "theme": "compose",
  "components": ["navigation", "syntax-highlighting"],
  "subdomain": "python-basics",
  "status": "active"
}
```

## Заметки для выполнения
- **Безопасность прежде всего:** Любые изменения не должны нарушить работу продакшена
- **Постепенность:** Новая функциональность добавляется опционально, старая остается по умолчанию
- **Тестирование:** Каждое изменение должно быть протестировано на всех типах модулей
- **Документация:** Обязательно обновить все инструкции и examples
- **Rollback plan:** Всегда иметь план быстрого отката к предыдущему состоянию

## Проблемы и решения
*Будут документироваться по мере выполнения*

## Следующий этап
**Готов к этапу 6:** Когда все legacy модули работают без изменений и новые модули корректно собираются с hugo-templates