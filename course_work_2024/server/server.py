import os
import socket
import struct


def receive_file_size(sck: socket.socket):
    fmt = "<Q"
    expected_bytes = struct.calcsize(fmt)
    received_bytes = 0
    stream = bytes()
    while received_bytes < expected_bytes:
        chunk = sck.recv(expected_bytes - received_bytes)
        stream += chunk
        received_bytes += len(chunk)
    filesize = struct.unpack(fmt, stream)[0]
    return filesize


def receive_bytes(sck: socket.socket, num_bytes):
    received_bytes = 0
    data = b""
    while received_bytes < num_bytes:
        chunk = sck.recv(min(1024, num_bytes - received_bytes))
        if not chunk:
            break
        data += chunk
        received_bytes += len(chunk)
    return data


def receive_string(sck: socket.socket):
    str_length = receive_file_size(sck)
    data = receive_bytes(sck, str_length)
    return data.decode("utf-8", errors='replace')


def receive_file(sck: socket.socket, filename, filesize):
    with open(filename, "wb") as f:
        received_bytes = 0
        while received_bytes < filesize:
            chunk = sck.recv(min(1024, filesize - received_bytes))
            if not chunk:
                break
            f.write(chunk)
            received_bytes += len(chunk)


def receive_files_from_directory(sck: socket.socket, server_directory):
    while True:
        num_files = receive_file_size(sck)
        if num_files == 0:
            break

        os.makedirs(server_directory, exist_ok=True)

        for _ in range(num_files):
            filename = receive_string(sck)
            print(f"Received filename: {filename}")
            filesize = receive_file_size(sck)
            print(f"Received filesize: {filesize}")
            filepath = os.path.join(server_directory, filename)
            receive_file(sck, filepath, filesize)


with socket.create_server(("0.0.0.0", 9999)) as server:
    print("Ожидание клиента...")
    conn, address = server.accept()
    print(f"{address[0]}:{address[1]} подключен.")
    while True:
        print("Получаем файлы...")
        receive_files_from_directory(conn, "received_files")
        print("Файлы получены ) збс")
        conn, address = server.accept()
        print(f"{address[0]}:{address[1]} подключен.")
