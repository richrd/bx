from mod_base import *
import re, string

# Try to respond to verbal queries without fancy logic

class UnknownCMD(Listener):
    """Intercept unknown commands and try to respond. Experimental!"""
    def init(self):
        self.events = [IRC_EVT_UNKNOWN_CMD]
        self.happy_smileys = [":D",":)",":>","=)","=>","xD",":P","=P","=]",":]","=}",":}","(:"]
        self.sad_smileys = [":(","=(",":[","=[",":{","={",":/",":\\"]
        
        self.replacements = {
            # Questions
            "whos": "who is",
            "whats": "what is",
            "wat":"what",
            "wut":"what",
            "wuts": "what is",
            "whens": "when is",
            "whr": "where",
            "wheres": "where is",
            "whys": "why is",
            "why's": "why is",
            "hows": "how is",
            "abt": "about",

            # Abbreviations
            "r": "are",
            "u": "you",
            "yo": "you",
            "ur": "your",
            "doin": "doing",
            "kool'": "cool",
            "livin": "living",
            "thnx": "thanks",
            "thx": "thanks",
            "m/f": "male or female",
            "f/m": "male or female",
            "m / f": "male or female",
            "f / m": "male or female",
            "wbu": "what about you",
            "fack": "fuck",
            "frm": "from",
            "m or f": "male of female",
            "f or m": "male of female",

            "lvl": "level",

            "hii": "hi",
            "heyy": "hey",
            "heya": "hey",

            "wassup": "what is up",
            "/w": "with",

            "im": "i am",
            "som": "some",
            "drinkin": "drinking",
            "wanna": "want to",
            "coz": "because",
        }

        self.responses = [
            ("what your name", "my name is [nick]"),
            ("what are you", "I'm an IRC bot. What about you, mortal?"),
            ("who are you", "I'm [nick]"),
            ("who you trust", "I trust [trusted_users]"),
            ("where you live", "i live at [source_link]"),
            ("how old you", "I'm eternal and immortal, but i've been here since [time_connected]"),
            ("channels you on", "I'm hanging out on [channel_names]"),
            ("are you bot", "yep, call me [nick]"),
            ("what you do", "say help or cmds to know what I do"),
            ("what commands", "you can use the following commands: [command_names]"),
            ("where you", "I'm at [channel_names]"),
            ("where we", "we're at [current_win]"),
            ("what time", "the time is [current_time]"),
            ("many users", "I know [user_count] users"),
            ("many channels", "I know [channel_count] channels"),
            ("am i vip", "[user_authed]"),
            ("like me", "me is liek a bot."),
            ("my level", "your level is [user_level]"),
            ("trust me", "[trust]"),
            ("what up", "just stalking..."),
            ("use you", "say help and I'll tell you"),
            ("hello", "hi [user_nick]"),
            ("hi", "greetings [user_nick]"),
            ("you", "me? dunno."),
            ("me", "i don't know about you"),
            ("nom", "so munchy, so nom"),
            ("doge", "yeah me so doge"),
            ("if", "maybe!"),
            ("here", "or maybe there? or somewhere else..."),
            ("what", "no idea"),
            ("party", "party so hard!"),
        ]

        self.substitutions = {
            "user_count": lambda event: len(self.bot.users),
            "channel_count": lambda event: len([win for win in self.bot.windows if win.zone == IRC_ZONE_CHANNEL]),
            "time_connected": lambda event: time_stamp_numeric(self.bot.connection_time),
            "channel_names": lambda event: ", ".join([win.name for win in self.bot.windows if win.zone == IRC_ZONE_CHANNEL]),
            "command_names": lambda event: ", ".join(self.bot.GetCommandsByPermission(event.user.GetPermission())),
            "current_win": lambda event: event.win.GetName(),
            "nick": lambda event: self.bot.me.GetNick(),
            "user_nick": lambda event: event.user.GetNick(),
            "user_level": lambda event: event.user.GetPermission(),
            "user_authed": lambda event: "yes" if event.user.IsAuthed() else "no",
            "trust": lambda event: "yes sir!" if event.user.IsAuthed() else "nah, you better auth if you want trust",
            "current_time": lambda event: time_stamp_short(),
            "source_link": "https://github.com/richrd/bx",
            "trusted_users": lambda event: ", ".join([user.nick for user in self.bot.users if user.IsAuthed() and user.IsOnline()] or "nobody"),
        }

    def event(self, event):
        data = event.cmd
        if event.cmd_args:
            data += " " + event.cmd_args
        data = " " + data + " "
        sentences = re.findall('[\w\d][\w\d\s]*[^\.\!\?]*[\.\!\?]*', data)
        if sentences:
            for sentence in sentences:
                reply = self.GetReply(sentence)
                if reply:
                    reply = self.SubstituteReply(reply, event)
                    event.win.Send(reply)
                    return True

    def SubstituteReply(self, reply, event):
        for key in self.substitutions.keys():
            subst = self.substitutions[key]
            if type(subst) != type(""):
                subst = str(subst(event))
            reply = reply.replace("["+key+"]", subst)
        return reply

    def GetReply(self, data):
        data = self.ReplaceWords(data)
        words = self.GetWords(data)
        print data, words
        for s_in, s_out in self.responses:
            resp_list = s_in.split(" ")
            if self.WordsInSequence(words, resp_list):
                return s_out
        return False


    def GetWords(self, data):
        return re.findall('[\w]+[\ ]*', data)

    # Check wether the list of words, contains the
    # words of a given sequence in the right order
    def WordsInSequence(self, words, sequence, debug=0):
        i = 0
        print words, len(words), sequence, len(sequence)
        for word in words:
            word = word.strip()
            if word == sequence[i]:
                if i == len(sequence) - 1:
                    return True
                i += 1
        return False

    def ReplaceWords(self, data):
        """Replace words with normalized equivalents"""
        words = re.findall('[\w]*', data)
        new = []
        for word in words:
            if word in self.replacements.keys():
                word = self.replacements[word]
            new.append(word)
        return " ".join(new)





module = {
    "class": UnknownCMD,
    "type": MOD_LISTENER,
}