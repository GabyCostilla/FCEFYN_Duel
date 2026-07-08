# StudyDuel 📚⚔️

## Correr localmente

### 1. Crear la base de datos en MySQL
```sql
CREATE DATABASE studyapp;
```
(Las tablas se crean solas al iniciar la app)

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar la conexión (opcional)
Por defecto conecta a `localhost` con usuario `root` y password `root`.
Si tu MySQL tiene otra config, editá `config.py`:
```python
'mysql+pymysql://TU_USUARIO:TU_PASSWORD@localhost/studyapp'
```

### 4. Correr
```bash
python run.py
```

Abrí `http://localhost:5000` en el browser. ¡Listo!

---

## Deploy en Clever Cloud

1. Subir todo el proyecto como app **Python**
2. Linkear el addon **MySQL**
3. Cambiar en `config.py` para leer las variables de entorno de Clever Cloud:
```python
SQLALCHEMY_DATABASE_URI = os.environ.get('MYSQL_ADDON_URI')
```
