class NoSuchLayerError(Exception):
    """Raised when a layer does not exist and cannot be created"""

    pass


class ClientError(Exception):
    """Raised when a client makes an invalid request"""

    pass
