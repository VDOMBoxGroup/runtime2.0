
from builtins import str
from builtins import map
import os
import re


rexp = re.compile(r"vr0\:.+inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+netmask\s+(\S+)\s", re.IGNORECASE | re.DOTALL)


def get_ip_and_mask():
    # return (ip, mask)
    try:
        f = os.popen("ifconfig vr0")
        outp = f.read()
        f.close()
        ret = rexp.search(outp, 0)
        if ret and ret.group():
            the_ip = ret.group(1)
            the_mask = ret.group(2)
            m = int(the_mask, 16)
            parts = [255 & (m >> 24), 255 & (m >> 16), 255 & (m >> 8), 255 & m]
            the_mask = ".".join(map(str, parts))
            return (the_ip, the_mask)
    except Exception as e:
        debug("Error: " + str(e))
    return (None, None)


def set_ip_and_mask(ip, mask):
    f = os.popen("ifconfig vr0 inet %s netmask %s" % (ip, mask))
    outp = f.read()
    f.close()

rexp1 = re.compile(r"gateway: (\S+)", re.IGNORECASE | re.DOTALL)


def get_default_gateway():
    try:
        f = os.popen("route -n get default")
        outp = f.read()
        f.close()
        ret = rexp1.search(outp, 0)
        if ret and ret.group():
            gate = ret.group(1)
            return gate
    except Exception as e:
        debug("Error: " + str(e))
    return None


def set_default_gateway(gate):
    try:
        f = os.popen("route delete default")
        outp = f.read()
        f.close()
        f = os.popen("route add default " + gate)
        outp = f.read()
        f.close()
    except Exception as e:
        debug("Error: " + str(e))


def get_dns():
    pdns = sdns = ""
    try:
        f = open("/etc/resolv.conf", "rt")
        data = f.read()
        f.close()
        x = data.splitlines()
        if len(x) > 0:
            pdns = x[0]
            if pdns.startswith("nameserver"):
                pdns = pdns[10:].strip()
            else:
                pdns = ""
        if len(x) > 1:
            sdns = x[1]
            if sdns.startswith("nameserver"):
                sdns = sdns[10:].strip()
            else:
                sdns = ""
    except Exception as e:
        debug("get_dns: " + str(e))
    return (pdns, sdns)


def set_dns(pdns, sdns):
    try:
        a = b = ""
        if pdns:
            a = "nameserver " + pdns
        if sdns:
            b = "nameserver " + sdns
        f = open("/etc/resolv.conf", "wt")
        f.write("\n".join([a, b]))
        f.close()
    except Exception as e:
        debug("Error: " + str(e))


def get_date_and_time():
    try:
        f = os.popen('date "+%Y%m%d%H%M.%S"')
        outp = f.read()
        f.close()
        outp = outp.strip()
        if 15 == len(outp):
            the_date = "%s.%s.%s %s:%s" % (outp[:4], outp[4:6], outp[6:8], outp[8:10], outp[10:])
            return the_date
    except Exception as e:
        debug("Error: " + str(e))
    return None

rexp2 = re.compile(r"/dev/ad4f\s+\S+\s+\S+\s+(\S+)", re.IGNORECASE | re.DOTALL)


def get_free_space():
    try:
        f = os.popen("df -m")
        outp = f.read()
        f.close()
        ret = rexp2.search(outp, 0)
        if ret and ret.group():
            x = ret.group(1)
            return int(x) / 1024.0
    except Exception as e:
        debug("Error: " + str(e))
    return 0

rexp3 = re.compile(r"/dev/ad4f\s+\S+\s+(\S+)\s+(\S+)", re.IGNORECASE | re.DOTALL)


def get_hd_size():
    try:
        f = os.popen("df -m")
        outp = f.read()
        f.close()
        ret = rexp3.search(outp, 0)
        if ret and ret.group():
            x = ret.group(1)
            y = ret.group(2)
            return (int(x) + int(y)) / 1024.0
    except Exception as e:
        debug("Error: " + str(e))
    return 0


def get_external_drives():
    result = []
    f = os.popen("ls /dev/da*")
    outp = f.read()
    f.close()
    k = 0
    while True:
        p = "/dev/da%ds1" % k
        if -1 == outp.find(p):
            break
        result.append("da%ds1" % k)
        k += 1
    return [{"device": "/dev/%s" % d, "label": d} for d in result]


def device_exists(dev):
    return os.path.exists(dev)


def mount_device(dev):

    if not os.path.isdir("/mnt/dev"):
        os.mkdir("/mnt/dev")
    if not os.path.isdir("/mnt/" + dev):  # /mnt/dev/da1s1
        os.mkdir("/mnt/" + dev)
    f = os.popen("/sbin/mount -t msdos %s /mnt/%s" % (dev, dev))
    outp = f.read()
    f.close()
    return "/mnt/" + dev


def umount_device(dev):
    f = os.popen("/sbin/umount /mnt/%s" % dev)
    outp = f.read()
    f.close()


def get_vfs_users():
    r = []
    f = os.popen("/sbin/vfs_users")
    userlist = f.read()
    f.close()
    ll = userlist.splitlines()
    for s in ll:
        i = s.find(":")
        if i < 0:
            i = len(s)
        r.append(s[:i])
    return r


def move(src, dst):
    try:
        subprocess.check_call(["mv", src, dst])
    except CalledProcessError as e:
        debug("Error: return code: %s" % str(e))
        managers.log_manager.error_server("System call error: %s" % str(e), "system_freebsd")


def copy(src, dst):
    try:
        subprocess.check_call(["cp", src, dst])
    except CalledProcessError as e:
        debug("Error: return code: %s" % str(e))
        managers.log_manager.error_server("System call error: %s" % str(e), "system_freebsd")
