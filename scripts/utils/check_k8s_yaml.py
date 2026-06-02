#!/usr/bin/env python3
"""
K8s Manifests Validator

Validates Kubernetes YAML manifests for:
- YAML syntax errors
- Required fields
- Deprecated API versions
- Common misconfigurations
"""

import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any


def validate_yaml_syntax(file_path: Path) -> tuple[bool, str]:
    """Check if YAML file is syntactically valid."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            list(yaml.safe_load_all(f))
        return True, ""
    except yaml.YAMLError as e:
        return False, str(e)


def check_deprecated_apis(manifests: List[Dict[str, Any]]) -> List[str]:
    """Check for deprecated Kubernetes API versions."""
    deprecated = [
        "extensions/v1beta1",
        "apps/v1beta1",
        "apps/v1beta2",
        "extensions/v1beta1",
        "networking.k8s.io/v1beta1",
    ]

    issues = []
    for manifest in manifests:
        if not manifest:
            continue
        api_version = manifest.get("apiVersion", "")
        if any(dep in api_version for dep in deprecated):
            issues.append(f"Deprecated API version: {api_version}")

    return issues


def check_required_fields(manifests: List[Dict[str, Any]]) -> List[str]:
    """Check for required fields in K8s manifests."""
    issues = []

    for manifest in manifests:
        if not manifest:
            continue

        kind = manifest.get("kind", "")
        metadata = manifest.get("metadata", {})

        # Check for required metadata
        if not metadata.get("name"):
            issues.append(f"{kind}: Missing metadata.name")

        # Check Deployment/StatefulSet specific fields
        if kind in ["Deployment", "StatefulSet", "DaemonSet"]:
            spec = manifest.get("spec", {})
            template = spec.get("template", {})
            if not template.get("metadata"):
                issues.append(f"{kind}: Missing spec.template.metadata")
            if not spec.get("selector"):
                issues.append(f"{kind}: Missing spec.selector")

        # Check Pod spec containers
        if kind in ["Pod", "Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"]:
            containers = _get_containers(manifest)
            for container in containers:
                if not container.get("name"):
                    issues.append(f"{kind}: Container missing name")
                if not container.get("image"):
                    issues.append(f"{kind}: Container missing image")

    return issues


def _get_containers(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract containers from various K8s resource types."""
    containers = []
    spec = manifest.get("spec", {})

    if "template" in spec:
        # Deployment, StatefulSet, DaemonSet, Pod
        template_spec = spec["template"].get("spec", {})
        containers.extend(template_spec.get("containers", []))
        containers.extend(template_spec.get("initContainers", []))
    elif "jobTemplate" in spec:
        # CronJob
        job_spec = spec["jobTemplate"].get("spec", {})
        template_spec = job_spec.get("template", {}).get("spec", {})
        containers.extend(template_spec.get("containers", []))
    else:
        # Pod, Job
        containers.extend(spec.get("containers", []))

    return containers


def check_security_issues(manifests: List[Dict[str, Any]]) -> List[str]:
    """Check for common security issues."""
    issues = []

    for manifest in manifests:
        if not manifest:
            continue

        containers = _get_containers(manifest)
        for container in containers:
            # Check for privileged containers
            security_context = container.get("securityContext", {})
            if security_context.get("privileged") is True:
                issues.append(f"Privileged container: {container.get('name', 'unknown')}")

            # Check for running as root
            if security_context.get("runAsUser") == 0:
                issues.append(f"Container running as root: {container.get('name', 'unknown')}")

            # Check for missing resource limits
            resources = container.get("resources", {})
            if not resources.get("limits"):
                issues.append(
                    f"Container missing resource limits: {container.get('name', 'unknown')}"
                )

    return issues


def validate_k8s_manifests(directory: Path) -> int:
    """Validate all K8s manifests in a directory."""
    errors = []
    warnings = []

    # Find all YAML files
    yaml_files = list(directory.glob("**/*.yaml")) + list(directory.glob("**/*.yml"))

    if not yaml_files:
        print("⚠️  No YAML files found in", directory)
        return 0

    print(f"🔍 Validating {len(yaml_files)} YAML files...")

    for yaml_file in yaml_files:
        print(f"\n  Checking: {yaml_file}")

        # Check YAML syntax
        is_valid, error = validate_yaml_syntax(yaml_file)
        if not is_valid:
            errors.append(f"{yaml_file}: YAML syntax error - {error}")
            continue

        # Load and validate manifests
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                manifests = list(yaml.safe_load_all(f))
        except Exception as e:
            errors.append(f"{yaml_file}: Failed to load - {e}")
            continue

        # Run checks
        for manifest in manifests:
            if not manifest:
                continue

            # Check for deprecated APIs
            deprecated_issues = check_deprecated_apis([manifest])
            warnings.extend([f"{yaml_file}: {issue}" for issue in deprecated_issues])

            # Check required fields
            required_issues = check_required_fields([manifest])
            errors.extend([f"{yaml_file}: {issue}" for issue in required_issues])

            # Check security issues
            security_issues = check_security_issues([manifest])
            warnings.extend([f"{yaml_file}: {issue}" for issue in security_issues])

    # Print summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    if errors:
        print(f"\n❌ {len(errors)} ERROR(S):")
        for error in errors:
            print(f"  • {error}")

    if warnings:
        print(f"\n⚠️  {len(warnings)} WARNING(S):")
        for warning in warnings:
            print(f"  • {warning}")

    if not errors and not warnings:
        print("\n✅ All manifests are valid!")
        return 0

    if errors:
        print(f"\n❌ Validation failed with {len(errors)} error(s)")
        return 1

    print(f"\n⚠️  Validation completed with {len(warnings)} warning(s)")
    return 0


def main():
    """Main entry point."""
    # Default to deployment/k8s directory
    k8s_dir = Path("deployment/k8s")

    # Allow override via command line
    if len(sys.argv) > 1:
        k8s_dir = Path(sys.argv[1])

    if not k8s_dir.exists():
        print(f"❌ Directory not found: {k8s_dir}")
        sys.exit(1)

    print("🚀 K8s Manifest Validator")
    print(f"📁 Scanning: {k8s_dir.absolute()}")
    print()

    exit_code = validate_k8s_manifests(k8s_dir)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
