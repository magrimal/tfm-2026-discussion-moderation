# DDA-0043: Autenticación HTTP Basic Auth para el dashboard y la API

## Estado

Propuesto

## Contexto

El servicio se despliega en dos entornos: idril.fdi.ucm.es (accesible solo bajo VPN de la UCM) y AWS EC2 (acceso público). En el despliegue en EC2, el dashboard y la API REST quedan expuestos sin ningún mecanismo de autenticación, de modo que cualquier persona con la URL puede disparar ejecuciones de evaluación y consumir cuota de API de los modelos LLM. El acceso al sistema es exclusivamente desde el navegador; no hay scripts automatizados ni clientes no interactivos. El objetivo es protección mínima contra uso no autorizado en el entorno público, sin añadir complejidad operacional ni dependencias nuevas.

## Decisión

Decidimos proteger todos los endpoints de la API REST (excepto `/health`) con HTTP Basic Auth, configurando las credenciales mediante variables de entorno y delegando el diálogo y el almacenamiento de credenciales en sesión al propio navegador.

## Consecuencias

### Positivas

- Protección inmediata sin dependencias adicionales: FastAPI incluye soporte nativo para `HTTPBasic`
- Sin cambios en la lógica del frontend: el navegador gestiona el desafío 401, el diálogo de credenciales y el envío automático en peticiones subsiguientes
- Credenciales en variables de entorno; sin base de datos de usuarios ni gestión de sesiones en el servidor
- El endpoint `/health` queda libre de autenticación para que los healthchecks de despliegue sigan funcionando

### Negativas

- Credencial única compartida: no permite auditoría por usuario ni revocación selectiva si se comprometiera
- Las credenciales viajan en cada petición codificadas en Base64; es seguro solo bajo HTTPS (requisito en producción)
- El diálogo nativo del navegador no tiene la misma apariencia que un formulario de login propio
- No escala a múltiples usuarios con permisos diferenciados sin rediseñar la capa de autenticación

## Alternativas Consideradas

- **JWT con formulario de login en React**: descartado porque requiere un endpoint `/login`, gestión de tokens en `localStorage`, lógica de rutas protegidas en el dashboard y renovación de tokens, sin añadir valor real para un acceso de usuario único desde el navegador
- **Autenticación a nivel de proxy (nginx basic auth)**: descartado porque no todos los despliegues tienen nginx configurado; añadiría una dependencia de infraestructura no presente en el entorno de desarrollo local
- **API key como cabecera personalizada**: descartado porque exige que el dashboard gestione la clave explícitamente y la incluya en cada petición, añadiendo lógica en el frontend que el navegador ya provee de forma nativa con Basic Auth
