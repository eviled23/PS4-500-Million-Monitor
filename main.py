import requests, datetime, webbrowser
import lxml.etree as etree
from concurrent import futures as cf

session = requests.session()
session.headers.update({'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'})
links = [line.rstrip('\n') for line in open('links.txt', 'r')]
inStock = []

popUp = False

def getDatetime():
    return '[{}]'.format(str(datetime.datetime.now())[:-3])

def monitor(link):
    try:
        with session as s:
            r = s.get(link)
            r.raise_for_status()

            tree = etree.HTML(r.content)
            if 'walmart' in link:
                oos = True if tree.xpath('//div[@class="prod-ProductOffer-oosMsg prod-PaddingTop--xxs"]/span/text()') else False
            elif 'gamestop' in link:
                oos = False if tree.xpath('//div[@class="button qq"]') else False
            elif 'bestbuy' in link:
                oos = True if 'Sold' in tree.xpath('//*[@id="priceblock-wrapper"]/div[2]/script/text()')[0] else False
            elif 'target' in link:
                oos = False if tree.xpath('//button[@data-test="addToCartBtn"]') else True

            if oos and link in inStock:
                inStock.remove(link)
            elif not oos and link not in inStock:
                inStock.append(link)
                if popUp:
                    print(getDatetime(), 'In Stock: {}'.format(link))
                    webbrowser.open(link)

    except Exception as e:
        print(getDatetime(), e)

if __name__ == '__main__':
    print(getDatetime(), 'Starting initial scanning.')
    with cf.ThreadPoolExecutor(len(links)) as pool:
        pool.map(monitor, links)
    print(getDatetime(), 'Finished initial scanning.')

    while True:
        popUp = True
        with cf.ThreadPoolExecutor(len(links)) as pool:
            pool.map(monitor, links)