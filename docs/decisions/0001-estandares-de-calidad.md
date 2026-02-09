# ADR 0001: Estándares de calidad de código

**Estado**: Aceptado
**Fecha**: 2025-02-09

## Descripción

Este proyecto requiere estándares de calidad que garanticen código mantenible, seguro y consistente. Se definen convenciones para contribución, estilo de código y revisiones.

Los detalles específicos de revisión de código están documentados en `.github/copilot-instructions.md`.

## Decision

Adoptar un conjunto de convenciones y herramientas que estandaricen la contribución y calidad del código.

### Idioma

- Código, commits y documentación técnica en **inglés**
- Documentación del TFM (memoria, ADRs) en **español**

### Contribución

- Seguir el flujo de trabajo de GitHub (branch, PR)
- Usar **conventional commits** para mensajes de commit
- Las PRs requieren revisión antes de merge
- CI debe pasar antes de merge

### Estilo de código

- **PEP 8** como guía de estilo para Python
- **ruff** como herramienta unificada de linting y formateo
- Longitud máxima de línea: 80 caracteres
- Imports ordenados automáticamente por ruff

### Testing

- **pytest** como framework de testing
- Tests requeridos para funcionalidad nueva
- Estructura Arrange-Act-Assert

### Principios de diseño

- Simple sobre complejo
- Explícito sobre implícito
- Comentarios solo para explicar "por qué", no "qué"
- YAGNI: no implementar hasta que sea necesario

### Seguridad

- No hardcodear secretos
- Validar inputs en los límites del sistema
- Usar consultas parametrizadas

## Consecuencias

- Consistencia en todo el código base
- Revisiones más eficientes con criterios claros
- Automatización de validaciones en CI
- Historial de commits legible y estructurado

### Referencias

- Github Workflow: https://docs.github.com/en/get-started/quickstart/github-flow
- Ruff: https://docs.astral.sh/ruff/
- Instrucciones detalladas de revisión: [.github/copilot-instructions.md](../../.github/copilot-instructions.md)
- Conventional Commits: https://www.conventionalcommits.org/
- PEP 8: https://peps.python.org/pep-0008/
