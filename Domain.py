class Domain:
    string:str
    hex:bytearray
    after:int
    def __init__(self,domain_str:str="",domain_hex:bytearray=None,after_domain:int=None):
        self.string=domain_str
        self.hex=domain_hex
        self.after=after_domain
        return
    def encoder(self)->bytearray:
        domain_sp=self.string.split(".")
        domain_hex=bytearray()
        for sp in domain_sp:
            domain_hex.append(len(sp))
            domain_hex+=sp.encode('ascii')
        domain_hex.append(0)
        self.hex=domain_hex
        return domain_hex
    @classmethod
    def decoder(cls,index:int,byte:bytearray):# index 域名起始索引，byte完整二进制
        pos:int=index #当前解析指针
        after_pos:int=index #解析结束后指针
        inst=cls() # 返回对象
        i=0 #迭代上限，包括域名字符解析和指针
        is_po=False #如果在index都出现压缩指针，则将解析后位置挪动到指针后
        pos_array=set()
        pos_array.add(index)
        while i<10:
            if byte[pos]&0XC0==0XC0:#压缩指针处理
                if not is_po:
                    after_pos=pos+2#结束指针挪动到压缩指针后
                    is_po=True
                pos=int.from_bytes(byte[pos:pos+2], 'big')&0X3fff
                if pos in pos_array:
                    print("ERROR:指针循环")#循环判定
                    raise Exception("指针循环")
                pos_array.add(pos)
            else:
                char_num=byte[pos]
                pos+=1
                if char_num==0:# 如果为0则到达域名末端
                    if pos==index+1:#处理根域
                        inst.string+="."
                    if is_po:
                        inst.after=after_pos
                    else:
                        inst.after=pos
                    return inst
                try:
                    char=byte[pos:pos+char_num].decode('ascii')#主解码
                except UnicodeDecodeError:
                    raise ValueError("解码错误，未知字符")
                inst.string+=char+"."#域名分割
                pos=pos+char_num
            i+=1
        raise Exception("超过循环上限")