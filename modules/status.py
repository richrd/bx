# -*- coding: utf-8 -*-
from mod_base import *

class Status(Command):
    """Get status information of the host running the bot."""

    def run(self, win, user, data, caller=None):
        items = self.get_items()
        strs = []
        for item in items:
            strs.append( item[0] + ":" + str(item[1]) )
        win.Send(", ".join(strs))      

    def get_items(self):
        items = []
        power = self.get_power_state()
        bat = "!"
        if power:
            if power[0]:
                bat = "+"
            bat += str(power[1])
            items.append(("bat", bat))

        temp = self.get_temp()
        if temp: items.append(("temp", temp))

        load = self.get_sys_laod()
        if load: items.append(("load", load))
           
        link = self.get_wifi_quality()
        if link: items.append(("link", link))

        return items

    def get_power_state(self):
        output = run_shell_cmd("acpi").lower()
        if output.find("not found") == -1:
            parts = output.split(",")
            state = False
            raw_state = parts[0][parts[0].find(":") + 1:].strip()
            if raw_state == "full":
                state = True
            percent = int(parts[1].replace("%","").strip())
            return [state,percent]
        else:
            return False

    def get_wifi_quality(self):
        output = run_shell_cmd("iwconfig")
        start = "Link Quality="
        if output.find(start) != -1:
            part = output[output.find(start) + len(start):]
            part = part[:part.find(" ")]
            return part
        return False

    def get_sys_laod(self):
        uptime = run_shell_cmd("uptime")
        if uptime:
            load = " ".join(uptime.split(" ")[-3:]).replace(", ", " ").replace(",", ".")
            return load
        return False

    def get_temp(self):

        try:
            # lm-sensors
            line = run_shell_cmd("sensors | grep Core")
            start = "+"
            end = "°C"
            if line.find(start) != -1 and line.find(end) != -1:
                line = line[line.find(start) + 1:]
                temp = float(line[:line.find(end)])
                return temp
        except:
            pass

        try:
            # Raspberry Pi
            line = run_shell_cmd("/opt/vc/bin/vcgencmd measure_temp")
            temp = float(get_string_between("temp=","'",line))
            return temp
        except:
            pass
            
        return False

module = {
    "class": Status,
    "type": MOD_COMMAND,
    "level": 0,
    "aliases": ["sta"],
}
