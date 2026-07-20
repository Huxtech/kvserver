import os, socket, pickle, time, select, json
from json import dumps, load as load_json_data
from threading import Thread
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from qrcode_term import qrcode_string
from kvserver.soc_ip import wlan_ip
from kvserver.brand import print_logo
import struct

observer_path = os.getcwd()
ip = "127.0.0.1"


class SocketServer(FileSystemEventHandler):
    def __init__(self, port):
        self.HEADER_LENGTH = 64

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        try:
            self.server_socket.bind((wlan_ip, port))
            addr = wlan_ip
        except Exception as e:
            print(f"WLAN bind failed: {e}")
            self.server_socket.bind((ip, port))
            addr = ip

        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        print_logo(logo_path)
        print(qrcode_string(f"kvc://{addr}:{port}", frame_width=1, ansi_white=False))
        print(f"› URL: kvc://{addr}:{port}")
        print("› Scan the QR code above with KivyDevClient app\n    or\n› Enter the above generated url in the app")
        print("› Logs for your project will appear below. Press Ctrl+C to exit.")

        self.server_socket.listen(5)
        self.server_socket.setblocking(False)

        self.clients = {}
        self.running = True

        Thread(target=self.accept_loop, daemon=True).start()
        Thread(target=self._observer, daemon=True).start()

    # ---------------- SOCKET PROTOCOL ---------------- #

    def send_packet(self, sock, header, body=b""):
        try:
            header_bytes = dumps(header).encode()

            # pack lengths (4 bytes each)
            header_len = struct.pack('!I', len(header_bytes))
            body_len = struct.pack('!I', len(body))

            # send everything in ONE flow
            sock.sendall(header_len + header_bytes + body_len + body)

        except Exception as e:
            print(f"Send error: {e}")
            self.remove_client(sock)

    def broadcast(self, header, body=b""):
        for addr, client in list(self.clients.items()):
            try:
                self.send_packet(client, header, body)
            except Exception as e:
                print(f"Error sending to {addr}: {e}")
                client.close()
                del self.clients[addr]

    def remove_client(self, sock):
        for addr, s in list(self.clients.items()):
            if s == sock:
                print(f"{addr} disconnected")
                try:
                    s.close()
                except:
                    pass
                del self.clients[addr]

    # ---------------- CONNECTION ---------------- #

    def accept_loop(self):
        while self.running:
            try:
                read, _, _ = select.select([self.server_socket], [], [], 1)
                for s in read:
                    client_socket, address = s.accept()
                    client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

                    addr_key = f"{address[0]}:{address[1]}"
                    self.clients[addr_key] = client_socket

                    print(f"\nConnected: {addr_key}\n")

                    Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

            except Exception:
                continue

    def recv_exact(self, sock, size):
        data = b""
        while len(data) < size:
            packet = sock.recv(size - len(data))
            if not packet:
                raise ConnectionError("\nConnection dropped by remote device")
            data += packet
        return data

    def handle_client(self, client_socket):
        try:
            # Force the socket to block in its handler thread
            client_socket.setblocking(True)
            
            # First task: Sync initial files out to the client
            self.send_initial_files(client_socket)
            
            # Second task: Keep reading execution traffic coming back from the app
            while self.running:
                raw_header_len = self.recv_exact(client_socket, 4)
                header_len = struct.unpack('!I', raw_header_len)[0]
                
                header_data = self.recv_exact(client_socket, header_len)
                # FIX: Use json.loads instead of json.load for string parsing
                message = json.loads(header_data.decode('utf-8'))
                
                raw_body_len = self.recv_exact(client_socket, 4)
                body_len = struct.unpack('!I', raw_body_len)[0]
                
                body = self.recv_exact(client_socket, body_len) if body_len > 0 else b""
                
                if message.get("cmd") == "LOGCAT":
                    log_line = body.decode('utf-8', errors='ignore')
                    print(f"[DEVICE LOG] {log_line.strip()}")
                    
        except Exception as e:
            print(f"\nClient session closed: {e}")
        finally:
            self.remove_client(client_socket)

    # ---------------- FILE SYNC ---------------- #

    def send_initial_files(self, sock):
        try:
            with open(os.path.join(observer_path, "setup.json"), "r", encoding="utf-8") as f:
                setup_data = load_json_data(f)
        except:
            setup_data = {"exclude_dirs": [], "exclude_files": [], "ignore_pattern": []}

        file_dir = {}

        for root, _, files in os.walk(observer_path):
            if "__pycache__" in root:
                continue

            for name in files:
                try:
                    if name in setup_data["exclude_files"]:
                        continue

                    path = os.path.join(root, name)
                    rel = os.path.relpath(path)

                    with open(path, "rb") as f:
                        file_dir[rel] = f.read()

                except Exception as e:
                    print(f"Read error: {e}")
                    continue

        body = pickle.dumps(file_dir)

        self.send_packet(sock, {
            "cmd": "INIT",
            "size": len(body)
        }, body)

    def safe_read(self, path):
        try:
            time.sleep(0.3)  # stabilize writes
            with open(path, "rb") as f:
                return f.read()
        except Exception:
            return None

    # ---------------- WATCHDOG EVENTS ---------------- #

    def on_created(self, event):
        path = event.src_path

        rel_path = os.path.relpath(path)

        if event.is_directory:
            self.broadcast({"cmd": "CREATE", "path": rel_path})
            return

        data = self.safe_read(path)
        if data is None:
            return
        

        self.broadcast({
            "cmd": "MODIFY",
            "path": rel_path,
            "size": len(data)
        }, pickle.dumps(data))

    def on_modified(self, event):
        if event.is_directory:
            return

        path = event.src_path
        rel_path = os.path.relpath(path)

        data = self.safe_read(path)
        if data is None:
            return

        self.broadcast({
            "cmd": "MODIFY",
            "path": rel_path,
            "size": len(data)
        }, pickle.dumps(data))

    def on_deleted(self, event):
        rel_path = os.path.relpath(event.src_path)

        self.broadcast({
            "cmd": "DELETE",
            "path": rel_path
        })

    # ---------------- OBSERVER ---------------- #

    def _observer(self):
        observer = Observer()
        observer.schedule(self, path=observer_path, recursive=True)
        observer.start()

        while self.running:
            time.sleep(1)

        observer.stop()
        observer.join()

