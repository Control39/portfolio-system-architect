from .code_analyzer import AnalysisResult, AnalysisTool, CodeAnalyzer

# Optional CLI entrypoint (may be absent in some distributions)
try:
    from .code_analyzer_cli import cli  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    cli = None  # type: ignore

__all__ = ["CodeAnalyzer", "AnalysisTool", "AnalysisResult", "cli"]
