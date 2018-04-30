import requests


r = requests.get('https://coinmarketcap.com/all/views/all/', allow_redirects=False)
if r.status_code != 200:
    print("Error fetching all coins form cmc. Response code: "+str(r.status_code))

page_file = open('all.html', "w")
page_file.write(r.text.encode('utf8'))
page_file.close()

