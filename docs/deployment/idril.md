# TFM Discussion Moderation

- **Proyecto:** 2526-moderacion
- **Curso:** 2025/2026
- **Supervisores:** Antonio F. G. Sevilla <afgs@ucm.es>

---

## Instrucciones de uso del contenedor

- **Directorio de trabajo del proyecto:** `/home/2526-moderacion/`
  Aquí van los ficheros compartidos del equipo. Todos los miembros del
  proyecto tienen acceso de lectura y escritura.

- **Home personal:** `/home/<tu_usuario>/`
  Para tu configuración personal (dotfiles, claves SSH, etc.).

### Apps web

- La URL de vuestro trabajo es: https://thalia.fdi.ucm.es/2526-moderacion

- **Frontend / web:** coloca los ficheros en `/home/2526-moderacion/public_html/`, y
  se verán en la raíz.

- **Backend**: se redirigirán las URLs que empiecen por `api/` al puerto 8080 de
  vuestro contenedor.

### Desarrollo

- **Python:** usa `uv` para gestionar entornos y paquetes
  (`uv venv`, `uv add`).
  https://docs.astral.sh/uv/getting-started/features/

- **Node:** usa `npm` para instalar paquetes.

- **Servicios persistentes:** usa `su - 2526-moderacion` para cambiar al usuario
  del proyecto y gestionar servicios con `systemctl --user`. Por ejemplo:
  ```
  su - 2526-moderacion
  systemctl --user start mi-servicio
  systemctl --user enable mi-servicio  # arranca automáticamente al reiniciar
  ```
  https://wiki.archlinux.org/title/Systemd/User

- **Paquetes del sistema:** se gestionan centralmente. En casos justificados
  se pueden instalar paquetes adicionales.
