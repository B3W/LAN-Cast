'''
Module simulating client broadcasting to LAN server and waiting for response
'''
from collections import deque
import netifaces
import socket
import threading

RECV_BUF_SZ = 1024  # In bytes
RECV_TIMEOUT = 5.0  # In seconds
done = 0


def get_broadcast_addrs():
    '''
    Determines IP addresses for brodcasting

    :returns: List of broadcasting IP addresses (xxx.xxx.xxx.xxx)
    '''
    broadcast_ips = []  # IP addresses for broadcasting

    # Get list of network adapters
    net_adapters = netifaces.interfaces()

    # Search through list for appropriate adapter
    for adapter in net_adapters:
        # Get AF_INET adapter info (list of dicts of addresses)
        af_inet_info = netifaces.ifaddresses(adapter)[netifaces.AF_INET]

        # Check for broadcasting addresses
        for addr_dict in af_inet_info:
            try:
                # Skip loopback adapter
                if addr_dict['addr'] not in ['127.0.0.1']:
                    broadcast_ips.append(addr_dict['broadcast'])
            except KeyError:
                pass

    return broadcast_ips


def broadcast(msg, broadcast_ip, broadcast_port, data_queue):
    done = False
    opt_value = 1  # Value for setsockopt to enable options
    broadcast_addr = (broadcast_ip, broadcast_port)  # Address to broadcast to

    # Create UDP socket
    with socket.socket(family=socket.AF_INET,
                       type=socket.SOCK_DGRAM) as sock:

        # Configure UDP socket for reuse if error occurs
        sock.setsockopt(socket.SOL_SOCKET,
                        socket.SO_REUSEADDR,
                        opt_value)

        # Configure UDP socket for broadcasting
        sock.setsockopt(socket.SOL_SOCKET,
                        socket.SO_BROADCAST,
                        opt_value)

        # Send out broadcast message
        sock.sendto(msg.encode('utf-8'), broadcast_addr)

        # Wait for response
        while not done:
            try:
                data, src_addr = sock.recvfrom(RECV_BUF_SZ)

                if len(data) > 0:
                    data = data.decode('utf-8')

                    data_queue.append('Received: \'%s\' from IP \'%s\''
                                      % (data, src_addr[0]))

                    if data == 'stop':
                        done = True

            except socket.timeout:
                pass


def run(port):
    threads = []
    queue = deque()  # Deque holding broadcasting results
    host_ip = socket.gethostbyname(socket.gethostname())  # Get localhost's IP
    msg = 'This is a message!'
    broadcast_ips = get_broadcast_addrs()  # Get localhost's broadcasting IPs

    # Start thread for each broadcast
    for ip in broadcast_ips:
        queue.append('Sending \'%s\' to %s' % (msg, ip))
        thread = threading.Thread(target=broadcast,
                                  args=(msg, host_ip, port, queue))
        thread.start()
        threads.append(thread)

    # Wait for broadcasts to complete
    for thread in threads:
        thread.join()

    # Print results
    for res in queue:
        print(res)
