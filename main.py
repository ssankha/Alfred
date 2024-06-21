import smtplib
def fetch_credentials():
    with open("credentials.txt", "r") as file:
        creds = file.readlines()

    return [creds[0].strip(), creds[1].strip()]

def fetch_receiver():
    with open("recipient.txt", "r") as file:
        to_address = file.readline()
        
    return to_address


def main():
    origin_email, origin_pass = fetch_credentials()
    receive_email = fetch_receiver()
    
    print(origin_email, origin_pass)
   
    # creates SMTP session
    s = smtplib.SMTP('smtp-mail.outlook.com', 587)
    # start TLS for security
    s.starttls()
    # Authentication
    s.login(origin_email, origin_pass)
    # message to be sent
    parts = ("From: " + origin_email,
         "To: " + receive_email,
         "Subject: " + "test",
         "",
         "Hello World2")    
    msg = '\r\n'.join(parts)
    # sending the mail
    s.sendmail(origin_email, receive_email, msg)
    # terminating the session
    s.quit()

if __name__ == "__main__":
    main()