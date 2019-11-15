class Attribute:
    NO_ACCESS = 0
    OPEN = 0
    ENCRYPT_NO_MITM = 0
    ENCRYPT_WITH_MITM = 0
    LESC_ENCRYPT_WITH_MITM = 0
    SIGNED_NO_MITM = 0
    SIGNED_WITH_MITM = 0

class UUID:
    def __init__(self, uuid):
        pass

class Characteristic:
    BROADCAST = 0
    READ = 0
    WRITE = 0
    NOTIFY = 0
    INDICATE = 0
    WRITE_NO_RESPONSE = 0
