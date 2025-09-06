# Диагностика и решение проблем с Notify Hub Workflow

**Дата создания:** 2025-09-03  
**Статус:** Активное расследование  
**Приоритет:** Критический (блокирует полную автоматизацию CI/CD)

## Описание проблемы

### Основная проблема
Workflow `Notify Hub on Content Update` в репозитории `mod_linux_base` не работает автоматически при push изменений в папку `content/**`. Workflow запускается, но падает с ошибкой на шаге "Notify infotecha hub".

### Симптомы
1. ❌ Workflow запускается автоматически при push, но завершается с `"conclusion": "failure"`
2. ❌ Шаг "Notify infotecha hub" падает через 1 секунду после запуска
3. ❌ Шаг "Log notification" пропускается (skipped) из-за ошибки предыдущего шага
4. ❌ API запросы с использованием PAT_TOKEN возвращают "Bad credentials" (HTTP 401)

## Техническая диагностика

### Анализ workflow файла
**Файл:** `/root/info-tech/workspace/mod_linux_base/.github/workflows/notify-hub.yml`

```yaml
name: Notify Hub on Content Update

on:
  push:
    branches: [main]
    paths:
      - 'content/**'
  workflow_dispatch:

jobs:
  notify-infotecha-hub:
    runs-on: ubuntu-latest
    
    steps:
    - name: Notify infotecha hub
      uses: peter-evans/repository-dispatch@v3
      with:
        token: ${{ secrets.PAT_TOKEN }}
        repository: info-tech-io/infotecha
        event-type: module-updated
        client-payload: |
          {
            "module_name": "linux_base",
            "content_repo": "mod_linux_base",
            "updated_at": "${{ github.event.head_commit.timestamp }}",
            "commit_sha": "${{ github.sha }}",
            "commit_message": "${{ github.event.head_commit.message }}"
          }
```

### История выполнений workflow
**Последний неуспешный запуск:** Run #14 (ID: 17442173630)  
- **Время выполнения:** 2025-09-03T18:09:49Z - 2025-09-03T18:09:54Z (5 секунд)
- **Триггер:** Push commit `be06046e857c6d31ff972b558f043897effa9da0`
- **Статус:** `"conclusion": "failure"`

### Детали выполнения job
```json
{
  "name": "notify-infotecha-hub",
  "status": "completed",
  "conclusion": "failure",
  "steps": [
    {
      "name": "Set up job",
      "conclusion": "success"
    },
    {
      "name": "Notify infotecha hub", 
      "conclusion": "failure"  // ❌ Здесь происходит ошибка
    },
    {
      "name": "Log notification",
      "conclusion": "skipped"   // Пропущен из-за ошибки
    }
  ]
}
```

## Основная причина проблемы

### PAT_TOKEN не настроен или недействителен

**Диагностические проверки:**
1. ✅ Переменная `$PAT_TOKEN` в среде выполнения имеет длину 0 символов
2. ✅ API запросы с токеном возвращают `{"message": "Bad credentials", "status": "401"}`
3. ✅ Repository dispatch запросы не выполняются

**Вывод:** Секрет `PAT_TOKEN` либо не установлен в настройках репозитория `mod_linux_base`, либо содержит недействительный токен.

## Возможные решения

### 1. Проверка и настройка GitHub Secrets (Рекомендуемое)

**Шаги для проверки:**
1. Перейти в репозиторий `https://github.com/info-tech-io/mod_linux_base`
2. Открыть Settings → Secrets and variables → Actions
3. Проверить наличие секрета `PAT_TOKEN`
4. Если секрет отсутствует или устарел - обновить

**Требования к PAT_TOKEN:**
- **Тип:** Personal Access Token (Classic) или Fine-grained personal access token
- **Владелец:** Пользователь с доступом к обоим репозиториям (`mod_linux_base` и `infotecha`)
- **Необходимые права:**
  - `repo` - полный доступ к репозиториям
  - `workflow` - управление workflow
  - `metadata:read` - чтение метаданных репозитория

**Целевые репозитории для доступа:**
- `info-tech-io/mod_linux_base` (источник)
- `info-tech-io/infotecha` (целевой для dispatch)

### 2. Альтернативное решение: GitHub App

**Преимущества:**
- Более безопасно чем PAT
- Можно настроить точные права доступа
- Не привязано к конкретному пользователю

**Изменения в workflow:**
```yaml
- name: Get GitHub App Token
  id: get_token
  uses: tibdex/github-app-token@v1
  with:
    app_id: ${{ secrets.APP_ID }}
    private_key: ${{ secrets.PRIVATE_KEY }}
    repository: info-tech-io/infotecha

- name: Notify infotecha hub
  uses: peter-evans/repository-dispatch@v3
  with:
    token: ${{ steps.get_token.outputs.token }}
    repository: info-tech-io/infotecha
    event-type: module-updated
```

### 3. Временное решение: Manual workflow dispatch

**Для тестирования без исправления PAT_TOKEN:**
```bash
curl -X POST \
  https://api.github.com/repos/info-tech-io/infotecha/actions/workflows/module-updated.yml/dispatches \
  -H "Authorization: token VALID_PAT_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -d '{
    "ref": "main",
    "inputs": {
      "module_name": "linux_base",
      "content_repo": "mod_linux_base",
      "trigger": "manual_test"
    }
  }'
```

## Влияние на CI/CD pipeline

### Текущее состояние автоматизации
1. ✅ **mod_linux_base:** Изменения в content успешно коммитятся
2. ❌ **Notify Hub:** Автоматическое уведомление не работает
3. ✅ **Module Updated:** Работает при ручном запуске
4. ✅ **Build Module:** Работает корректно после исправления
5. ✅ **Deploy:** Успешная доставка на сервер

### Обходное решение (текущее)
Полная цепочка работает при ручном запуске Module Updated workflow через API или GitHub UI.

## Рекомендации по решению

### Приоритет 1: Исправить PAT_TOKEN
1. **Немедленно:** Проверить настройки секретов в `mod_linux_base`
2. **Создать новый PAT** с правильными правами доступа
3. **Обновить секрет** `PAT_TOKEN` в настройках репозитория
4. **Протестировать** автоматический запуск workflow

### Приоритет 2: Добавить отладку
Временно добавить debug-шаг в workflow для диагностики:

```yaml
- name: Debug PAT_TOKEN
  run: |
    echo "PAT_TOKEN length: ${#PAT_TOKEN}"
    echo "PAT_TOKEN first 4 chars: ${PAT_TOKEN:0:4}..."
    if [ -z "$PAT_TOKEN" ]; then
      echo "❌ PAT_TOKEN is empty"
      exit 1
    fi
  env:
    PAT_TOKEN: ${{ secrets.PAT_TOKEN }}
```

### Приоритет 3: Улучшить мониторинг
Добавить уведомления о статусе workflow для быстрого обнаружения проблем.

## Заключение

**Блокирующая проблема:** Неправильно настроенный `PAT_TOKEN` секрет препятствует полной автоматизации CI/CD pipeline.

**Простое решение:** Обновление секрета `PAT_TOKEN` в настройках репозитория `mod_linux_base` с действительным токеном должно решить проблему полностью.

**Время на исправление:** 5-10 минут (при наличии доступа к настройкам репозитория).

---

**Последнее обновление:** 2025-09-03 18:15 UTC  
**Следующий шаг:** Ожидание обновления PAT_TOKEN для повторного тестирования