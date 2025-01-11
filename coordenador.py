import socket
import threading
from queue import Queue
from datetime import datetime

F = 10  # Tamanho da mensagem
IP = "127.0.0.1"
PORT = 59672
REQUEST = 1
GRANT = 2
RELEASE = 3

class Coordinator:
    def __init__(self):
        self.process_sockets = {}
        self.request_queue = Queue()
        self.process_count = {}
        self.lock = threading.Lock()
        self.running = True

    def log_message(self, message_type, process_id):
        timestamp = (datetime.now().strftime("%d/%m/%Y as %H:%M:%S.%f")[:-3])
        print(f"Processo {process_id} - {message_type} - {timestamp}")
        with open("log.txt", "a") as f:
            f.write(f"Processo {process_id} - {message_type} - {timestamp}\n")

    def handle_request(self, process_id, addr):
        with self.lock:
            self.request_queue.put(process_id)
            self.process_sockets[process_id] = addr
            self.log_message("REQUEST", process_id)
            if self.request_queue.queue[0] == process_id:
                self.grant_access(process_id, addr)

    def grant_access(self, process_id, addr):
        message = f"{GRANT}|{process_id}|{'0' * (F - len(f'{GRANT}|{process_id}|'))}"
        self.udp_socket.sendto(message.encode(), addr)
        self.log_message("GRANT", process_id)
        self.process_count[process_id] = self.process_count.get(process_id, 0) + 1

    def release_access(self, process_id):
        with self.lock:
            if not self.request_queue.empty() and self.request_queue.queue[0] == process_id:
                self.request_queue.get()
                self.process_sockets.pop(process_id, 0)
                self.log_message("RELEASE", process_id)
                if not self.request_queue.empty():
                    self.grant_access(self.request_queue.queue[0], self.process_sockets[self.request_queue.queue[0]])

    def process_requests(self):
        while self.running:
            data, addr = self.udp_socket.recvfrom(10)
            data = data.decode()
            process_id = int(data.split('|')[1])
            if data.startswith(f"{REQUEST}"):
                self.handle_request(process_id, addr)
            elif data.startswith(f"{RELEASE}"):
                self.release_access(process_id)

    def command_interface(self):
        while self.running:
            command = input("\nInsira o comando:\
                            \n1: Imprimir fila de pedidos atual\
                            \n2: Imprimir quantas vezes cada processo foi atendido\
                            \n3: Encerrar execução\n\n")
            if command == "1":
                print("Fila de pedidos atual:", list(self.request_queue.queue))
            elif command == "2":
                print("Contagem de serviços:", self.process_count)
            elif command == "3":
                print("Encerrando execução...")
                self.running = False
            else:
                print("Comando inválido")

    def start(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((IP, PORT))
        print("Coordenador em execução")

        threading.Thread(target=self.command_interface, daemon=True).start()
        threading.Thread(target=self.process_requests, daemon=True).start()

        while self.running:
            pass

if __name__ == "__main__":
    coordinator = Coordinator()
    coordinator.start()