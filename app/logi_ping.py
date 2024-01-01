import subprocess
import time
import datetime
import json
from elasticsearch import Elasticsearch
from pathlib import Path
import os
print("zaczynam")
# Parametry konfiguracyjne
es_host = "http://87.207.10.127"
es_port = "9200"
index_name = "search-pingi"

# Odczytanie zmiennych środowiskowych
miejsce = os.environ.get('Miejsce')
es_username = os.environ.get('ESUsername')
es_password = os.environ.get('ESPassword')
# Parametry pingu
default_url = "wp.pl"
packet_size = 1
print("wczytalem credentail")
# Utworzenie połączenia z Elasticsearch
es = Elasticsearch(es_host+":"+es_port, basic_auth=(es_username, es_password))
print("wczytalem sie do ES")
# Ścieżka do zapisu danych, gdy nie ma połączenia
offline_data_path = Path("offline_ping_data.json")

def ping_server(url, packet_size):
    try:
        output = subprocess.check_output(["ping", "-c", str(packet_size), url])
        output = output.decode()
        if 'bytes from' in output:
            for line in output.splitlines():
                if 'bytes from' in line:
                    parts = line.split()
                    if len(parts) > 7:
                        ping_time = parts[7].split('=')[1]
                        return float(ping_time)
        return None
    except subprocess.CalledProcessError:
        return None

def save_offline_data(data):
    try:
        if offline_data_path.exists():
            with open(offline_data_path, "r+") as file:
                offline_data = json.load(file)
                offline_data.append(data)
                file.seek(0)
                json.dump(offline_data, file)
        else:
            with open(offline_data_path, "w") as file:
                json.dump([data], file)
    except Exception as e:
        print(f"Błąd podczas zapisywania danych offline: {e}")

def send_data_to_es(doc):
    try:
        response = es.index(index=index_name, body=doc)
        if response.get('_shards', {}).get('successful', 0) > 0:
            # print(f"Dane zostały wysłane i zaakceptowane przez Elasticsearch: {doc}")
            return True
        else:
            # print("Wystąpił problem z zapisem danych do Elasticsearch.")
            return False
    except Exception as e:
        # print(f"Błąd podczas wysyłania danych do Elasticsearch: {e}")
        return False
print("wchodze w petle")
while True:
    ping_value = ping_server(default_url, packet_size)
    current_time = datetime.datetime.now()

    # Tworzenie dokumentu do wysłania
    doc = {
        'timestamp': current_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'city': miejsce,
        'url': default_url,
        'ping': ping_value,
        'is_online': ping_value is not None
    }
    print(f"ping: {ping_value}")
    # Próba wysłania danych
    if not send_data_to_es(doc):
        save_offline_data(doc)

    # Jeśli istnieją zapisane dane offline, spróbuj je wysłać
    if offline_data_path.exists():
        with open(offline_data_path, "r") as file:
            offline_data = json.load(file)

        if offline_data:
            succeeded = []
            for data in offline_data:
                if send_data_to_es(data):
                    succeeded.append(data)

            # Usuwanie wysłanych danych
            offline_data = [d for d in offline_data if d not in succeeded]
            with open(offline_data_path, "w") as file:
                json.dump(offline_data, file)

    # Czekanie 60 sekund
    time.sleep(60.0)