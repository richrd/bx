from mod_base import *

class Calc(Command):
    """Calculate math expressions. e.g. calc 3+4*6"""

    def run(self, win, user, data, caller=None):
        """Evaluate a python expression semi-safely."""
        if not data:
            win.Send("specify what to calculate")
        else:
            try:
                # Remove quotes to prevent attacks like "spam"*100000
                data = data.replace("\"", "")
                data = data.replace("'", "")
                result = eval(data, {"__builtins__": {}})
                win.Send(str(result))
            except:
                win.Send("failed to calculate")

module = {
    "class": Calc,
    "type": MOD_COMMAND,
    "level": 0,
}
