prueba alexandria 

🧪 Shadow Testing Demo – Flask
Este proyecto es una demostración de Shadow Testing, con dos versiones del mismo sistema web:

Producción: Estilo claro (versión principal)

Sombra: Estilo oscuro (versión alternativa)

Ambas versiones usan el mismo login y lógica, pero se acceden por URLs distintas.

▶️ Requisitos
Python 3.10 o superior

Instalar dependencias:

bash
Copy
Edit
pip install flask
🚀 Ejecución
Abre dos terminales distintas.

En la primera, ejecuta la versión de producción:

bash
Copy
Edit
cd prod_app
python app.py
En la segunda, ejecuta la versión sombra:

bash
Copy
Edit
cd shadow_app
python app.py
🔑 Credenciales de ejemplo
El login se valida con el archivo usuarios.txt:

makefile
Copy
Edit
admin:1234
usuario1:pass1
usuario2:pass2
