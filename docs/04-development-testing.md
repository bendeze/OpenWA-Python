# 04 - Development & Testing

## Setting Up Development Environment

Clone the repository and install development dependencies in an editable environment:

```bash
git clone git@github.com:bendeze/OpenWA-Python.git
cd OpenWA-Python

# Install package with development tools
pip install -e ".[dev]"
```

---

## Running the Engine for Integration Testing

You can use the bundled `docker-compose.yml` to launch an upstream OpenWA engine locally:

```bash
docker compose up -d
```

---

## Running Tests

Run the Pytest unit test suite:

```bash
pytest tests/
```

---

## Code Style & Formatting

We maintain code quality using `black` and `isort`:

```bash
# Format Python code
black openwa/ tests/ examples/
isort openwa/ tests/ examples/
```
