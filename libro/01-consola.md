# Capítulo 1. La consola: dialogar con la computadora

## 1.1. Definición académica

La interfaz de línea de comandos (CLI) es un medio textual de interacción con el sistema operativo y sus programas. El usuario envía instrucciones a un intérprete de comandos —shell— que ejecuta operaciones, devuelve resultados y permite automatizar secuencias. La terminal es la aplicación que proporciona la ventana de interacción; el shell interpreta las órdenes.

## 1.2. Explicación para quien recién empieza

Pensá en una computadora como un edificio lleno de habitaciones: las carpetas son habitaciones, los archivos son objetos y las rutas son direcciones. La consola es una forma de moverse y trabajar diciendo exactamente qué acción realizar. No reemplaza toda interfaz gráfica, pero permite repetir tareas de manera predecible y trabajar en servidores sin escritorio.

## 1.3. Rutas, directorios y acciones esenciales

Una ruta absoluta comienza desde un origen conocido: `/home/ana/proyecto` en Linux o `C:\Users\Ana\proyecto` en Windows. Una relativa parte de la carpeta actual: `./datos` o `../documentos`. El símbolo `..` indica el directorio superior. Los comandos no son idénticos entre shells; comprobar primero si se está usando Bash, PowerShell o CMD.

Terminal Bash (macOS/Linux):

```bash
pwd                      # Mostrar dónde estoy
ls -la                   # Listar, incluidos archivos ocultos
mkdir mi_proyecto        # Crear una carpeta
cd mi_proyecto           # Entrar
touch notas.txt          # Crear archivo vacío
cd ..                    # Volver a la carpeta superior
```

Terminal PowerShell (Windows):

```powershell
Get-Location                              # Mostrar ubicación actual
Get-ChildItem                             # Listar archivos
New-Item -ItemType Directory mi_proyecto  # Crear una carpeta
Set-Location mi_proyecto                  # Entrar
New-Item -ItemType File notas.txt         # Crear archivo vacío
Set-Location ..                           # Volver a la carpeta superior
```

Bash y PowerShell aceptan también algunos alias comunes, como `cd`. Los comandos de eliminación recursiva borran datos y deben reservarse para prácticas supervisadas; antes de borrar, verificar la ruta. `Ctrl+C` interrumpe una operación, la tecla `Tab` autocompleta y las flechas recuperan comandos anteriores.

## 1.4. Aplicación al caso EcoBottle

El estudiante usará la consola para clonar su fork, activar un entorno virtual, instalar dependencias, ejecutar el programa de construcción del warehouse y verificar cambios del repositorio. El uso de consola no es accesorio: forma parte de la reproducibilidad del trabajo.

## 1.5. Ejercicios propuestos

- **Ejercicio inicial.** Crear una carpeta `laboratorio-datos` con subcarpetas `raw`, `sql` y `docs`. Mostrar la ruta absoluta y documentar en un archivo qué comando se usó.
- **Ejercicio guiado.** Navegar desde el directorio principal hasta `sql` y volver mediante rutas relativas. Explicar qué cambia entre `./` y `../`.
- **Ejercicio de transferencia.** Imaginar que un script falla porque no encuentra `raw/ventas.csv`: proponer tres comprobaciones desde la terminal antes de editar código.

**Evidencia de aprendizaje:** captura del árbol de carpetas y breve registro de comandos, sin capturas de datos privados.

---

[← Presentación](00-presentacion.md) · [Índice](README.md) · [Capítulo 2 →](02-git-github.md)
