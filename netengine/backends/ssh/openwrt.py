"""
Class to extract information from  OpenWRT devices
"""

__all__ = ['OpenWRT']


from netengine.backends.ssh import SSH
import json

class OpenWRT(SSH):
    """
    OpenWRT SSH backend
    """
    
    _dict = {}

    def __str__(self):
        """ print a human readable object description """
        return u"<SSH (OpenWRT): %s@%s>" % (self.username, self.host)

    @property
    def name(self):
        """ get device name """
        return self.run('uname -a').split(' ')[1]

    @property
    def os(self):
        """ get os name and version, return as tuple """
        # cache command output
        output = self.run('cat /etc/openwrt_release')

        # init empty dict
        info = {}

        # loop over lines of output
        # parse output and store in python dict
        for line in output.split('\n'):
            # tidy up before filling the dictionary
            key, value = line.split('=')
            key = key.replace('DISTRIB_', '').lower()
            value = value.replace('"', '')
            # fill!
            info[key] = value

        os = info['id']
        version = info['release']

        if info['description']:

            if info['revision']:
                additional_info = "%(description)s, %(revision)s" % info
            else:
                additional_info = "%(description)s" % info

            # remove redundant OpenWRT occuerrence
            additional_info = additional_info.replace('OpenWrt ', '')

            version = "%s (%s)" % (version, additional_info)

        return (os, version)
    
    @property
    def _ubus_call(self):
        self._dict = json.loads(self.run('ubus call network.device status'))
    
    @property
    def _ubus_interface_infos(self):
        """
        returns a list of dict with infos about the interfaces
        """
        list = []
        for interface in self.run('ubus list').split():
            if "network.interface." in interface:
                list.append(json.loads(self.run('ubus call '+ interface + ' status')))
        return list
    
    @property
    def interfaces_to_dict(self):
        if not self._dict:
            self._ubus_call
        for interface in self._ubus_interface_infos:
            for key, values in interface.iteritems():
                self._dict[interface["l3_device"]][str(key)] = values
        return self._dict
    
    @property
    def model(self):
        """ get device model name, eg: Nanostation M5, Rocket M5 """
        output = self.run('iwinfo | grep -i hardware')

        if "not found" in output:
            return None
        elif "Usage" in output:
            return None
        # will return something like
        # Hardware: 168C:002A 0777:E805 [Ubiquiti Bullet M5]
        # and we'll extract only the string between square brackets
        else:
            return output.split('[')[1].replace(']','')
        
    @property
    def wireless_mode(self):
        """ retrieve wireless mode (AP/STA) """

        output = self.run("iwconfig 2>/dev/null | grep Mode | awk '{print $4}' | awk -F ':' '{print $2}'")
        output = output.strip()

        if output == "Master":
            return "ap"
        else:
            return "sta"

    @property
    def RAM_total(self):
        return int(self.run("cat /proc/meminfo | grep MemTotal | awk '{print $2}'"))

    @property
    def uptime(self):
        """
        returns an integer representing the number of seconds of uptime
        """
        output = self.run('cat /proc/uptime')
        seconds = float(output.split()[0])
        return int(seconds)
    
    def get_manufacturer_of_interfaces(self):
        """
        returns a list containing the manufacturer of the device interfaces
        """
        interfaces_mac = []
        if not self._dict:
            self._ubus_call
        for interface in self._dict.keys():
            interfaces_mac.append(self.get_manufacturer(str(interface)))
        return interfaces_mac[::-1]
        
    @property
    def uptime_tuple(self):
        """
        Return a tuple (days, hours, minutes)
        """
        uptime = float(self.run('cat /proc/uptime').split()[0])
        seconds = int(uptime)
        minutes = int(seconds // 60)
        hours = int(minutes // 60)
        days = int(hours // 24)
        output = days, hours, minutes
        return output

    def _filter_interfaces(self):
        """
        returns a list containing the device interfaces
        """
        if not self._dict:
            self._ubus_call
        return self._dict.keys()
        
    def _filter_routing_protocols(self):
        results = []
        olsr = self.olsr
        if olsr:
            results.append(self._dict({
            "name" : "olsr",
            "version" : olsr[0]
            }))
        return results

    def to_dict(self):
        return self._dict({
            "name": self.name,
            "type": "radio",
            "os": self.os[0],
            "os_version": self.os[1],
            "manufacturer": self.get_manufacturer_of_interfaces(),
            "model": self.model,
            "RAM_total": self.RAM_total,
            "uptime": self.uptime,
            "uptime_tuple": self.uptime_tuple,
            "interfaces": self._filter_interfaces(),
            "interfaces_info": self.interfaces_to_dict,
            "antennas": [],
            "routing_protocols": self._filter_routing_protocols()
        })


