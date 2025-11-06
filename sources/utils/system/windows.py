
from builtins import str
import os
import re
import subprocess
import managers


rexp_ifconfig = re.compile(r"inet addr:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*Mask:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", re.IGNORECASE | re.DOTALL)
rexp_gateway = re.compile(r"^0\.0\.0\.0\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", re.IGNORECASE | re.DOTALL | re.MULTILINE)


def reinit_network():
    pass


def get_ip_and_mask(interface="eth0"):
    """return (ip, mask)"""
    return ("127.0.0.1", "255.0.0.0")


def set_ip_and_mask(ip, mask):
    pass


def get_default_gateway():
    pass


def set_default_gateway(gate):
    pass


def get_dns():
    pass


def set_dns(pdns, sdns):
    pass


def get_date_and_time():
    pass


def vdom_df():
    pass


def get_free_space():
    return 1024 * 1024 * 1024


def get_hd_size():
    return 1024 * 1024 * 1024


def get_external_drives():
    return ()


def device_exists(dev):
    pass


def mount_device(dev):
    """returns mountpoint of the device. raise CalledProcessError if can't"""
    pass


def umount_device(dev):
    pass


def get_vfs_users():
    pass


def move(src, dst):
    try:
        subprocess.check_call(["move", "/Y", os.path.abspath(src), os.path.abspath(dst)], shell=True)
    except Exception as e:
        debug("Error: return code: %s" % str(e))
        managers.log_manager.error_server("System call error: %s" % str(e), "system_windows")


def copy(src, dst):
    try:
        subprocess.check_call(["copy", os.path.abspath(src), os.path.abspath(dst), "/Y"], shell=True)
    except Exception as e:
        debug("Error: return code: %s" % str(e))
        managers.log_manager.error_server("System call error: %s" % str(e), "system_windows")
