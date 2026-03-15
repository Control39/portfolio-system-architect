# План создания единой структуры

## Новая структура репозитория

cognitive-architect-manifesto/
├── 01_JOURNEY/
│   ├── 01_excel-to-methodology/
│   │   ├── README.md (из cognitive-architect-manifesto/01_JOURNEY/01_excel-to-methodology/README.md)
│   │   └── [уникальные файлы из it-compass версий]
│   ├── 02_chaos-to-system/
│   │   ├── README.md (из cognitive-architect-manifesto/01_JOURNEY/02_chaos-to-system/README.md)
│   │   └── [уникальные файлы из cloud-reason и system-proof]
│   └── 03_projects-to-ecosystem/
│       ├── README.md (из cognitive-architect-manifesto/01_JOURNEY/03_projects-to-ecosystem/README.md)
│       └── [уникальные файлы из всех компонентов]
│
├── 02_METHODOLOGY/
│   ├── it-compass/
│   │   ├── README.md (объединенный из всех версий)
│   │   ├── ARCHITECTURE.md (из components/it-compass/ARCHITECTURE.md)
│   │   ├── src/
│   │   │   ├── core/tracker.py
│   │   │   ├── data/markers.json
│   │   │   ├── data/user_progress.json
│   │   │   └── utils/portfolio_gen.py
│   │   └── decisions/
│   │       └── 0001-use-submodules-for-modularity.md
│   ├── arch-compass/
│   │   ├── README.md (объединенный из всех версий)
│   │   ├── ArchCompass.psd1
│   │   ├── ArchCompass.psm1
│   │   └── src/infrastructure/security/SecretManager.psm1
│   ├── markers/
│   │   └── [файлы маркеров из различных компонентов]
│   └── career-development/
│       ├── README.md (из components/career-development-system/README.md)
│       ├── src/
│       │   ├── api/app.py
│       │   ├── core/competency_tracker.py
│       │   ├── core/models.py
│       │   ├── utils/helpers.py
│       │   └── web/index.html
│       └── docs/API_REFERENCE.md
│
├── 03_EVIDENCE/
│   ├── rag-system/
│   │   ├── README.md (из cognitive-architect-manifesto/03_EVIDENCE/rag-system/README.md)
│   │   └── [файлы из system-proof/RAG/]
│   ├── reasoning-loop/
│   │   ├── README.md (из cognitive-architect-manifesto/03_EVIDENCE/reasoning-loop/README.md)
│   │   └── [файлы из cloud-reason/scripts/]
│   └── portfolio-generator/
│       ├── README.md (из cognitive-architect-manifesto/03_EVIDENCE/portfolio-generator/README.md)
│       └── [файлы из it-compass/src/utils/ и portfolio-organizer/src/]
│
├── 04_ARTIFACTS/
│   ├── case-studies/
│   │   ├── README.md (из cognitive-architect-manifesto/04_ARTIFACTS/case-studies/README.md)
│   │   └── [файлы из thought-architecture/cases/]
│   ├── demos/
│   │   ├── README.md (из cognitive-architect-manifesto/04_ARTIFACTS/demos/README.md)
│   │   └── [файлы из demos/]
│   └── grants/
│       ├── README.md (из cognitive-architect-manifesto/04_ARTIFACTS/grants/README.md)
│       └── [материалы для гранта]
│
└── 05_MANIFEST/
    ├── README.md (из cognitive-architect-manifesto/05_MANIFEST/README.md)
    ├── ARCHITECTURE.md (из cognitive-architect-manifesto/05_MANIFEST/ARCHITECTURE.md)
    └── METHODOLOGY.md (из cognitive-architect-manifesto/05_MANIFEST/METHODOLOGY.md)

## Подход к объединению версий

1. Для каждого компонента:
   - Объединить README.md из всех версий в один документ
   - Сохранить все уникальные файлы из каждой версии
   - Организовать файлы в логическую структуру

2. Для документации:
   - Объединить ARCHITECTURE.md и METHODOLOGY.md в соответствующие файлы в 05_MANIFEST/
   - Сохранить все уникальные документы в соответствующих разделах

3. Для кода:
   - Объединить все исходные коды в соответствующие подкаталоги
   - Убедиться в совместимости и отсутствии конфликтов