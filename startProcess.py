import win32com.client
import os
import numpy as np
from emailClass import Email
from datetime import datetime, timedelta

'''
Global Variables
'''
emails = np.array([])
last_processed_time = None # Stores the last processed email's time

'''
function name: openOutlook
inputs: None
outputs: None
side effects: None
References: https://www.codeforests.com/2020/06/04/python-to-read-email-from-outlook/, ChatGPT 3.5
'''
def openOutlook():

    # Access the Outlook Application and its MAPI (Messaging Application Programming Interface) namespace
    outlook_app = win32com.client.Dispatch('outlook.application').GetNamespace("MAPI")

'''
function name: extractEmailsfromInbox
inputs: app - connection to the Outlook application
        account - name of the email account being examined
        folder - name of the folder that emails are being read from
        subfolder - name of the subfolder that contains the emails to be extracted
outputs: None
side effects: Populates global "emails" NumPy array with Email Objects that contain all of the necessary email data from a particular inbox
References: https://medium.com/@balakrishna0106/automating-outlook-effortless-email-retrieval-using-pythons-win32com-client-796b13746ad9, 
            ChatGPT 3.5
'''
def extractEmailsfromInbox(app, account, folder, subfolder):

    global last_processed_time

    # Checks to see if the desired email account exists within the Outlook application
    myAccount = None
    for acc in app.Accounts:
        if acc.DisplayName == account:
            account = acc
            break
    
    if not myAccount:
        print(f"Account '{account}' not found.")
        return
    
    primary_inbox = app.Folders(myAccount.DeliveryStore.DisplayName).Folders[folder]
    
    subfolder_inbox = primary_inbox.Folders[subfolder]

    emails = subfolder_inbox.Items

    # Filter emails received after the last processed email's time
    if last_processed_time:
        emails = emails.Restrict(f"[ReceivedTime] > '{last_processed_time}'")

    for em in emails:

        received_time = em.ReceivedTime

        if received_time > last_processed_time:
            last_processed_time = received_time
        
         np.append(emails, Email(em))

'''
function name: main
inputs: None
outputs: None
side effects: None
References: ChatGPT 3.5
'''
def main():
    global last_processed_time

    openOutlook()
    
    while True:
        # Retrieve new emails periodically
        extractEmailsfromInbox(outlook_app, "Logistic System Alert", "Inbox", "Do Not Delete!!!")
        
        # Time interval (in seconds) for how often the emails will be extracted
        time.sleep(60)

# Starts the program
if __name__ == "__main__":
    main()