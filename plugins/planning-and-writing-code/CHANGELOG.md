# Changelog

All notable changes to the Planning and Writing Code plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-13

### Added

- Initial release of planning-and-writing-code plugin
- `/planning-and-writing-code:create-plan` command for generating execution plans from Jira tickets or task descriptions
- `/planning-and-writing-code:review-plan` command for validating plans before implementation
- `/planning-and-writing-code:implement-plan` command for executing validated plans stage by stage
- `structuring-execution-plans` skill with TDD-enforced plan template and parallelization analysis framework
- `reviewing-plan-quality` skill for assessing requirements completeness, technical approach, and plan clarity
- `validating-codebase-references` skill for verifying file paths, classes, methods, and namespaces against the codebase
