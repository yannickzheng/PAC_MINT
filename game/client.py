

class Client:

    """Gère la connexion au serveur (TCP/UDP), envoie et reçoit des messages, il sert juste à communiquer avec le serveur"""
    def __init__(self,server_host,server_port_tcp=1234,server_port_udp=1234,client_port_udp=1235):
        """

        """

        self.server_message = []
        self.room_id = None
        self.client_udp = ("0.0.0.0", client_port_udp)
        self.server_udp = (server_host, server_port_udp)
        self.server_tcp = (server_host, server_port_tcp)
