import aws_access
import gmail_api_access


def lambda_handler(event, context):

    email_report_list = []

    number_of_emails_deleted = 0

    aws_access_obj = aws_access.AwsAccess()

    parameter_value = aws_access_obj.get_secret("mail_credentials")

    SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
    gmail_api = gmail_api_access.GmailAPI(SCOPES, parameter_value)

    aws_access_obj.update_token_in_parameter_store(gmail_api.creds.to_json())

    maxResults = 500

    query_list = [
        "from:group-digests@linkedin.com",
        "from:ebill@dialog.lk",
        "from:openhouse-group.com",
        "from:Sandaru.Gunasekara@sgs.com",
        "from:ecommerce@seylan.lk",
        "from:boconlinebanking@boc.lk",
        "from:HNBAlerts@hnb.lk",
        "from:no-reply@mail.instagram.com",
        "from:no-reply@mail.goodreads.com",
        "from:groups-noreply@linkedin.com",
        "from:flysmilesupdates@srilankan.com",
        "from:noreply@couchsurfing.org",
        "from:jobalerts-noreply@linkedin.com",
        "from:velocity@e.velocityfrequentflyer.com",
        "from:newsletters@fishpond.com.au",
        "from:eservice@mh1.evaair.com",
        "from:info@news.groupon.com.au",
        "from:comment-reply@wordpress.com",
        "from:no-reply@primevideo.com",
        "from:noreply@news.delonghi.com",
        "from:promo@oncredit.lk",
        "from:no-reply@extremecloudiq.com",
        "from:no-reply@e.siriusxm.com",
        "from:web.jms@keells.com",
        "from:invitationtoapply-au@match.indeed.com",
        "from:no-reply@channels.primevideo.com",
        "from:hello@email.m.bigw.com.au",
        "from:ana-asia-oceania@121.ana.co.jp",
        "from:anamail@121.ana.co.jp",
        "from:sampathotp@sampath.lk",
        "subject: email deletion report from:ruwanindika@gmail.com to:ruwanindika@gmail.com",
        "from:carsales@mail.carsales.com.au",
        "from:shipment-tracking@amazon.com.au older_than:5d",
        "from:store-news@amazon.com.au",
        "from:flybuys@edm.flybuys.com.au",
        "from:smbc_info@msg.smbc.co.jp",
        "from:myqinfo@info.chamberlain.com",
        "from:didi@jp.didiglobal.com",
        "from:order-update@amazon.com.au older_than:5d",
        "from:estatement@info.nationstrust.com",
        "from:estatements@ndbbank.com",
        "from:newsletter@m.finder.com.au",
        "from:noreply@mail.schoolbytes.education older_than:60d",
        "from:donotreply@afterpay.com subject:Thanks for your payment! older_than:2d",
        "from:donotreply@afterpay.com subject:Payment reminder older_than:2d",
        "from auto-confirm@amazon.com.au older_than:5d",
        "from:no-reply@amazon.com.au older_than:5d",
        "from:eBayDeals@e.deals.ebay.com.au",
        "from:qantasff@e.qantas.com",
        "from:jobs-listings@linkedin.com",
        "from:promotion@aliexpress.com",
        "from:notifications-noreply@linkedin.com older_than:15d",
        "from:store-news@amazon.co.jp older_than:5d",
        "from:auto-confirm@amazon.co.jp older_than:15d",
        "from:shipment-tracking@amazon.co.jp older_than:15d",
        "from:aquinasadmin@aquinas.edu.au subject:Schedule Report",
        "from:no-reply@employmenthero.com subject:Security alert older_than:15d",
        "from:no-reply@employmenthero.com subject:Your timesheets have been updated older_than:15d",
        "from:messages-noreply@linkedin.com older_than:15d",
        "from:Retail@shinseibank.com older_than:15d",
        "from:contacts@email.woolworthsrewards.com.au older_than:15d",
        "from:eBay@e.reply.ebay.com.au older_than:15d",
        "from:noreply@youtube.com older_than:30d",
        "from:contacts@email.everydayrewards.com.au older_than:2d",
        "from:noreply@ato.gov.au subject:Payment plan instalment reminder [SEC=OFFICIAL] older_than:5d",
        "from messaging-digest-noreply@linkedin.com older_than:30d",
        "from:gitlab@mg.gitlab.com older_than:30d",
        "from:no-reply@amazonmusic.com older_than:3d",
        "from:service@paypal.com.au subject:Your PayPal Pay in 4 payment went through older_than:3d",
        "from:noreply@mail.schoolbytes.education subject:BPS - No School Crossing Supervisor older_than:3d",
        "from:noreply@mail.schoolbytes.education subject:BPS - Health Alert older_than:3d",
        "from:NetBankNotification@cba.com.au subject:**** **** 3135 to Vanguard Super Pty Ltd ATF Vanguard Super older_than:3d",
        "from:noreply@my.gov.au subject:New myGov Inbox message older_than:30d",
    ]

    for i in query_list:
        mails_deleted = gmail_api.search_and_delete(i, maxResults)

        number_of_emails_deleted = number_of_emails_deleted + mails_deleted

        if mails_deleted > 0:
            email_report_list.append({"filter": i, "deleted": mails_deleted})

    print(f"Total Number of emails deleted : {number_of_emails_deleted}")

    email_report_string = ""

    for j in email_report_list:
        email_report_string = email_report_string + "\n" + str(j)

    print(email_report_string)

    email_string = f"Number of emails deleted : {number_of_emails_deleted}\n\n{email_report_string}"

    gmail_api.send_email(email_string)
