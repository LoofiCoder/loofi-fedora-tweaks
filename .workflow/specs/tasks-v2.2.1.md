# Tasks - v2.2.1

## Contract

- [x] ID: T1 | Files: tests/test_ai_models.py | Dep: none | Agent: CodeGen | Description: Fix cached_which and subprocess @patch targets for core.ai.ai_models namespace
  Acceptance: test_ai_models.py passes on CI
  Docs: CHANGELOG.md
  Tests: tests/test_ai_models.py

- [x] ID: T2 | Files: tests/test_ai_polish.py | Dep: T1 | Agent: CodeGen | Description: Fix cached_which and subprocess @patch targets for core.ai.ai_models namespace
  Acceptance: test_ai_polish.py passes on CI
  Docs: CHANGELOG.md
  Tests: tests/test_ai_polish.py

- [x] ID: T3 | Files: tests/test_ai.py | Dep: none | Agent: CodeGen | Description: Fix cached_which @patch targets for core.ai.ai namespace
  Acceptance: test_ai.py passes on CI
  Docs: CHANGELOG.md
  Tests: tests/test_ai.py

- [x] ID: T4 | Files: tests/test_agent_planner_dedicated.py | Dep: none | Agent: CodeGen | Description: Fix cached_which @patch targets for services.system.system namespace
  Acceptance: test_agent_planner_dedicated.py passes on CI
  Docs: CHANGELOG.md
  Tests: tests/test_agent_planner_dedicated.py

- [x] ID: T5 | Files: tests/test_ansible_export.py | Dep: none | Agent: CodeGen | Description: Fix cached_which and subprocess.run @patch targets for core.export.ansible_export namespace
  Acceptance: test_ansible_export.py passes on CI
  Docs: CHANGELOG.md
  Tests: tests/test_ansible_export.py

- [x] ID: T6 | Files: tests/conftest.py | Dep: none | Agent: CodeGen | Description: Add FirewallManager._available_cached = None reset to _clear_lru_caches fixture
  Acceptance: test_firewall_manager.py passes on CI
  Docs: CHANGELOG.md
  Tests: tests/test_firewall_manager.py