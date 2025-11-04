import socket
import threading
import os

HOST = '0.0.0.0'
PORT = 2121

def handle_client(conn, addr):
    print(f"[+] Connected by {addr}")
    conn.sendall(b"Welcome to the FTP server.\n")

    try:
        while True:
            data = conn.recv(1024).decode().strip()
            if not data:
                break

            print(f"[*] Command from {addr}: {data}")
            parts = data.split(maxsplit=1)
            cmd = parts[0].upper()

            if cmd == "LIST":
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
        print(f"[!] Error with {addr}: {e}")

    finally:
        conn.close()
        print(f"[-] Connection closed from {addr}")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(5)
        print(f"[*] FTP server running on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
            print(f"[+] Active clients: {threading.active_count() - 1}")

if __name__ == "__main__":
    main()