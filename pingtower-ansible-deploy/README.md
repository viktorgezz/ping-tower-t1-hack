# Ansible Playbook для локального развертывания репозиториев с Docker Compose

Этот проект содержит Ansible плейбук для автоматического клонирования репозиториев и запуска Docker Compose сервисов для развертки, сборки и запуска сайта PingTower.

## Структура проекта

```
.
├── local-deploy.yml      # Плейбук для локального развертывания
├── inventory.ini         # Инвентарь для localhost
└── README.md            # Этот файл
```

## Быстрый старт

### 1. Установка Ansible

**Windows:**
```bash
# Через pip
pip install ansible

# Или через Chocolatey
choco install ansible
```

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ansible

# macOS
brew install ansible
```

### 2. Настройка репозиториев

Отредактируйте файл `local-deploy.yml` и укажите ваши репозитории в секции `vars` (все репозитории уже указаны):

```yaml
vars:
  repositories:
    - name: "my-project"
      url: "https://github.com/your-username/your-project.git"
      branch: "main"
      path: "./projects/my-project"
```

### 3. Запуск плейбука

```bash
# Запуск локального плейбука
ansible-playbook -i inventory.ini local-deploy.yml
```

## Что делает плейбук

1. **Проверяет зависимости:**
   - Git (устанавливает если отсутствует)
   - Docker и Docker Compose

2. **Клонирует репозитории:**
   - Создает папку `./projects`
   - Клонирует каждый репозиторий в указанную папку
   - Обновляет существующие репозитории

3. **Запускает Docker Compose:**
   - Ищет файлы `docker-compose.yml` или `docker-compose.yaml`
   - Запускает сервисы для каждого проекта
   - Показывает статус запущенных контейнеров

## Настройка репозиториев

В файле `local-deploy.yml` найдите секцию `repositories` и добавьте ваши проекты:

```yaml
repositories:
  - name: "service_scripts"
    url: "https://gitlab.com/t1_hack/service_scripts.git"
    branch: "main"
    path: "./projects/service_scripts"
    
  - name: "ai-agent"
    url: "https://gitlab.com/t1_hack/ai-agent.git"
    branch: "main"
    path: "./projects/ai-agent"
```

### Параметры репозитория

- `name` - имя проекта (для отображения)
- `url` - URL репозитория Git
- `branch` - ветка для клонирования
- `path` - путь для клонирования (относительно текущей папки)

## Требования

- Ansible 2.9+
- Git
- Docker
- Docker Compose

## Troubleshooting

### Проблемы с Docker

1. Убедитесь, что Docker запущен
2. Проверьте права доступа к Docker
3. На Linux добавьте пользователя в группу docker: `sudo usermod -aG docker $USER`

### Проблемы с Git

1. Убедитесь, что Git установлен
2. Проверьте доступ к репозиториям
3. Настройте SSH ключи для приватных репозиториев

### Проблемы с Ansible

1. Проверьте версию Ansible: `ansible --version`
2. Убедитесь, что инвентарь настроен правильно
3. Проверьте подключение: `ansible all -i inventory.ini -m ping`
