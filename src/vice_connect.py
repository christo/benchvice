#!/usr/bin/env python

from abc import ABC, abstractmethod
import socket
import struct

# binary monitor interface with partial command implementation
# see vice manual section 12 https://vice-emu.sourceforge.io/vice_12.html

# TODO need to make socket connection asynchronous

API_START = 2
API_VERSION = 2


# TODO send_keys
# TODO save_mem filename
# TODO screenshot filename?
# TODO save_snapshot
# TODO load_snapshot

CMD_MEMORY_GET = 0x01
CMD_DUMP = 0x41
CMD_UNDUMP = 0x42
CMD_KEYBUF = 0x72
CMD_EXIT = 0xaa
CMD_QUIT = 0xbb

MEM_BANK_CPU = 0
MEM_SIDE_FX_NONE = 0
MEM_SPACE_MAIN = 0

# monitor response types
RES_INVALID = 0x00
RES_REGISTER_INFO = 0x31
RES_STOPPED = 0x62

RESPONSE_NAMES = {
    RES_INVALID: "invalid response",
    RES_REGISTER_INFO: "register response",
    RES_STOPPED: "stopped response"
}

# a response arriving with this request id originated from an internal event
REQ_ID_EVENT = struct.unpack("<I", b'\xff\xff\xff\xff')[0]

ERR_NONE = 0x00
ERR_MESG = {
    0x00: "OK, everything worked",
    0x01: "The object you are trying to get or set doesn't exist.",
    0x02: "The memspace is invalid",
    0x80: "Command length is not correct for this command",
    0x81: "An invalid parameter value was present",
    0x82: "The API version is not understood by the server",
    0x83: "The command type is not understood by the server",
    0x8f: "The command had parameter values that passed basic checks, but a general failure occurred",

}

# non-threadsafe monotonically increasing sequence number
request_id = 0

class SocketPair(ABC):

    @abstractmethod
    def connect(self, host, port):
        pass

    @abstractmethod
    def read(self, length):
        pass

    @abstractmethod
    def write(self, data):
        pass

    @abstractmethod
    def command(self, data):
        pass

class AsyncSocketPair(SocketPair):

    def connect(self, host, port):
        pass

    def read(self, length):
        pass

    def write(self, data):
        pass

    def command(self, data):
        pass

    def __init__(self):
        super().__init__()


class SyncSocketPair(SocketPair):

    def connect(self, host, port):
        pass

    def read(self, length):
        pass

    def write(self, data):
        pass

    def command(self, data):
        pass


def build_memory_get(from_addr, to_addr):

    # length of request body is fixed for memory get
    # side effects (1), from addr (2), to addr (2), memspace (1), bank_id (2)
    mem_get_req_length = 1 + 2 + 2 + 1 + 2

    global request_id
    request_id = request_id + 1
    # format the request packet, everything is little endian
    request = struct.pack(">BBIIBBHHBH",
                          API_START,            # api start: 8 bit
                          API_VERSION,          # api version 8 bit
                          mem_get_req_length,   # body size: 32 bit
                          request_id,           # request id: 32 bit
                          CMD_MEMORY_GET,       # command id: 8 bit
                          MEM_SIDE_FX_NONE,     # side_effects: 8bit
                          from_addr,            # from_addr: 16 bit
                          to_addr,              # to_addr: 16 bit
                          MEM_SPACE_MAIN,       # mem_space: 8 bit
                          MEM_BANK_CPU)         # bank_id:16 bit
    return request


def write_binary_file(data, filename):
    with open(filename, 'wb') as file:
        file.write(data)

def hex_n_decimal(value):
    return f"{hex(value)} ({value})"

def get_vice_memory_contents_binary(host: str, port: int, from_addr: int, to_addr: int) -> bytes:
    """
    Connect to the VICE binary monitor and get memory contents of a given address range.

    :param host: The IP address or hostname of the VICE monitor.
    :param port: The port number of the VICE monitor.
    :param from_addr: The start address of the memory range.
    :param to_addr: The end address of the memory range.
    :return: The memory contents as bytes.
    """
    response_header_length = 1 + 1 + 4 + 1 + 1 + 4

    if not 0 <= from_addr <= to_addr <= 0xffff:
        raise ValueError("start and finish must be in range 0x0-0xffff and start <= finish")

    def parse_response_header_actual(header):
        actual_len_header = len(header)
        if (actual_len_header == 0):
            raise ValueError("Socket was closed :(")
        if len(header) < response_header_length:
            raise ValueError(f"Incomplete response header: {len(header)} bytes")
        # api start: 8 bit
        # api version 8 bit
        # body size: 32 bit
        # response type: 8 bit
        # error code: 8 bit
        # request id: 32 bit
        (magic, ver, resp_length, response_type, error_code, resp_req_id) = struct.unpack("<BBIBBI", header)
        print(f" magic/version: {magic}/{ver}")
        print(f" resp_length: {hex_n_decimal(resp_length)}")
        print(f" response_type: {hex(response_type)} ({RESPONSE_NAMES[response_type]})")
        print(f" error_code: {error_code} ({ERR_MESG[error_code]})")
        print(f" resp_req_id: {hex(resp_req_id)}")
        if magic != API_START or ver != API_VERSION:
            # TODO skip over unrelated responses. 3 responses received:
            # 1. register get with id 0xffffff
            # 2. response stopped with id 0xffffff
            # 3. response with expected id
            raise ValueError("weird response packet")
        elif error_code != ERR_NONE:
            raise ValueError(ERR_MESG[error_code])
        return magic, ver, resp_length, response_type, error_code, resp_req_id

    def read_body(sockt, resp_length):
        # TODO move into socket read
        body = sockt.recv(resp_length)
        while len(body) < resp_length:
            print(f" ...read {len(body)}")
            body += sockt.recv(length - len(body))
        return body

    def receive_response(sockt):

        # Read the response header 12 bytes:
        # api_start: 1
        # api_version: 1
        # response_body_length: 4
        # response_type: 1
        # error_code: 1
        # request_id: 4
        # then read the body
        # body: response_body_length
        response = 1
        body = b''
        event_response = True
        while event_response:
            print(f"\nresponse {response} reading {response_header_length} header bytes")
            header = sockt.recv(response_header_length)
            magic, ver, body_len, response_type, error_code, resp_req_id = parse_response_header_actual(header)
            event_response = resp_req_id == REQ_ID_EVENT
            if body_len > 0:
                # reading body bytes but it's not the droids we're looking for
                body = read_body(sockt, body_len)
                print(f" body: {body}")
            if not event_response and resp_req_id != request_id:
                raise ValueError(f"got response for request {resp_req_id} expected {request_id}")
            response = response + 1

        # response body format for get memory:
        # length of memory segment: 2 bytes
        # value at memory address from_addr + n for each n: n+1 bytes
        return body

    # TODO move this implementation to SyncSocketPair.command
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        request = build_memory_get(from_addr, to_addr)
        write_binary_file(request, 'memory_get_req.bin')
        sock.sendall(request)
        return receive_response(sock)



def main():
    resp = get_vice_memory_contents_binary("127.0.0.1", 6502, 15, 16)
    print(resp)


if __name__ == "__main__":
    main()

