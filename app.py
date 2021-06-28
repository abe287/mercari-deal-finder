from bs4 import BeautifulSoup
import cloudscraper
import time, calendar
import datetime as dt
import random
from discord_webhook import DiscordWebhook, DiscordEmbed
from tinymongo import TinyMongoClient
import json, re

#Custom console print
def console_log(message):
    currentDT = calendar.timegm(time.gmtime())
    currentDT = dt.datetime.fromtimestamp(currentDT).strftime('%m/%d/%Y - %H:%M:%S')

    print(f"[{currentDT}] [{message}]")

#Make scraper session object (bypasses Cloudflare anti-bot if necessary) 
def make_scraper():
    browsers = [
        {'browser': 'chrome', 'platform': 'windows', 'mobile': False},
        {'browser': 'chrome', 'platform': 'ios', 'desktop': False},
        {'browser': 'chrome', 'platform': 'android', 'desktop': False}
        ]

    browser = random.choice(browsers)
    scraper = cloudscraper.CloudScraper(interpreter='nodejs', browser = browser)

    return scraper

#Send discord webhook notification
def send_discord_webhook(product_details):
    webhook = DiscordWebhook(url=settings['discord_webhook'], username="Mercari Deals", avatar_url="https://pbs.twimg.com/profile_images/1279060433102680064/NTY0fQFR_400x400.jpg")

    #Set webhook title and color
    product_url = f"https://www.mercari.com/us/item/{product_details['product_id']}/"
    embed = DiscordEmbed(title = product_details['title'], url = product_url, color=65280)

    #Set webhook thumbnail
    embed.set_thumbnail(url=product_details['image'])

    #Set webhook fields
    brand = "None" if product_details['brand'] == None else product_details['brand']
    embed.add_embed_field(name="Brand", value = brand, inline=True)
    embed.add_embed_field(name="Condition", value = product_details['condition'], inline=True)
    embed.add_embed_field(name="Price", value = "$"+ str(product_details['price']), inline=True)
    embed.add_embed_field(name="SKU", value = product_details['product_id'], inline=False)

    embed.add_embed_field(name="Description", value = "```" + product_details['description'] + "```", inline=True)

    #Set webhook footer
    currentDT = calendar.timegm(time.gmtime())
    currentDT = dt.datetime.fromtimestamp(currentDT).strftime('%m/%d/%Y - %H:%M:%S')
    embed.set_footer(text="Mercari Deals Finder | " + currentDT)

    #Add embeds and send to discord
    webhook.add_embed(embed)
    response = webhook.execute()

#Search Mercari
def search_mercari(scraper, query):
    search_query = query['search_query'].replace(" ", "%20")
    link = f"https://www.mercari.com/search/?itemStatuses=1&keyword={search_query}"
    src = scraper.get(link).content
    soup = BeautifulSoup(src, 'lxml')

    #Find product ids for searching
    products = soup.find_all("a", attrs={"class": "beSDvJ"})
    skus = [product['href'].split("/")[3] for product in products]

    #Get product data in script tag
    script = soup.find("script", attrs={"id": "__NEXT_DATA__"}).contents
    data = json.loads(script[0])

    #Parse through data, save to database if not already
    for sku in skus:
        product = data['props']['pageProps']['serverState']["Item:"+sku]
        product_id = product['id']
        image = product['photos'][0]['thumbnail']
        price = int(str(product['price'])[:-2])
        title = product['name']
        description = product['description']
        condition = data['props']['pageProps']['serverState'][product['itemCondition']['__ref']]['name']
        brand = data['props']['pageProps']['serverState'][product['brand']['__ref']]['name']
        product_details = {"title": title, "product_id": product_id, "image": image, "price": price, "brand": brand, "description": description, "condition": condition}

        #If price is lower than desired price send webhook and add to database
        if price <= query['desired_price']:
            #If not in database add and send webhook
            if db.products.find_one({"product_id": product_id}) == None:
                console_log("Found product less than desired price")
                db.products.insert_one({"product_id": product_id, "latest_price": price})
                send_discord_webhook(product_details)
            #if in database and price has lowered update and send webhook
            elif db.products.find_one({"product_id": product_id})['latest_price'] != price:
                console_log("Previously found product lowered in price")
                db.products.update({'product_id': product_id}, {"latest_price": price})
                send_discord_webhook(product_details)

        time.sleep(0.20) #timeout for discord rate limit

def main():
    scraper = make_scraper()

    #Serach through queries
    queries = list(db.queries.find())
    for query in queries:
        console_log(f"Searching mercari for {query['search_query']}")
        search_mercari(scraper, query)
        time.sleep(1) #Sleep between queries
    

if __name__ == '__main__':
    #Connect to database
    connection = TinyMongoClient("mercari")
    db = connection.mercari

    #Read in settings from json file
    settings = json.load(open('settings.json'))

    #Run main function
    while True:
        main()
        console_log(f"Sleeping for {settings['timeout']} seconds")
        time.sleep(settings['timeout'])