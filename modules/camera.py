from mod_base import *

# Warning: incomplete. Still in developement.

# Make the bot take a photo (with webcam, or smartphone camera etc.)
# and upload it to a server
class Camera(Command):
    def init(self):
        self.filename = "bot-picture.jpg"
        self.link_base = ""
        self.storage.Load()
        self.ftp_config = self.storage["ftp"]

    def PicRaspi(self):
        try:
            response = run_shell_cmd("raspistill -o " + self.filename)
            # FIXME: make this check raspistill output
            # Currently checks for mplayer output
            if response.find("0 frames successfully processed") != -1:
                print response
                self.win.Send("could not process frame")
                return False
            return self.filename
        except Exception, e:
            self.win.Send(str(e))
            return False

    def UploadFile(self, local_filename, remote_filename):
        import ftplib
        if ftplib == None:
            return False
        # try:
        sess = ftplib.FTP(
            self.ftp_config["host"],
            self.ftp_config["user"],
            self.ftp_config["password"]
        )
        f = open(local_filename)
        sess.storbinary("STOR " + remote_filename, f)
        f.close()
        sess.quit()
        # except Exception, e:
            # self.win.Send(str(e))
            # return False
        return self.storage["link_base"] + remote_filename


    def run(self, win, user, data, caller=None):
        self.link_folder = self.storage["link_base"]
        remote_filename = self.filename

        photo_taken = self.PicRaspi()
        print photo_taken
        if not photo_taken:
            win.Send("Sorry, failed to capture photo.")
        else:
            url = self.UploadFile(photo_taken, remote_filename)
            if url != False:
                win.Send(url)
                return True
            win.Send("Failed to upload photo.")
        return False


module = {
    "class": Camera,
    "type": MOD_COMMAND,
    "level": 5,
    "zone": IRC_ZONE_BOTH,
    "storage": {
        "ftp": {
            "host": "",
            "user": "",
            "password": '',
            "path": "bot/",
        },
        "link_base": "",
    }
}
