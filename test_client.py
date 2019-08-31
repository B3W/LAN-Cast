'''
Testing module
'''
import lancast_client

if __name__ == '__main__':
    access_port = 10001

    # Send a broadcast
    lancast_client.run(access_port)
