
# dashboard

This frontend app hosts the UI for the project. It started as a
Figma-generated prototype and is being adapted into a generic run control and
inspection surface that complements LogFuse instead of duplicating it.

This app is intentionally named `dashboard` because it is the operational run
surface for the project.

The original design source is available at:
https://www.figma.com/design/0mDt7Ri4VjBqpYLWorreQE/AI-Pipeline-Review-Dashboard

## Running the code

From the repository root, run `uv run dev setup` to install the frontend
dependencies.

Run `uv run dev up` to start the backend API and the dashboard together.

If you only want the frontend, run `cd dashboard && npm run dev`.

## Local testing

1. Bootstrap the local dev environment from the repository root:

	`uv run dev setup`

2. Start both services:

	`uv run dev up`

3. Open the Vite URL shown in the terminal, usually `http://127.0.0.1:5173`.

4. The frontend is configured to proxy `/runs`, `/evals`, and `/health` to
	the local backend on port `8000`.

5. Quick manual checks:

	- Open Run history and switch between runs.
	- Open Run overview and verify the stage timeline and trace matrix render.
	- Open `http://127.0.0.1:5173/runs` in the browser dev tools network panel
	  once the frontend starts consuming backend data.
  