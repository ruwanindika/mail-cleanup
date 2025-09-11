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
        "from:info@fastimpressions.com.au",
        "from:ebill@dialog.lk",
        "from:openhouse-group.com",
        "from:Sandaru.Gunasekara@sgs.com",
        "from:deals@livingsocial.com",
        "from:subscriptions@message.bloomberg.com",
        "from:boconlinebanking@boc.lk",
        "from:HNBAlerts@hnb.lk",
        "from:no-reply@mail.instagram.com",
        "from:no-reply@mail.goodreads.com",
        "from:groups-noreply@linkedin.com",
        "from:flysmilesupdates@srilankan.com",
        "from:noreply@ondemandmsg.sbs.com.au",
        "from:jobalerts-noreply@linkedin.com",
        "from:velocity@e.velocityfrequentflyer.com",
        "from:newsletters@fishpond.com.au",
        "from:eservice@mh1.evaair.com",
        "from:info@mailer.netflix.com",
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
        "from:update+mihpmuki@facebookmail.com",
        "from:sampathotp@sampath.lk",
        "subject: email deletion report from:ruwanindika@gmail.com to:ruwanindika@gmail.com",
        "from:carsales@mail.carsales.com.au",
        "from:shipment-tracking@amazon.com.au",
        "from:store-news@amazon.com.au",
        "from:flybuys@edm.flybuys.com.au",
        "from:smbc_info@msg.smbc.co.jp",
        "from:myqinfo@info.chamberlain.com",
        "from:didi@jp.didiglobal.com",
        "from:order-update@amazon.com.au older_than:15d",
        "from:estatement@info.nationstrust.com",
        "from:estatements@ndbbank.com",
        "from:newsletter@m.finder.com.au",
        "from:noreply@mail.schoolbytes.education older_than:60d",
        "from:donotreply@afterpay.com older_than:30d",
        "from auto-confirm@amazon.com.au older_than:15d",
        "from:no-reply@amazon.com.au older_than:15d",
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
        "from:messages-noreply@linkedin.com older_than:15d",
        "from:Retail@shinseibank.com older_than:15d",
        "from:contacts@email.woolworthsrewards.com.au older_than:15d",
        "from:eBay@e.reply.ebay.com.au older_than:15d",
        "from:noreply@youtube.com older_than:30d",
        "from:contacts@email.everydayrewards.com.au older_than:2d",
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
