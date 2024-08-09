Please read this file prior to using the program on your own machine.

Project Name: Logistics Help-Desk Alerts Dashboard

Project Description: 
This program is used to generate a dashboard for the Logistics Help-Desk team to have effective email alert data storage and analysis as well as easy access to essential processing documentation.

This is a full-stack web application with a few key components:
- The Data: The data used by this program originates from the "Do Not Delete!!!" subfolder of the Logistic System Alert inbox (LogisticSystemAlert@medline.com). To retrieve this data, 
            the program utilizes Python's win32com.client module to extract the emails from the Outlook application.
- The IDE: You are free to use an IDE of your choosing to compile and run this program. However, I've found that this application runs smoothly using the terminal within the Visual Studio IDE.
- The Backend: The backend is written entirely in Python. The code consists of the email extraction (found in startProcess.py), the sorting algorithm (found in sortEmail.py), and the database entry procedure as well (found in startProcess.py).
               Also uses Python's Flask framework to handle HTTP requests and database interactions (essentially the connection point between the Front-End and Back-End of this application)(found in app.py).
- The Frontend: The frontend is written in three different languages - HTML, CSS, and JavaScript. The HTML contains the code to display the webpage and all of its different features (found in Index.html, analytics.html).
                Embedded within the HTML files is the JavaScript that is used to make the displayed content such as the table and bar graph functional. The CSS file contains the code used to customize the webpage
                by manipulating the position, sizing, colors, etc. of all of the webpage contents (found in styles.css).

What to do if you want to extract more email data from Outlook:
- To change what email attributes are being extracted, simply navigate to the emailClass.py file and add code to the init section of the Email class. 
- To figure out what code to write for the new attributes you wish to retrieve, please reference Python's win32com.client module documentation about how to extract email data from Outlook.

What to do if you want to add a new alert to the application to be tracked:
- Navigate to the sortEmail.py file and find the subject_lines array. Add the name of the alert in String format to this array (the index where you place this alert in the array doesn't matter).
- Next, find the generateBucketSubstrings function and add the placeholder tag in the name of the alert in String format to the fillerKeywords array if it does not exist in it already (Ex:// Branch inside of less than and greater than signs is a placeholder tag).
- Lastly, go to the assignPriority function and add the name of the alert to its respective priority level array.
- Make sure to save this file after making all of these changes.

How to clone this repository to your computer and open the application:
- Go to Google and download Git Bash - 64 bit version to your PC. Open this application after downloading it and click Next on all of the popups.
- Go to Google and download the Visual Studio IDE for Windows (Only if you don't have a pre-existing IDE on your computer that you want to use).
- Next, navigate to this repository on Google and once you get to the main page for this repository that contains all of the code for this application and its folders, click the green button that says "<> Code".
- Now, copy the link shown on the HTTPS page after clicking this button.
- After this, navigate to the folder on your computer where you want to host this repository. Right click, then select Show More options, and click open Git Bash here.
- After doing this, a black terminal should show up. In this terminal, type git clone and then right click and paste the link copied from earlier. Now, hit enter.
- The repository should now be cloned to your desired location in your PC.
- Now, open up the Visual Studio IDE, click File on the top left, and click "Open Folder". Now, navigate to the location of this cloned repository, select the folder for it, and click open.

How to run the program:
- Navigate to the startProcess.py file and change the target_alerts_to_process variable at the top of the file to be the number of alerts you wish to process. It must be an integer.
- Open the terminal and type cd [insert Path to where this application exists].
- Open the Outlook application on your computer and make sure the LogisticSystemAlert email address is configured to your Outlook.
- Now, type python app.py. The program should display the name and email address of the inbox being extracted from, the total number of emails in the inbox at the time of compilation, and a running number of emails being processed.
- After the code is done running, click on the link at the bottom of the terminal to open up the webpage for this application.
- The first page of the webpage contains a table with all of the sorted email data and can be queried using the drop-down menus and text-field.
- The second page contains a bar graph that gets dynamically populated with the sorted alerts and how many exist per category in the taken snapshot.
- The next three navigation buttons at the top of the page are hyperlinks to the alerts processing life cycle, knowledge documents, and alert audit (documentation about all of the alerts).
- To run this program again, make sure to type "del .\data\process_complete.txt" in the terminal and hit Enter. Also, type "del .\data\alerts.db" and hit Enter. You do this is to clear all of the snapshot data prior to recompiling the program with the new number of emails to process.

To-do List:
1. Figure out why this application cannot extract all of the emails from this inbox (When trying to process all of the emails, I noticed that Outlook freezes at around 60,000 emails out of the almost 80,000 total emails).
2. Sometimes, when the number of emails to be processed exceeds 1000, the sorted email data doesn't display properly within the webpage's database table.
3. Host this application on a domain or server if you don't want to keep running this code locally.
4. Implement Medline's email retention policy.
5. Add a Sort By Date filter to the database table on the webpage.
6. Add more charts to the analytics page?
