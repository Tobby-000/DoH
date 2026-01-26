def read_bytes(index:int,byte,lenth:int,to_int:bool=False):
    if to_int:
        return int.from_bytes(byte[index:index+lenth]),index+lenth
    else:
        return byte[index:index+lenth],index+lenth

