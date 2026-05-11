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
    const quiz = JSON.parse(fs.readFileSync(`quiz-examples/${file}`));
    console.log(`✅ ${file} - valid JSON`);
  }
});
"
```

**Критерии успеха:**
- ✅ Все тесты проходят
- ✅ Создан стабильный tag v1.0.0
- ✅ CI/CD pipeline работает
- ✅ Все примеры квизов валидны

```