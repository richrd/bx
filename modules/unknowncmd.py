from mod_base import *
import re, string, random

# Try to respond to verbal queries without (too) fancy logic.
# This is mainly just an experiment for fun,
# and for learning list comprehensions and regex.

class Context:
    def __init__(self, sentence):
        self.sentence = sentence
        self.words = self.GetWords(sentence)
        self.reply = ""
        self.context_values = {}

    def AssignContext(self, name, value):
        self.context_values[name] = value

    def ReplaceWords(self, replacements):
        i = 0
        new = []
        for word in self.words:
            if word.lower() in replacements.keys():
                repl = replacements[word.lower()]
                parts = repl.split(" ")
                for part in parts:
                    new.append(part)
            else:
                new.append(word)
            i += 1
        self.words = new or [""]

    def GetWords(self, data):
        words = re.findall('[\#\w\-]*', data)
        words = map(lambda s:s.strip(), words)
        words = [word for word in words if word != ""]
        return words

    def SetReply(self, reply):
        self.reply = reply

    def ChooseReply(self, replys):
        self.reply = random.choice(replys)

    def ReplaceReply(self):
        for key in self.context_values.keys():
            self.reply = self.reply.replace(key, self.context_values[key])

    def GetReply(self):
        return self.reply


class UnknownCMD(Listener):
    """Intercept unknown commands and try to respond. Experimental!"""
    def init(self):
        self.events = [IRC_EVT_UNKNOWN_CMD]
        self.happy_smileys = [":-)", ":)", ":D", ":>", "=)", "xD", ":P", "=P", "=]", ":]", "=}", ":}", "(:", ":3"]
        self.sad_smileys = [
            ("you listening", "yep, all the time [happy_smiley]"),":(", ";(", "=(", ":[", ";[", "=[", ":{", "={", ":/", ":\\", ";_;"]
        
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

            "gimme": "give me",

            # Abbreviations
            "r": "are",
            "u": "you",
            "yo": "you",
            "ur": "your",
            "youre": "you are",
            "doin": "doing",
            "kool'": "cool",
            "livin": "living",
            "thnx": "thanks",
            "thx": "thanks",
            "plz": "please",
            "m/f": "male or female",
            "f/m": "male or female",
            "m / f": "male or female",
            "f / m": "male or female",
            "wbu": "what about you",
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
            ("what your name", "My name is [my_nick]"),
            ("what are you", "I'm an IRC bot. What about you, mortal?"),
            ("what you do", "say help or cmds to know what I do"),
            ("what commands", "you can use the following commands: [command_names]"),
            ("what time", "the time is [current_time]"),
            ("who are you", [
                "I'm [my_nick]",
                "My name is [my_nick]",
            ]),
            ("who you trust", "I trust [trusted_users]"),
            ("who is [my_nick]", "hey thats me [happy_smiley]"),
            ("who is [known_nick]", "[known_nick] is my friend"),
            ("who is", "I don't know"),
            ("been to [unknown_channel]", "No i haven't"),
            ("been to [known_channel]", "Sure, [known_channel] is one of my favourite places"),
            ("what about [known_channel]", "I like it [happy_smiley]"),
            ("why are you", "I like to be"),
            ("are you friend", "yeah, ofcourse I am"),
            ("are you at [known_channel]", "yeah, I am"),
            ("are you bot", "yep, call me [my_nick]"),
            ("are you on [known_channel]", "Yeah, I'm on [known_channel]"),
            ("are you on [unknown_channel]", "No, I'm not there"),
            ("you listening", "yep, all the time [happy_smiley]"),
            ("where you live", "I live at [source_link]"),
            ("how old you", "I'm eternal and immortal, but i've been here since [time_connected]"),
            ("how many channels on", "I'm on [channel_count] channels"),
            ("where you", "I'm at [channel_names]"),
            ("where we", "we're at [current_win]"),
            ("give me", "sorry, I can't"),
            ("channels you on", "I'm hanging out on [channel_names]"),
            ("many users", "I know [user_count] users"),
            ("many channels", "I know [channel_count] channels"),
            ("am i vip", "[user_authed]"),
            ("like me", ["ofcourse.", "sure [happy_smiley]", "yeah [user_nick]"]),
            ("my level", "your level is [user_level]"),
            ("trust me", "[trust]"),
            ("do trust [authed_nick]", "ofcourse I trust [authed_nick]"),
            ("thanks", "no problem [user_nick] [happy_smiley]"),
            ("thank you", "your welcome [happy_smiley]"),
            ("sorry", "oh thats ok [user_nick]"),
            ("what up", "just stalking..."),
            ("nope", "not nope!"),
            ("use you", "say help and I'll tell you"),
            ("hate you", "[user_nick] makes me sad [sad_smiley]"),
            ("you stupid", "sry im not so smart [sad_smiley]"),
            ("beer", [
                        "yeah, I like beer",
                        "drink it!",
                        "if drinking beer, remember the Ballmer peak!",
                        "beer every day [happy_smiley]",
            ]),
            ("hello", "hi [user_nick], how are you?"),
            ("hi", "greetings [user_nick] [happy_smiley] can I help you?"),
            ("you", "me? dunno."),
            ("me", "i don't know about you"),
            ("nom", "so munchy, so nom [happy_smiley]"),
            ("doge", "yeah me so doge"),
            ("if", "maybe!"),
            ("here", "or maybe there? or somewhere else..."),
            ("what", "no idea"),
            ("party", "party so hard!"),
            ("dafuq", "dafuq you back"),
            ("", [
                "What [user_nick]?",
                "Yeah?",
                "Hi [user_nick]",
                ]),
        ]

        # Substitutions for replys
        self.reply_subst = {
            "user_count": lambda event: len(self.bot.users),
            "channel_count": lambda event: len([win for win in self.bot.windows if win.zone == IRC_ZONE_CHANNEL]),
            "time_connected": lambda event: time_stamp_numeric(self.bot.connection_time),
            "channel_names": lambda event: ", ".join([win.name for win in self.bot.windows if win.zone == IRC_ZONE_CHANNEL]),
            "command_names": lambda event: ", ".join(self.bot.GetCommandsByPermission(event.user.GetPermission())),
            "current_win": lambda event: event.win.GetName(),
            "my_nick": lambda event: self.bot.me.GetNick(),
            "user_nick": lambda event: event.user.GetNick(),
            "user_level": lambda event: event.user.GetPermission(),
            "user_authed": lambda event: "yes" if event.user.IsAuthed() else "no",
            "trust": lambda event: "yes sir!" if event.user.IsAuthed() else "nah, you better auth if you want trust",
            "current_time": lambda event: time_stamp_short(),
            "source_link": "https://github.com/richrd/bx",
            "trusted_users": lambda event: ", ".join([user.nick for user in self.bot.users if user.IsAuthed() and user.IsOnline()] or "nobody"),
            "happy_smiley": lambda event: random.choice(self.happy_smileys),
            "sad_smiley": lambda event: random.choice(self.sad_smileys),
        }

        # Substitution tests for inputs
        self.input_subst = {
            "known_nick": lambda word: word in [user.GetNick() for user in self.bot.users],
            "authed_nick": lambda word: word in [user.GetNick() for user in self.bot.users if user.IsAuthed()],
            "known_channel": lambda word: word in [win.name for win in self.bot.windows if win.zone == IRC_ZONE_CHANNEL],
            "unknown_channel": lambda word: self.bot.IsChannelName(word) and (not word in [win.GetName() for win in self.bot.windows if win.zone == IRC_ZONE_CHANNEL]),
            "my_nick": lambda word: word == self.bot.me.GetNick(),
        }

    def event(self, event):
        data = event.cmd
        if event.cmd_args:
            data += " " + event.cmd_args
        sentences = re.findall('[\w\d][\w\d\s]*[^\.\!\?]*[\.\!\?]*', data) or [""]
        matched = False
        for sentence in sentences:
            context = Context(sentence)
            match = self.Match(context)
            if match:
                matched = True
                context.ReplaceReply()
                reply = context.GetReply()
                reply = self.SubstituteReply(reply, event)
                event.win.Send(reply)
        return matched

    def Match(self, context):
        context.ReplaceWords(self.replacements)
        for data_in, data_out in self.responses:
            words_in = data_in.split(" ")
            if self.WordsInSequence(context, words_in):
                if type(data_out) == type([]):
                    context.ChooseReply(data_out)
                else:
                    context.SetReply(data_out)
                return True
        return False

    def WordsInSequence(self, context, sequence):
        i = 0
        for word in context.words:
            if i == len(sequence):
                break
            word = word.strip()

            if word == sequence[i]:
                i += 1
            else:
                found_var = self.FindInputSubst(sequence[i], word)
                if found_var:
                    context.AssignContext(sequence[i], word)
                    i += 1

        if i == len(sequence):
            return True
        return False

    def FindInputSubst(self, key, word):
        for subst in self.input_subst.keys():
            s = "["+subst+"]"
            if s == key:
                return self.input_subst[subst](word)
                return True
        return False
        
    def SubstituteReply(self, reply, event):
        for key in self.reply_subst.keys():
            subst = self.reply_subst[key]
            if type(subst) != type(""):
                subst = str(subst(event))
            reply = reply.replace("["+key+"]", subst)
        return reply

module = {
    "class": UnknownCMD,
    "type": MOD_LISTENER,
}
