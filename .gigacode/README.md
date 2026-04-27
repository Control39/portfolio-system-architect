# GIGA IDE Configuration

This directory contains configuration files for GIGA IDE.

## Directory Structure

```
.gigacode/
├── config.json    # Main configuration file
├── logs/          # Log files
└── plans/         # Development plans
```

## Configuration

The `config.json` file contains settings for:

- MCP Server integration
- Feature toggles
- Logging configuration

### MCP Server Settings

- `enabled`: Whether MCP server integration is enabled
- `url`: Base URL of the MCP server
- `timeout`: Request timeout in milliseconds
- `retries`: Number of retry attempts
- `endpoints`: API endpoints mapping
- `headers`: Default HTTP headers

### Features

- `enable_prompt_validation`: Validate prompts before processing
- `enable_rule_engine`: Apply rules to prompts and responses
- `enable_response_enhancement`: Enhance responses with additional information

### Logging

- `level`: Log level (DEBUG, INFO, WARNING, ERROR)
- `file`: Log file path
- `max_size`: Maximum log file size
- `backup_count`: Number of backup files to keep

## Usage

The configuration is automatically loaded by GIGA IDE on startup. To apply changes, restart the IDE.