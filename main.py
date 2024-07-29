import smtplib
import requests
import os
import random
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import datetime
import matplotlib.pyplot as plt


def fetch_credentials():
    with open("credentials.txt", "r") as file:
        creds = file.readlines()

    return [creds[0].strip(), creds[1].strip()]

def fetch_recipient():
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
    weather_json = response.json()

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
    plt.savefig('images/forecasts/' + current_day + '_hourlytemps.png') 
    
    return [current_day, res]

def get_news_articles(category, num_articles=3):
    # fetch API key to call news API
    with open("news_key.txt", "r") as file:
        api_key = file.readline()
    
    # call API
    url = "https://newsapi.org/v2/top-headlines?country=us&category=" + category + "&apiKey=" + api_key
    response = requests.get(url)
    all_articles = response.json()['articles']
    
    select_articles = []
    
    for i in range(num_articles):
        index = random.randint(0, len(all_articles) - 1)
        select_articles.append(all_articles.pop(index))
    
    res = "<h3>News from the " + category[0].upper() + category[1:len(category)] + " Sector<h3>\n"
    res += "<h4>\n<ul>\n"
    
    for article in select_articles:
        res += '<li><a href="' + article['url'] +'">' + article['title'] + '</a>\n'
        
        if article['description'] != None:
            res += "<ul>\n<li>" + article['description'] + "</li>\n</ul>\n"
        
        res += "</li>\n"
    
    res += "</ul>\n</h4>\n"
    
    return res
        

def get_news_report():
    # get top business news
    business_news = get_news_articles(category="business")
     
    # get top sports news
    sports_news = get_news_articles(category="sports")
    
    # get top tech news
    tech_news = get_news_articles(category="technology")
    
    return business_news + "\n" + tech_news + "\n" + sports_news
    
    
def main():
    today, weather_report = get_weather_report()
    
    news_report = get_news_report()
    
    # fetch credentials for the sender email from credentials.txt
    origin_email, origin_pass = fetch_credentials()
    
    # fetch email address to send to (my email) from recipient.txt
    receive_email = fetch_recipient()
   
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
            <img src="cid:batmanlogo">
            
            <h2>Greetings Master Wayne,</h2>
            <h3>\n
        """+ weather_report + """
            </h3>
            
            <img src="cid:weatherforecast">\n
            </center>
            
            <h3>And here is your morning news...\n""" + news_report + """
        </body>
        </html>"""
    
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    
    # add batman logo to message
    image_file = open('images/assets/batman_logo.png', 'rb')
    batsymbol_image = MIMEImage(image_file.read())
    image_file.close()
    batsymbol_image.add_header('Content-ID', '<batmanlogo>')
    message.attach(batsymbol_image)
    
    # add forecast graph to message
    image_file = open('images/forecasts/' + today + '_hourlytemps.png', 'rb')
    forecast_image = MIMEImage(image_file.read())
    image_file.close()
    forecast_image.add_header('Content-ID', '<weatherforecast>')
    message.attach(forecast_image)
    
    # send the email
    s.sendmail(origin_email, receive_email, message.as_string())
    
    # terminate the session
    s.quit()

if __name__ == "__main__":
    main()