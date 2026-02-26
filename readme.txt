# 🧪 Shadow Testing Demo – Flask

Demo de Shadow Testing con dos versiones del mismo sistema web (misma lógica, distinta UI):

- **Producción:** estilo claro (versión principal)
- **Sombra:** estilo oscuro (versión alternativa)

Ambas versiones usan el mismo login y lógica, pero se acceden por URLs distintas.

## Requisitos
- Python 3.10+

## Instalación
```bash
pip install -r requirements.txt
Ejecución

Abre dos terminales distintas.

Producción
cd prod_app
python app.py
Sombra
cd shadow_app
python app.py
Credenciales de ejemplo

El login se valida contra usuarios.txt (formato usuario:password):

admin:1234
usuario1:pass1
usuario2:pass2

*(Si quieres, añadimos una nota de `FLASK_SECRET_KEY` para hacerlo más pro y alineado con el reporte.)*

---

# 3) Las 4 branches/PRs de prueba (qué cambiar exactamente)

## Branch A — `pr_docs_demo` (solo docs)
**Objetivo:** que el reporte salga **Risk BAJO** y no sobrerreaccione.

**Cambios**
- Solo tocar README (p.ej. aplicar el README limpio de arriba).
- No tocar código.

✅ Output esperado del swarm:
- Risk level: **BAJO**
- Confidence: LOW (si no hay CI)
- Decision: Go (o Go-with-conditions light)

---

## Branch B — `pr_deps_demo` (dependencias)
**Objetivo:** que active driver “Dependencies” y meta gates de deps.

**Cambios**
- Añadir `requirements.txt` con `Flask>=2.3`
- (Opcional) Ajustar README para instalar por requirements

✅ Output esperado:
- Risk: **MEDIO**
- Driver Dependencies aparece
- Gate: revisar deps/lockfile (si existe) + smoke

---

## Branch C — `pr_ci_fail_demo` (CI fail = blocker objetivo)
**Objetivo:** que el swarm haga **ALTO + No-Go** por trigger objetivo.

**Cambios**
Crea `.github/workflows/ci_fail.yml`:

```yaml
name: CI Fail Demo
on:
  pull_request:
jobs:
  fail:
    runs-on: ubuntu-latest
    steps:
      - name: Fail intentionally
        run: exit 1

✅ Output esperado:

Risk level: ALTO (por CI failing)

Decision: No-Go

Checklist/gates: “arreglar CI antes”
