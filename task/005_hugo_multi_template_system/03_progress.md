# Прогресс этапа 3: Параметризованная система сборки

## Статус: ⏳ Не начат (ожидает завершения этапа 2)

**Запланированный старт:** После завершения этапа 2  
**Запланированное завершение:** TBD (2 дня)  
**Фактический прогресс:** 0%

## План выполнения

- [ ] Шаг 3.1: Разработка главного скрипта build.sh
- [ ] Шаг 3.2: Система управления компонентами
- [ ] Шаг 3.3: Интеграция с системой тем
- [ ] Шаг 3.4: Система конфигурации Hugo
- [ ] Шаг 3.5: Вспомогательные скрипты

## Текущая задача
Этап ожидает завершения этапа 2

## Контрольные точки (не выполнены)

### 📋 Запланированные проверки:

#### 1. Главный скрипт build.sh функционален
- [ ] CLI аргументы парсятся корректно
- [ ] Базовая валидация параметров работает
- [ ] Help система (`--help`) информативна
- [ ] Error handling и понятные сообщения об ошибках
- [ ] Логирование процесса сборки

#### 2. Система компонентов работает
- [ ] components.yml файлы корректно обрабатываются
- [ ] Статические файлы компонентов правильно копируются
- [ ] Quiz Engine интегрируется без ошибок
- [ ] ⚠️ **ЗАГОТОВКИ:** Остальные компоненты только эмулируются (stub files)

#### 3. Интеграция с темами функционирует
- [ ] Compose тема подключается корректно  
- [ ] Fallback на compose при отсутствии запрошенной темы
- [ ] ⚠️ **ЗАГОТОВКИ:** Academic, corporate, minimal темы только проверяются на существование

#### 4. Динамическая конфигурация Hugo
- [ ] hugo.toml генерируется корректно для каждой комбинации
- [ ] Базовые настройки template + theme работают
- [ ] Компоненты правильно добавляют свои конфигурации
- [ ] Результирующая конфигурация валидна для Hugo

#### 5. Вспомогательные скрипты готовы
- [ ] `validate-components.sh` проверяет YAML синтаксис и схему
- [ ] `test-template.sh` может протестировать любой template
- [ ] `theme-switcher.sh` переключает темы (где возможно)
- [ ] Базовый `deploy.sh` создан для будущего использования

## Способы верификации (готовы к использованию)

### 🔍 Проверка основного функционала build.sh

#### Тест базовой сборки (default)
```bash
./scripts/build.sh --template=default --theme=compose --components=quiz-engine --content=test-content --module=test
echo $?  # Должен быть 0 (успех)
```

#### Тест minimal сборки  
```bash
./scripts/build.sh --template=minimal --theme=compose --components=navigation --content=test-content --module=test
ls output/  # Должен содержать базовые файлы Hugo
```

#### Тест валидации параметров
```bash
./scripts/build.sh --template=nonexistent 2>&1 | grep -i "error"
./scripts/build.sh --theme=nonexistent 2>&1 | grep -i "fallback"
./scripts/build.sh --help | wc -l  # > 20 строк справки
```

### 🔍 Проверка системы компонентов
```bash
# Тест валидации components.yml
./scripts/validate-components.sh templates/default/components.yml
./scripts/validate-components.sh templates/minimal/components.yml

# Проверка интеграции Quiz Engine
find output/ -path "*/quiz/*" | wc -l  # Должно быть > 0 для default template

# Проверка заглушек для планируемых компонентов  
./scripts/build.sh --components=analytics 2>&1 | grep -i "stub\|placeholder"
```

### 🔍 Проверка системы тем
```bash
# Тест существующей темы
./scripts/theme-switcher.sh compose
ls themes/compose/  # Должна существовать

# Тест fallback на несуществующую тему
./scripts/build.sh --theme=nonexistent 2>&1 | grep -i "fallback.*compose"
```

### 🔍 Проверка генерации конфигурации
```bash
# Тест генерации hugo.toml
./scripts/build.sh --template=default --theme=compose --components=quiz-engine --dry-run
cat generated-hugo.toml | grep -E "(theme|baseURL|title)"

# Валидация Hugo конфигурации
hugo config --config=generated-hugo.toml | grep -v "ERROR"
```

### 🔍 Проверка производительности
```bash
# Измерение времени сборки
time ./scripts/build.sh --template=minimal --theme=compose --components=navigation
time ./scripts/build.sh --template=default --theme=compose --components=quiz-engine
# minimal должен быть заметно быстрее default
```

## Риски для отслеживания

### 🔴 Высокие риски:
- **Сложность CLI интерфейса** - слишком сложный CLI может отпугнуть пользователей
- **Совместимость с Hugo** - динамически генерируемые конфигурации могут нарушить работу Hugo  

### 🟡 Средние риски:
- **Производительность системы сборки** - дополнительные проверки могут замедлить процесс сборки
- **Complexity debt от заготовок** - создание заглушек для несуществующих компонентов может запутать систему

## Планируемые результаты
- ✅ **scripts/build.sh** - полностью функциональный CLI для сборки (100% готов)
- ✅ **Система компонентов** - работает с Quiz Engine, заглушки для остальных (80% готов)
- ✅ **Интеграция с темами** - работает с compose, fallback для остальных (70% готов)  
- ✅ **Динамическая конфигурация Hugo** - генерирует валидные конфигурации (100% готов)
- ✅ **Вспомогательные скрипты** - набор утилит для работы с системой (90% готов)
- ✅ **Документация CLI** - подробное описание использования

### Примеры использования после этапа
```bash
# Стандартная сборка (как текущий hugo-base)
./scripts/build.sh --template=default --theme=compose --components=quiz-engine

# Быстрая легкая сборка  
./scripts/build.sh --template=minimal --theme=compose --components=navigation

# Пример академического модуля (заготовка)
./scripts/build.sh --template=academic --theme=academic --components=quiz-engine,references
```

## Заметки для выполнения
- **Приоритет:** Стабильность работы с существующими компонентами (Quiz Engine + compose theme)
- **Заглушки:** Все несуществующие компоненты должны давать понятные сообщения о статусе
- **CLI Design:** Делать интерфейс интуитивным, с хорошими defaults
- **Производительность:** minimal template должен показать значительное улучшение скорости
- **Документация:** Каждый скрипт должен иметь --help с примерами использования

## Проблемы и решения
*Будут документироваться по мере выполнения*

## Следующий этап
**Готов к этапу 4:** Когда build.sh работает с default и minimal templates, система компонентов функционирует