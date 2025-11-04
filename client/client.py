import socket
import os

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 2121

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_HOST, SERVER_PORT))
        print(s.recv(1024).decode(), end="")

        while True:
            cmd = input("ftp> ").strip()
            if not cmd:
                continue

            s.sendall(cmd.encode())
            parts = cmd.split(maxsplit=1)
            command = parts[0].upper()

            if command == "LIST":
                print(s.recv(4096).decode(), end="")

            elif command == "GET" and len(parts) == 2:
                response = s.recv(1024).decode()
                if response.startswith("OK"):
                    filename = os.path.basename(parts[1])
                    with open(filename, 'wb') as f:
                        while True:
                            data = s.recv(4096)
                            if b"EOF" in data:
                                f.write(data.replace(b"EOF", b""))
                                break
                            f.write(data)
                    print(f"Downloaded '{filename}' successfully.")
                else:
                    print(response.strip())

            elif command == "PUT" and len(parts) == 2:
                filename = parts[1]
                if not os.path.exists(filename):
                    print("File not found.")
                    continue

                resp = s.recv(1024).decode()
                if not resp.startswith("READY"):
                    print(resp.strip())
                    continue

                with open(filename, 'rb') as f:
                    while chunk := f.read(4096):
                        s.sendall(chunk)
                s.sendall(b"EOF")
                print(s.recv(1024).decode().strip())

            elif command == "QUIT":
                print(s.recv(1024).decode().strip())
                break

            else:
                print(s.recv(1024).decode().strip())

if __name__ == "__main__":
    main()