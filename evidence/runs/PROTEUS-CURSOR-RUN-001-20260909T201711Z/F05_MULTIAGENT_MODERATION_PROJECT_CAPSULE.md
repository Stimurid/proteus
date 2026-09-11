# Project Capsule

> Generated context, not a source of truth. Verify cited files and current Git state before changing the project.

## Receiver protocol

1. Treat the project instructions and constraints below as binding.
2. Preserve existing dirty work: inspect it before editing or cleaning anything.
3. Reconcile any conflicting roadmap/current-state material by checking Git history and the cited source files.
4. Before implementation, read the listed files most relevant to the chosen change and run the narrowest documented check.

## Observed repository

- Project: `C:\projects\multiagent-moderation-env`
- Generated (UTC): `2026-09-11T13:54:23.983023+00:00`
- Approximate tracked/working source files (excluding common dependency/cache directories): 4,207
- Top level: `.claude_note_ps_cd.tmp`, `.codex_authoritative_xlsx_fix.patch`, `.codex_authoritative_xlsx_fix.stat.txt`, `.codex_authoritative_xlsx_fix.status.txt`, `.gitignore`, `00_README.md`, `00_README_PUT_IN_REPO_ROOT.md`, `01_environment_architecture_v1.md`, `02_object_model_v1.md`, `03_agent_contract_v1.md`, `04_pipeline_templates_v1.md`, `05_SAS_VIEW3_LAYOUT_CONTRACT_v1.0.json`, `05_mvp_scope_and_roadmap.md`, `06_codex_handoff_prompt_v1.md`, `07_seed_data_and_test_scenario.md`, `1003-1037-1-SM.pdf`, `AGENTS.md`, `AGENT_OBJECT_COREA.md`, `ARCHITECTURE_AND_RUNTIME_STACK.md`, `Agent 0.md`, `Agent A.md`, `Agent C.md`, `CHECKLIST_v2_3_SESSION_CONTROL_ACTIVE_CONTEXT.md`, `CODEX_AGENT_WORKING_RULES.md`, `COMBINED_CODEX_BASE.md`, `INTERFACE_SURFACES_PLAN.md`, `KAYONA_LIVE_VOICE_AGENT.md`, `MODULE GUIDE CORE 42.pdf`, `NEXT_PROMPT_TEMPLATE.md`, `NEXT_PROMPT_v1_0_SESSION_HUB_GROUP_WORKSPACE.md`, `Orc_agent_met.md`, `PLAN_v2_6_to_v2_9__AGENTIC_LLM_WORKSPACE.md`, `PROJECT_INTENT_AND_CURRENT_STATE.md`, `README.md`, `RECOVERY_REENTRY_MASTER_PLAN_v2_3_to_v3_4.md`, `ROADMAP_NEXT_STEPS.md`, `SAS_CANONICAL_REPOSITORY/`, `SAS_VIEW3_DRAFT_RENDER_PACKAGE_v1.0.zip`, `SAS_VIEW3_ENTITY_REGISTRY_v1.0.csv`, `SAS_VIEW3_FUNCTIONAL_PLACE_REGISTRY_v1.0.csv`, `SAS_VIEW3_MODEL_v1.0.json`, `SAS_VIEW3_POSITION_REGISTRY_v1.0.csv`, `SAS_VIEW3_RELATION_REGISTRY_v1.0.csv`, `SAS_VIEW3_REPRESENTATION_REGISTRY_v1.0.csv`, `STRATEGIC_FUNCTION_REGISTRY__DGTU_MODERATION_ENV (1).md`, `STRATEGIC_FUNCTION_REGISTRY__DGTU_MODERATION_ENV.md`, `UM_2019_4_132-141.pdf`, `UNI Kayona 4.pdf`, `UX_ROLES_ACTIVITIES_OBJECTS.md`, `VIEW1_OUTPUT/`, `_debug_exports/`, `_local_docs_pack/`, `_ПТО-Ядро V1.3_пресс.docx`, `agents/`, `artifacts/`, `backend/`, `deliverables/`, `docker-compose.yml`, `docs/`, `draft_zip_verify/` …

## Git working situation

Git root: `C:/projects/multiagent-moderation-env`
Branch: `main`
HEAD: `e52389098cb21d9d65a6998702253a7535e25872`
Working tree: dirty (64 status entries; untracked directories summarized)
Changed-path triage: 64 non-cache-shaped paths; 0 browser/cache-shaped paths (not assumed disposable).
Non-cache-shaped changed paths (porcelain; inspect before editing):
```text
M backend/app/routers/api.py
 M frontend/app/components/ProductShell.tsx
 M scripts/smoke_structured_source_pack_no_llm.py
?? .codex_authoritative_xlsx_fix.patch
?? .codex_authoritative_xlsx_fix.stat.txt
?? .codex_authoritative_xlsx_fix.status.txt
?? 05_SAS_VIEW3_LAYOUT_CONTRACT_v1.0.json
?? SAS_CANONICAL_REPOSITORY/
?? SAS_VIEW3_DRAFT_RENDER_PACKAGE_v1.0.zip
?? SAS_VIEW3_ENTITY_REGISTRY_v1.0.csv
?? SAS_VIEW3_FUNCTIONAL_PLACE_REGISTRY_v1.0.csv
?? SAS_VIEW3_MODEL_v1.0.json
?? SAS_VIEW3_POSITION_REGISTRY_v1.0.csv
?? SAS_VIEW3_RELATION_REGISTRY_v1.0.csv
?? SAS_VIEW3_REPRESENTATION_REGISTRY_v1.0.csv
?? VIEW1_OUTPUT/
?? _local_docs_pack/
?? artifacts/SAS_TRANSITION_VIEW_2/
?? artifacts/SAS_VIEW2_V2/
?? artifacts/_capture_relational_v294a.js
?? artifacts/_prod_verify_sessions.sh
?? artifacts/group_only_prompt_preview_batch_1780050107090.json
?? artifacts/prod_ui_loop_2026-05-17T13-27-43-799Z/
?? artifacts/prod_ui_loop_2026-05-17T13-29-08-640Z/
?? artifacts/prod_ui_loop_2026-05-17T13-32-15-109Z/
?? artifacts/tmp_prod_scenario_check.py
?? artifacts/tmp_prod_upload_path_check.py
?? artifacts/ui_interfaces_pack_relational_canvas_v2_9_4a_2026-05-16T22-04-39.zip
?? artifacts/ui_interfaces_pack_relational_canvas_v2_9_4a_2026-05-16T22-04-39/agent-runtime.png
?? artifacts/ui_interfaces_pack_relational_canvas_v2_9_4a_2026-05-16T22-04-39/agent-workspace.png
?? artifacts/ui_interfaces_pack_relational_canvas_v2_9_4a_2026-05-16T22-04-39/rpr.png
?? artifacts/ui_interfaces_pack_v2_9_4b_gap_closure_2026-05-17T09-16-02.zip
?? artifacts/ui_interfaces_pack_v2_9_4b_gap_closure_2026-05-17T09-16-02/
?? artifacts/ui_interfaces_pack_v2_9_4c_semantic_ux_2026-05-17T14-27-05.zip
?? artifacts/ui_interfaces_pack_v2_9_4c_semantic_ux_2026-05-17T14-27-05/
?? deliverables/
?? draft_zip_verify/
?? fix_redownload.ps1
?? frontend/capture_ui_shell_pack.js
?? frontend/tmp_prod_ui_loop.js
?? frontend/tsconfig.tsbuildinfo
?? moderbober-clean2-gitdir/
?? moderbober-clean4-gitdir/
?? moderbober_state_coherence_fix.patch
?? moderbober_state_coherence_fix.stat.txt
?? moderbober_state_coherence_fix.status.txt
?? outputs/
?? recovery_structured_source_pack.patch
?? scripts/smoke_state_coherence_v2_9_6_5_p0.ps1
?? scripts/smoke_ui_shell.ps1
?? tmp/
?? tmp_candidate_db_verify.py
?? tmp_candidate_keys.py
?? tmp_group_only_inspect.py
?? tmp_group_only_post.py
?? tmp_group_only_verify.py
?? tmp_group_pack_get.py
?? tmp_group_semantic_post.py
?? tmp_group_verify.py
?? tmp_inspect_semantic_candidate.py
?? tmp_verify_semantic_state.py
?? tmp_workbench_main_panel_block.txt
?? tmp_workbench_refactor.py
?? tmp_workbench_right_rail_block.txt
```

### Recent commits

```text
e523890 2026-06-09 Ensure authoritative XLSX sheet coverage in semantic source pack
faa9301 2026-06-09 Preserve structured source bodies for semantic packs
ff9bf65 2026-06-04 narrow semantic participant row detection
29743bd 2026-06-04 tighten semantic participant accounting validation
8365e15 2026-06-04 strengthen semantic participant extraction guard
ef72e2f 2026-06-04 expand semantic run trace audit logging
1051514 2026-06-04 add semantic run trace export
bd585d1 2026-06-02 add semantic group source pack extraction path
```

## Runtime / build manifests

### `backend/requirements.txt`

```text
fastapi==0.115.6
uvicorn[standard]==0.32.1
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
pydantic==2.10.3
alembic==1.14.0
python-multipart==0.0.19
pypdf==5.9.0
python-docx==1.2.0
python-pptx==1.0.2
openpyxl==3.1.5
```

### `frontend/package.json`

```text
{
  "name": "moderation-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev -H 0.0.0.0 -p 3000",
    "build": "next build",
    "start": "next start -p 3000"
  },
  "dependencies": {
    "next": "14.2.25",
    "react": "18.3.1",
    "react-dom": "18.3.1"
  },
  "devDependencies": {
    "typescript": "5.6.3",
    "@types/node": "22.10.1",
    "@types/react": "18.3.12"
  }
}
```

### `docker-compose.yml`

```text
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: moderation_env
      POSTGRES_USER: postgres
      POSTGRES_<REDACTED>
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+psycopg2://postgres:postgres@db:5432/moderation_env
      DGTU_ENABLE_DEV_CLEANUP: ${DGTU_ENABLE_DEV_CLEANUP:-true}
    ports:
      - "8000:8000"
    depends_on:
      - db
    volumes:
      - ./backend:/app
      - ./agents:/app/agents:ro

  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/api
    command: ["sh", "-lc", "unset CI; npm run dev"]
    ports:
      - "3000:3000"
    depends_on:
      - backend

  worker:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+psycopg2://postgres:postgres@db:5432/moderation_env
      DGTU_WORKER_ENABLED: ${DGTU_WORKER_ENABLED:-false}
      DGTU_WORKER_BACKEND_URL: ${DGTU_WORKER_BACKEND_URL:-http://backend:8000}
      DGTU_WORKER_POLL_SECONDS: ${DGTU_WORKER_POLL_SECONDS:-10}
      DGTU_WORKER_INCLUDE_SMOKE: ${DGTU_WORKER_INCLUDE_SMOKE:-false}
      DGTU_WORKER_MAX_TICKS_PER_CYCLE: ${DGTU_WORKER_MAX_TICKS_PER_CYCLE:-1}
      DGTU_WORKER_MAX_EXECUTION_REQUESTS_PER_CYCLE: ${DGTU_WORKER_MAX_EXECUTION_REQUESTS_PER_CYCLE:-10}
      DGTU_WORKER_RUN_PROVIDER_EXECUTION: ${DGTU_WORKER_RUN_PROVIDER_EXECUTION:-true}
    depends_on:
      - backend
      - db
    volumes:
      - ./backend:/app
      - ./agents:/app/agents:ro
    command: ["python", "-m", "app.workers.agent_loop_worker"]

volumes:
  pgdata:
```

## Project instructions: `AGENTS.md`

# AGENTS

Before changing deploy, production checks, Caddy, LLM runtime, or manual-test gates, read:

- `docs/ops/PRODUCTION_TOPOLOGY_AND_GATES.md`

Before changing `/moderator`, `/workbench`, `/rpr`, Kayona Dock, task strips, timelines, agent buttons, report/plenary/canvas UX, read:

- `docs/product/MODERATOR_COCKPIT_INTERFACE_LAW_v0_1.md`

Mandatory rules:

- Moderator Cockpit must be canvas-first, not runtime-first.
- Kayona Dock must be resizable and placeable right or bottom.
- Main app layout must not become a scrolling landing page.
- ModerBober product URL is `https://moderbober.mindkampf.ru/`.
- `81.26.176.248` is shared server/debug only (SSH/server-local checks), not product URL.
- Do not use bare IP as ModerBober product URL.
- Do not change `ANTHROPIC_MODEL` unless explicitly requested.
- Do not expose secrets in code, logs, status output, or frontend payloads.
- Manual testing is blocked while LLM gate is `mock`/`missing_config`/opaque `provider_error`.

## Operations constraints: `docs/ops/PRODUCTION_TOPOLOGY_AND_GATES.md`

# ModerBober Production Topology And Gates

## A. Server topology

- `81.26.176.248` = shared production server / SSH / debug host.
- Known project roots on this server:
  - `/opt/moderbober`
  - `/opt/quinta`
  - `/opt/whitecrow`
- Caddy/subdomain routing is shared across projects; avoid changes that can break other projects.

## B. Product URLs

- ModerBober canonical production URL:
  - `https://moderbober.mindkampf.ru/`
- Quinta:
  - `https://quinta.mindkampf.ru/`
- WhiteCrow:
  - same shared server; exact subdomain/route must be verified before using.
- Rule:
  - never treat bare IP as ModerBober product URL.

## C. Check discipline

- Browser/manual product checks:
  - use `https://moderbober.mindkampf.ru/`
- SSH/deploy/status checks:
  - use `81.26.176.248` via
  - `C:\Windows\System32\OpenSSH\ssh.exe -l deploy 81.26.176.248 ...`
- Server-local diagnostics:
  - `docker exec` / internal endpoint / `/opt/moderbober/bin/*`
- Public API checks may be auth-gated or redirected.
  - Do not treat `308` / `401` at edge as product failure without server-local verification.

## D. Manual-test gates

Manual test of real DGTU archive is blocked unless:

- production URL opens;
- Russian UI encoding is normal;
- clean test/demo session works;
- upload/intake hardening is active;
- reset/archive is active for test sessions;
- LLM status is one of:
  - `live_ok`
  - or explicit deterministic/mock mode accepted as a waived non-live test;
- opaque `provider_error` is not acceptable;
- `provider_error` must include:
  - `error_class`
  - `sanitized_error_message`
  - `http_status` if available
  - `failing_stage`
  - verification method.

## E. LLM production gate

- Runtime env file path:
  - `/opt/moderbober/secrets/llm.env`
- Backend must see:
  - `ANTHROPIC_API_KEY` as boolean presence only;
  - `ANTHROPIC_MODEL` as configured model name.
- Frontend must not receive API key.
- UI badge must be clickable and show diagnostics/settings.
- `provider_error` without class/message fails the gate.
- `mock` is not an acceptable silent fallback when live provider config exists.
- Server-local diagnostics must work behind public auth gate.
- Never leak API key in git/logs/frontend/status output.

## F. Current known LLM status (as of 2026-05-27)

- Env is wired into backend runtime.
- Model is preserved from env; do not switch model automatically.
- Current live smoke result:
  - `provider_error / auth_error / HTTP 403`
- Next investigation:
  - Anthropic auth/access/request issue; do not start with model switching by default.

## Product law: `docs/product/MODERATOR_COCKPIT_INTERFACE_LAW_v0_1.md`

# ModerBober Moderator Cockpit Interface Law v0.1

Дата фиксации: 2026-05-17
Статус: рабочая спецификация для Codex / продуктовый интерфейсный закон
Назначение: прекратить деградацию интерфейса МодерБобра в CRM, Kubernetes-панель, файловый архив, smoke-board или runtime console; вернуть проект к основной логике — поддержке модераторской и проектной работы на 2–3 день стратегической / проектно-проблемной сессии.

## 0. Главная формула

МодерБобер — не RAG по материалам, не чат-бот, не CRM, не dashboard backend-сущностей и не интерфейс наблюдения за agent runs.

МодерБобер — событийно-онтологическая среда поддержки модераторской и проектной работы на сессии.

Главный объект продукта — не файл, не чат, не агентный запуск, не review item, не лог и не endpoint.

Главный объект продукта — изменяющееся состояние группы:

- объект работы;
- тема;
- проблема;
- ситуация;
- цель;
- проектное решение;
- эффект / критерии;
- оргпроект;
- план действий;
- риски / ограничения;
- основания / аргументы / доказательства;
- вопросы;
- критика;
- поручения;
- позиции участников;
- самоопределение;
- групповая динамика;
- линия докладов;
- ответ на критику;
- движение по арке сессии.

Главная поверхность модератора должна строиться вокруг проектного канваса группы.

Любая поверхность, которая главным объектом делает файлы, таблицы, agent runs, provider status, smoke, raw logs, execution requests или backend entities, является backstage и не должна быть основным интерфейсом модератора.

## 1. Текущий рабочий контекст: второй-третий день сессии

Проектируем не подготовительный день, не загрузку материалов, не настройку провайдеров и не создание первой сессии.

Целевой сценарий для Moderator Cockpit — второй-третий день программы:

- сессия уже создана;
- группы уже есть;
- материалы уже загружены;
- расписание известно;
- были предыдущие групповые работы;
- были доклады;
- была критика;
- есть задачи на доработку;
- есть текущий день и текущий такт работы;
- модератору нужно не «настроить систему», а вести группу и удерживать содержание;
- РПР нужно видеть движение всех групп и точки вмешательства;
- группа работает не в realtime voice/ASR режиме, а через уже существующие материалы и периодические сборки.

В текущей фазе НЕ предполагается:

- live transcription на ходу;
- голосовой интерфейс;
- постоянное распознавание групповой работы в реальном времени;
- автоматическое переписывание состояния группы без review;
- показ runtime-debug модератору как основного интерфейса.

В текущей фазе предполагается:

- работа с результатами предыдущих тактов;
- работа с уже загруженными транскриптами, докладами, материалами;
- диалог с Кайоной внутри контекста текущей поверхности;
- генерация заметок / сборок / планов доклада;
- сохранение удачных ответов ЛЛМ как заметок или дельт в материалы/канвас;
- ручной или полуавтоматический review;
- периодические сборки внутри такта.

## 2. Главный интерфейсный закон

Moderator Cockpit = Canvas-first app screen без page scroll, где центральный канвас группы показывает состояние проекта и логические напряжения; вокруг него тонкие операционные слои — позиции, участники, доклад, задачи, timeline, материалы, РПР-установка и Kayona Dock; все генеративные действия являются настраиваемыми agent commands, но в первом слое представлены как простые рабочие операторы модератора.

Не «страница сайта».
Не «лендинг».
Не «таблица карточек».
Не «панель Kubernetes».
Не «все сущности backend на одном экране».

Это приложение с фиксированным рабочим полем.

Основной layout должен помещаться в экран без прокрутки страницы. Детальные области могут иметь внутреннюю прокрутку, но главный layout не должен превращаться в длинный сайт.

Формула:

- нет page scroll у основного cockpit;
- есть resizable panels;
- есть раскрытия / шторки / модальные рабочие области;
- есть внутренние scroll у длинных текстов, расшифровок, ответов Кайоны и source lists;
- основной canvas всегда остаётся главным объектом.

## 3. Центральный канвас

В центре экрана находится проектный канвас группы.

Он похож не на таблицу и не на dashboard, а на карту вроде Osterwalder canvas: набор полей/карточек, между которыми видны связи.

Базовые блоки канваса:

1. Тема / объект работы
2. Проблема
3. Ситуация / модель «как есть»
4. Цель
5. Проектное решение
6. Эффект / критерии
7. Оргпроект
8. План действий
9. Риски / ограничения
10. Оргпроект как вложенный блок: роли, процессы, ресурсы, коммуникации
11. Вложенные элементы оргпроекта
12. Вложенные элементы оргпроекта
13. Вложенные элементы оргпроекта
14. Основания / аргументы / доказательства по каждому блоку
15. Общий набор содержательных вопросов и задач группы

В каждом блоке на обзорном слое виден один главный тезис, сформированный на основе материалов и принятых состояний группы.

Источники тезиса:

- расшифровки групповой работы;
- предыдущие доклады;
- критика пленара;
- постановка дня;
- методические консультации;
- принятые заметки модератора;
- сохранённые ответы Кайоны;
- принятые canvas deltas;
-

[Excerpt truncated at 5,000 characters; inspect MODERATOR_COCKPIT_INTERFACE_LAW_v0_1.md before relying on omitted detail.]

## Project overview: `README.md`

# Multiagent Moderation Environment (Milestone 1)

Typed substrate MVP for:
- workspace/session/group/event lifecycle
- transcript ingestion (immutable raw text)
- fragment generation
- mock extraction (claim/question/task candidates)
- review queue with accept/reject/revise
- provenance links
- draft project state snapshots
- kernel state snapshots (`snapshot_type` + `payload`)
- pipeline and agent run records

## Stack
- Backend: FastAPI + SQLAlchemy + Alembic
- Frontend: Next.js + TypeScript
- DB: PostgreSQL 16
- Runtime: Docker Compose

## Start
```bash
docker compose up --build
```

Services:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

## Seed Scenario
1. Open `/workspaces` and click **Load seed**.
2. Open API docs (`/docs`) or UI routes to continue flow.
3. Go to `/events/{event_id}/transcript` (seed already has transcript).
4. Go to `/events/{event_id}/fragments` and click auto-generate.
5. Go to `/events/{event_id}/analytical-units` and run mock extraction.
6. Go to `/review` and accept/reject units.
7. Go to `/groups/{group_id}/project-state` and generate a draft from accepted units.
8. Inspect created kernel snapshots via `/api/groups/{group_id}/state-snapshots`.
9. Check `/pipelines` and `/agent-runs`.
10. Run full kernel smoke: `powershell -ExecutionPolicy Bypass -File .\docs\smoke\smoke_kernel_mvp.ps1`

## Key API Routes
- `POST /api/workspaces`
- `POST /api/programs`
- `POST /api/sessions`
- `POST /api/groups`
- `POST /api/events`
- `POST /api/transcripts`
- `POST /api/events/{event_id}/fragments/auto`
- `POST /api/pipelines/mock-extract`
- `POST /api/events/{event_id}/run-mock-extraction` (kernel alias)
- `GET/POST /api/review`
- `POST /api/analytical-units/{unit_id}/review` (kernel alias)
- `POST /api/project-state/from-accepted`
- `POST /api/groups/{group_id}/build-state-snapshot` (kernel alias)
- `GET /api/state-snapshots`
- `GET /api/groups/{group_id}/state-snapshots`
- `POST /api/seed/load`

## Smoke Validation
- Full reproducible path and commands: [KERNEL_MVP_SMOKE.md](/C:/projects/multiagent-moderation-env/docs/smoke/KERNEL_MVP_SMOKE.md)

## Principles Enforced
- Raw transcript text is stored as source material and never overwritten.
- Analytical units are candidates first; acceptance is explicit review.
- Provenance links are created from each extracted unit to source fragment.
- Typed relational substrate is primary; no embedding-first/RAG foundation.
- Mock extraction only validates workflow mechanics, not NLP quality.

## Current-state carrier: `PROJECT_INTENT_AND_CURRENT_STATE.md`

# Project Intent and Current State

## Рабочее имя

`multiagent-moderation-env`

Смысловой проект: ДГТУ Moderator / multiagent moderation environment.

## Что строится

Строится не “чат-бот” и не “панель с метриками”. Строится операционная среда для проектно-модерационной сессии, где можно:

- создать или открыть сессию;
- завести группы и участников;
- загрузить материалы: списки, презентации, расшифровки, заметки, артефакты групповой работы;
- запустить обработку материалов агентами;
- получить фрагменты, аналитические единицы, проблемные формулировки, понятийные узлы, предупреждения;
- видеть состояние каждой группы и всех групп вместе;
- удерживать таймлайн событий;
- собирать отчёты;
- строить очередь действий для модератора;
- давать РПР обзор движения групп;
- подключить голосовой/командный слой Kayona Live;
- сохранять воспроизводимую историю действий и решений.

Проект должен поддерживать живую сессию, а не только постфактум-анализ. Поэтому важны быстрые рабочие поверхности, минимальный когнитивный шум, ясные статусы и возможность быстро запускать пайплайны.

## Что уже реализовано локально

На момент фиксации контекста последняя известная локальная линия коммитов:

- `d4a1d02` — bootstrap executable dgtu moderator kernel mvp
- `10c9acc` — harden moderator workbench ui for dgtu smoke flow
- `bd9a4b3` — add concept passport ontology workbench v0
- `ddf11f7` — generalize concept passport correction flow v0.1
- `dc29dea` — add moderator workbench launcher v0
- `670e3eb` — add deterministic group session report draft v0
- `3c4e601` — add agentic context and research runtime v0.1
- `2afce1e` — add role surfaces provider budget recording runtime v0.1
- `d481e3c` — add agent worker event loop runtime v0.1
- `143a973` — harden agent worker event loop runtime v0.2
- `6606065` — add runtime hygiene smoke isolation scoped views v0.3
- `1ba4601` — add provider execution boundary v0.4
- `a77bae2` — add worker service continuous runtime v0.5
- `3b7fdf5` — add agent action executor domain reducers v0.6
- `8156518` — add moderator action queue human review control plane v0.7
- `2ab829d` — end-to-end moderator session flow v0.8
- `201c7e1` — add moderator console operator cockpit v0.9
- `8348374` — demo readiness / export layer

Если фактический git log отличается, считать git log источником истины, но эту последовательность использовать как смысловую карту.

## Что уже есть по слоям

### Kernel / domain moderation

Есть базовый доменный слой: workspace, program, session, group, event, transcript, fragment, analytical units, review decisions, state snapshots, provenance links.

### Concept passport

Есть слой понятий и коррекции понятий: problem concept, resource deficit, negative/positive examples, scope, challenge/update actions, impact preview.

### Reports

Есть deterministic group session report draft: отчёт по группе на основе имеющихся данных, с placeholder-ами и warnings, если данных мало.

### Agentic runtime

Есть AgentRun / ResearchRequest / EvidenceItem / ResearchMemo и связанные mock-эндпоинты.

### Role / provider / recording runtime

Есть поверхности и объекты для ролей, resource profiles, usage ledger, recording/transcription mock jobs.

### Agent Worker Event Loop

Есть event-driven runtime через StateSnapshot:

- AgentEvent
- AgentTrigger
- AgentActivation
- AgentState
- AgentHandoff

Есть tick / run-pending, trigger matching, activation creation, dedupe, smoke tagging.

### Runtime hygiene

Default API views исключают smoke. Есть `include_smoke`, `test_run_id`, scoped runtime filters, runtime overview, dev cleanup smoke.

### Provider Execution Boundary

Есть executable mock boundary: ProviderCapability, ProviderPolicy, ExecutionRequest, ExecutionResult, guard-check, mock-execute, usage ledger, blocking live/non-mock providers.

### Worker Service

Есть continuous worker container/service, который вызывает health, seed-default, tick, run-pending, provider boundary, heartbeat/status.

### Agent Action Executor / Domain Reducers

Есть deterministic reducers, превращающие AgentRun / AgentActivation в доменные артефакты:

- `content_extractor`
- `concept_guardian`
- `project_state_compiler`
- `report_synthesizer`
- `research_router`
- `moderator_copilot`

### Moderator Action Queue / Human Review Control Plane

Есть очередь модератора: build, approve, reject, defer, request-revision, resolve. Решения marker-based и non-destructive.

### Moderator Session Flow / Console

Есть end-to-end deterministic session flow и Operator Cockpit на `/moderator`.

### Demo readiness/export

Есть слой demo readiness, reset-demo, run-demo, export, acceptance.

## Главное ограничение

До отдельного решения не включать реальные внешние вызовы:

- no real LLM;
- no real web search;
- no real n8n;
- no real transcription provider;
- no new database tables без явного решения;
- smoke isolation сохранять;
- секреты в payload не хранить.

## Текущий риск

Проект стал технически насыщенным, но UX-замысел начал отрываться от живых сценариев сессии. Следующий этап должен не просто добавлять endpoints, а привести рабочие поверхности к базовым сценариям:

1. быстрый старт сессии;
2. рабочая страница группы;
3. РПР-радар всех групп;
4. модераторская консоль во время групповой работы;
5. материалы дня / вечерняя сборка;
6. Kayona Live как командный/голосовой слой.

## v1.5 update
Deterministic Materials Library layer added: material records, bundles, processing markers, lightweight keyword search/ask, and cross-surface material panels (workbench/moderator/rpr/group-live/agent-runtime).

## v1.6 update
Session Setup / Agent Launch Orchestrator added with deterministic setup-readiness and launch-plan endpoints, plus /session-setup UI surface.

## v1.7 Operator Journey Navigation
Added operator-journey context, role-entry, surface-map, next-action, and demo-progress spine for coherent cross-surface navigation (bounded, deterministic, smoke-safe).

## v1.8 Demo UX Walkthrough
Added a deterministic operator-facing demo walkthrough/acceptance layer with step progress, per-surface acceptance, and markdown reporting over existing v1.0-v1.7 surfaces.

## v1.9 Bulk Material Intake
Added operator-facing bulk intake gate for messy multi-source materials (files, links, text, late uploads) with deterministic triage, assignment, bundle, process, and readiness flows.

## v1.9.2 Demo Rehearsal / Operator Path Hardening
- Added deterministic /api/demo-rehearsal/* orchestration wrappers over existing setup/intake/moderator/rpr/group-live/kayona surfaces.
- Focus: one executable operator demo path with idempotent step markers and markdown report.


## v2.0 Russian Unified Operator Workspace
- Unified Russian-language operator-facing surfaces across workbench/setup/material-intake/moderator/rpr/group-live/demo.
- Technical runtime page is explicitly marked as appendix/debug only.


## v2.1 update
Visual unified product interface — shared ProductShell with Russian nav, full-page CSS design system, consistent surfa

[Excerpt truncated at 7,000 characters; inspect PROJECT_INTENT_AND_CURRENT_STATE.md before relying on omitted detail.]

## Current plan referenced by roadmap: `RECOVERY_REENTRY_MASTER_PLAN_v2_3_to_v3_4.md`

# Recovery Re-Entry Master Plan (v2.3 -> v3.4)

Starting point:
- Stable recovery baseline commit: `07a81d7`
- Intent: session moderation operating environment with traceable memory.

Execution policy:
- Do not reattempt "big v3.0 all-at-once".
- One subversion = one closed working loop + targeted smoke + `smoke_changed_fast`.
- No speculative rebuild loops.
- No git plumbing.

Core product loop:
1. Session
2. Group
3. Day/Stage/Event
4. Material/Transcript
5. Fragment
6. AnalyticalUnit
7. ReviewDecision
8. GroupProjectState
9. Report/Briefing/ResearchRequest
10. New analytical memory

Layer model:
- Session contour: active session/group/day/stage context.
- Materials contour: scoped artifacts with status, authority, provenance.
- Agents/prompts contour: managed Agent Specs + Prompt Packs + Context Packs.
- LLM/provider/safety contour: explicit live/mock mode, visible fallback, no key leakage.

Roadmap order:
1. v2.3 Session Control / Active Context
2. v2.4 Material Desk / Bulk Intake working contour
3. v2.5 LLM Settings / Provider Adapter / visible fallback
4. v2.6 Prompt Pack + Agent Spec registry
5. v2.7 Run Recipes + Context Packs
6. v2.8 First real LLM agent: Analytical Extraction
7. v2.9 Project State Compiler + Moderator Review
8. v3.0 Session Schedule / Program Timeline
9. v3.1 Group Workspace + Group Live
10. v3.2 Evening Synthesis + Report Studio
11. v3.3 Search/RAG/Evidence/Research Desk
12. v3.4 Voice Kayona

Current implementation focus:
- v2.3 Session Control / Active Context only.
- No LLM settings changes.
- No prompt registry changes.
- No schedule timeline expansion.

## v2.5.1 hotfix note
- Distinguish strictly between session program schedule and activity feed.
- Material intake accepts messy mixed clipboard blobs and drag/drop placeholders in active session.

- v2.6 ����������: LLM Processing Agents for Active Session Materials (bounded, fail-soft, review-required).

## Roadmap / next work: `ROADMAP_NEXT_STEPS.md`

# Roadmap Next Steps

## Recovery re-entry control note

- Stable baseline after runtime break: `07a81d7`.
- Master plan source of truth: `RECOVERY_REENTRY_MASTER_PLAN_v2_3_to_v3_4.md`.
- Immediate implementation step: `v2.3 Session Control / Active Context`.
- Execution rule: one closed loop per subversion + targeted smoke + `smoke_changed_fast`.
- Current loop in progress: `v2.4 Active Session Material Desk` (active-session scoped bulk add, classification, and deterministic mock analysis).

## Где мы находимся

Текущий проект прошёл фазу backend/runtime MVP:

- kernel;
- concept passport;
- reports;
- agent runtime;
- provider/resource/recording mock;
- event loop;
- smoke isolation;
- provider boundary;
- worker service;
- domain reducers;
- human review queue;
- moderator session flow;
- moderator console;
- demo readiness/export.

Теперь нельзя продолжать бесконечно наращивать endpoints без UX-центрирования. Следующие шаги должны связать runtime с живыми сценариями сессии.

## Стратегическая линия

Движение дальше:

1. Session Hub / Group Workspace foundation
2. Materials Intake / Session Folder Model
3. Kayona Live command layer
4. RPR Radar
5. Day Assembly / Evening Room
6. Participant-facing group mode
7. Real recording/transcription integration
8. Real RAG/vector storage
9. Deployment/push/repo hygiene

## v1.0 Session Hub / Group Workspace

Цель: создать нормальный входной и групповой интерфейс.

### Backend

Добавить или обобщить endpoints:

- `GET /api/session-hub/overview`
- `POST /api/session-hub/create-session`
- `POST /api/session-hub/open-or-ensure-demo`
- `POST /api/session-hub/configure-groups`
- `GET /api/groups/{group_id}/workspace`
- `GET /api/groups/{group_id}/timeline`
- `GET /api/groups/{group_id}/materials`
- `GET /api/groups/{group_id}/people-dynamics`
- `GET /api/groups/{group_id}/concept-map`
- `GET /api/groups/{group_id}/project-state-summary`

Если можно, реализовать wrappers над существующими сущностями без миграций.

### UI

- `/workbench` превратить в Session Hub.
- Добавить/создать `/groups/[group_id]/workspace`.
- Оставить `/moderator` как cockpit, но связать его с выбранной группой.
- `/agent-runtime` оставить advanced.

### Smoke

- создать сессию;
- создать несколько групп;
- загрузить/создать mock materials;
- открыть group workspace;
- увидеть timeline/materials/state/concept map placeholders;
- smoke_all pass.

## v1.1 Materials Intake / Session Folder Model

Цель: привести материалы к нормальной операционной модели.

### Нужно

- папки/пакеты материалов;
- типы материалов: transcript, slide, doc, participant list, photo, note, artifact;
- связь material → session/group/event;
- processed/unprocessed status;
- запуск обработки по материалу/папке;
- видимость в Group Workspace и Session Hub.

### Без реальных внешних API

Пока mock/file metadata/text intake. Реальное чтение Google Docs, Telegram, audio — позже.

## v1.2 Kayona Live Command Layer

Цель: добавить верхний командный слой.

### Сначала text-first

- command bar в Session Hub / Group Workspace / Moderator / RPR Radar;
- endpoints `/api/kayona/...`;
- command types: answer/retrieve/run/guide;
- deterministic/mock command handling;
- запуск существующих pipelines;
- command journal;
- provenance.

### Потом voice

Реальный микрофон и speech-to-text после стабилизации command layer.

## v1.3 RPR Radar

Цель: поверхность руководителя проектной рамки.

### Нужно показать

- все группы;
- статус движения;
- понятийную согласованность/расхождение;
- риски;
- handoffs;
- вопросы к пленару;
- day synthesis.

## v1.4 Day Assembly / Evening Room

Цель: вечерняя сборка дня.

### Нужно

- необработанные материалы;
- сводка по группам;
- отчёты;
- вопросы на завтра;
- research gaps;
- export.

## v1.5 Participant Mode

Цель: безопасный режим для группы/участников.

### Нужно

- group-facing page;
- simplified timeline;
- materials;
- current task;
- idea/concept map;
- Kayona group mode;
- no private moderator warnings.

## v1.6 Real Recording / Transcription

Только после v1.0–v1.2.

### Нужно

- browser recording;
- upload audio;
- transcription job;
- provider boundary;
- transcript versioning;
- real provider disabled by default unless explicitly enabled.

## v1.7 Real RAG / Vector Store

Только после нормализации materials.

### Нужно

- chunking;
- embeddings;
- vector store;
- retrieval endpoint;
- citations/provenance;
- Kayona RAG integration.

## v1.8 GitHub / deployment hygiene

Пока можно продолжать локальные коммиты. Но административно нужно:

- настроить remote;
- проверить autopush;
- не терять локальные коммиты;
- иметь `PROJECT_CONTEXT` files in repo root;
- smoke before commit;
- no push without known remote unless user explicitly configured.

## Smoke iteration rule

- For normal iteration, run targeted smoke plus `scripts/smoke_changed_fast.ps1`.
- Use bounded `smoke_all` as a final acceptance pass, not as a long blocking loop.

- v1.5 Materials / Files / RAG-ready Library: deterministic material rec

[Excerpt truncated at 5,000 characters; inspect ROADMAP_NEXT_STEPS.md before relying on omitted detail.]

## What to inspect before changing code

- The mandatory instruction files above, plus any documents named by them for the surface you will change.
- The current diff for every dirty path that overlaps your task; do not assume it is disposable.
- The owning backend/frontend module and its nearest existing smoke or test script.
- Deployment/production gates before touching deploy, Caddy, provider configuration, or a manual-test gate.

## Capsule boundaries

- This is a compact index and excerpts, not an archive, a transcript, or a substitute for source inspection.
- It intentionally omits untracked file contents, Git diff bodies, binaries, dependency trees, and environment files.
- Common credential-shaped values are redacted heuristically; never treat a capsule as a safe place for secrets.
- `current` and `next` claims remain attributed to the included documents and Git observation; documents can be stale or conflict.

## Included source map

- `AGENTS.md`
- `docs/ops/PRODUCTION_TOPOLOGY_AND_GATES.md`
- `docs/product/MODERATOR_COCKPIT_INTERFACE_LAW_v0_1.md`
- `README.md`
- `PROJECT_INTENT_AND_CURRENT_STATE.md`
- `RECOVERY_REENTRY_MASTER_PLAN_v2_3_to_v3_4.md`
- `ROADMAP_NEXT_STEPS.md`
