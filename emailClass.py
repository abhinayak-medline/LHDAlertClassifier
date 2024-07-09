
'''
class name: Email
functions: __init__ - initializes all of the attributes of an Email object
           __str__ - prints all attributes of an Email object to the terminal
References:  ChatGPT 3.5
'''
class Email:
    def __init__(self, message):
        # Define properties and default values
        properties = {
            'subject': "No Subject",
            'sender_name': "Unknown Sender",
            'sender_email': "Unknown Email",
            'to_recipients': "No recipients",
            'cc_recipients': "",
            'bcc_recipients': "",
            'received_time': "Unknown",
            'sent_on': "Unknown",
            'html_body': "",
            'text_body': "",
            'attachments': [],
            'size': 0
        }

        for prop, default_value in properties.items():
            try:
                setattr(self, prop, getattr(message, prop))
            except AttributeError:
                setattr(self, prop, default_value)

    # Used to print all data of a particular Email object
    def __str__(self):
        return f"Subject: {self.subject}\n" \
               f"From: {self.sender_name} <{self.sender_email}>\n" \
               f"To: {self.to_recipients}\n" \
               f"CC: {self.cc_recipients}\n" \
               f"BCC: {self.bcc_recipients}\n" \
               f"Received Time: {self.received_time}\n" \
               f"Sent On: {self.sent_on}\n" \
               f"Size: {self.size} bytes"