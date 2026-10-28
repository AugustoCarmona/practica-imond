# Capítulo 2. Git, GitHub y la trazabilidad del trabajo

## 2.1. Definición académica

Git es un sistema distribuido de control de versiones. Registra estados y cambios de archivos, permite trabajar en ramas y preservar un historial verificable. GitHub es un servicio de alojamiento y colaboración para repositorios Git, no un sustituto de la tecnología Git.

## 2.2. Analogía sencilla

Escribir un trabajo sin Git se parece a guardar «final.doc», «final2.doc» y «final_ahora_si.doc». Con Git, cada cambio relevante deja una fotografía identificable, acompañada de su propósito. Una rama permite ensayar una idea sin alterar la versión estable del equipo.

## 2.3. Flujo de trabajo mínimo

```bash
git clone URL_DEL_FORK
git status
git branch
git add sql/01_dimensiones.sql
git commit -m "feat: crear dimension producto"
git push origin main
```

Para trabajar con otros integrantes: crear una rama de función, registrar cambios pequeños, revisar diferencias con `git diff`, integrar mediante pull request y resolver conflictos con criterio. La convención `feat:`, `fix:`, `docs:` corresponde a Conventional Commits; mejora la interpretación del historial, pero un mensaje útil debe además expresar qué se cambió.

## 2.4. Qué no subir

No incorporar contraseñas, tokens, archivos personales, bases voluminosas prescindibles ni el entorno virtual `.venv`. El repositorio de la práctica ignora `warehouse.duckdb` porque puede regenerarse: el producto importante son los scripts SQL y su documentación. Antes de publicar, revisar `git status` y el archivo `.gitignore`.

## 2.5. Ejercicios propuestos

- **Ejercicio inicial.** Inicializar un repositorio, agregar `README.md`, crear dos commits con mensajes significativos y reconstruir la historia con `git log`.
- **Ejercicio aplicado.** Hacer fork del repositorio de la materia, clonarlo, abrir una rama `feat/primera-consulta` y registrar una consulta de exploración.
- **Ejercicio crítico.** Explicar diferencias entre `git add`, `git commit`, `git push` y `git pull`; describir por qué usar `git reset --hard` sin comprenderlo puede causar pérdida de trabajo.

**Evidencia:** URL del fork, historial de commits y explicación de la estrategia de ramas.

---

[← Capítulo 1](01-consola.md) · [Índice](README.md) · [Capítulo 3 →](03-dato-informacion-conocimiento.md)
