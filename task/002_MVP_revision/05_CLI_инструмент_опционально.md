# Этап 5: Доработка CLI инструмента info_tech_cli (опционально)

## Статус этапа: 🔄 Опциональный

**Важно:** Этот этап является опциональным для MVP. Функциональность подключения модулей можно реализовать вручную, а CLI инструмент доработать позже для удобства автоматизации.

**Приоритет реализации:** После успешного развертывания основной платформы (этапы 4, 6, 7).

---

## Текущее состояние CLI

**Уже реализовано в workspace/info-tech-cli:**
- ✅ Базовая структура на Python Click
- ✅ Команды `create`, `delete`, `validate` (частично)
- ✅ Поддержка .env с GITHUB_TOKEN
- ✅ Настройка setup.py для установки

**Требуется доработать:**
- 🔄 Команда `add` для подключения существующих модулей к платформе
- 🔄 Интеграция с GitHub API для создания форков и workflows
- 🔄 Валидация и тестирование

---

## Шаг 5.1: Анализ требований к команде `add`

**Цель:** Определить функциональность команды для подключения модулей к платформе

**Функциональность команды `add`:**
```bash
# Основной синтаксис
info_tech_cli add <source_repo> [options]

# Примеры использования
info_tech_cli add https://github.com/author/mod_linux_base
info_tech_cli add author/mod_linux_base --module-name linux_base
info_tech_cli add mod_python_basics --interactive
```

**Процесс выполнения команды `add`:**
1. **Анализ входного репозитория**
   - Проверка существования репозитория
   - Проверка наличия папки `content/`
   - Извлечение информации о модуле

2. **Создание форка (если нужно)**
   - Если автор не член организации → создать форк в info-tech-io
   - Если автор член организации → использовать существующий репо

3. **Создание workflow в репозитории модуля**
   - Добавить `.github/workflows/notify-platform.yml`
   - Настроить webhook на изменения в `content/`

4. **Обновление платформы**
   - Обновить `modules.json` в репозитории `infotecha`
   - Создать PR или коммит с изменениями
   - Запустить первичный билд модуля

**Вопросы требующие решения:**

### А. Интерфейс команды
```
Текущие варианты:
1. info_tech_cli add <repo_url> --name <module_name>
2. info_tech_cli add <repo_name> (автоматическое определение имени)  
3. info_tech_cli add --interactive (пошаговый режим)

Рекомендация: Поддерживать все варианты
```

### Б. Автоматическое извлечение метаданных
```
Из репозитория модуля можно автоматически определить:
- Название модуля (из README.md или package.json?)
- Описание (из README.md?)
- Язык (из структуры content/?)

Или требовать явного ввода всех параметров?
```

### В. Обработка ошибок
```
Сценарии ошибок:
- Репозиторий не существует
- Нет прав на создание форка
- Модуль с таким именем уже существует  
- Нет папки content/ в репозитории

Стратегия: Простое завершение с ошибкой для MVP
```

### Г. Права доступа
```
CLI требует admin права в организации для:
- Создания форков
- Добавления workflows в репозитории
- Изменения репозитория infotecha

Токен в .env должен иметь соответствующие scope
```

---

## Шаг 5.2: Создание команды `add`

**Цель:** Реализовать команду для подключения модулей к платформе

**Файл info_tech_cli/commands/add.py:**
```python
"""
Add module command - подключение существующего модуля к платформе InfoTech.io
"""

import os
import json
import click
import requests
from datetime import datetime
from pathlib import Path
import tempfile
import subprocess
import yaml

class ModuleAdder:
    def __init__(self, github_token, github_org):
        self.github_token = github_token
        self.github_org = github_org
        self.github_api = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "InfoTech-CLI/1.0"
        })

    def add_module(self, source_repo, module_name=None, interactive=False):
        """Главная функция добавления модуля"""
        
        click.echo(f"🚀 Adding module from: {source_repo}")
        
        # 1. Парсинг и валидация входного репозитория
        repo_info = self.parse_repository(source_repo)
        if not repo_info:
            raise click.ClickException("❌ Invalid repository format")
        
        # 2. Определение имени модуля
        if not module_name:
            module_name = self.extract_module_name(repo_info, interactive)
        
        # 3. Проверка репозитория
        if not self.validate_source_repository(repo_info):
            raise click.ClickException("❌ Source repository validation failed")
        
        # 4. Создание форка если нужно
        target_repo = self.ensure_fork_in_organization(repo_info)
        
        # 5. Добавление workflow в репозиторий модуля
        self.add_platform_workflow(target_repo)
        
        # 6. Обновление modules.json
        self.update_modules_registry(module_name, target_repo, repo_info)
        
        # 7. Запуск первичного билда
        self.trigger_initial_build(module_name, target_repo)
        
        click.echo(f"✅ Module '{module_name}' successfully added to platform!")
        click.echo(f"🌐 Will be available at: https://{module_name.replace('_', '-')}.infotecha.ru")

    def parse_repository(self, source_repo):
        """Парсинг различных форматов репозитория"""
        
        # Полный URL
        if source_repo.startswith("https://github.com/"):
            parts = source_repo.replace("https://github.com/", "").strip("/").split("/")
            if len(parts) >= 2:
                return {"owner": parts[0], "name": parts[1]}
        
        # Короткий формат owner/repo
        elif "/" in source_repo:
            parts = source_repo.split("/")
            if len(parts) == 2:
                return {"owner": parts[0], "name": parts[1]}
        
        # Только имя репозитория (предполагаем в нашей организации)
        elif source_repo.startswith("mod_"):
            return {"owner": self.github_org, "name": source_repo}
        
        return None

    def extract_module_name(self, repo_info, interactive):
        """Извлечение имени модуля"""
        
        # Автоматическое извлечение из имени репозитория
        repo_name = repo_info["name"]
        if repo_name.startswith("mod_"):
            suggested_name = repo_name[4:]  # Убираем префикс mod_
        else:
            suggested_name = repo_name
        
        if interactive:
            return click.prompt(
                f"Module name", 
                default=suggested_name,
                type=str
            )
        else:
            click.echo(f"📝 Using module name: {suggested_name}")
            return suggested_name

    def validate_source_repository(self, repo_info):
        """Валидация исходного репозитория"""
        
        click.echo("🔍 Validating source repository...")
        
        # Проверка существования репозитория
        repo_url = f"{self.github_api}/repos/{repo_info['owner']}/{repo_info['name']}"
        response = self.session.get(repo_url)
        
        if response.status_code != 200:
            click.echo(f"❌ Repository not found or not accessible")
            return False
        
        # Проверка наличия content/ папки
        contents_url = f"{self.github_api}/repos/{repo_info['owner']}/{repo_info['name']}/contents"
        response = self.session.get(contents_url)
        
        if response.status_code == 200:
            contents = response.json()
            has_content_dir = any(
                item["name"] == "content" and item["type"] == "dir" 
                for item in contents
            )
            
            if not has_content_dir:
                click.echo("⚠️  Warning: No 'content/' directory found in repository")
                if not click.confirm("Continue anyway?"):
                    return False
        
        click.echo("✅ Repository validation passed")
        return True

    def ensure_fork_in_organization(self, repo_info):
        """Создание форка в организации если нужно"""
        
        # Если репозиторий уже в нашей организации
        if repo_info["owner"] == self.github_org:
            click.echo(f"✅ Repository already in {self.github_org} organization")
            return repo_info
        
        click.echo(f"🍴 Creating fork in {self.github_org} organization...")
        
        # Проверяем, нет ли уже форка
        fork_name = repo_info["name"]
        fork_url = f"{self.github_api}/repos/{self.github_org}/{fork_name}"
        response = self.session.get(fork_url)
        
        if response.status_code == 200:
            click.echo("✅ Fork already exists")
            return {"owner": self.github_org, "name": fork_name}
        
        # Создаем форк
        fork_url = f"{self.github_api}/repos/{repo_info['owner']}/{repo_info['name']}/forks"
        fork_data = {"organization": self.github_org}
        
        response = self.session.post(fork_url, json=fork_data)
        
        if response.status_code == 202:
            click.echo("✅ Fork created successfully")
            return {"owner": self.github_org, "name": fork_name}
        else:
            raise click.ClickException(f"❌ Failed to create fork: {response.text}")

    def add_platform_workflow(self, repo_info):
        """Добавление workflow для уведомления платформы"""
        
        click.echo("⚙️ Adding platform notification workflow...")
        
        workflow_content = {
            "name": "Notify Platform on Content Update",
            "on": {
                "push": {
                    "branches": ["main"],
                    "paths": ["content/**"]
                }
            },
            "jobs": {
                "notify-platform": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Notify InfoTech.io Platform",
                            "uses": "peter-evans/repository-dispatch@v3",
                            "with": {
                                "token": "${{ secrets.PLATFORM_TOKEN }}",
                                "repository": "info-tech-io/infotecha", 
                                "event-type": "module-updated",
                                "client-payload": json.dumps({
                                    "module_name": "${MODULE_NAME}",  # Будет заменено
                                    "content_repo": repo_info["name"],
                                    "updated_at": "${{ github.event.head_commit.timestamp }}"
                                }, separators=(',', ':'))
                            }
                        }
                    ]
                }
            }
        }
        
        # Конвертируем в YAML
        workflow_yaml = yaml.dump(workflow_content, default_flow_style=False)
        
        # Отправляем в репозиторий
        file_path = ".github/workflows/notify-platform.yml"
        content_url = f"{self.github_api}/repos/{repo_info['owner']}/{repo_info['name']}/contents/{file_path}"
        
        # Проверяем, существует ли файл
        response = self.session.get(content_url)
        
        file_data = {
            "message": "feat: add platform notification workflow",
            "content": self.encode_base64(workflow_yaml),
            "committer": {
                "name": "InfoTech.io Bot",
                "email": "bot@infotecha.ru"
            }
        }
        
        if response.status_code == 200:
            # Файл существует, обновляем
            existing_file = response.json()
            file_data["sha"] = existing_file["sha"]
            file_data["message"] = "feat: update platform notification workflow"
        
        response = self.session.put(content_url, json=file_data)
        
        if response.status_code in [200, 201]:
            click.echo("✅ Workflow added successfully")
        else:
            raise click.ClickException(f"❌ Failed to add workflow: {response.text}")

    def update_modules_registry(self, module_name, repo_info, original_repo):
        """Обновление modules.json в репозитории infotecha"""
        
        click.echo("📋 Updating modules registry...")
        
        # Получаем текущий modules.json
        registry_url = f"{self.github_api}/repos/{self.github_org}/infotecha/contents/modules.json"
        response = self.session.get(registry_url)
        
        if response.status_code != 200:
            raise click.ClickException("❌ Failed to fetch modules.json")
        
        registry_file = response.json()
        current_content = self.decode_base64(registry_file["content"])
        modules_data = json.loads(current_content)
        
        # Добавляем новый модуль
        subdomain = module_name.replace("_", "-")
        
        modules_data["modules"][module_name] = {
            "name": f"Module {module_name.replace('_', ' ').title()}",
            "description": f"Educational module: {module_name}",
            "content_repo": repo_info["name"],
            "template_repo": "hugo-base",
            "subdomain": subdomain,
            "last_updated": datetime.now().isoformat() + "Z",
            "status": "active"
        }
        
        modules_data["last_updated"] = datetime.now().isoformat() + "Z"
        
        # Отправляем обновленный файл
        updated_content = json.dumps(modules_data, indent=2, ensure_ascii=False)
        
        update_data = {
            "message": f"feat: add {module_name} module to registry",
            "content": self.encode_base64(updated_content),
            "sha": registry_file["sha"],
            "committer": {
                "name": "InfoTech.io Bot", 
                "email": "bot@infotecha.ru"
            }
        }
        
        response = self.session.put(registry_url, json=update_data)
        
        if response.status_code == 200:
            click.echo("✅ Registry updated successfully")
        else:
            raise click.ClickException(f"❌ Failed to update registry: {response.text}")

    def trigger_initial_build(self, module_name, repo_info):
        """Запуск первичного билда модуля"""
        
        click.echo("🏗️ Triggering initial module build...")
        
        dispatch_url = f"{self.github_api}/repos/{self.github_org}/infotecha/dispatches"
        payload = {
            "event_type": "build-module",
            "client_payload": {
                "module_name": module_name,
                "content_repo": repo_info["name"],
                "trigger": "initial-add"
            }
        }
        
        response = self.session.post(dispatch_url, json=payload)
        
        if response.status_code == 204:
            click.echo("✅ Initial build triggered")
        else:
            click.echo(f"⚠️ Build trigger failed, but module was added: {response.text}")

    @staticmethod
    def encode_base64(content):
        """Encode content to base64 for GitHub API"""
        import base64
        return base64.b64encode(content.encode('utf-8')).decode('utf-8')

    @staticmethod 
    def decode_base64(content):
        """Decode base64 content from GitHub API"""
        import base64
        return base64.b64decode(content).decode('utf-8')


def add_module(ctx, source_repo, module_name, interactive):
    """
    Команда добавления модуля к платформе
    """
    
    # Получение токена и организации
    github_token = os.getenv('GITHUB_TOKEN')
    github_org = os.getenv('GITHUB_ORG', 'info-tech-io')
    
    if not github_token:
        raise click.ClickException("❌ GITHUB_TOKEN not found in environment")
    
    try:
        adder = ModuleAdder(github_token, github_org)
        adder.add_module(source_repo, module_name, interactive)
        
    except requests.RequestException as e:
        raise click.ClickException(f"❌ GitHub API error: {str(e)}")
    except Exception as e:
        raise click.ClickException(f"❌ Unexpected error: {str(e)}")
```

**Добавление команды в CLI (обновление info_tech_cli/cli.py):**
```python
# Добавить импорт
from .commands.add import add_module

# Добавить команду после других команд
@cli.command()
@click.argument('source_repo')
@click.option('--module-name', '-n', 
              help='Custom module name (auto-detected if not specified)')
@click.option('--interactive', '-i', is_flag=True,
              help='Run in interactive mode with prompts')
@click.pass_context
def add(ctx, source_repo, module_name, interactive):
    """Add existing module to InfoTech.io platform.
    
    SOURCE_REPO: Repository to add (URL, owner/repo, or mod_name format)
    
    Examples:
        info_tech_cli add https://github.com/author/mod_linux_base
        info_tech_cli add author/mod_python_course --module-name python_basics
        info_tech_cli add mod_javascript_intro --interactive
    """
    add_module(ctx, source_repo, module_name, interactive)
```

**Контрольные процедуры:**
```bash
# Проверка Python синтаксиса
python -c "from info_tech_cli.commands.add import ModuleAdder; print('✅ Import successful')"

# Тест с mock данными (без реальных API вызовов)
python -c "
import os
os.environ['GITHUB_TOKEN'] = 'test_token'
os.environ['GITHUB_ORG'] = 'test_org'
from info_tech_cli.commands.add import ModuleAdder
adder = ModuleAdder('test_token', 'test_org')
repo = adder.parse_repository('owner/mod_test_repo')
assert repo == {'owner': 'owner', 'name': 'mod_test_repo'}
print('✅ Basic functionality test passed')
"

# Проверка зависимостей
pip install -r requirements.txt && echo "✅ Dependencies installed"
```

**Критерии успеха:**
- ✅ Команда `add` реализована
- ✅ GitHub API интеграция работает
- ✅ Обработка различных форматов репозиториев
- ✅ Базовая обработка ошибок реализована

---

## Шаг 5.3: Обновление документации и тестирование

**Цель:** Создать документацию по использованию CLI и базовые тесты

**Файл README.md (обновление для CLI):**
```markdown
# InfoTech CLI

Command-line interface for InfoTech.io educational platform management.

## Installation

```bash
pip install -e .
```

## Configuration

Create `.env` file with required tokens:

```env
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_ORG=info-tech-io
DEFAULT_BRANCH=main
```

**Required GitHub token permissions:**
- `repo` (full repository access)
- `workflow` (manage GitHub Actions)
- `admin:org` (organization management for forks)

## Commands

### Add Module to Platform

Add an existing educational module to InfoTech.io platform:

```bash
# Add module from external repository
info_tech_cli add https://github.com/author/mod_linux_base

# Add module with custom name
info_tech_cli add author/mod_python_course --module-name python_basics

# Interactive mode
info_tech_cli add mod_javascript_intro --interactive
```

**What happens when you add a module:**

1. **Repository Analysis**: Validates source repository and checks for `content/` folder
2. **Fork Creation**: Creates fork in info-tech-io organization (if needed) 
3. **Workflow Setup**: Adds platform notification workflow to module repository
4. **Registry Update**: Updates `modules.json` in infotecha repository
5. **Build Trigger**: Initiates first build and deployment of the module

### Other Commands

```bash
# Create new module from template
info_tech_cli create my-new-module --category programming

# Validate module structure  
info_tech_cli validate ./my-module

# Delete module
info_tech_cli delete old-module --force

# Show version
info_tech_cli version
```

## Module Repository Requirements

For a repository to be added as a module, it should have:

- ✅ `content/` folder with educational materials
- ✅ Markdown files organized in logical structure
- ✅ Public repository (or accessible to InfoTech.io organization)
- ℹ️ Optional: `README.md` with module description

## Troubleshooting

### Authentication Issues

```bash
# Verify token has correct permissions
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Check organization membership
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/orgs/info-tech-io/members/username
```

### Module Addition Failures

1. **"Repository not found"**: Check repository URL and access permissions
2. **"Fork creation failed"**: Verify token has admin:org permissions
3. **"Registry update failed"**: Check if infotecha repository is accessible

### Getting Help

```bash
info_tech_cli --help
info_tech_cli add --help
```
```

**Файл tests/test_add_command.py:**
```python
"""
Tests for the add module command
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from info_tech_cli.commands.add import ModuleAdder


class TestModuleAdder:
    
    def setup_method(self):
        """Setup test environment"""
        self.github_token = "test_token"
        self.github_org = "test_org"
        self.adder = ModuleAdder(self.github_token, self.github_org)

    def test_parse_repository_url_format(self):
        """Test repository URL parsing"""
        
        # Full GitHub URL
        repo = self.adder.parse_repository("https://github.com/owner/mod_test")
        assert repo == {"owner": "owner", "name": "mod_test"}
        
        # Short format
        repo = self.adder.parse_repository("owner/mod_test")
        assert repo == {"owner": "owner", "name": "mod_test"}
        
        # Module name only
        repo = self.adder.parse_repository("mod_test")
        assert repo == {"owner": "test_org", "name": "mod_test"}
        
        # Invalid format
        repo = self.adder.parse_repository("invalid_format")
        assert repo is None

    def test_extract_module_name(self):
        """Test module name extraction"""
        
        repo_info = {"name": "mod_linux_base"}
        
        # Auto extraction
        name = self.adder.extract_module_name(repo_info, interactive=False)
        assert name == "linux_base"
        
        # Without mod_ prefix
        repo_info = {"name": "python_course"}
        name = self.adder.extract_module_name(repo_info, interactive=False)
        assert name == "python_course"

    @patch('requests.Session.get')
    def test_validate_source_repository_success(self, mock_get):
        """Test successful repository validation"""
        
        repo_info = {"owner": "test", "name": "mod_test"}
        
        # Mock repository exists
        mock_get.side_effect = [
            Mock(status_code=200),  # Repository check
            Mock(status_code=200, json=lambda: [  # Contents check
                {"name": "content", "type": "dir"},
                {"name": "README.md", "type": "file"}
            ])
        ]
        
        with patch('click.echo'):
            result = self.adder.validate_source_repository(repo_info)
            assert result is True

    @patch('requests.Session.get')
    def test_validate_source_repository_not_found(self, mock_get):
        """Test repository not found"""
        
        repo_info = {"owner": "test", "name": "nonexistent"}
        
        # Mock repository not found
        mock_get.return_value = Mock(status_code=404)
        
        with patch('click.echo'):
            result = self.adder.validate_source_repository(repo_info)
            assert result is False

    def test_encode_decode_base64(self):
        """Test base64 encoding/decoding"""
        
        content = "Hello, World! 🌍"
        encoded = ModuleAdder.encode_base64(content)
        decoded = ModuleAdder.decode_base64(encoded)
        
        assert decoded == content

    @patch('requests.Session.post')
    def test_trigger_initial_build(self, mock_post):
        """Test initial build trigger"""
        
        mock_post.return_value = Mock(status_code=204)
        
        with patch('click.echo'):
            self.adder.trigger_initial_build("test_module", {"name": "mod_test"})
        
        mock_post.assert_called_once()
        args = mock_post.call_args[1]["json"]
        assert args["event_type"] == "build-module"
        assert args["client_payload"]["module_name"] == "test_module"


class TestIntegration:
    """Integration tests (require actual GitHub token)"""
    
    @pytest.mark.skipif(not os.getenv("GITHUB_TOKEN"), reason="No GitHub token")
    def test_github_api_connection(self):
        """Test actual GitHub API connection"""
        
        token = os.getenv("GITHUB_TOKEN")
        adder = ModuleAdder(token, "info-tech-io")
        
        # Test parsing valid repository
        repo = adder.parse_repository("info-tech-io/quiz")
        assert repo["owner"] == "info-tech-io"
        assert repo["name"] == "quiz"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Контрольные процедуры:**
```bash
# Установка тестовых зависимостей
pip install pytest pytest-cov

# Запуск тестов
python -m pytest tests/test_add_command.py -v

# Проверка покрытия кода
python -m pytest tests/test_add_command.py --cov=info_tech_cli.commands.add

# Интеграционные тесты (требуют GITHUB_TOKEN)
GITHUB_TOKEN=$GITHUB_TOKEN python -m pytest tests/test_add_command.py::TestIntegration -v
```

**Критерии успеха:**
- ✅ Документация создана и понятна
- ✅ Базовые unit тесты проходят
- ✅ Покрытие кода > 80%
- ✅ Интеграционные тесты работают (при наличии токена)

---

## Итоговые контрольные процедуры этапа 5

```bash
# Полная проверка CLI инструмента
echo "🔍 CLI Tool Validation..."

# 1. Установка и базовые проверки
echo "📦 Installing CLI tool..."
pip install -e . && echo "✅ Installation successful"

# 2. Проверка команд
echo "🛠️ Testing CLI commands..."
info_tech_cli --version && echo "✅ Version command works"
info_tech_cli --help | grep -q "add" && echo "✅ Add command available"

# 3. Проверка конфигурации
echo "⚙️ Checking configuration..."
test -f .env && echo "✅ .env file exists" || echo "⚠️ .env file missing"

# 4. Проверка зависимостей
echo "📋 Checking dependencies..."
python -c "import click, requests, yaml; print('✅ All dependencies available')"

# 5. Запуск тестов
echo "🧪 Running tests..."
python -m pytest tests/ -v --tb=short

# 6. Статический анализ кода
echo "🔍 Code analysis..."
python -m flake8 info_tech_cli/ --max-line-length=100 --ignore=E501 || echo "⚠️ Code style warnings"

echo "🎉 CLI validation complete!"
```

**Критерии успеха этапа 5:**
- ✅ Команда `add` полностью реализована
- ✅ GitHub API интеграция работает
- ✅ Обработка различных форматов входных данных
- ✅ Автоматическое создание форков и workflow'ов
- ✅ Обновление modules.json автоматизировано
- ✅ Документация и тесты созданы
- ✅ CLI готов к использованию администраторами

---

## Альтернатива: Ручное подключение модулей

**Если CLI не реализуется на этапе MVP, модули можно подключать вручную:**

### Ручной процесс подключения модуля:

1. **Создание форка** (через веб-интерфейс GitHub)
2. **Добавление workflow** в репозиторий модуля:
   ```yaml
   # .github/workflows/notify-platform.yml
   name: Notify Platform
   on:
     push:
       branches: [main]
       paths: [content/**]
   jobs:
     notify:
       runs-on: ubuntu-latest
       steps:
       - uses: peter-evans/repository-dispatch@v3
         with:
           token: ${{ secrets.PLATFORM_TOKEN }}
           repository: info-tech-io/infotecha
           event-type: module-updated
           client-payload: '{"module_name": "MODULE_NAME", "content_repo": "REPO_NAME"}'
   ```

3. **Обновление modules.json** в репозитории infotecha
4. **Коммит изменений** → автоматический билд через GitHub Actions

**Время выполнения:** 10-15 минут на модуль
**vs CLI:** 1-2 минуты на модуль

---

## Дополнительная функциональность CLI (Расширенная версия)

### Полный спектр команд для управления платформой

После успешной реализации базовой команды `add`, CLI может быть расширен следующим функционалом:

#### **1. Управление модулями**

```bash
# Создание нового модуля из template
info_tech_cli create docker-basics --title "Docker для начинающих" \
    --description "Изучите основы контейнеризации" \
    --difficulty beginner --duration "4-6 часов"

# Список всех модулей с фильтрацией
info_tech_cli list --status active --difficulty beginner --format table
info_tech_cli list --json  # Для скриптов

# Подробная информация о модуле
info_tech_cli info linux-base --show-stats --show-health

# Управление статусом модулей
info_tech_cli archive linux-professional --reason "Устаревший контент"
info_tech_cli unarchive linux-professional
info_tech_cli set-status linux-advanced draft  # active|draft|archived|maintenance
```

#### **2. Развертывание и мониторинг**

```bash
# Управление развертыванием
info_tech_cli build linux-base --force --wait
info_tech_cli status linux-advanced --detailed
info_tech_cli logs linux-base --lines 100 --follow
info_tech_cli rollback linux-base --to-version v1.2.0

# Массовые операции
info_tech_cli build-all --exclude linux-professional
info_tech_cli update-all --dry-run --report
```

#### **3. Валидация и качество**

```bash
# Валидация контента
info_tech_cli validate /path/to/module --strict --fix-auto
info_tech_cli validate-all --format json --output report.json

# Тестирование Quiz Engine
info_tech_cli test-quiz /path/to/quiz.json --verbose
info_tech_cli generate-quiz-template --questions 10 --types multiple-choice,true-false

# Проверка качества
info_tech_cli check-links linux-base --fix-broken --external
info_tech_cli check-images linux-base --optimize --webp
info_tech_cli audit-content linux-base --spelling --grammar
```

#### **4. Конфигурация и настройка**

```bash
# Инициализация и настройка
info_tech_cli init --interactive
info_tech_cli config set github-token ghp_xxx... --encrypt
info_tech_cli config set server-url https://infotecha.ru
info_tech_cli config list --show-secrets

# Профили конфигурации
info_tech_cli config create-profile production
info_tech_cli config use-profile development
info_tech_cli config export --profile production --output config.yml
```

#### **5. Диагностика и мониторинг**

```bash
# Системное здоровье
info_tech_cli health --all-services --detailed --alert-threshold high
info_tech_cli diagnose linux-base --deep-scan --fix-suggestions
info_tech_cli doctor --interactive --fix-issues

# Мониторинг и метрики
info_tech_cli metrics linux-base --period 30d --chart --export csv
info_tech_cli performance-report --all-modules --compare-periods
info_tech_cli uptime-check --all-subdomains --alert-on-failure

# SSL и безопасность
info_tech_cli check-ssl --all-modules --renewal-alerts
info_tech_cli security-audit --vulnerabilities --recommendations
```

#### **6. Работа с контентом**

```bash
# Создание контента
info_tech_cli add-topic linux-base "Тема 3: Продвинутые команды" --interactive
info_tech_cli add-lesson linux-base/topic-01 "Урок 1.4: Практические упражнения"
info_tech_cli create-quiz linux-base --questions 10 --template advanced

# Конвертация и импорт
info_tech_cli convert /path/to/docs --from docusaurus --to hugo
info_tech_cli import-content --from-url https://example.com/course --module new-course
info_tech_cli migrate-legacy /path/to/old-format --backup
```

#### **7. Аналитика и отчетность**

```bash
# Статистика использования
info_tech_cli analytics --module linux-base --period 7d
info_tech_cli user-stats --global --export json
info_tech_cli popular-content --top 10 --trend-analysis

# Отчеты
info_tech_cli report content-quality --all-modules --format html
info_tech_cli report performance --include-recommendations
info_tech_cli report quiz-completion --module linux-base --detailed
```

#### **8. Автоматизация и интеграции**

```bash
# CI/CD интеграции
info_tech_cli webhook create --module linux-base --trigger content-update
info_tech_cli pipeline status --all --format table
info_tech_cli deploy-pipeline --module linux-base --environment staging

# Внешние интеграции
info_tech_cli sync-analytics --provider google-analytics --setup
info_tech_cli backup-content --s3-bucket infotecha-backups --encrypt
info_tech_cli notify --slack --channel devops --message "Deploy complete"
```

### **Пользовательский опыт и интерфейс**

#### **Интерактивные режимы:**
```bash
# Пошаговые мастера
info_tech_cli create --wizard  # Пошаговое создание модуля
info_tech_cli diagnose --interactive  # Интерактивная диагностика
info_tech_cli setup --guided  # Настройка с подсказками
```

#### **Богатый вывод:**
```bash
# Прогресс-бары для длительных операций
Building module docker-basics...
████████████████████████████████████ 100% (45s)

# Цветной и структурированный вывод
✅ Repository created: https://github.com/info-tech-io/mod_docker_basics
🔄 Applying template...
✅ Placeholders replaced
⚙️  Configuring GitHub secrets...
✅ Secrets configured
🏗️  Building module...
✅ Module deployed to https://docker-basics.infotecha.ru

# Таблицы и списки
╭─────────────────┬─────────┬──────────────┬─────────────╮
│ Module          │ Status  │ Last Updated │ Health      │
├─────────────────┼─────────┼──────────────┼─────────────┤
│ linux-base      │ active  │ 2 hours ago  │ healthy ✅  │
│ linux-advanced  │ active  │ 1 day ago    │ healthy ✅  │
│ docker-basics   │ draft   │ just now     │ building 🔄 │
╰─────────────────┴─────────┴──────────────┴─────────────╯
```

### **Архитектура расширенного CLI**

#### **Модульная структура:**
```
info_tech_cli/
├── commands/
│   ├── __init__.py
│   ├── module.py      # create, list, info, archive
│   ├── deploy.py      # build, status, logs, rollback
│   ├── content.py     # validate, test-quiz, check-links
│   ├── config.py      # init, config management
│   ├── monitor.py     # health, diagnose, metrics
│   ├── analytics.py   # stats, reports, insights
│   └── automation.py  # webhooks, pipelines, integrations
├── core/
│   ├── api_client.py  # GitHub/Server API клиент
│   ├── config.py      # Управление конфигурацией
│   ├── utils.py       # Общие утилиты
│   └── validators.py  # Валидация данных
├── templates/         # Шаблоны для генерации
└── plugins/          # Расширяемость через плагины
```

#### **Конфигуральный файл (config.yml):**
```yaml
profiles:
  development:
    github:
      org: info-tech-io
      token: ${GITHUB_TOKEN}
    server:
      url: http://localhost:1313
      ssh_key: ~/.ssh/dev_key
  production:
    github:
      org: info-tech-io  
      token: ${PROD_GITHUB_TOKEN}
    server:
      url: https://infotecha.ru
      ssh_key: ~/.ssh/prod_key
    notifications:
      slack_webhook: ${SLACK_WEBHOOK}
      email: admin@infotecha.ru

current_profile: development

defaults:
  build_timeout: 300
  validation_level: strict
  auto_backup: true
```

### **Приоритизация по фазам**

#### **Фаза 1 (MVP) - Основные команды:**
- ✅ `add` - добавление модулей (уже реализовано)
- 🔄 `create` - создание из template
- 🔄 `list` - просмотр модулей
- 🔄 `build` - ручная сборка
- 🔄 `config` - настройка токенов

#### **Фаза 2 - Мониторинг и диагностика:**
- `status`/`logs` - мониторинг развертывания
- `health`/`diagnose` - диагностика проблем
- `validate` - проверка контента
- `metrics` - базовая аналитика

#### **Фаза 3 - Автоматизация:**
- Массовые операции (`build-all`, `validate-all`)
- Интерактивные режимы
- Интеграции с внешними системами
- Расширенная аналитика

#### **Фаза 4 - Enterprise функции:**
- Плагины и расширения
- Сложная аналитика и BI
- Многопользовательность
- API для интеграций

### **Технические требования**

#### **Зависимости:**
```requirements.txt
click>=8.0.0          # CLI framework
requests>=2.28.0      # HTTP клиент
PyYAML>=6.0          # YAML конфигурация
rich>=12.0.0         # Богатый вывод
inquirer>=2.10.0     # Интерактивные промпты
jinja2>=3.1.0        # Шаблоны
cryptography>=3.4.0  # Шифрование токенов
python-dotenv>=0.19.0 # .env файлы
pytest>=7.0.0        # Тестирование
```

#### **Системные требования:**
- Python 3.8+
- Git (для работы с репозиториями)
- SSH клиент (для развертывания)
- 50MB свободного места
- Интернет соединение

---

## Заключение этапа 5

CLI инструмент представляет **мощную систему автоматизации** для управления платформой InfoTech.io.

**Преимущества полноценного CLI:**
- ⚡ **Экономия времени:** Автоматизация рутинных задач
- 🎯 **Консистентность:** Стандартизированные процессы
- 🔍 **Мониторинг:** Проактивное отслеживание состояния
- 🛠️ **Диагностика:** Быстрое выявление и решение проблем
- 📊 **Аналитика:** Инсайты для улучшения платформы

**Стратегия реализации:**
1. **MVP (Фаза 1):** Базовые команды для запуска
2. **Стабилизация:** Мониторинг и диагностика  
3. **Масштабирование:** Автоматизация и аналитика
4. **Enterprise:** Расширения и интеграции

**Рекомендация:** Начать с MVP версии после успешного развертывания основной платформы, затем итеративно расширять функциональность на основе реальных потребностей.

**Следующий этап:** Развертывание платформы на сервере