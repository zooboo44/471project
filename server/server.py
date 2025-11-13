import socket
import threading
import os
import sys

HOST = '0.0.0.0'
PORT = 2121

# Global variables
shutdown_event = threading.Event()
connections = []
connections_lock = threading.Lock()


def handle_client(conn, addr):
    print(f"[+] Connected by {addr}")
    with connections_lock:
        connections.append(conn)

    conn.sendall(b"Welcome to the FTP server.\n")

    try:
        while not shutdown_event.is_set():
            data = conn.recv(1024).decode().strip()
            if not data:
                break

            print(f"[*] Command from {addr}: {data}")
            parts = data.split(maxsplit=1)
            cmd = parts[0].upper()

            if cmd == "SHUTDOWN":
                conn.sendall(b"Server is shutting down...\n")
                print("[!] Shutdown initiated by client.")
                shutdown_event.set()
                break

            elif cmd == "LIST":
                files = "\n".join(os.listdir('.')) + "\n"
                conn.sendall(files.encode())

            elif cmd == "GET" and len(parts) == 2:
                filename = parts[1]
                if os.path.exists(filename):
                    conn.sendall(b"OK\n")
                    with open(filename, 'rb') as f:
                        while chunk := f.read(4096):
                            conn.sendall(chunk)
                    conn.sendall(b"EOF")
                else:
                    conn.sendall(b"ERR File not found\n")

            elif cmd == "PUT" and len(parts) == 2:
                filename = os.path.basename(parts[1])
                conn.sendall(b"READY\n")
                with open(filename, 'wb') as f:
                    while True:
                        chunk = conn.recv(4096)
                        if b"EOF" in chunk:
                            f.write(chunk.replace(b"EOF", b""))
                            break
                        f.write(chunk)
                conn.sendall(b"Upload complete\n")

            elif cmd == "QUIT":
                conn.sendall(b"Goodbye.\n")
                break

            else:
                conn.sendall(b"ERR Unknown command\n")

    except Exception as e:
        if not shutdown_event.is_set():
            print(f"[!] Error with {addr}: {e}")

    finally:
        with connections_lock:
            if conn in connections:
                connections.remove(conn)
        conn.close()
        print(f"[-] Connection closed from {addr}")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(5)
        s.settimeout(1.0)  # Check shutdown every second
        print(f"[*] FTP server running on {HOST}:{PORT}")

        try:
            while not shutdown_event.is_set():
                try:
                    conn, addr = s.accept()
                    thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                    thread.start()
                    print(f"[+] Active clients: {threading.active_count() - 1}")
                except socket.timeout:
                    continue

        except KeyboardInterrupt:
            print("\n[!] Keyboard interrupt received. Shutting down...")
            shutdown_event.set()

        finally:
            print("[*] Closing all client connections...")
            with connections_lock:
                for c in connections:
                    try:
                        c.sendall(b"Server shutting down.\n")
                        c.close()
                    except:
                        pass
                connections.clear()

            print("[*] Server shutting down now.")
            s.close()
            sys.exit(0)


if __name__ == "__main__":
    main()
