FIRST CURSOR RUN — BOOTSTRAP PROMPT v0.1

Выполняй задачу как один непрерывный инженерный run до первой рабочей инкарнации и проверяемого результата. Не заканчивай ответом-планом. План нужен как промежуточный артефакт, после него сразу переходи к исполнению в пределах доступных инструментов.

0\. СОЗДАЙ ЛОКАЛЬНЫЙ ДОМ  
Создай каталог:  
C:\\Projects\\Proteus

Если он уже существует, сначала обследуй его и не уничтожай содержимое. Если текущий Cursor workspace не указывает на этот каталог, создай его, подготовь bootstrap, затем открой C:\\Projects\\Proteus как отдельный Cursor workspace. Если смена workspace разрывает текущую агентную сессию, до переключения запиши в C:\\Projects\\Proteus\\\_BOOTSTRAP\\RESUME\_FIRST\_RUN.md точный handoff: что уже сделано, что читать и с какого шага продолжить.

1\. ПОЛУЧИ BOOTSTRAP-КОРПУС  
Первый run получает только физически отделённый blind-start пакет:  
00\_BLIND\_START\_MD — give this folder to first Cursor  
Drive folder ID: 1Z9UJQ7LR\_gaPw4b0T8fUPd1luUG8FE0x  
URL: https://drive.google.com/drive/folders/1Z9UJQ7LR\_gaPw4b0T8fUPd1luUG8FE0x

Полный bootstrap root существует отдельно (ID 13FtIeCLUSh6oNFPa6rA7KvWphw9qT7Oh), но ДО BLIND CHECKPOINT не обходи его и не читай соседние папки.

Скопируй весь blind-start пакет в:  
C:\\Projects\\Proteus\\\_BOOTSTRAP\\BLIND\_START\\  
с сохранением имён \`.md\`. Не добавляй туда файлы из соседнего \`90\_OPERATOR\_ONLY\` до разрешённого checkpoint.

Сначала проверь, нет ли доступного локального Google Drive mirror/Drive for Desktop. Если есть — используй его. Если нет, используй уже авторизованный доступ к Google Drive или браузерный download/export. Не строй Drive gateway только ради первого скачивания. Google Docs должны оказаться локально в форме, которую ты способен полноценно читать; при необходимости экспортируй их в plain text/Markdown или другой читаемый формат, сохранив исходный Drive ID и title в заголовке локальной копии.

Если получить bootstrap из Drive невозможно из\-за авторизации, создай C:\\Projects\\Proteus\\BOOTSTRAP\_ACCESS\_BLOCKED.md с точным перечнем недоступных объектов и остановись ДО любых изменений Cursor-конфигурации. Не подменяй отсутствующие документы догадками.

2\. ЧТО ЧИТАТЬ ДО ПЕРВОЙ МУТАЦИИ  
Прочитай полностью локальные копии:  
\- 00\_READ\_FIRST.md;  
\- 01\_LOCAL\_LAYOUT\_AND\_SYNC.md;  
\- 10\_AGENT\_SPEC.md;  
\- 11\_AGENT\_CAPABILITY\_BACKLOG.md;  
\- 15\_WORKLOG\_AND\_TELEMETRY.md;  
\- 16\_EXTERNAL\_CONTROL.md;  
\- 20\_PRODUCT\_SPEC.md;  
\- 21\_PRODUCT\_BACKLOG.md;  
\- 30\_CORPUS\_MAP.md;  
\- 40\_FIRST\_RUN\_PROMPT.md;  
\- 41\_MUTATION\_PROTOCOL.md;  
\- 50\_GATE1\_EVAL.md;  
\- 51\_RUN\_RECEIPT\_TEMPLATE.md;  
\- 60\_CURRENT\_PROTEUS\_STATUS.md;  
\- 70\_PLUGIN\_SOURCE\_MAP.md и 71\_PLUGIN\_RECOVERY\_LEDGER.md; 72\_PRIMARY\_SOURCE\_PLUGIN\_LAUNCH.md — если нужен первичный смысл anti-reduction линии.

По CORPUS MAP открой current Proteus status. Из plugin recovery прочитай source map/recovery ledger настолько, чтобы понимать происхождение проблемы и anti-reduction constraint. ДО BLIND CHECKPOINT не открывай \`OPERATOR\_DOCUMENT\_A–E\` и любые материалы, помеченные OPERATOR\_ONLY / POST-BLIND. Они содержат более позднюю интерпретацию эксперимента и намеренно исключены из первого чтения.

До первого embodiment НЕ читай operator-only документы, которые CORPUS MAP помечает как post-run/operator interpretation. Это часть экспериментальной слепоты первого запуска.

3\. СОЗДАЙ RUN И BASELINE  
Создай RUN\_ID, например:  
PROTEUS-CURSOR-RUN-001-\<timestamp\>

Инициализируй Git repository в C:\\Projects\\Proteus, если его ещё нет. Не коммить секреты, токены, cookies, credentials и unrelated user settings.

До изменения Cursor или project config создай в локальном run/evidence пространстве:  
\- BASELINE.md — версия Cursor, OS, workspace, обнаруженные supported surfaces, пути конфигурации, существующие relevant files, Git status;  
\- AUTHORITY\_READ.md — какие документы реально прочитаны, их local path \+ Drive ID/status;  
\- MUTATION\_SCOPE.md — какие файлы разрешено менять в этом run;  
\- ROLLBACK.md — как вернуть состояние до run;  
\- BASELINE\_COMMIT или другой воспроизводимый snapshot проекта.

Если пользовательские/system Cursor файлы находятся вне Git, сделай их отдельные безопасные backup-копии перед изменением. Секреты не копируй в project repo.

4\. ОБСЛЕДУЙ РЕАЛЬНЫЙ CURSOR  
Не проектируй по памяти. Определи фактически доступные в установленной версии Cursor механизмы и пути:  
\- project rules/instructions;  
\- global/user rules/config;  
\- AGENTS.md / CLAUDE.md compatibility surfaces;  
\- skills;  
\- hooks и события жизненного цикла;  
\- commands;  
\- subagents/agents;  
\- MCP;  
\- plugin/package mechanisms;  
\- workspace/session/compaction hooks или ближайшие доступные аналоги;  
\- user-level global hooks path (\~/.cursor/hooks.json on the current platform);  
\- availability/version/auth state of Cursor Agent CLI (\`agent\`);  
\- whether transcript\_path / CURSOR\_TRANSCRIPT\_PATH is actually exposed and transcripts are enabled;  
\- ACP support (\`agent acp\`) and usable session/control behavior.

При необходимости сверяйся с актуальной официальной документацией Cursor. Отделяй «обнаружено в host» от «предполагается по документации».

5\. СПРОЕКТИРУЙ МИНИМАЛЬНУЮ ПЕРВУЮ ИНКАРНАЦИЮ  
На основе AGENT SPEC \+ PRODUCT SPEC \+ реального host inspection предложи минимальный первый Proteus-Cursor embodiment.

Он обязан дать как минимум:  
\- persistent agent orientation;  
\- project identity/current/frontier loading;  
\- project bootstrap;  
\- checkpoint/handoff;  
\- correction/learning capture;  
\- anti-reduction guidance;  
\- host mutation baseline/rollback;  
\- installation/version receipt;  
\- один durable current-run/project-state carrier;  
\- global Cursor worklog/telemetry that activates in every workspace and flushes useful status to Runtime Observatory;  
\- external command ingress using verified stop-hook \+ CLI/ACP surface with acknowledgement;  
\- путь source → install/update → verify.

Не принимай заранее заданную folder topology как обязательную. Создай структуру local ideal-body/source сам, исходя из реального Cursor и требований. Перед реализацией запиши DESIGN\_v0.1.md: выбранные surfaces, почему они выбраны, что сознательно отложено и какие альтернативы остаются открытыми.

6\. ПОСТРОЙ EXECUTABLE IDEAL BODY  
Реализуй в локальном Proteus repository исходники/шаблоны/install/update/test logic, достаточные для воспроизводимого получения первой Cursor-инкарнации.

Главное требование: generated/installed host state должен иметь понятный источник в repo. Не превращай ручное редактирование .cursor/AGENTS/settings в основной способ развития.

6.5. УСТАНОВИ ГЛОБАЛЬНЫЙ OBSERVABILITY / CONTROL CONTOUR  
До перехода к обычным smoke tests реализуй первый глобальный user-scope контур:  
\- global Cursor hook(s), действующие во всех workspaces;  
\- append-only local telemetry spool;  
\- active-run registry/card;  
\- collector/flush в Runtime Observatory Drive folder ID 1Cg0X2\_\_jRf-LtMstPfLTDTPTKK33-bhx либо в подтверждённый локальный Google Drive synced path;  
\- redaction/secret guard;  
\- stop/session/compaction logging;  
\- transcript pointer/capture только если реально доступен;  
\- тестовую внешнюю команду через stop followup\_message и отдельный CLI/ACP ingress/ack path.

Не заставляй каждое hook-событие синхронно ждать Google Drive. При transport failure local evidence обязано сохраняться.

7\. УСТАНОВИ ПЕРВУЮ CURSOR-ИНКАРНАЦИЮ  
Перед установкой вычисли bounded intended delta и сверь его с MUTATION\_SCOPE.

Затем:  
\- snapshot затрагиваемых host/project files;  
\- install/update;  
\- перечитай результат;  
\- проверь, что unrelated settings не изменились;  
\- запиши INSTALL\_RECEIPT с version/source revision/file list/diffs/postconditions/rollback.

При провале postcondition откати изменение и зафиксируй failure evidence.

8\. ПРОВЕДИ FIRST SMOKE TESTS  
Проверь минимум:  
\- persistent instructions действительно подхватываются Cursor;  
\- project current/frontier можно восстановить из durable state;  
\- checkpoint/handoff создаётся без ручной сортировки пользователем;  
\- correction может быть зафиксирована с scope/provenance;  
\- UNKNOWN остаётся UNKNOWN;  
\- agent может объяснить происхождение одного правила/решения;  
\- anti-reduction instruction реально присутствует в рабочем контексте;  
\- install/update можно повторить идемпотентно или получить понятный bounded delta;  
\- открой/переключи тестовый workspace и проверь, что global worklog продолжает работать;  
\- Runtime Observatory показывает host/project/RUN/model/status/stage evidence без ручного копирования чата;  
\- отправь одну bounded test-команду через поддержанный внешний control path и зафиксируй acknowledgement/result.

Не маркируй fresh-session/restart/compaction tests PASS, пока они физически не выполнены в независимом контексте. Для них подготовь точные test scripts/prompts и состояние, которое следующий запуск должен восстановить.

8.5. BLIND DISCOVERY CHECKPOINT  
До чтения любых OPERATOR\_ONLY / POST-BLIND материалов создай BLIND\_OBSERVATION.md. Опиши только из собственного опыта этого run:  
\- какие неожиданные отношения, совпадения или напряжения ты обнаружил между AGENT\_SPEC, PRODUCT\_SPEC и фактически установленной системой;  
\- какие свойства продукта начали менять способ твоей собственной работы;  
\- какие свойства агента пришлось материализовать как часть продукта;  
\- что в этой связи кажется случайным, а что структурным;  
\- какие выводы ты пока НЕ имеешь права делать.  
Не пытайся угадывать «правильную идею авторов». Это независимое наблюдение до раскрытия операторской интерпретации.

После сохранения BLIND\_OBSERVATION.md открой \`99\_POST\_BLIND\_UNLOCK.md\`, выполни указанный там release protocol и только затем читай закрытый operator layer. После чтения добавь отдельный POST\_BLIND\_COMPARISON.md: что ты обнаружил сам, что совпало с операторской гипотезой, что не совпало, и что операторская гипотеза пропустила. BLIND\_OBSERVATION.md после раскрытия не переписывай.

9\. ИСПОЛЬЗУЙ УСТАНОВЛЕННЫЕ ВОЗМОЖНОСТИ ДЛЯ ОДНОГО СЛЕДУЮЩЕГО ШАГА ПРОДУКТА  
После успешной установки выбери ОДИН bounded недостаток Proteus, обнаруженный в этом run. Используя уже установленную persistent/project/checkpoint machinery как часть рабочего процесса:  
\- сформулируй deficit;  
\- измени local ideal-body/source;  
\- прогони relevant tests;  
\- обнови Cursor-инкарнацию через созданный install/update path;  
\- проверь результат;  
\- зафиксируй второй receipt.

Не считай этот пункт выполненным, если второе изменение снова сделано только ручным редактированием host files в обход source/install path.

10\. ПОДГОТОВЬ CLEAN REENTRY TEST  
Создай точный независимый prompt для новой Cursor session, которая НЕ получает transcript этого run и должна восстановить:  
\- кто действует;  
\- что за проект открыт;  
\- текущий frontier;  
\- последние принятые решения;  
\- одно unresolved;  
\- состояние тестов;  
\- следующий шаг.

Сохрани его в evidence/run folder. Подготовь expected answers/postconditions. После этого сообщи пользователю только минимальную операцию, необходимую для физического открытия новой независимой session, если сам host не позволяет создать её программно.

11\. RECEIPT И STOP CONDITION  
Перед завершением run создай RUN\_RECEIPT.md:  
\- RUN\_ID;  
\- source docs/IDs/revisions прочитаны;  
\- baseline;  
\- design choices;  
\- files/source created;  
\- host files changed;  
\- tests PASS/FAIL/NOT\_RUN с доказательствами;  
\- rollback;  
\- deficits discovered;  
\- infrastructure hypotheses возникшие из реального опыта;  
\- exact next frontier.

Не пиши «архитектура готова». После первого run архитектура остаётся provisional до clean reentry и реального project-mount case.

12\. ЗАПРЕТЫ FIRST RUN  
\- Не строить production vector DB без доказанной необходимости.  
\- Не строить полный Google Drive gateway ради bootstrap download.  
\- Не переносить весь исторический corpus в permanent prompt.  
\- Не создавать global rule из единичного эпизода.  
\- Не заменять LLM-native орган эвристикой ради простоты реализации.  
\- Не удалять UNKNOWN/конфликты.  
\- Не менять unrelated Cursor/user configuration.  
\- Не скрывать FAIL под PARTIAL/PASS.

НАЧИНАЙ С ШАГА 0 И ПРОДОЛЖАЙ ДО ПЕРВОЙ ПРОВЕРЕННОЙ ИНКАРНАЦИИ И ОДНОГО BOUNDED FOLLOW-UP IMPROVEMENT.  
