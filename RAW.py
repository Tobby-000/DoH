import random
import requests as req
import base64

type_map = {
    bytes.fromhex("0001"): "A",
    bytes.fromhex("001c"): "AAAA",
    bytes.fromhex("0005"): "CNAME",
    bytes.fromhex("000f"): "MX"
}
reverse_map = {v: k for k, v in type_map.items()}
def read_bytes(hex,index,len,is_int=False):
    if is_int:
        return int.from_bytes(hex[index:index+len]),index+len
    else:
        return hex[index:index+len],index+len
def hex_to_base64(hex):
    base64_bytes = base64.b64encode(hex)
    base64_str = base64_bytes.decode('ascii')
    base64_str=base64_str.replace('=', '')
    base64_str=base64_str.replace('+','-')
    base64_str=base64_str.replace('/', '_')
    return base64_str
def decode_RCODE(rcode):
    RCODE_map={
        0: "查询成功(SUCCESS)",
        1: "请求格式错误 (FORMERR)",
        2: "服务器内部错误 (SERVFAIL)",
        3: "域名不存在 (NXDOMAIN)",
        4: "查询类型未实现 (NOTIMP)",
        5: "查询被拒绝 (REFUSED)",
    }
    return RCODE_map.get(rcode,"未知错误(UNKNOWN)")
def domain_decode(index:int,hex,depth=0):#index索引，hex原始二进制，depth深度   输出domain解析后的域名，after_domain域名后的索引
    domain = ""
    after_domain=index
    i=0
    while i<10:
        if hex[after_domain]&0xC0==0xC0:
            if after_domain!=index:
                domain+="."
            pos = int.from_bytes(hex[after_domain:after_domain+2])-0XC000
            if hex == "":
                print("domain_decode ERROR:full_hex is empty")
            if depth > 10:
                print("domain_decode ERROR:depth is too high")
            domain_full, pos = domain_decode(pos, hex, depth + 1)
            domain += domain_full
            after_domain += 2
            break
        else:
            domain_num=hex[after_domain]
            if domain_num==0:
                after_domain=after_domain+1
                if after_domain==index:
                    domain+="."
                break
            if after_domain!=index:
                domain+="."
            domain_sp=hex[after_domain+1:after_domain+domain_num+1].decode('ascii')
            domain+=domain_sp
            after_domain+=1+domain_num
            i+=1
    return domain,after_domain
def type_coder(data,reserve=0):
    if reserve:
        return reverse_map.get(data, "0001")
    else:
        return type_map.get(data, "UNKNOWN")
def decode_A(data):
    i=0
    result=""
    while i<4:
        data_sp=str(data[i])
        result+=data_sp
        if i!=3:
            result+="."
        i+=1
    return result
def decode_CNAME(index,full_hex):
    cname,_=domain_decode(index,full_hex)
    return cname
def decode_AAAA(data):
    group=[]
    ipv6=""
    for i in range(0,16,2):
        group.append(data[i:i+2].hex())
    for g in group:
        ipv6+=format(int(g,16),"x")+":"
    ipv6=ipv6[:-1]
    return ipv6
def query(q_domain="",q_type=""):
    if q_domain == "":
        q_domain=input("请输入查询需要查询的域名")
    if q_type == "":
        q_type=input("请输入想要的类型，A，AAAA,CNAME,MX(输入错误则默认A)").upper()
    type_hex=type_coder(q_type,1)
    domainsp=q_domain.split(".")
    domainhex=bytearray()
    for sp in domainsp:
        domainhex.append(len(sp))
        domainhex+=sp.encode('ascii')
    domainhex.append(0)
    txid_hex=bytearray()
    txid_hex.append(random.randint(0, 255))
    txid_hex.append(random.randint(0, 255))
    print("事务ID：",txid_hex.hex())
    base64str=txid_hex+bytearray.fromhex("01000001000000000000")+domainhex+type_hex+bytearray.fromhex("0001")
    reqstr="https://223.5.5.5/dns-query?dns="+hex_to_base64(base64str)
    headers = {
        'accept': 'application/dns-message'
    }
    print("request:"+reqstr)
    resp=req.get(reqstr,headers=headers)
    reshex=resp.content
    print("Raw Response:",reshex.hex())
    # 头部解码
    if reshex[0:2]!=txid_hex:
        print("ERROR")
        return
    flag_hex=bytearray(reshex[2:4])
    print("---响应解析---")
    print("权威解析" if int(flag_hex[0])>>2&1 else "非权威解析")
    print(decode_RCODE(flag_hex[1]&15))
    if flag_hex[1]&15!=0:
        return
    # 回复数解码
    res_num=int.from_bytes(reshex[6:8])
    print("回复数量:",res_num)
    index=12
    # 回复解码
    if res_num>0:
        domain,index= domain_decode(index,reshex)
        type_hex,index = read_bytes(reshex,index,2)
        type=type_coder(type_hex)
        class_hex,index= read_bytes(reshex,index,2)
        class_name=""
        if class_hex==bytes.fromhex("0001"):
            class_name += "IN"
        print("问题: domain=",domain,"type=",type,"class=",class_name)
        print('{0:<20}{1:<7}{2:<6}{3:<}'.format("domain", "type","ttl","result"))
        # 回答解码
        for i in range(res_num):
            res_domain,index=domain_decode(index,reshex)
            type_hex, index = read_bytes(reshex, index, 2)
            type = type_coder(type_hex)
            class_hex, index = read_bytes(reshex, index, 2)
            class_name = ""
            if class_hex == bytes.fromhex("0001"):
                class_name += "IN"
            ttl,index=read_bytes(reshex,index,4,True)
            rd_len,index=read_bytes(reshex,index,2,True)
            rd_start=index
            rd_data_hex,index=read_bytes(reshex,index,rd_len)
            rd_data=""
            if type=="A":
                rd_data+=decode_A(rd_data_hex)
            if type=="CNAME":
                rd_data+=decode_CNAME(rd_start,reshex)
            if type=="MX":
                rd_data+=str(int.from_bytes(rd_data_hex[:2]))+"  "
                rd_data+=decode_CNAME(rd_start+2,reshex)
            if type=="AAAA":
                rd_data+=decode_AAAA(rd_data_hex)
            print('{0:<20}{1:<7}{2:<6}{3:<}'.format(res_domain,type,ttl,rd_data))

if __name__ == '__main__':
    while True:
        query()