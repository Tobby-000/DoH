from Domain import *
from TypeAdapter import *
class DnsQuestion:
    domain:str
    dns_type:int
    dns_class:int
    def __init__(self,domain:str="",dns_type:int=1,dns_class:int=1):
        self.domain=domain
        self.dns_type=dns_type
        self.dns_class=dns_class
    @classmethod
    def from_bytearray(cls,index:int,byte:bytearray):
        inst=cls()
        inst.domain,index=domain_decoder(index,byte)
        inst.dns_type,index=read_bytes(index,byte,2,True)
        inst.dns_class,index=read_bytes(index,byte,2,True)
        return inst,index
    def to_bytearray(self):
        byte=bytearray()
        byte.extend(domain_encoder(self.domain))
        byte.extend(self.dns_type.to_bytes(2,'big'))
        byte.extend(self.dns_class.to_bytes(2,'big'))
        return byte
    def print_member(self):
        print("Domain",self.domain)
        print("Type",self.dns_type)
        print("Class",self.dns_class)
class DnsMessage:
    domain:str
    dns_type:str
    dns_class:str

    def __int__(self):
        return
