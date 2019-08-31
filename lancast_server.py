'''
Module providing server functionality for broadcast messages over subnet
'''
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


def receive_broadcasts(broadcast_port):
    global done
    opt_value = 1  # Value for setsockopt to enable options
    bind_addr = ('', broadcast_port)

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
                    # Send data back
                    sock.sendto('Broadcast Received'.encode('utf-8'), src_addr)
                    sock.sendto('stop'.encode('utf-8'), src_addr)

            except socket.timeout:
                pass


def run(port):
    global done
    threads = []
    broadcast_ips = get_broadcast_addrs()  # Get localhost's broadcasting IPs

    # Start broadcast listeners
    # TODO Reduce to only one broadcast listener
    for ip in broadcast_ips:
        thread = threading.Thread(target=receive_broadcasts, args=(port,))
        thread.start()
        threads.append(thread)

    # Wait until terminated
    while not done:
        pass

    # Join threads
    for thread in threads:
        thread.join()
