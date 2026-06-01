import sys

import pytest


sys.exit(
    pytest.main(
        [
            "apps/career_development/tests/",
            "--cov=apps/career_development/src",
            "--cov=apps/career_development/utils",
            "--cov-report=term-missing",
            "--cov-fail-under=80",
            "-v",
        ]
    )
)
