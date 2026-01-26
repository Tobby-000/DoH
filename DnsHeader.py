from typing import Optional
class DnsFlags(object):
    # dns flags类
    qr:bool=True;opcode:int=0;aa:bool=False
    tc:bool=False;rd:bool=True;ra:bool=True
    z:int;rcode:int
    def __init__(self,qr:bool=True,opcode:int=0,aa:bool=False,tc:bool=False
    ,rd:bool=True,ra:bool=True,z:int=0,rcode:int=0):
        self.qr=qr;self.opcode=opcode;self.aa=aa
        self.tc=tc;self.rd=rd;self.ra=ra
        self.z=z;self.rcode=rcode
    @classmethod
    def from_bytearray(cls, byte:bytearray):
        byte_num=int.from_bytes(byte,'big')
        inst=cls()
        inst.qr=(byte_num>>15&1)==1
        inst.opcode=(byte_num>>11)&0b1111
        inst.aa=(byte_num>>10&1)==1
        inst.tc=(byte_num>>9&1)==1
        inst.rd=(byte_num>>8&1)==1
        inst.ra=(byte_num>>7&1)==1
        inst.z=(byte_num>>4)&0b111
        inst.rcode=byte_num&0b1111
        return inst
    def to_bytearray(self)->bytes:
        byte_num=(self.qr&1)<<15
        byte_num|=(self.opcode&0b1111)<<11
        byte_num|=(self.aa&1)<<10
        byte_num|=(self.tc&1)<<9
        byte_num|=(self.rd&1)<<8
        byte_num|=(self.ra&1)<<7
        byte_num|=(self.z&0b111)<<4
        byte_num|=self.rcode&0b1111
        return byte_num.to_bytes(2,'big')
    def print_member(self):
        print(self.to_bytearray().hex())
        print("QR",self.qr)
        print("OPCODE",self.opcode)
        print("AA",self.aa)
        print("TC",self.tc)
        print("RD",self.rd)
        print("RA",self.ra)
        print("Z",self.z)
        print("RCODE",self.rcode)
    @staticmethod
    def rcode_decode(rcode:int):
        rcode_map = {
            0: "查询成功(SUCCESS)",
            1: "请求格式错误 (FORMERR)",
            2: "服务器内部错误 (SERVFAIL)",
            3: "域名不存在 (NXDOMAIN)",
            4: "查询类型未实现 (NOTIMP)",
            5: "查询被拒绝 (REFUSED)",
        }
        return rcode_map.get(rcode,"未知(UNKNOWN)")
class DnsHeader:
    transaction_id:int
    flags:DnsFlags
    question:int
    answer:int
    ns_answer:int
    ex_answer:int
    def __init__(self,transaction_id:int=0,flags: Optional[DnsFlags] = None,question:int=0,answer:int=0,ns_answer:int=0,ex_answer:int=0):
        self.transaction_id=transaction_id
        if flags is None:
            self.flags = DnsFlags()
        else:
            self.flags = flags
        self.question=question
        self.answer=answer
        self.ns_answer=ns_answer
        self.ex_answer=ex_answer
    @classmethod
    def from_bytes(cls, byte:bytearray):
        inst=cls()
        inst.transaction_id=int.from_bytes(byte[:2], 'big')
        inst.flags=DnsFlags.from_bytearray(byte[2:4])
        inst.question=int.from_bytes(byte[4:6], 'big')
        inst.answer=int.from_bytes(byte[6:8], 'big')
        inst.ns_answer=int.from_bytes(byte[8:10], 'big')
        inst.ex_answer=int.from_bytes(byte[10:12], 'big')
        print("transaction_id",inst.transaction_id)
        return inst
    def to_bytearray(self)->bytearray:
        byte=bytearray()
        byte+=self.transaction_id.to_bytes(2,'big')
        byte+=self.flags.to_bytearray()
        byte+=self.question.to_bytes(2,'big')
        byte+=self.answer.to_bytes(2,'big')
        byte+=self.ns_answer.to_bytes(2,'big')
        byte+=self.ex_answer.to_bytes(2,'big')
        return byte
    def print_member(self,show_flags:bool=True)->None:
        print(self.to_bytearray().hex())
        print("transaction_id",self.transaction_id)
        if show_flags:
            print("flags")
            self.flags.print_member()
        else:
            print("flags",self.flags.to_bytearray().hex())
        print("question",self.question)
        print("answer",self.answer)
        print("ns_answer",self.ns_answer)
        print("ex_answer",self.ex_answer)
        return