# Użyj oficjalnego obrazu Pythona jako obrazu bazowego
FROM python:3.9-slim

RUN apt-get update && apt-get install -y iputils-ping

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Skopiuj plik requirements.txt do katalogu roboczego
COPY requirements.txt .

# Zainstaluj wymagane pakiety
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj resztę kodu do katalogu roboczego w kontenerze
COPY . .

# Uruchom skrypt, gdy kontener zostanie uruchomiony
CMD ["python", "logi_ping.py"]
