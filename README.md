# Logbuch

## Projekt starten
### Virtual Environment anlegen
Beispiel pyenv:
```bash
cd server
pyenv virtualenv <python-version> logbuch-server
pyenv local logbuch-server
```

Beispiel Python:
```bash
cd server
python3 -mvenv venv
source venv/bin/activate
```

### Virtual Environment einrichten
```bash
pip install --upgrade pip
pip install -r requirements
```

optional:
```bash
pip install pytest black flake8
```

### Logbuch bootstrappen
Im Verzeichnis server:

#### Secret Key anlegen
```bash
mkdir -p instance
head -c 32 /dev/urandom > instance/secret_key
```

#### Datenbank anlegen
```bash
flask db upgrade
```

### E-Mail Server starten
Logbuch verschickt Tokens und Error-Logs per E-Mail und braucht daher einen Mail-Server.
Debug/Entwicklungs E-Mail-Server in einem _eigenen Terminal_ starten:
```bash
python3 -m smtpd -n -c DebuggingServer localhost:8025
```

oder:
```bash
sh ./start_debug_email_server.sh
```

### Logbuch Server starten
```bash
MAIL_SERVER=localhost MAIL_PORT=8025 FLASK_DEBUG=1 flask run
```
