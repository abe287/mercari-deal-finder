## Description
A script made to find deals on Mercari. You add some search queries to the database and it will monitor the website for products that meet your desired price. When the script finds a product that meets your desired price it will send you a discord notification.
## Usage
In the settings JSON file, you need to specify the timeout and your discord webhook. The default timeout is 1800 seconds (30 minutes), this is the time it will sleep for before checking the website again. The discord webhook will be used to send a notification when an item that meets your requirements is found.

To delete or insert a search query into the database you will have to run the database.py script and follow the instructions given. There you will add the search queries and desired price.

After setting up the settings and database you can run the main app.py script.


## Discord Notification
When the script finds an item that matches your desired price it will send you a discord notification with the full details of the item.
![alt text](https://i.ibb.co/gzGC7Lv/Capture.jpg)
