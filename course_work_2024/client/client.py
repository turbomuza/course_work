import os
import socket
import struct
import matplotlib.pyplot as plt


def send_file_size(sck: socket.socket, filesize):
    sck.sendall(struct.pack("<Q", filesize))


def plot_network_load(filesize_list):
    x = list(range(1, len(filesize_list) + 1))
    y = [size / 1024 for size in filesize_list]
    plt.plot(x, y, marker='o')
    plt.xlabel('File Number')
    plt.ylabel('Network Load (KB)')
    plt.title('Network Load Over Time')

    plot_filename = "network_load.png"
    plt.savefig(plot_filename)

    plt.show()

    plt.clf()

    return plot_filename


def send_string(sck: socket.socket, data):
    str_length = len(data)
    sck.sendall(struct.pack("<Q", str_length))
    sck.sendall(data.encode("utf-8"))


def send_file(sck: socket.socket, filepath):
    with open(filepath, "rb") as f:
        while read_bytes := f.read(1024):
            sck.sendall(read_bytes)


def send_files_from_directory(sck: socket.socket, client_directory):
    files = [f for f in os.listdir(client_directory) if
             os.path.isfile(os.path.join(client_directory, f)) and f != ".DS_Store"]

    send_file_size(sck, len(files))
    filesize_list = []
    for filename in files:
        send_string(sck, filename)
        print(f"Sent filename: {filename}")
        filepath = os.path.join(client_directory, filename)
        filesize = os.path.getsize(filepath)
        send_file_size(sck, filesize)
        print(f"Sent filesize: {filesize}")
        send_file(sck, filepath)

        filesize_list.append(filesize)

    plot_filename = plot_network_load(filesize_list)
    print(f"график сохранен в : {plot_filename}")
    send_file_size(sck, 0)


with socket.create_connection(("0.0.0.0", 9999)) as conn:
    print("Подключение к серверу.")
    print("Передача файлов...")
    send_files_from_directory(conn, "/Users/muza/Documents/coursework_testfiles/")
    print("Файлы отправлены.")
print("Соединение закрыто.")
