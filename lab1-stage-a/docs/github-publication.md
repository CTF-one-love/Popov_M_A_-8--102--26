# Безопасная публикация этапа А в GitHub

Инструкция выполняется пользователем после успешной локальной проверки. Проект поставляется без `.git`, коммитов, токенов и настроенного remote.

## 1. Условия допуска

Из корня проекта в VS Code / PowerShell:

```powershell
.\.venv\Scripts\python.exe scripts/verify.py
if ($LASTEXITCODE -ne 0) { throw "Quality gate failed" }
Get-Content docs/verification-local.md
```

Все четыре проверки должны быть PASS. Если исправляли код, повторите gate. Проверьте успешный и смешанный импорт. Убедитесь, что фикстуры — только синтетические; не заменяйте их реальными работами.

## 2. Создание пустого GitHub-репозитория

В GitHub → New repository: предлагаемое имя `python-lab1-submissions`, видимость Private (особенно если эталон не должен быть доступен студентам). Не добавляйте README, .gitignore или License при создании: они не нужны для первичного импорта уже готового проекта. Публичность и лицензию согласуйте отдельно. Используйте Git Credential Manager (авторизация через браузер) или SSH; токен не должен входить в URL.

## 3. Локальный Git и контроль содержимого

Команды выполнять в новой распакованной папке, не внутри чужого репозитория. Перед инициализацией проверьте, что `git rev-parse --show-toplevel` не указывает на другой проект.

```powershell
git init -b main
git status --short --untracked-files=all
```

При необходимости настройте имя автора и GitHub noreply email (возьмите точный адрес из Settings → Emails); не используйте служебный или личный email, если его раскрытие нежелательно. Настройка локальная:

```powershell
git config user.name "YOUR_GITHUB_NAME"
git config user.email "YOUR_GITHUB_NOREPLY_EMAIL"
```

Проверьте `.gitignore`; он защищает от случайного добавления `.venv`, `.env`, приватных файлов и сырых результатов. Но `.gitignore` не гарантирует отсутствие секретов в разрешённых файлах, особенно в трёх JSON/JSONL-фикстурах. Не используйте `git add .` без проверки; добавьте именно подготовленные файлы:

```powershell
git add .gitignore .gitattributes .editorconfig pyproject.toml README.md AI_USAGE.md
git add src/lab1 tests scripts .vscode .github/workflows
git add data/submissions.jsonl data/invalid_submissions.jsonl data/assignments.json
git add docs/stage-a-report.md docs/verification-initial.md docs/verification-local.md docs/github-publication.md
git status --short
git diff --cached --stat
git diff --cached
```

Проверьте каждый добавляемый файл: нет токенов, паролей, ключей, cookie, реальных ФИО, ID студентов, кодов их работ, корпоративных URL, локальных путей и вывода переменных окружения. В `.vscode` только переносимые настройки. Сырые coverage/JUnit, `.git` из других проектов, архивы и окружение не публикуются. Дополнительно можно запустить локальный secret scanner (например, Gitleaks) и проверить GitHub secret scanning, если функция доступна. Даже успешное сканирование не заменяет ручной проверки. Не отправляйте содержимое секретов внешним сервисам.

Если случайно добавили файл, снимите его с индекса до коммита (`git rm --cached -- <путь>`; для каталога `-r`), внесите нужное правило игнорирования и повторите проверку. Если действующий секрет когда-либо попал в историю/публичный remote, отзовите/замените его; удаления из последнего коммита недостаточно.

## 4. Коммит этапа А и публикация

Только после PASS и проверки индекса:

```powershell
git commit -m "feat: implement submission intake and validation stage-a"
git log -1 --oneline
git status --short
git remote add origin https://github.com/YOUR_GITHUB_NAME/python-lab1-submissions.git
git remote -v
git push -u origin main
```

Замените имя владельца и при необходимости имя репозитория. Если remote уже существует, проверьте его адрес вместо повторного добавления; не используйте `--force`. В GitHub откройте Actions и проверьте обе версии Python в CI. При ошибке исправьте её отдельным коммитом после полного локального gate. Не подменяйте историю и не выставляйте искусственные даты.

В задании сказано отметить промежуточный коммит суффиксом `stage-a`, поэтому сообщение заканчивается этим суффиксом. Дополнительно можно после успешного CI поставить отдельный аннотированный тег `lab-1-stage-a` и отправить только его:

```powershell
git tag -a lab-1-stage-a -m "Lab 1: stage A"
git push origin lab-1-stage-a
```

Итоговый тег `lab-1` создаём только после полного завершения этапа Б.

## 5. План следующих коммитов (не выполнены)

- A: `feat: implement submission intake and validation stage-a` — пакет, тесты, отчёт.
- B1: контракты анализатора/источника, тесты.
- B2: JSONL и in-memory источники, контрактные тесты и управление ресурсом.
- B3–B4: LengthAnalyzer и TemplateAnalyzer, тесты каждого.
- B5–B6: реестр, сервис анализа, тесты ошибок/evidence, третий анализатор для защиты.
- Итог: проверка, документация и отчёт; сообщение с суффиксом `lab-1`, тег `lab-1`.

На каждом шаге: небольшое законченное изменение, документация контрактов, тесты, реальный результат gate в коммите и CI. Не создавать коммиты задним числом. Эталон проекта можно держать закрытым до согласования с коллегой.
