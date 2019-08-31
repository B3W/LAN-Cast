'''
Testing module
'''
import lancast_server

if __name__ == '__main__':
    access_port = 10001

    # Setup server to receive and respond to broadcasts
    lancast_server.run(access_port)
