'''
class name: Email
functions: __init__ - initializes all of the attributes of an Email object
           __str__ - prints all attributes of an Email object to the terminal
References:
'''
class Email:
    def __init__(self, message):
        try:
            self.subject = message.Subject if message.Subject else "No Subject"
            self.sender_name = message.SenderName if message.SenderName else "Unknown Sender"
            self.sender_email = message.SenderEmailAddress if message.SenderEmailAddress else "Unknown Email"
            self.to_recipients = self.get_recipients(message.To)
            self.cc_recipients = self.get_recipients(message.CC)
            self.bcc_recipients = self.get_recipients(message.BCC)
            self.received_time = message.ReceivedTime.strftime('%Y-%m-%d %H:%M:%S') if message.ReceivedTime else "Unknown"
            self.sent_on = message.SentOn.strftime('%Y-%m-%d %H:%M:%S') if message.SentOn else "Unknown"
            self.size = message.Size
            self.html_body = message.HTMLBody
            self.text_body = message.Body
            self.attachments = self.extract_attachments(message)
        except Exception as e:
            print(f"Error initializing Email object: {e}")
            # Handle the exception as needed

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
        return f"Subject: {self.subject}\n" \
               f"From: {self.sender_name} <{self.sender_email}>\n" \
               f"To: {self.to_recipients}\n" \
               f"CC: {self.cc_recipients}\n" \
               f"BCC: {self.bcc_recipients}\n" \
               f"Received Time: {self.received_time}\n" \
               f"Sent On: {self.sent_on}\n" \
               f"Size: {self.size} bytes"