
RECV_SIZE = 1024
def recv_line(conn):
    buf = ""
    while True:
        buf += conn.recv(RECV_SIZE)
        if not data:
            break
    return buf


