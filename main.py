from DnsHeader import DnsHeader
from Domain import Domain
if __name__ == "__main__":
    dns_data=bytearray()
    dns_data+=bytes.fromhex("d06d8180000100010000000103777777076b6f6d6f6e6d6302636e0000010001c00c000100010000025800046e2a6d7700002904d0000000000000")
    print("RAW dns_data",dns_data.hex())
    dns_header=DnsHeader.from_bytes(dns_data)
    dns_header.print_member()
    domain=Domain()
    domain=domain.decoder(32,dns_data)
    print(domain.string)
    print("ababa")