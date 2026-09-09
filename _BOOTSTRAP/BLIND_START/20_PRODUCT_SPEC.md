PROTEUS — ОПИСАНИЕ ПРОДУКТА v0.1

СТАТУС  
Рабочая продуктовая спецификация первого воплощения. Этот документ описывает, что должно быть построено, какие способности изделие должно давать coding-agent, как оно устанавливается в host и как проверяется.

1\. НАЗНАЧЕНИЕ  
Proteus — переносимая когнитивная инфраструктура для coding-agent, которая делает длительную работу устойчивой между сессиями, проектами и впоследствии между разными host-средами.

Главная практическая задача первой версии: дать Cursor долговременную рабочую непрерывность, накопление правил и навыков, project reentry, checkpoint/handoff, безопасное самообновление и защиту LLM-native механизмов от смысловой редукции при реализации.

2\. ПЕРВЫЙ HOST  
Первый целевой host: Cursor.

Первая версия должна использовать нативные поверхности Cursor настолько далеко, насколько они реально пригодны: project rules, global/user instructions, skills, hooks, commands, agents, MCP и другие поддерживаемые механизмы. Конкретный набор определяется инспекцией установленной версии Cursor.

3\. ФОРМЫ ПРОДУКТА  
Proteus должен существовать минимум в трёх формах.

A. IDEAL / PORTABLE BODY  
Версионированный исходный репозиторий и build/install logic, из которых можно воспроизвести host-воплощение. Носитель может включать plugin/package, MCP, scripts, host adapters, rules/skills/hooks templates, tests, migration/rollback logic. Формат определяется работой, а не заранее выбранной модой.

B. HOST INCARNATION  
Реально установленное состояние в Cursor: системные и проектные инструкции, hooks, skills, MCP/config, runtime state, markers, receipts и иные поверхности, созданные из ideal body.

C. PROJECT MOUNT  
Связь Proteus с конкретным рабочим проектом. Mount даёт host доступ к project identity, current goals, backlog, decisions, unresolved, relevant rules, authoritative carriers и checkpoint state, не копируя без необходимости весь corpus.

4\. БАЗОВЫЕ СПОСОБНОСТИ ПРОДУКТА  
4.1 Persistent orientation  
После новой сессии, restart или compaction Cursor должен получать устойчивые agent/project instructions без ручного восстановления человеком.

4.2 Project reentry  
По команде «работай с Paideia/Hermes/Tinkuy/другим проектом» Proteus должен идентифицировать проект, найти его локальные и облачные carriers, восстановить current/frontier и продолжить работу.

4.3 Project bootstrap  
Для нового проекта Proteus должен создать минимальный durable project corpus и project-facing инструкции. Для старого проекта — сначала обследовать существующее состояние и встроиться без разрушения чужой структуры.

4.4 Checkpoint / handoff  
Перед session end, compaction, длинным разрывом или передачей другому agent/body Proteus сохраняет завершённое, решения, незавершённость, frontier, состояние тестов и working tree.

4.5 Learning from corrections  
Существенная коррекция пользователя фиксируется как evidence, классифицируется по scope и способна повлиять на будущие независимые сессии после проверки.

4.6 Provenance and authority  
Proteus хранит происхождение правил, решений, воспоминаний, конфликтов и синхронизаций. Он различает current authority, historical evidence, donor material и собственный inference.

4.7 UNKNOWN preservation  
Система обязана уметь хранить неопределённость и противоречивые версии. Она не закрывает дырки дефолтами только ради удобства кода.

4.8 Anti-reduction / organ preservation  
Если проект содержит содержательный LLM-native орган, Proteus должен предотвращать его бесследную замену keyword/if-then/state-machine/graph логикой, когда такая замена уничтожает исходную способность.

4.9 Safe host mutation  
Изменения Cursor/config/project surfaces проходят baseline, diff, test, verification, receipt и rollback.

4.10 Parallel run safety  
Параллельные чаты/run должны сохранять собственные baseline и журналы и не перетирать deep/current state друг друга без reconciliation.

4.11 Global observability  
Независимо от открытого проекта Proteus должен логировать жизненный цикл Cursor-agent, project/workspace, model/session/run, значимые tool/file/test события, stop/error/compaction и формировать внешний active-run status. Другой агент с доступом к Drive должен понимать ход работы без ручного копирования чата.

4.12 External steering  
Proteus должен использовать поддерживаемые Cursor hooks/CLI/ACP/cloud-agent API как control surfaces: продолжить bounded run, запустить headless работу в workspace, принять команду из внешней очереди и вернуть acknowledgement/receipt. Нельзя заявлять управление произвольным idle editor-thread, пока это не доказано реальным host test.

5\. PROJECT MOUNT: МИНИМАЛЬНОЕ ПОВЕДЕНИЕ  
Mount(project) должен:  
\- определить project identity;  
\- найти authoritative cloud/file/repo carriers;  
\- обнаружить local workspace;  
\- сравнить local/cloud current state;  
\- создать/обновить host-readable project instructions;  
\- установить project marker с версией Proteus и ссылками на authority;  
\- загрузить current goals/frontier/decisions/unresolved;  
\- подключить релевантные skills/rules;  
\- после работы сохранить checkpoint и reconciliation receipt.

Схема project mount должна быть адаптивной: проекты могут иметь разные собственные структуры и канонические поверхности.

6\. ПАМЯТЬ И ЗНАНИЯ  
Первая версия не обязана иметь vector DB. Она обязана иметь воспроизводимую durable модель хранения/извлечения, достаточную для Gate 1\.

Минимальные классы:  
\- current project state;  
\- decisions;  
\- episodes/run receipts;  
\- rules;  
\- skills;  
\- facts/reference pointers;  
\- unresolved/conflicts;  
\- agent/project identity pointers.

Embeddings/vector index/knowledge graph могут быть производными и пересобираемыми, если появятся.

7\. CLOUD / LOCAL  
На первом run Google Drive хранит developmental descriptions и corpus; локальный Git repo становится executable source. Полноценный bidirectional gateway пока не обязателен.

Продукт должен фиксировать реальные проблемы транспорта и определить после Gate 1, нужен ли:  
\- простой export/sync script;  
\- Drive API adapter;  
\- MCP server;  
\- daemon;  
\- Archivarius-facing reconciliation organ;  
\- более сложный shared substrate.

8\. HOST ADAPTER  
Cursor adapter обязан:  
\- обнаруживать реальную host version и поддерживаемые surfaces;  
\- устанавливать только нужные компоненты;  
\- различать global/user/project scope;  
\- сохранять чужие unrelated settings;  
\- уметь uninstall/rollback;  
\- выдавать installation receipt;  
\- проверять postconditions;  
\- избегать ручного дрейфа generated state.

Позднее аналогичные adapters могут появиться для Claude Code, Codex, Kimi, OpenClaw и локальных runtime.

9\. BUILD / UPDATE LOOP  
Изменение ideal body:  
source change → relevant tests → build/compile if needed → plan host delta → snapshot embodiment → install/update → verify → receipt → keep/rollback.

Продукт считается воспроизводимым, когда чистая установка способна получить эквивалентное host behavior из repository source.

10\. GATE 1 — ОБЯЗАТЕЛЬНЫЕ ДОКАЗАТЕЛЬСТВА  
Первая Cursor-версия должна пройти:  
\- fresh-session reentry;  
\- full Cursor restart;  
\- compaction survival;  
\- correction influences future independent session;  
\- project isolation;  
\- global rule continuity только для действительно глобального;  
\- provenance of remembered rule/decision;  
\- UNKNOWN preserved;  
\- parallel run safety;  
\- automatic project bootstrap;  
\- organ-preservation test;  
\- usability: пользователь не ведёт память вручную;  
\- first self-update: изменение ideal body устанавливается и используется в следующем действии.

11\. ПЕРВЫЙ REAL-WORLD CASE  
После smoke tests продукт должен быть применён к сложному существующему проекту, например Paideia/Hermes/Tinkuy-класса. Проверяется:  
\- восстановление истории;  
\- правильный current frontier;  
\- работа с несколькими authoritative carriers;  
\- отсутствие уничтожения существующей project structure;  
\- сохранение решений и незавершённости;  
\- полезность без ручного обслуживания.

12\. ЧТО НЕ ВХОДИТ В ОБЯЗАТЕЛЬНЫЙ FIRST BUILD  
До доказанной необходимости можно отложить:  
\- production-grade vector memory;  
\- universal knowledge graph;  
\- полноценный Drive gateway;  
\- OpenClaw persistent runtime;  
\- multi-host identity synchronization;  
\- Agentum auto-organogenesis;  
\- browser extensions;  
\- key/router management;  
\- local-model orchestration;  
\- cockpit/UI;  
\- автономный web-search evolution loop.

13\. БУДУЩЕЕ РАЗВИТИЕ  
После Gate 1 продукт может расширяться в направлениях:  
\- shared agent substrate между Cursor/Claude/Codex/Kimi/OpenClaw;  
\- автоматическое рождение/отбор органов;  
\- периодический поиск новых analogues/plugins/tools и оценка заимствований;  
\- синтез облачных и локальных моделей;  
\- browser/desktop interfaces;  
\- credentials/model routing;  
\- multi-machine sync;  
\- sensory/action surfaces;  
\- включение в более широкую структуру Айе.

14\. КРИТЕРИЙ ПРОДУКТОВОГО СОСТОЯНИЯ v0.1  
Proteus v0.1 существует, когда из версионированного local source можно установить проверяемую Cursor-инкарнацию, новая сессия через неё восстанавливает работу, проект можно bootstrap/mount/checkpoint, коррекция может пережить сессию, а изменение ideal body проходит source→install→verify и начинает реально влиять на последующее действие.  
