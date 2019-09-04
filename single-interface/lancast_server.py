# MIT License
#
# Copyright (c) 2019 Weston Berg
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
'''
Module providing server functionality for broadcast messages over subnet
'''
import socket
import threading

RECV_BUF_SZ = 1024  # In bytes
RECV_TIMEOUT = 1.0  # In seconds
done = False


def receive_broadcasts(interface_ip, broadcast_port):
    global done
    opt_value = 1  # Value for setsockopt to enable options
    bind_addr = (interface_ip, broadcast_port)

    # Create UDP socket
    with socket.socket(family=socket.AF_INET,
                       type=socket.SOCK_DGRAM) as sock:

        # Configure UDP socket
        sock.setsockopt(socket.SOL_SOCKET,
                        socket.SO_REUSEADDR,
                        opt_value)

        sock.setsockopt(socket.SOL_SOCKET,
                        socket.SO_BROADCAST,
                        opt_value)

        sock.settimeout(RECV_TIMEOUT)

        # Bind socket to receive broadcasts
        sock.bind(bind_addr)

        while not done:
            try:
                # Service broadcasts
                data, src_addr = sock.recvfrom(RECV_BUF_SZ)

                if len(data) > 0:
                    print('Recieved \'%s\' broadcast from \'%s\''
                          % (data, src_addr))

                    # Send data back
                    sock.sendto('Broadcast Received'.encode('utf-8'), src_addr)

            except socket.timeout:
                pass


def kill_server():
    global done
    done = True


def run(port):
    global done
    # Get localhost's IP
    host_ip = socket.gethostbyname(socket.gethostname())

    # Start broadcast listener
    listener = threading.Thread(target=receive_broadcasts,
                                args=(host_ip, port))
    listener.start()

    # Wait until terminated
    while not done:
        pass

    # Join thread
    listener.join()
