# Eliminador de Duplicados

Aplicación de escritorio en Python para encontrar y eliminar archivos duplicados en cualquier carpeta usando comparación de hashes MD5.

## Características

- **Escaneo inteligente**: Agrupa archivos por tamaño primero (optimización rápida), luego calcula hashes MD5 solo para archivos del mismo tamaño.
- **Interfaz estilo Explorador**: Vista en árbol con grupos de duplicados expandibles.
- **Eliminación segura**: Los archivos se envían a la Papelera de Reciclaje (no eliminación permanente).
- **Soporte multi-seleción**: Selecciona múltiples archivos para eliminar a la vez.

## Requisitos

- Python 3.7+
- tkinter (incluido en Python para Windows)
- send2trash

## Instalación

1. Clona o descarga el repositorio
2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Uso

```bash
python "eliminar datos duplicados.py"
```

### Instrucciones

1. Haz clic en **"Seleccionar Carpeta"**
2. Elige la carpeta que deseas escanear
3. Revisa los grupos de duplicados encontrados
4. Selecciona los archivos que deseas eliminar (puedes seleccionar varios manteniendo Ctrl)
5. Haz clic en **"Eliminar Seleccionados"**
6. Confirma la eliminación

## Cómo funciona

1. **Paso 1**: El programa recorre todos los archivos y los agrupa por tamaño
2. **Paso 2**: Solo para archivos con igual tamaño, calcula el hash MD5
3. **Paso 3**: Los archivos con el mismo hash se consideran duplicados
4. **Paso 4**: Los duplicados seleccionados se mueven a la Papelera de Reciclaje

## Licencia

MIT License
