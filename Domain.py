def domain_encoder(domain:str)->bytearray:
    domain_sp=domain.split(".")
    domain_hex=bytearray()
    for sp in domain_sp:
        domain_hex.append(len(sp))
        domain_hex+=sp.encode('ascii')
    domain_hex.append(0)
    return domain_hex
def domain_decoder(index:int,domain_hex,depth=0):#index索引，domain_hex原始二进制，depth深度   输出domain解析后的域名，after_domain域名后的索引
    domain = ""
    after_domain=index
    i=0
    while i<10:
        if domain_hex[after_domain]&0xC0==0xC0:
            if after_domain!=index:
                domain+="."
            pos = int.from_bytes(domain_hex[after_domain:after_domain+2])-0XC000
            if domain_hex == "":
                print("domain_decode ERROR:full_domain_hex is empty")
            if depth > 10:
                print("domain_decode ERROR:depth is too high")
            domain_full, pos = domain_decoder(pos, domain_hex, depth + 1)
            domain += domain_full
            after_domain += 2
            break
        else:
            domain_num=domain_hex[after_domain]
            if domain_num==0:
                after_domain=after_domain+1
                if after_domain==index:
                    domain+="."
                break
            if after_domain!=index:
                domain+="."
            domain_sp=domain_hex[after_domain+1:after_domain+domain_num+1].decode('ascii')
            domain+=domain_sp
            after_domain+=1+domain_num
            i+=1
    return domain,after_domain