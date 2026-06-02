# Services Health Report (Compositional Architecture)

**Generated:** 2026-05-30T11:15:45.241792

**Total molecules with tests:** 18
- ✅ Passing: 8
- ❌ Failing: 10

## Detailed

### ❌ ai_config_manager (C:\repo\apps\ai_config_manager)

```
ImportError while loading conftest 'C:\repo\apps\ai_config_manager\tests\conftest.py'.
tests\__init__.py:2: in <module>
    from ai_config_manager import ConfigManager, AIConfig, AgentConfig
E   ModuleNotFoundError: No module named 'ai_config_manager'
```

### ✅ auth_service (C:\repo\apps\auth_service)

```
✅ Loaded test environment from C:\repo\.env.test
.................................................s.....                  [100%]
============================== warnings summary ===============================
apps/auth_service/tests/test_auth_real.py: 18 warnings
  C:\repo\.venv\Lib\site-packages\jwt\api_jwt.py:147: InsecureKeyLengthWarning: The HMAC key is 27 bytes long, which is below the minimum recommended length of 32 bytes for SHA256. See RFC 7518 Section 3.2.
    return self._jws.encode(

apps/auth_service/tests/test_auth_real.py: 14 warnings
  C:\repo\.venv\Lib\site-packages\jwt\api_jwt.py:368: InsecureKeyLengthWarning: The HMAC key is 27 bytes long, which is below the minimum recommended length of 32 bytes for SHA256. See RFC 7518 Section 3.2.
    decoded = self.decode_complete(

apps/auth_service/tests/test_auth_real.py::TestAPIEndpoints::test_health_endpoint
apps/auth_service/tests/test_auth_real.py::TestAPIEndpoints::test_health_endpoint_details
  C:\repo\apps\auth_service\tests\..\..\..\src\common\health_check.py:109: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent da...
```

### ✅ career_development (C:\repo\apps\career_development)

```
✅ Loaded test environment from C:\repo\.env.test
...................................s.................................... [ 98%]
.                                                                        [100%]
72 passed, 1 skipped in 1.43s
```

### ❌ chat_backend (C:\repo\apps\chat_backend)

```
✅ Loaded test environment from C:\repo\.env.test

=================================== ERRORS ====================================
__________ ERROR collecting apps/chat_backend/tests/test_chat_api.py __________
ImportError while importing test module 'C:\repo\apps\chat_backend\tests\test_chat_api.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Users\Z\.pyenv\pyenv-win\versions\3.12.5\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_chat_api.py:11: in <module>
    from flask import Flask
E   ModuleNotFoundError: No module named 'flask'
___________ ERROR collecting apps/chat_backend/tests/test_readyz.py ___________
ImportError while importing test module 'C:\repo\apps\chat_backend\tests\test_readyz.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Users\Z\.pyenv\pyenv-win\versions\3.12.5\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_re...
```

### ❌ cognitive_agent (C:\repo\apps\cognitive_agent)

```
✅ Loaded test environment from C:\repo\.env.test
...............sFFFFF................                                    [100%]
================================== FAILURES ===================================
_____ TestCognitiveAgentConfigIntegration.test_config_integration_module ______
tests\test_config_integration.py:29: in test_config_integration_module
    from config_integration import CognitiveAgentConfig
E   ModuleNotFoundError: No module named 'config_integration'
________ TestCognitiveAgentConfigIntegration.test_get_config_singleton ________
tests\test_config_integration.py:35: in test_get_config_singleton
    from config_integration import get_config
E   ModuleNotFoundError: No module named 'config_integration'
______ TestCognitiveAgentConfigIntegration.test_get_config_returns_dict _______
tests\test_config_integration.py:45: in test_get_config_returns_dict
    from config_integration import get_config
E   ModuleNotFoundError: No module named 'config_integration'
___________ TestCognitiveAgentConfigIntegration.test_reload_config ____________
tests\test_config_integration.py:55: in test_reload_config
    from config_integration import reload_config
E   ModuleNotFoundEr...
```

### ❌ competency_gap_engine (C:\repo\apps\competency_gap_engine)

```
✅ Loaded test environment from C:\repo\.env.test

no tests ran in 0.03s
```

### ❌ context_builder (C:\repo\apps\context_builder)

```
ImportError while loading conftest 'C:\repo\apps\context_builder\tests\conftest.py'.
tests\conftest.py:8: in <module>
    from apps.context_builder.config.settings import settings
config\settings.py:7: in <module>
    class Settings(BaseSettings):
..\..\.venv\Lib\site-packages\pydantic\_internal\_model_construction.py:131: in __new__
    config_wrapper = ConfigWrapper.for_model(bases, namespace, raw_annotations, kwargs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..\..\.venv\Lib\site-packages\pydantic\_internal\_config.py:139: in for_model
    raise PydanticUserError('"Config" and "model_config" cannot be used together', code='config-both')
E   pydantic.errors.PydanticUserError: "Config" and "model_config" cannot be used together
E
E   For further information visit https://errors.pydantic.dev/2.13/u/config-both
```

### ✅ decision_engine (C:\repo\apps\decision_engine)

```
✅ Loaded test environment from C:\repo\.env.test
s.........................................s.................             [100%]
58 passed, 2 skipped in 0.53s
```

### ❌ infra_orchestrator (C:\repo\apps\infra_orchestrator)

```
✅ Loaded test environment from C:\repo\.env.test
.....sFFFFF................F.F.F.F.F......FFF......                      [100%]
================================== FAILURES ===================================
____ TestInfraOrchestratorConfigIntegration.test_config_integration_module ____
tests\test_config_integration.py:29: in test_config_integration_module
    from config_integration import InfraOrchestratorConfig
E   ModuleNotFoundError: No module named 'config_integration'
______ TestInfraOrchestratorConfigIntegration.test_get_config_singleton _______
tests\test_config_integration.py:35: in test_get_config_singleton
    from config_integration import get_config
E   ModuleNotFoundError: No module named 'config_integration'
_____ TestInfraOrchestratorConfigIntegration.test_get_config_returns_dict _____
tests\test_config_integration.py:45: in test_get_config_returns_dict
    from config_integration import get_config
E   ModuleNotFoundError: No module named 'config_integration'
__________ TestInfraOrchestratorConfigIntegration.test_reload_config __________
tests\test_config_integration.py:55: in test_reload_config
    from config_integration import reload_config
E   ModuleNotFoun...
```

### ✅ it_compass (C:\repo\apps\it_compass)

```
============================= test session starts =============================
platform win32 -- Python 3.12.5, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\repo\apps\it_compass
configfile: pyproject.toml
plugins: anyio-4.13.0, langsmith-0.8.5, asyncio-1.3.0, base-url-2.1.0, cov-7.1.0, html-4.2.0, metadata-3.1.1, mock-3.15.1, playwright-0.8.0, xdist-3.8.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 54 items

tests\test_basic.py ...                                                  [  5%]
tests\test_config_integration.py s.....                                  [ 16%]
tests\test_integration_it_compass.py ................                    [ 46%]
tests\test_tracker.py ..                                                 [ 50%]
tests\test_tracker_integration.py .........                              [ 66%]
tests\test_tracker_real.py ..................
WARNING: Failed to generate report: No data to report.

                                                                         [100%]

======================== 53 passed, 1 skipped in 0.67s ========================

C:\repo\.venv\Lib\site-packages\covera...
```

### ❌ job_automation_agent (C:\repo\apps\job_automation_agent)

```
✅ Loaded test environment from C:\repo\.env.test

=================================== ERRORS ====================================
___ ERROR collecting apps/job_automation_agent/tests/test_agent_business.py ___
ImportError while importing test module 'C:\repo\apps\job_automation_agent\tests\test_agent_business.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Users\Z\.pyenv\pyenv-win\versions\3.12.5\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_agent_business.py:26: in <module>
    from src.resume import ResumeParser  # noqa: E402
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'src.resume'
=========================== short test summary info ===========================
ERROR tests\test_agent_business.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.34s
```

### ✅ knowledge_graph (C:\repo\apps\knowledge_graph)

```
✅ Loaded test environment from C:\repo\.env.test
........................s............................................    [100%]
68 passed, 1 skipped in 0.49s
```

### ❌ mcp_server (C:\repo\apps\mcp_server)

```
✅ Loaded test environment from C:\repo\.env.test
FFFFFFFF...F...FF...........sFFFFFFFFF..........FFF............F.F.F.F.F [ 43%]
......FFFF.FF.................FF..............sssssss.ss.FFFFFFFF....... [ 86%]
......................                                                   [100%]
================================== FAILURES ===================================
__________________ TestChromaToolsModule.test_module_imports __________________
tests\test_chroma_tools.py:16: in test_module_imports
    from apps.mcp_server.src.tools import chroma_tools
src\tools\__init__.py:12: in <module>
    from .chroma_tools import init_chroma_tools
src\tools\chroma_tools.py:12: in <module>
    from fastmcp import FastMCP
E   ModuleNotFoundError: No module named 'fastmcp'
_____________ TestChromaToolsModule.test_init_chroma_tools_exists _____________
tests\test_chroma_tools.py:22: in test_init_chroma_tools_exists
    from apps.mcp_server.src.tools import chroma_tools
src\tools\__init__.py:12: in <module>
    from .chroma_tools import init_chroma_tools
src\tools\chroma_tools.py:12: in <module>
    from fastmcp import FastMCP
E   ModuleNotFoundError: No module named 'fastmcp'
_____________ Test...
```

### ❌ ml_model_registry (C:\repo\apps\ml_model_registry)

```
✅ Loaded test environment from C:\repo\.env.test

=================================== ERRORS ====================================
_________ ERROR collecting apps/ml_model_registry/tests/test_fuzz.py __________
ImportError while importing test module 'C:\repo\apps\ml_model_registry\tests\test_fuzz.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Users\Z\.pyenv\pyenv-win\versions\3.12.5\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_fuzz.py:3: in <module>
    from hypothesis import (
E   ModuleNotFoundError: No module named 'hypothesis'
=========================== short test summary info ===========================
ERROR tests\test_fuzz.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.52s
```

### ✅ portfolio_organizer (C:\repo\apps\portfolio_organizer)

```
✅ Loaded test environment from C:\repo\.env.test
.....................s.................................................. [100%]
71 passed, 1 skipped in 5.70s
```

### ❌ system_proof (C:\repo\apps\system_proof)

```
✅ Loaded test environment from C:\repo\.env.test
...................sFFFFF........................................        [100%]
================================== FAILURES ===================================
_______ TestSystemProofConfigIntegration.test_config_integration_module _______
tests\test_config_integration.py:29: in test_config_integration_module
    from config_integration import SystemProofConfig
E   ModuleNotFoundError: No module named 'config_integration'
_________ TestSystemProofConfigIntegration.test_get_config_singleton __________
tests\test_config_integration.py:35: in test_get_config_singleton
    from config_integration import get_config
E   ModuleNotFoundError: No module named 'config_integration'
________ TestSystemProofConfigIntegration.test_get_config_returns_dict ________
tests\test_config_integration.py:45: in test_get_config_returns_dict
    from config_integration import get_config
E   ModuleNotFoundError: No module named 'config_integration'
_____________ TestSystemProofConfigIntegration.test_reload_config _____________
tests\test_config_integration.py:55: in test_reload_config
    from config_integration import reload_config
E   ModuleNotFoundError...
```

### ✅ template_service (C:\repo\apps\template_service)

```
✅ Loaded test environment from C:\repo\.env.test
.....                                                                    [100%]
5 passed in 0.24s
```

### ✅ thought_architecture (C:\repo\apps\thought_architecture)

```
✅ Loaded test environment from C:\repo\.env.test
.........s......................                                         [100%]
31 passed, 1 skipped in 0.38s
```
