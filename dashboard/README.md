
# dashboard

This frontend app hosts the UI for the project. It started as a
Figma-generated prototype and is being adapted into a generic run control and
inspection surface that complements LogFuse instead of duplicating it.

This app is intentionally named `dashboard` because it is the operational run
surface for the project.

The original design source is available at:
https://www.figma.com/design/0mDt7Ri4VjBqpYLWorreQE/AI-Pipeline-Review-Dashboard

## Running the code

From the repository root, run `make dev-setup` to install the frontend
dependencies.

Run `make dev-up` to start the backend API and the dashboard together.

These two Make targets are the canonical local workflow for the repository.
`Procfile.dev` is the process definition, and the root `Makefile` is the
single ergonomic entrypoint that developers are expected to use.

The backend port is controlled by `DISCUSSION_MODERATION_API_PORT` and
defaults to `8765`. Set it in `.env` or `.env.local`, or override it for a
single command with `DISCUSSION_MODERATION_API_PORT=8765 make dev-up`.

If you only want the frontend, run `cd dashboard && npm run dev`.

## Local testing

1. Bootstrap the local dev environment from the repository root:

	`make dev-setup`

2. Start both services:

	`make dev-up`

3. Open the Vite URL shown in the terminal, usually `http://127.0.0.1:5173`.

4. The frontend is configured to proxy `/runs`, `/evals`, and `/health` to
	the local backend on the port defined by
	`DISCUSSION_MODERATION_API_PORT`, which defaults to `8765`.

5. Quick manual checks:

	- Open Run history and switch between runs.
	- Open Run overview and verify the stage timeline and trace matrix render.
	- Open `http://127.0.0.1:5173/runs` in the browser dev tools network panel
	  once the frontend starts consuming backend data.
  