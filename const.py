"""
Constants used for irc and botz
"""
# Modes
IRC_MODE_CHR_NONE = ""
IRC_MODE_CHR_OP = "@"
IRC_MODE_CHR_VOICE = "+"
IRC_MODE_VOICE = u"v"
IRC_MODE_OP = u"o"

# Different types of windows used for irc
IRC_ZONE_SERVER = 0
IRC_ZONE_QUERY = 1
IRC_ZONE_CHANNEL = 2
IRC_ZONE_BOTH = 3

# Events
IRC_EVT_ANY = "any"
IRC_EVT_CONNECTED = "connected"
IRC_EVT_READY = "ready"
IRC_EVT_I_JOINED = "ijoined"
IRC_EVT_CHAN_JOIN = "join"
IRC_EVT_CHAN_PART = "part"
IRC_EVT_CHAN_KICK = "kick"
IRC_EVT_CHAN_MSG = "chanmsg"
IRC_EVT_CHAN_TOPIC = "topic"
IRC_EVT_USER_QUIT = "join"
IRC_EVT_USER_AUTHED = "authed"
IRC_EVT_MSG = "msg"
IRC_EVT_PRIVMSG = "privmsg"
IRC_EVT_CHAN_MODE_CHANGE = "chanmodechng"
IRC_EVT_CHAN_USER_MODE_CHANGE = "chanusermodechng"

# Bot specific
IRC_EVT_UNKNOWN_CMD = "unknowncmd"

MOD_COMMAND = 1
MOD_LISTENER = 2
MOD_BOTH = 3
