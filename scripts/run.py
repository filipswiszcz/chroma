import socket
import struct


def test_dns_lookup(domain):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)

    dns_server = "8.8.8.8"
    dns_port = 53

    trans_id = b'\x12\x34'
    header = trans_id + b'\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'

    qname = b''
    for i in domain.split("."):
        qname += bytes([len(i)]) + i.encode("ascii")
    qname += b'\x00'

    quest = qname + b'\x00\x01\x00\x01'
    query = header + quest

    sock.sendto(query, (dns_server, dns_port))
    response, _ = sock.recvfrom(1024)

    ans_start = 12 + len(qname) + 4
    ans = response[ans_start:]
    
    ip_b = ans[-4:]
    ip = socket.inet_ntoa(ip_b)
    sock.close()
    
    return ip

def run():
    try:
        ip = test_dns_lookup("youtube.com")
        print(f"domain=youtube.com, ip={ip}")
    except Exception as e:
        print(f"DNS lookup err: {e}")


if __name__ == "__main__":
    run()