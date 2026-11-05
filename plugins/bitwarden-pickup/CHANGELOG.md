# Changelog

All notable changes to the Bitwarden Pickup Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-05

### Added

- `/pickup`, which runs `/clear` and then starts the next conversation with the last two exchanges of the cleared one. The exchanges reach the model as a hidden row, between `<transcript-excerpt>` tags and marked as a record, not a new request: each prompt and its final reply, cut at 1,000 characters, without tool calls, tool output, or skill bodies. A toast reports any step that fails after `/clear`. The submitted prompt names the old session and, when a hook has named it, its transcript path. `/pickup <question>` replaces the default question, "Where did we leave off?".
