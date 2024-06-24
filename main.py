import smtplib
import requests
import os
import json

def fetch_credentials():
    with open("credentials.txt", "r") as file:
        creds = file.readlines()

    return [creds[0].strip(), creds[1].strip()]

def fetch_receiver():
    with open("recipient.txt", "r") as file:
        to_address = file.readline()
        
    return to_address


def get_weather_report():
    # get the the postal code of the user's IP to feed into the weather API call
    postal_code = os.popen("curl ipinfo.io/postal").read()
    
    # fetch the API key from a file in order to call the weather API
    with open("weather_key.txt", "r") as file:
        api_key = file.readline()
    
    # call API
    url = "http://api.weatherapi.com/v1/forecast.json?key=" + api_key + "&q=" + str(postal_code) + "&days=1&aqi=yes&alerts=yes"
    response = requests.get(url)
    
    # convert to json
    weather_json = json.dumps(response.text)
    print(weather_json)
    
    city = weather_json['name']
    region = weather_json['region']
    

def main():
    weather_report = get_weather_report()
    # fetch credentials for the sender email from credentials.txt
    origin_email, origin_pass = fetch_credentials()
    
    # fetch email address to send to (my email) from recipient.txt
    receive_email = fetch_receiver()
   
    # create SMTP session
    s = smtplib.SMTP('smtp-mail.outlook.com', 587)
    
    # start TLS for security
    s.starttls()
    
    # login on sender email
    s.login(origin_email, origin_pass)
    
    # Construct message
    parts = ("From: " + origin_email,
         "To: " + receive_email,
         "Subject: " + "test",
         "",
         weather_report)    
    msg = '\r\n'.join(parts)
    
    # send the email
    s.sendmail(origin_email, receive_email, msg)
    
    # terminate the session
    s.quit()

if __name__ == "__main__":
    main()