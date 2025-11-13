import socket
import os
import sys

SERVER_HOST = '20.163.11.193'
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

            # Shutdown command — send, then exit immediately after response
            if command == "SHUTDOWN":
                resp = s.recv(1024).decode().strip()
                print(resp)
                print("Server initiated shutdown. Closing connection...")
                break

            elif command == "LIST":
                response = s.recv(4096).decode()
                print(response, end="")
                if "Server shutting down" in response:
                    print("\nServer is shutting down. Closing connection...")
                    break

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
                    if "Server shutting down" in response:
                        print("Server is shutting down. Closing connection...")
                        break

            elif command == "PUT" and len(parts) == 2:
                filename = parts[1]
                if not os.path.exists(filename):
                    print("File not found.")
                    continue

                resp = s.recv(1024).decode()
                if not resp.startswith("READY"):
                    print(resp.strip())
                    if "Server shutting down" in resp:
                        print("Server is shutting down. Closing connection...")
                        break
                    continue

                with open(filename, 'rb') as f:
                    while chunk := f.read(4096):
                        s.sendall(chunk)
                s.sendall(b"EOF")
                resp = s.recv(1024).decode().strip()
                print(resp)
                if "Server shutting down" in resp:
                    print("Server is shutting down. Closing connection...")
                    break

            elif command == "QUIT":
                print(s.recv(1024).decode().strip())
                break

            else:
                resp = s.recv(1024).decode().strip()
                print(resp)
                if "Server shutting down" in resp:
                    print("Server is shutting down. Closing connection...")
                    break

        print("Connection closed.")
        s.close()
        sys.exit(0)

if __name__ == "__main__":
    main()