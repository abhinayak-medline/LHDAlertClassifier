import numpy as np

'''
Global Variables
'''
sl_buckets_dict = {}
subject_line_buckets = [
    "*URGENT*HTTP Service is down on <TMAP Server> at <Date>", "<Branch> - CROSSDOCK SERVICE CALL FAILURE", 
    "<Branch> - ERROR RECORDS IN T_CSINTERFACE", "<Branch> - RP Failed Messages", "<Branch> - WORK ASSIGN FAILED TO CATEGORIZE",
    "<Branch> dispatcher alert", "<Branch> G2P Incorrect Employee Issues", "<Branch> G2P MHE Pick Errors",
    "<Branch> G2P MHE Putaway Errors", "<Branch> ZPOGI - Stuck in picking", "<Server> - Hourly upload files",
    "<Server> HeartBeat Status is down", "<Service> down on <Server>", "15 minute old file on <Server>", "Additional Pick Errors",
    "Additional Pick not processed", "ADDPICKWQ Alert", "Alert : <Branch> Containers zero picked and in status 16 - need destaging."
    "Alert t_csmastcontdtl multiple label_addr1 for mark_num", 
    'Alert: [HIGH] 1 alert for "CBMA_ExtEOIOPick" on "af.p42.prdsapgpidbha" by scenario "G2P_<Branch>_PickConfirmOut"',
    "Alert: Down: <Service> on Node <Server>", "Alert: ORA-00018 and ORA-03114", "ASN Not in CCT","BAM Notification",
    "Bot Loading # Error Message For Processing", "Branches with more than 150 orders not assigned carrier code",
    "CA APM Alert from munprdsmap31: G2P Backlog Messages in Caution state", "Carrier close alert",
    "CCT C_QUEUEDMESSAGE INPROCESS FAILURE", "CCT C_QUEUEDMESSAGE Threshold of 3500 Exceeded", "CCT T_QUEUEDMESSAGE INPROCESS FAILURE",
    "Completed wave still in 29", "Container stuck in status 11", "CPU utilization is at <##%> on <Server>",
    "Critical events detected for All Critical Alerts!", "Dead Message - order_close_ul-UpdatePickList",
    "Defunct process in prdcatap03 : High Priority", "Deleted Wave Stranded Pick WKA", "Delivery Not In Catalyst",
    "Delivery Not In CCT", "Down: <Service> on Node <Server>", "Embroidery non-LFE", "Error records in T_CSINTERFACE table",
    "Error while adjusting inventory from Auto lot update process", "Events detected for All Critical Alerts.","Failed Ship Close",
    "FedEx Database Service Error - NEW", "G2P <Branch> Location Checks - ALERT", "G2P <Branch> Pick Confirm Issues",
    "G2P <Branch> PRD Interface XML Errors", "G2P <Branch> Swisslog Pick Confirm Issues", "G2P AUTOSTORE <Branch> Order Download Issues",
    "G2P CARRYPICK <Branch> Order Download Issues", "G2P Download Order Issue Transaction Report",
    "G2P KNAPP <Branch> Order Download Issues", "G2PPA printing error - G2PPA device unavailable", "High : Missed H and Z Schedule",
    "HIGH: <Loftware Server> - Old files on the Loftware Shares", "High: MTP duplicate tracking", "HZ Backorders that Missed Cutoffs",
    "List of Deliveries missing Guaranteed flag", "Medline ship units need closing", "Message based Alerting Alert: CBMA_WMS",
    "Missing ITEMLOCCLS records", "Missing mark_num detail", "Missing t_csinterface Records", "More than 10 ship units have rating error"
    "MUNPRDFDX03 - FedEx DB Log File Size Threshold", "MUNPRDP<##> - - 0 KB files found", "Packlist Error", "PCAT<P#> Blocking Alert",
    "Precision file older than 2 days", "Print and Apply Error (G2P)", "Print and Apply Error (Numina)", 
    "Print Spooler Service is <Status> on <Server>", "Qty_alloc with no open work Assignment", "Recoverable Message Alert",
    "Setupsysctrl Error Record", "Shipments in status 60 for over 60 minutes", "Shipments not shipclosed",
    "Splunk Alert: Logistics_Alert and MIS_WMS-SHP_PRE_POGI_ASN_GENERATE", "Stranded Moves","t_csmastconthdr with no detail records",
    "Transhist Recovery File : Medium", "Unwaved delivery with Alloc_Qty", "UPS File Monitor",
    "Warning events detected for All Critical Alerts!", "Wave check failed", "Wave Errors", "Wave not processed","WDScan.dir is missing",
    "Whszone alert", "WMS <Branch> crossdock service call errors", "WMS <Branch> Missing Ship Units", "Work assign fail to categorize",
    "XML Recovery File : Medium", "Zero picked WKA", "Unmatched"
    ]

'''
function name: buildBucketDictionary
inputs: None
outputs: None
side effects: Populates the sl_buckets_dict dictionary with keys representing the different subject lines of the email alerts
'''
def buildBucketsDictionary():
    sl_buckets_dict = {key: [] for key in subject_line_buckets}

'''
function name: sortEmail
inputs: email - Email Object to be sorted
outputs: None
side effects: Pushes email object into a database where it will be sorted by Priority Level and Subject Line
References:
'''
def sortAlerts(email):

    # Process:
    # Count the number of occurrences of the Keywords within the key (Max is 2), Keep a running total as you iterate through the keywords
    # If the count is 0, then simply check if the key exists within the email's subject line
    # If the count is 1, split the key by the keyword and check if each index within the list exists within the email's subject line
    # If the count is 2, split the key into two separate lists by keywords and combine the lists by their differences, 
    # then follow the process above
    # If every index within the list is contained within the email's subject line, then there is a match and we can push this email
    # object into the dictionary to its respective key

    fillerKeywords = ["<Branch>", "<TMAP Server>", "<Date>", "<Server>", "<Service>", "<##%>", "<Loftware Server>", "<##>", "<P#>", "<Status>"]

    for key in sl_buckets_dict:

        curr_key = key
        keyword_total = 0
        keywords_in_key = []

        for keyword in fillerKeywords:

            num = curr_key.count(keyword)
            keyword_total += num
            if num != 0:
                keywords_in_key.append(keyword)
        
        if keyword_total == 0:

            if curr_key in email.subject:
                sl_buckets_dict[curr_key].append(email)
            else:
                sl_buckets_dict["Unmatched"].append(email) # Pushes email to Unmatched branch if it can't be matched to one of the 98 types of alerts

        elif keyword_total == 1:

            keyword_substrings = curr_key.split(keywords_in_key[0])

            # Used to check if every substring in the key is found within the email's subject line
            target_match_num = len(keyword_substrings)
            curr_match_num = 0

            for ks in keyword_substrings:
                if ks in email.subject:
                    curr_match_num += 1
            
            if curr_match_num == target_match_num:
                sl_buckets_dict[curr_key].append(email)
            else:
                sl_buckets_dict["Unmatched"].append(email)
        
        elif keyword_total == 2:

            keyword_substrings_A = curr_key.split(keywords_in_key[0])
            keyword_substrings_B = curr_key.split(keywords_in_key[1])

            keyword_substrings = list(set(keyword_substrings_A+keyword_substrings_B))

            # Used to check if every substring in the key is found within the email's subject line
            target_match_num = len(keyword_substrings)
            curr_match_num = 0

            for ks in keyword_substrings:
                if ks in email.subject:
                    curr_match_num += 1
            
            if curr_match_num == target_match_num:
                sl_buckets_dict[curr_key].append(email)
            else:
                sl_buckets_dict["Unmatched"].append(email)