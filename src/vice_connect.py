import socket

# binary monitor interface with partial command implementation

API_START = 2
API_VERSION = 2

cmd_memory_get = 0x01
cmd_dump = 0x41
cmd_undump = 0x42
cmd_keybuf = 0x72
cmd_exit = 0xaa
cmd_quit = 0xbb


def build_memory_get(from_addr, to_addr):
    # everything is little endian (TODO verify)

    # request
    # api start: 8 bit
    # api version 8 bit
    # body size: 32 bit
    # request id: 32 bit
    # command: 8 bit

    # response
    # api start: 8 bit
    # api version 8 bit
    # body size: 32 bit
    # response type: 8 bit
    # error code: 8 bit
    # request id: 32 bit

    # from_addr: np.uint16
    # to_addr: np.uint16
    # bank_id: np.uint16
    bank_id = 0
    header = [
        API_START,
        API_VERSION
    ]
    no_side_effects = 0
    mem_space_main = 0
    body = [no_side_effects, little16(from_addr), little16(to_addr), mem_space_main, bank_id]


def vice_read_mem(host, port, start, finish):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(command.encode('utf-8'))
        data = s.recv(1024)
        return data.decode('utf-8')

# TODO send_keys
# TODO save_mem filename
# TODO screenshot filename
# TODO save_snapshot
# TODO load_snapshot
