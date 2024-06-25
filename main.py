import smtplib
import requests
import os
import json
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import datetime
import matplotlib.pyplot as plt

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
    weather_json = json.loads(response.text)

    city = weather_json['location']['name']
    region = weather_json['location']['region']
    
    # get current conditions
    current_day, current_time = weather_json['location']['localtime'].split(' ')
    current_tempf = weather_json['current']['temp_f']
    current_tempc = weather_json['current']['temp_c']
    last_updated = weather_json['current']['last_updated'].split(' ')[1] # only return the time, not the date
    current_condition = weather_json['current']['condition']['text'].lower()
    
    res = "It is currently " + current_condition + " at " + current_time + " and the temperature is recorded to be "  + str(current_tempf) + "\N{DEGREE SIGN} F/" + str(current_tempc) + "\N{DEGREE SIGN} C (as of " + last_updated + ").\n"
    
    # get forecast
    day_condition = weather_json['forecast']['forecastday'][0]['day']['condition']['text'].lower()
    max_tempf = weather_json['forecast']['forecastday'][0]['day']['maxtemp_f']
    max_tempc = weather_json['forecast']['forecastday'][0]['day']['maxtemp_c']
    min_tempf = weather_json['forecast']['forecastday'][0]['day']['mintemp_f']
    min_tempc = weather_json['forecast']['forecastday'][0]['day']['mintemp_c']
    res += "\nThe majority of the day should be " + day_condition + ". The high will be " + str(max_tempf) + "\N{DEGREE SIGN} F/" + str(max_tempc) + " \N{DEGREE SIGN} C, and the low will be " + str(min_tempf) + "\N{DEGREE SIGN} F/" + str(min_tempc) + " \N{DEGREE SIGN} C."
    res += "\nA graph of the forecast shown in Fahrenheit is shown below."
    
    print (res)
    # collect hourly and temperatures to generate hourly graph
    times = []
    temps = []
    
    for hourcast in weather_json['forecast']['forecastday'][0]['hour']:
        times.append(hourcast['time'].split(' ')[1])
        temps.append(hourcast['temp_f'])
        
    # construct graph and download it 
    fig = plt.figure(figsize=(10, 4))  # Adjust the figure size as needed
    ax = fig.add_subplot(111)
    plt.plot(times, temps, linestyle='-', color='g', label='Temperature')

    # Add labels and title
    plt.xlabel('Hour')
    plt.ylabel('Temperature (°F)')
    plt.title('Hourly Forecasted Temperature')

    # Add gridlines
    plt.grid(True)

    # Add legend
    plt.legend()
    
    for x, y in zip(times[::3], temps[::3]):                                      
        ax.annotate('%s' % y, xy=(x,y), weight='bold', textcoords='data')
    
    ax.set_xticks(times[::3])
    

    # Save the plot as an image file (PNG format by default)
    plt.savefig('images/' + current_day + '_hourlytemps.png') 
    
    return [current_day, res]
    
def main():
    today, weather_report = get_weather_report()
    
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
    message = MIMEMultipart("alternative")
    message['Subject'] = str(datetime.date.today()) + " Report from Alfred"
    message['From'] = origin_email
    message['To'] = receive_email
    
    text = """\
        Greetings, Master Wayne,""" + weather_report

    html = """\
        <html>
        <body>
        <center>
            <img src="https://m.media-amazon.com/images/I/31x+q3aNVKL._AC_.jpg">
            
            <h4>Greetings Master Wayne,
        """+ weather_report + """
            </h4>
            
            <img src="cid:weatherforecast">
            </center>
        </body>
        </html>"""
    
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    
    image_file = open('images/' + today + '_hourlytemps.png', 'rb')
    forecast_image = MIMEImage(image_file.read())
    image_file.close()

    # Specify the  ID according to the img src in the HTML part
    forecast_image.add_header('Content-ID', '<weatherforecast>')
    message.attach(forecast_image)
    
    # send the email
    s.sendmail(origin_email, receive_email, message.as_string())
    
    # terminate the session
    s.quit()

if __name__ == "__main__":
    main()