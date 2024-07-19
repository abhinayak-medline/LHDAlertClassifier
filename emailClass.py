'''
Global Variables
'''
error_counter = 0

'''
class name: Email
functions: __init__ - initializes all of the attributes of an Email object
           __str__ - prints all attributes of an Email object to the terminal
References:
'''
class Email:
    def __init__(self, message):
        try:
            self.subject = message.Subject if hasattr(message, 'Subject') else "No Subject"
            self.sender_name = message.SenderName if hasattr(message, 'SenderName') else "Unknown Sender"
            self.sender_email = message.SenderEmailAddress if hasattr(message, 'SenderEmailAddress') else "Unknown Email"
            self.to_recipients = self.get_recipients(message.To) if hasattr(message, "To") else "No recipients"
            self.cc_recipients = self.get_recipients(message.CC) if hasattr(message, "CC") else "No recipients"
            self.bcc_recipients = self.get_recipients(message.BCC) if hasattr(message, "BCC") else "No recipients"
            self.received_time = message.ReceivedTime.strftime('%Y-%m-%d %H:%M:%S') if hasattr(message, 'ReceivedTime') else "Unknown"
            self.sent_on = message.SentOn.strftime('%Y-%m-%d %H:%M:%S') if hasattr(message, 'SentOn') else "Unknown"
            self.size = message.Size if hasattr(message, "Size") else "Size not Found"
            self.html_body = message.HTMLBody if hasattr(message, "HTMLBody") else "HTMLBody not Found"
            self.text_body = message.Body if hasattr(message, "Body") else "Body not Found"
            self.attachments = self.extract_attachments(message) if hasattr(message, "extract_attachments") else "None"
        except AttributeError as ae:
            print(f"- AttributeError (Property Not Found): {ae}\n")
            # Handle attribute errors (e.g., property not found)
        except Exception as e:
            print(f"- Error initializing Email object: {e}\n")
            # Handle other exceptions as needed

    def get_recipients(self, recipients):
        if recipients:
            return recipients
        return "No recipients"

    def extract_attachments(self, message):
        attachments = []
        for attachment in message.Attachments:
            attachments.append({
                'filename': attachment.FileName,
                'size': attachment.Size
            })
        return attachments

    def __str__(self):
        return f"- Subject: {self.subject}\n" \
               f"- From: {self.sender_name} <{self.sender_email}>\n" \
               f"- To: {self.to_recipients}\n" \
               f"- CC: {self.cc_recipients}\n" \
               f"- BCC: {self.bcc_recipients}\n" \
               f"- Received Time: {self.received_time}\n" \
               f"- Sent On: {self.sent_on}\n" \
               f"- Size: {self.size} bytes\n\n" \
               f"Alert Contents: \n\n{self.text_body}\n\n" \
               f"Attachments: \n{self.attachments}\n"