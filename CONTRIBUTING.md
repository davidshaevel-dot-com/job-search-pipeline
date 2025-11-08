# Contributing Guidelines

## Git Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/) format for all commit messages.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, setup, dependencies
- **ci**: CI/CD changes
- **build**: Build system changes

### Scope (Optional)

Scope indicates the area of the codebase affected:
- `search`: Search engine
- `adapters`: Job board adapters
- `evaluation`: AI evaluation engine
- `organization`: File organization
- `integrations`: Slack, Linear integrations
- `config`: Configuration files
- `workflows`: GitHub Actions workflows
- `docker`: Docker configuration
- `docs`: Documentation

### Subject

- Use imperative mood ("add" not "added" or "adds")
- First letter lowercase
- No period at the end
- Maximum 72 characters

### Body (Optional)

- Explain what and why, not how
- Wrap at 72 characters
- Can include multiple paragraphs

### Footer

Always include Linear issue references:

```
related-issues: TT-45, TT-46
```

### Examples

**Feature:**
```
feat(adapters): add LinkedIn job board adapter

Implement LinkedIn API integration for job search functionality.
Supports keyword search, location filtering, and pagination.

related-issues: TT-45
```

**Bug Fix:**
```
fix(evaluation): handle missing salary data in AI evaluation

Previously crashed when salary information was not available.
Now defaults to 0 and includes note in evaluation output.

related-issues: TT-48
```

**Documentation:**
```
docs: add Slack integration setup guide

Comprehensive guide for setting up Slack webhooks and slash commands.
Includes troubleshooting section and security best practices.

related-issues: TT-50
```

**Chore:**
```
chore(deps): update anthropic SDK to 0.18.0

Update Claude API client to latest version for improved error handling.

related-issues: TT-48
```

**Multiple Issues:**
```
feat(integrations): implement Slack notifications and triggers

Add Slack webhook integration for pipeline status notifications.
Implement slash commands for manual pipeline triggers.

related-issues: TT-50, TT-51
```

## Branch Naming

Use descriptive branch names:
- `feat/TT-45-linkedin-adapter`
- `fix/TT-48-evaluation-salary-handling`
- `docs/TT-50-slack-integration-guide`

## Pull Requests

- Reference Linear issues in PR description
- Use conventional commit format for PR title
- Include "related-issues: TT-xx" in PR description
- Link to Linear issues: `[TT-45](https://linear.app/...)`

---

**Last Updated:** November 8, 2025

