# Discussion Moderation

A multi-agent service for analyzing and facilitating asynchronous academic
discussions with local or hosted language models.

## Purpose

Discussion Moderation helps instructors inspect a discussion thread, decide
whether it needs support, and generate a contextual facilitation response when
appropriate. Its pipeline separates four decisions so that each one can be
inspected:

1. Classify the state and trajectory of the discussion.
2. Decide whether to intervene.
3. Select a facilitation role.
4. Choose a technique and draft the response.

The repository includes:

- a Python and FastAPI backend built with `pydantic-ai`;
- a React dashboard for running experiments and reviewing results;
- adapters for local fixtures and Open edX discussions;
- evaluation tools and reproducible discussion scenarios;
- deployment automation for local development and hosted environments;
- the design records, experiments, and thesis produced alongside the project.

This is a research prototype. The live integration can publish generated
responses automatically when a bot user is configured, so it should not be
connected to a production course without an appropriate review and approval
workflow.

## Getting Started with Development

### Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)
- Node.js and npm
- An LLM supported by `pydantic-ai`

For the default local configuration, install
[Ollama](https://ollama.com/) and pull a tool-capable model:

```bash
ollama pull qwen2.5:14b
```

### Setup

Clone the repository and create your local configuration:

```bash
git clone https://github.com/magrimal/tfm-2026-discussion-moderation.git
cd tfm-2026-discussion-moderation
cp .env.local.example .env.local
uv sync --extra dev
make local-setup
```

Review `.env.local` before starting the application. The example uses Ollama
and the stub discussion backend, so Open edX is not required for local
development.

Start the API and dashboard together:

```bash
make local-deploy
```

The dashboard is normally available at <http://127.0.0.1:5173>. The API uses
<http://127.0.0.1:8765> by default, and its health endpoint is
<http://127.0.0.1:8765/health>.

Stop the development processes with:

```bash
make local-down
```

### Deployment configuration

The repository contains the deployment mechanics—`Containerfile`,
`docker-compose.yml`, Make targets, and bootstrap/restart scripts. The actual
production environment files are private and managed locally. They contain
environment-specific endpoints and credentials and are intentionally excluded
from version control.

`.env.local.example` is the public development template. This repository is
therefore sufficient for local development, but it is not a turnkey copy of
the deployed environments.

### Tests and checks

Run the backend tests and lint both applications:

```bash
uv run --extra dev pytest
uv run --extra dev ruff check .
npm --prefix dashboard run lint
make dashboard-build
```

Useful Python entry points are declared in `pyproject.toml`. For example,
`uv run facilitate` runs a single thread through the pipeline and
`uv run eval-models` compares configured models.

## Getting Help

### Documentation

- [Project documentation](docs/README.md)
- [Pipeline guide](docs/pipeline.md)
- [Architecture decisions](docs/decisions/README.md)
- [Experiment documentation](docs/experiments.md)
- [Open edX integration decision](docs/decisions/0030-integracion-forum-api-openedx.md)
- [Dashboard development](dashboard/README.md)
- [Project website](https://magrimal.github.io/tfm-2026-discussion-moderation/)

### More help

If the documentation does not answer your question, or you find a bug, please
[open a GitHub issue](https://github.com/magrimal/tfm-2026-discussion-moderation/issues/new).
Include the command you ran, the expected behavior, the actual behavior, and
any relevant logs with secrets removed.

## Contributing

Contributions are welcome:

1. Open an issue before starting a substantial change.
2. Create a focused branch from the default branch.
3. Add or update tests and documentation with the implementation.
4. Run the checks listed above.
5. Open a pull request explaining the problem, the approach, and how the
   change was verified.

Do not commit credentials, `.env` files, student identifiers, or
non-anonymized discussion data.

## License

Copyright 2026 María Grimaldi.

Licensed under the [Apache License 2.0](LICENSE).
