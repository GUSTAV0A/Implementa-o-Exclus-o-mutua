import socket
import time
import sys
import random
from datetime import datetime
import os


F = 10  # Tamanho da mensagem
COORDINATOR_IP = "127.0.0.1"
PORT = 59672

R = 5  # Número de requisições
REQUEST = 1
GRANT = 2
RELEASE = 3

caminho = os.path.dirname(os.path.abspath(__file__))
caminho_resultado = os.path.join(caminho, "resultado.txt")

class Process:
    def __init__(self, process_id):
        self.process_id = process_id
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (COORDINATOR_IP, PORT)

    def log_access(self):
        timestamp = datetime.now().strftime("%d/%m/%Y as %H:%M:%S.%f")[:- 3]
        caminho = os.path.dirname(os.path.abspath(__file__))
        caminho_resultado = os.path.join(caminho, "resultado.txt")
        with open(caminho_resultado, "a") as f:
            timestamp = datetime.now().strftime("%d/%m/%Y as %H:%M:%S.%f")[:- 3]
            f.write(f"Processo {self.process_id} acessou em {timestamp}\n")

    def request_access(self):
        message = f"{REQUEST}|{self.process_id}|{'0' * (F - len(f'{REQUEST}|{self.process_id}|'))}"
        self.socket.sendto(message.encode(), self.addr)

    def release_access(self):
        message = f"{RELEASE}|{self.process_id}|{'0' * (F - len(f'{RELEASE}|{self.process_id}|'))}"
        self.socket.sendto(message.encode(), self.addr)

    def run(self):
        for _ in range(R):
            self.request_access()
            while True:
                try:
                    self.socket.settimeout(1)
                    response, _ = self.socket.recvfrom(10)
                    if response.decode().startswith(f"{GRANT}"):
                        self.log_access()
                        time.sleep(random.uniform(0,3))  # Tempo de espera variável
                        self.release_access()
                        time.sleep(random.uniform(2,5))  # Tempo de espera variável
                        break
                except socket.timeout:
                    continue
        self.socket.close()

if __name__ == "__main__":
   
    if len(sys.argv) != 2:
        print(f"Uso: python {sys.argv[0]} id_processo")
        sys.exit(1)

    process = Process(int(sys.argv[1]))
    process.run()
