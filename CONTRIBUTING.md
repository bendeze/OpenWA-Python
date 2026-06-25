# Contributing to OpenWA-Python

First off, thank you for considering contributing to OpenWA-Python! It's people like you that make OpenWA such a great tool. 

OpenWA-Python is a Hybrid Architecture (FastAPI API Gateway + Node.js Worker) designed for developers who want to integrate WhatsApp natively into Python ecosystems. We welcome contributions of all kinds: bug reports, feature requests, documentation improvements, and code contributions.

This document serves as a guide for contributors. It relies on our more detailed development and community documentation found in the `docs/` directory.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Development Workflow](#development-workflow)
  - [Local Setup](#local-setup)
  - [Python Environment (API Gateway & SDK)](#python-environment-api-gateway--sdk)
  - [Node.js Environment (Worker & JS SDK)](#nodejs-environment-worker--js-sdk)
- [Styleguides](#styleguides)
  - [Git Commit Messages](#git-commit-messages)
  - [Code Formatting](#code-formatting)
- [Architecture & Further Reading](#architecture--further-reading)

---

## Code of Conduct

This project and everyone participating in it is governed by the [OpenWA-Python Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

---

## How Can I Contribute?

### Reporting Bugs

If you find a bug in the source code or a mistake in the documentation, you can help us by submitting an issue to our GitHub Repository.

Before submitting a bug report:
- **Check existing issues** to see if the problem has already been reported.
- **Provide context** by including your operating system, Node.js/Python versions, and the steps to reproduce the issue. 
- Use the standard issue format described in our [Issue Guidelines](docs/20-community-guidelines.md#203-issue-guidelines).

### Suggesting Enhancements

If you have a feature idea, we would love to hear about it! 
- **Submit an issue** describing the feature and its use case.
- For major architectural changes, we use an RFC (Request for Comments) process. Please refer to our [Governance & RFC Process](docs/20-community-guidelines.md#205-governance).

### Pull Requests

We actively welcome your pull requests. To submit one:

1. **Fork the repo** and create your branch from `main`.
2. **Name your branch** according to our conventions (e.g., `feature/add-group-management`, `bugfix/fix-qr-timeout`).
3. **Make your changes**, ensuring you follow our [Code Styleguides](#styleguides).
4. **Test your code**. Run the existing test suites to ensure your changes do not break existing functionality.
5. **Issue a Pull Request**. Make sure to fill out the PR description template and reference any related issues.

---

## Development Workflow

Our hybrid architecture requires standard setups for both Python and Node.js. 

### Local Setup

The easiest way to get the full stack running locally is via Docker Compose:

```bash
# 1. Clone your fork
git clone https://github.com/bendeze/openwa.git
cd openwa

# 2. Start the full stack
docker compose --profile full up --build
```

### Python Environment (API Gateway & SDK)

The API Gateway uses FastAPI. We enforce virtual environments and strictly typed code.

```bash
cd api-gateway
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> **Best Practice:** Keep the gateway "dumb." It should strictly validate requests, update the database, and publish to Redis. Do not perform heavy blocking CPU operations here.

### Node.js Environment (Worker & JS SDK)

The underlying WhatsApp Engine is written in TypeScript. 

```bash
cd wa-worker
npm install
```

> **Best Practice:** The Node.js worker must gracefully close Puppeteer browsers when it receives a `SIGTERM` to prevent memory leaks.

---

## Styleguides

### Git Commit Messages

We strictly follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that don't affect code meaning
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests
- `chore`: Changes to build process or auxiliary tools

**Example:**
`feat(sessions): add support for multiple proxy configurations`

### Code Formatting

We use automated formatters to avoid bikeshedding during code reviews. Please run them before committing.

**Python (Black & Isort):**
```bash
black api-gateway/ sdk/python/ test/
isort api-gateway/ sdk/python/ test/
```

**TypeScript (Prettier):**
```bash
npx prettier --write "wa-worker/src/**/*.ts"
npx prettier --write "sdk/javascript/src/**/*.ts"
```
*Note: We enforce `strict: true` in our TypeScript configurations.*

---

## Architecture & Further Reading

To gain a deeper understanding of OpenWA-Python, please review the documentation in the `docs/` folder:

- [System Architecture](docs/03-system-architecture.md)
- [Development Guidelines](docs/08-development-guidelines.md)
- [Testing Strategy](docs/09-testing-strategy.md)
- [Community Guidelines](docs/20-community-guidelines.md)

---

Thank you for helping make OpenWA-Python better!
