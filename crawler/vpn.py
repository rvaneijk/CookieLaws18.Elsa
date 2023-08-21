# Cookie Laws project vpn utilities
from __future__ import absolute_import, division, print_function
from abc import ABCMeta, abstractmethod
from subprocess import call, check_output, CalledProcessError
from os import path
from time import sleep
try:
    import requests  # insall from pip; required for VPN-utils function
except ImportError:
    pass


class VPN:
    __metaclass__ = ABCMeta

    @abstractmethod
    def connect(self, cc, disconnect_first, override_ns, timeout):
        pass

    @abstractmethod
    def disconnect(self, timeout):
        pass

    @abstractmethod
    def is_connected(self):
        pass

    def __del__(self):
        self.disconnect(timeout=None)


class VPNutil:
    @staticmethod
    def is_route0_via_tun():
        with open("/proc/net/route") as f:
            s = f.readlines()
            # find 0.0.0.0 routes to a tunX interface
            s = [ss for ss in s if ss.startswith("tun") and ss.split("\t")[1] == "00000000"]
        return len(s)

    @staticmethod
    def get_public_ip():
        ip = requests.get("https://api.ipify.org").text
        return ip

    @staticmethod
    def override_nameserver():
        call(["sudo", "bash", "-c", "echo 'nameserver 8.8.8.8' > /etc/resolv.conf"])  # on Linux
        sleep(1)

    @staticmethod
    def reset_nameserver():
        # we reset nameserver by reconnecting the interface (works on Fedora; possibly other Linux)
        # we need to find the default interface first (could use 'route' command too)
        # Q: is there a better/faster way?
        #    (nmcli dev up same; ifcfg?; NOT: dhclient/dnsmasq/resolvconf)

        iface = None
        for s in open('/proc/net/route').readlines():
            ss = s.split('\t')
            if ss[1] == "00000000":
                iface = ss[0]
                break
        call(["sudo", "bash", "-c", "nmcli conn up ifname %s" % iface])
        sleep(1)  # for routes to resettle on multihomed systems

    @staticmethod
    def get_nameserver():
        out = check_output(["bash", "-c", "dig something.unknown  | grep SERVER:"])
        return out.strip()

    @staticmethod
    def ping(dest):
        try:
            out = check_output(["ping", dest, "-n", "-c 1", "-q", "-w 2"]).splitlines()
        except CalledProcessError as pe:
            if pe.returncode == 1:
                out = pe.output.splitlines()
                out.append("rtt min/avg/max/mdev = timeout/timeout/timeout/timeout")
            else:
                return "PING ERROR %s (host unknown? code: %d)" % (dest, pe.returncode)

        # assert 3 < len(out) < 10
        s = "PING " + dest
        s += " => " + out[0][5:].replace("56(84) bytes of data.", "")
        s += "=> " + out[-1].split('/')[4]
        return s

    # Possible util extensions:
    # Speed test:
    #   call(["speedtest-cli"])  # pip install speedtestcli.
    # Host to IP
    #   try: ip = socket.gethostbyname(r.site)
    #   except socket.gaierror: ip = '0.0.0.0'
    # IP to CC:
    #   geodb = pygeoip.GeoIP("...", pygeoip.MEMORY_CACHE)
    #   cc0 = geodb.country_code_by_addr(ip0)
    #   or geoip.hidemyass.com / iplocation.net / ripe / ...

    @staticmethod
    def wait_then_assert(condition_method, condition_value, timeout):
        assert callable(condition_method)
        for t in range(timeout):  # here timeout=0 means don't wait (not infinity)
            if condition_method() == condition_value:
                break
            sleep(1)
        assert condition_method() == condition_value


class VPN_HMA(VPN):
    # HideMyAss VPN

    def __init__(self, user_cred_file):
        self.creds = user_cred_file
        our_dir = path.dirname(path.realpath(__file__))
        self.script = path.join(path.join(our_dir, "vpn-scripts"), "vpn-hma.sh")
        assert path.isfile(self.script)
        self.prot = "udp"

    def __str__(self):
        return "VPN-HMA"

    def server(self, cc):
        # HMA works with both .UK & .GB -- we'll keep .UK as that's the TLD
        return cc.lower() + ".hma.rocks"

    def is_connected(self):
        r = call(["sudo", "bash", "-c", "%s -s" % self.script])  # returns 0 if vpn connected
        return r == 0

    def connect(self, cc, disconnect_first=True, override_nameserver=True, timeout=30):
        assert len(cc) == 2
        if disconnect_first and self.is_connected():
            self.disconnect(reset_nameserver=override_nameserver)
        cmd = ["sudo", "bash", "-c",  # works more reliability with sudo
               "%s -d -c %s -p %s %s" % (self.script, self.creds, self.prot, self.server(cc))]
        call(cmd)
        if timeout:
            VPNutil.wait_then_assert(self.is_connected, True, timeout)
        if override_nameserver:
            VPNutil.override_nameserver()
        sleep(1)

    def disconnect(self, reset_nameserver=True, timeout=10):
        call(["sudo", "bash", "-c", "%s -x" % self.script])
        if timeout:
            VPNutil.wait_then_assert(VPNutil.is_route0_via_tun, False, timeout)
        if reset_nameserver:
            VPNutil.reset_nameserver()
        sleep(1)


# class VPN_CG(VPN):
#     # CyberGhost VPN
#
#     def connect(self,...):
#         l = ["sudo", "openvpn", "--config", "vpn_%s.ovpn" % VCC.lower()]
#         pvpn = Popen(l, cwd=OVPN_DIR)
#         wait(is_default_via_tun, 180)
#
#     def disconnect(self, ...):
#         try:
#             kill(pvpn.pid, 15)  # sometimes doesn't work and throws if not sudo?
#         except:
#             pass
#         sleep(15)
#         if is_proc_running('openvpn'):
#            call(["sudo", "killall", "openvpn"])
#
#     def is_proc_running(proc_name):
#         proc_name = proc_name.lower()
#         for pid in [p for p in listdir('/proc') if p.isdigit()]:
#             try:
#                 if proc_name in open(path.join('/proc', pid, 'cmdline'), 'rb').read().lower():
#                 return True
#             except IOError: # proc has already terminated
#                 continue
#         return False
