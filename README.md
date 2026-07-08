# FCEFYN Duel ⚔️

[![Licencia](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Estado del Proyecto](https://img.shields.io/badge/status-en%20desarrollo-orange.svg)]()
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)]()
[![Flask](https://img.shields.io/badge/flask-3.0-lightgrey.svg)]()
[![MySQL](https://img.shields.io/badge/mysql-8.0-orange.svg)]()

**FCEFYN Duel** es una aplicación web de competencia de estudio en tiempo real, desarrollada por estudiantes de **Facultad de Ciencias Exactas, Físicas y Naturales (FCEFYN)**. Dos usuarios se enfrentan midiendo sus horas de estudio diarias y semanales, con cronómetros sincronizados, estadísticas, logros y apuestas.

---

## 🚀 Características Principales

- **⏱ Cronómetros en tiempo real:** Cada usuario tiene su propio cronómetro con soporte de pausa y reanudación. Ambos se sincronizan automáticamente cada 5 segundos.
- **📊 Estadísticas completas:** Horas de hoy, esta semana y totales históricos. Gráfico de barras de los últimos 7 días comparando a ambos jugadores.
- **🎯 Metas diarias y semanales:** Cada usuario configura sus propias metas. La app muestra una barra de progreso en tiempo real.
- **🔥 Racha de días consecutivos:** Se calcula automáticamente y se muestra en la card de cada jugador.
- **🏅 Sistema de logros (badges):** 10 logros desbloqueables automáticamente por hitos de estudio (primera sesión, rachas, horas acumuladas, etc.).
- **📋 Historial de sesiones:** Tabla con fecha, duración y materia de cada sesión registrada.
- **🎲 Apuestas semanales:** Los jugadores pueden definir una apuesta para la semana (ej: "el que pierde paga el café") y registrar el ganador.
- **🏆 Banner de liderazgo:** Muestra en tiempo real quién lleva más horas acumuladas en total.

---

## 🛠️ Tecnologías Utilizadas

- **Frontend:** HTML5, CSS3, JavaScript vanilla, Chart.js
- **Backend:** Python 3.10+, Flask 3.0, Flask-SQLAlchemy
- **Base de Datos:** MySQL 8.0 (local o Clever Cloud)
- **ORM:** SQLAlchemy + PyMySQL
- **Deploy:** Clever Cloud (MySQL addon)
- **Herramientas:** Git, GitHub

---

## 🗂️ Estructura del Proyecto
FCEFYN_Duel/
├── run.py               ← Punto de entrada, ejecuta la app
├── config.py            ← Configuración de la base de datos
├── models.py            ← Modelos de SQLAlchemy (tablas)
├── routes.py            ← Todos los endpoints de la API REST
├── requirements.txt     ← Dependencias Python
├── app/
│   └── init.py      ← Factory de Flask, inicializa DB
└── templates/
└── index.html       ← Frontend completo (SPA)

---

## 🗃️ Modelos de Base de Datos

| Tabla | Descripción |
|---|---|
| `users` | Usuarios registrados |
| `sessions` | Sesiones de estudio (inicio, fin, duración, materia) |
| `active_timers` | Cronómetros activos en este momento (incluyendo pausa) |
| `goals` | Metas diarias y semanales por usuario |
| `bets` | Apuestas semanales entre los jugadores |
| `user_badges` | Logros desbloqueados por usuario |

---

## 📦 Instalación Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/GabyCostilla/FCEFYN_Duel.git
cd FCEFYN_Duel
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Crear la base de datos en MySQL
```sql
CREATE DATABASE studyapp;
CREATE USER 'estudio'@'localhost' IDENTIFIED BY 'tu_password';
GRANT ALL PRIVILEGES ON studyapp.* TO 'estudio'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Configurar la conexión en `config.py`
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://estudio:tu_password@localhost/studyapp'
```
Las tablas se crean automáticamente al iniciar la app.

### 5. Ejecutar
```bash
python run.py
```
Abrí `http://localhost:5000` en el browser.

---

## ☁️ Deploy en Clever Cloud

1. Crear una app **Python** en Clever Cloud
2. Agregar un addon **MySQL** y vincularlo a la app
3. En `config.py`, usar la URI del addon:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://USUARIO:PASSWORD@HOST:3306/DB'
```
4. Subir el código — Clever Cloud detecta el `Procfile` automáticamente

> ⚠️ Clever Cloud no permite conexiones directas al MySQL desde IPs externas. La app Flask debe correr en el mismo entorno que la base de datos.

---

## 🎮 Uso

1. Registrate la primera vez con tu nombre de usuario
2. La próxima vez, ingresá directamente con ese nombre
3. Con dos usuarios registrados, cada uno ve su cronómetro y el del rival en tiempo real
4. Presioná **▶ Iniciar sesión** cuando empieces a estudiar
5. Podés pausar con ⏸ y retomar cuando quieras
6. Al terminar, escribís qué materia estudiaste (opcional)
7. Las estadísticas, logros y apuestas se actualizan automáticamente

---

## 🔌 API REST

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/users` | Registrar usuario |
| GET | `/users/<username>/login` | Login |
| POST | `/timer/start` | Iniciar cronómetro |
| POST | `/timer/pause` | Pausar cronómetro |
| POST | `/timer/resume` | Reanudar cronómetro |
| POST | `/timer/stop` | Terminar sesión |
| POST | `/goals` | Guardar metas |
| GET | `/bets` | Listar apuestas |
| POST | `/bets` | Crear apuesta |
| POST | `/bets/<id>/resolve` | Resolver apuesta |
| GET | `/sessions/<user_id>` | Historial de sesiones |
| GET | `/stats` | Estadísticas completas de todos los usuarios |
| GET | `/health` | Health check |

---

## 🗺️ Roadmap

- [ ] Separación del código en módulos (routes/, static/js/, static/css/)
- [ ] Animación de confeti al completar meta diaria
- [ ] Animación más escandalosa al completar meta semanal
- [ ] Racha rota con animación y aviso visual
- [ ] Historial del rival visible en la misma pestaña
- [ ] Meta diaria → semanal automática al llegar al 100%
- [ ] Calendario de actividad tipo GitHub
- [ ] Gráfico de torta por materias
- [ ] Notificaciones del browser cuando el rival empieza a estudiar
- [ ] Modo Pomodoro integrado
- [ ] Soporte para más de 2 jugadores
- [ ] PWA instalable en celular
- [ ] Resumen semanal con IA (API de Claude)

---

## 🤝 Contribuciones

1. Hacé un fork del proyecto
2. Creá tu rama (`git checkout -b feature/NuevaFeature`)
3. Commiteá tus cambios (`git commit -m 'Agrega NuevaFeature'`)
4. Pusheá la rama (`git push origin feature/NuevaFeature`)
5. Abrí un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consultá el archivo `LICENSE` para más detalles.

---

## ✉️ Contacto

Gabriel Costilla — [@GabyCostilla](https://github.com/GabyCostilla)

Link del proyecto: [https://github.com/GabyCostilla/FCEFYN_Duel](https://github.com/GabyCostilla/FCEFYN_Duel)
