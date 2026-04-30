$files = @(
    "apps/career-development/src/tests/test_competency_tracker.py",
    "apps/career-development/src/tests/test_helpers.py",
    "apps/career-development/tests/test_competency_tracker.py",
    "apps/career-development/tests/test_helpers.py",
    "apps/career-development/tests/tests/test_competency_tracker.py",
    "apps/career-development/tests/tests/test_helpers.py"
)

foreach ($f in $files) {
    if (Test-Path $f) {
        $content = Get-Content $f -Raw
        $newContent = $content -replace 'from apps\\.career_development\\.career_development_system\\.src\\.', 'from src.'
        $newContent | Set-Content $f -NoNewline
        Write-Host "✅ Исправлено: $f" -ForegroundColor Green
    }
}
