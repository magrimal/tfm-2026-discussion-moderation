# Design: Environments Landing Page

**Date:** 2026-07-16
**Status:** Approved

## Goal

A single static HTML page that gives evaluators an overview of the project and links to each live environment. Hosted on GitHub Pages at `https://magrimal.github.io/tfm-2026-discussion-moderation/`.

## Audience

TFM evaluators with no prior context. Not developer-facing. No SSH commands, no deployment runbooks.

## Infrastructure

- Single `index.html` file at `docs/index.html`
- GitHub Pages enabled on `main`, serving from `/docs`
- URL: `https://magrimal.github.io/tfm-2026-discussion-moderation/`
- No build step. No external framework. Self-contained HTML + CSS.
- TLS and CDN handled by GitHub Pages.

## Page Structure

### 1. Header

- Full thesis title in Spanish
- One sentence in English describing what the system does for a reader with no context
- Link to the GitHub repository
- Author, institution (UCM), year

### 2. Environments section

Two cards side by side (stacks on mobile), one per environment:

**IDRIL card**
- Name: IDRIL
- Live URL: `https://idril.fdi.ucm.es/2526-moderacion`
- Description: UCM academic server. Runs the facilitation pipeline with local Ollama models on UCM hardware. Requires UCM network or VPN.
- Default model: `ministral-3:14b` (14B, local Ollama)

**MGMDY card**
- Name: MGMDY
- Live URL: `https://facilitation.mgmdy.xyz`
- Description: AWS EC2 deployment. Runs the same pipeline with external models via OpenRouter.
- Default model: `gpt-4o` (via OpenRouter)

### 3. How it works section

Global section below the cards. Covers:
- What the facilitation pipeline does: classifies the discussion state, decides whether to intervene, and generates a facilitation message
- What differs between environments: IDRIL uses local LLMs running on UCM hardware; MGMDY uses external LLMs via OpenRouter API
- What an evaluator can do: submit a discussion thread and observe the pipeline output in the dashboard

## Styling

Plain HTML and CSS, no external dependencies. Goals:
- Clean, readable layout
- Cards use a subtle border and rounded corners (matching the sketch)
- Mobile-responsive via CSS grid that collapses to a single column
- No JavaScript

## Out of scope

- Live status badges per environment
- Authentication or login
- Any dynamic content
- Custom domain (using GitHub Pages URL directly)
