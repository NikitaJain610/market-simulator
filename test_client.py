import socket
import simplefix
import time

HOST = "127.0.0.1"
PORT = 5001


def send_and_receive(sock, msg):
    sock.sendall(msg.encode())
    time.sleep(0.5)
    response = sock.recv(4096)
    print("Received:", response)
    print("-" * 60)


def create_logon(seq=1):
    msg = simplefix.FixMessage()
    msg.append_pair(8, "FIX.4.4")
    msg.append_pair(35, "A")
    msg.append_pair(34, str(seq))
    msg.append_pair(49, "CLIENT")
    msg.append_pair(56, "SERVER")
    msg.append_pair(108, "30")
    return msg


def create_buy_order(seq=2):
    msg = simplefix.FixMessage()
    msg.append_pair(8, "FIX.4.4")
    msg.append_pair(35, "D")
    msg.append_pair(34, str(seq))
    msg.append_pair(11, "ORD1")
    msg.append_pair(55, "AAPL")
    msg.append_pair(54, "1")
    msg.append_pair(38, "100")
    msg.append_pair(44, "150")
    msg.append_pair(49, "CLIENT")
    msg.append_pair(56, "SERVER")
    return msg


def create_sell_order(seq=3):
    msg = simplefix.FixMessage()
    msg.append_pair(8, "FIX.4.4")
    msg.append_pair(35, "D")
    msg.append_pair(34, str(seq))
    msg.append_pair(11, "ORD2")
    msg.append_pair(55, "AAPL")
    msg.append_pair(54, "2")
    msg.append_pair(38, "100")
    msg.append_pair(44, "150")
    msg.append_pair(49, "CLIENT")
    msg.append_pair(56, "SERVER")
    return msg


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    print("Connected to server")
    print("-" * 60)

    print("Sending Logon...")
    send_and_receive(sock, create_logon(1))

    print("Sending BUY Order...")
    send_and_receive(sock, create_buy_order(2))

    print("Sending SELL Order...")
    send_and_receive(sock, create_sell_order(3))

    sock.close()
    print("Connection closed")


if __name__ == "__main__":
    main()
