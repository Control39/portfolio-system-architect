#!/usr/bin/env python3
"""
Prompt Engine - Strategy Manager for Cognitive Agent

This module implements Layer 2 of the Hybrid Architecture:
- Loads prompt templates from text files
- Renders templates with context variables
- Executes prompt-driven strategies via LLM calls
- Supports duel mode (code vs prompt comparison)

Architecture:
    Layer 1: Orchestrator (Python code) - Infrastructure glue
    Layer 2: Strategy Manager (Prompt Engine) - THIS MODULE
    Layer 3: Prompt Templates (Text files) - Business logic
"""

import json
import time
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class PromptTemplate:
    """Represents a single prompt template with metadata"""

    def __init__(self, name: str, content: str, metadata: dict | None = None):
        self.name = name
        self.content = content
        self.metadata = metadata or {}
        self.version = self.metadata.get("version", "1.0")
        self.description = self.metadata.get("description", "")

    def render(self, context: dict[str, Any]) -> str:
        """Render template with context variables using format()"""
        try:
            return self.content.format(**context)
        except KeyError as e:
            logger.error(f"Missing context variable: {e}")
            raise ValueError(f"Template '{self.name}' requires variable: {e}")
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            raise


class PromptEngine:
    """
    Strategy Manager for prompt-driven agent behavior

    Responsibilities:
    - Load and cache prompt templates
    - Render templates with dynamic context
    - Execute strategies via LLM calls
    - Support duel mode (compare code vs prompt approaches)
    """

    def __init__(self, prompts_dir: Path, llm_client=None):
        """
        Initialize Prompt Engine

        Args:
            prompts_dir: Path to directory containing prompt templates
            llm_client: Optional LLM client for executing prompts
        """
        self.prompts_dir = Path(prompts_dir)
        self.llm_client = llm_client
        self.templates: dict[str, PromptTemplate] = {}
        self.template_cache: dict[str, str] = {}

        # Create prompts directory if it doesn't exist
        self.prompts_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"✅ Prompt Engine initialized: {self.prompts_dir}")
        self._discover_templates()

    def _discover_templates(self):
        """Discover and load all prompt templates from directory"""
        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory not found: {self.prompts_dir}")
            return

        for md_file in self.prompts_dir.glob("*.md"):
            try:
                template = self._load_template_from_file(md_file)
                self.templates[template.name] = template
                logger.debug(f"Loaded template: {template.name} v{template.version}")
            except Exception as e:
                logger.error(f"Failed to load template {md_file}: {e}")

        logger.info(f"📚 Discovered {len(self.templates)} prompt templates")

    def _load_template_from_file(self, file_path: Path) -> PromptTemplate:
        """Load a prompt template from markdown file"""
        content = file_path.read_text(encoding="utf-8")

        # Extract metadata from YAML frontmatter (if present)
        metadata = {}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                import yaml

                try:
                    metadata = yaml.safe_load(parts[1]) or {}
                    content = parts[2].strip()
                except Exception as e:
                    logger.warning(f"Failed to parse frontmatter in {file_path}: {e}")

        # Template name is filename without extension
        name = file_path.stem

        return PromptTemplate(name=name, content=content, metadata=metadata)

    def load_template(self, name: str) -> PromptTemplate:
        """
        Load a prompt template by name

        Args:
            name: Template name (without .md extension)

        Returns:
            PromptTemplate object

        Raises:
            ValueError: If template not found
        """
        if name in self.templates:
            return self.templates[name]

        # Try to load from file if not cached
        template_file = self.prompts_dir / f"{name}.md"
        if template_file.exists():
            template = self._load_template_from_file(template_file)
            self.templates[name] = template
            return template

        raise ValueError(f"Template '{name}' not found in {self.prompts_dir}")

    def render(self, template_name: str, context: dict[str, Any]) -> str:
        """
        Render a template with context variables

        Args:
            template_name: Name of template to render
            context: Dictionary of variables to substitute

        Returns:
            Rendered prompt string
        """
        template = self.load_template(template_name)
        rendered = template.render(context)

        # Cache rendered result for debugging
        cache_key = f"{template_name}_{hash(json.dumps(context, sort_keys=True))}"
        self.template_cache[cache_key] = rendered

        logger.debug(f"Rendered template '{template_name}' with {len(context)} variables")
        return rendered

    async def execute_strategy(self, strategy: str, context: dict[str, Any], timeout: int = 60) -> dict[str, Any]:
        """
        Execute a prompt-driven strategy

        Args:
            strategy: Name of strategy template
            context: Context variables for template
            timeout: Timeout in seconds for LLM call

        Returns:
            Dictionary with result and metadata
        """
        start_time = time.time()

        # Step 1: Render template
        prompt = self.render(strategy, context)

        # Step 2: Call LLM
        if self.llm_client:
            try:
                response = await self.llm_client.generate(prompt=prompt, timeout=timeout)
                result = {
                    "success": True,
                    "output": response,
                    "strategy": strategy,
                    "execution_time": time.time() - start_time,
                    "prompt_length": len(prompt),
                    "response_length": len(response),
                }
                logger.info(f"✅ Strategy '{strategy}' executed in {result['execution_time']:.2f}s")
                return result
            except Exception as e:
                logger.error(f"Strategy execution failed: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "strategy": strategy,
                    "execution_time": time.time() - start_time,
                }
        else:
            logger.warning("No LLM client configured, returning prompt only")
            return {
                "success": True,
                "output": prompt,
                "strategy": strategy,
                "execution_time": time.time() - start_time,
                "note": "LLM client not configured, prompt returned as-is",
            }

    async def execute_duel_mode(
        self,
        task_description: str,
        code_approach_result: Any,
        prompt_strategy: str,
        context: dict[str, Any],
        evaluation_criteria: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute duel mode: compare code-based approach vs prompt-based approach

        Args:
            task_description: Description of the task being solved
            code_approach_result: Result from code-based implementation
            prompt_strategy: Name of prompt strategy to compare against
            context: Context variables for prompt rendering
            evaluation_criteria: Optional criteria for judging results

        Returns:
            Dictionary with comparison results and winner
        """
        logger.info(f"⚔️ Starting duel mode for: {task_description}")

        # Execute prompt approach
        prompt_result = await self.execute_strategy(prompt_strategy, context)

        # Compare results (placeholder - needs actual evaluation logic)
        comparison = {
            "task": task_description,
            "code_approach": {
                # Truncate for logging
                "result": str(code_approach_result)[:500],
                "type": "code-based",
            },
            "prompt_approach": {
                "result": str(prompt_result.get("output", ""))[:500],
                "type": "prompt-based",
                "execution_time": prompt_result.get("execution_time", 0),
            },
            "evaluation_criteria": evaluation_criteria or ["performance", "readability", "maintainability", "security"],
            "winner": "pending_manual_review",  # TODO: Implement auto-judging
            "recommendation": "Both approaches have merits. Review manually.",
        }

        logger.info("⚔️ Duel complete. Code vs Prompt comparison ready")
        return comparison

    def list_templates(self) -> dict[str, dict[str, Any]]:
        """List all available templates with metadata"""
        return {
            name: {
                "version": template.version,
                "description": template.description,
                "content_length": len(template.content),
            }
            for name, template in self.templates.items()
        }

    def clear_cache(self):
        """Clear rendered template cache"""
        self.template_cache.clear()
        logger.debug("Template cache cleared")
