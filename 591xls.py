from bs4 import BeautifulSoup
import requests
import re

from requests_html import HTMLSession
from openpyxl import Workbook
from openpyxl.utils import get_column_letter


def gather_info(url):

    result = requests.get(url,headers={'User-Agent': 'Chrome/35.0.1916.47'})
    if result.status_code != 200:
        return None, None
    soup1 = BeautifulSoup(result.content, 'html.parser')
#    addrs = soup1.find_all('span', class_='info-addr-value')
#    for s in addrs:
#        print("地址：" + s.text)
    name = soup1.find("span", class_="info-span-name").text
    print("姓名：" + soup1.find("span", class_="info-span-name").text)
    phone = soup1.find("span", class_="info-host-word").text
    print("電話：" + re.sub(r"\s+", "", phone))
    remark = soup1.find("span", class_="info-span-msg").text
    print("訊息：" + soup1.find("span", class_="info-span-msg").text)
#    detail = soup1.find("div", class_="info-detail-show").text
#    print("詳情：" + re.sub(r"\s+", "", detail))
    ws.append([name, re.sub(r"\s+", "", phone), remark])


if __name__ == '__main__':
    init_url = 'https://sale.591.com.tw/?shType=list&kind=9&pattern=3&regionid=5&section=54'
    total_num = '1413'
    pages = 48

    excelfile = "591.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.append(['姓名', '電話', '訊息'])
    count = 0;
    for i in range(pages):
        url = init_url +'&firstRow='+ str(i*30) + '&totalRows='+total_num
        print("target URL:", url)
        s = HTMLSession()
        r = s.get(url)
        r.html.render(sleep = 1, timeout = 20)
        products = r.html.xpath('//*[@id="app"]/div[4]/div[2]/section/div[3]', first=True)
        print('Page: ',i+1,'+++++++++++++++++++++++++++++++')
        if not products:
            print("No jobs")
            continue
        print("links:",products.absolute_links)
        for item in products.absolute_links:
            print("item:", item)
            if 'sale.591.com.tw' in item:
                count = count + 1;
                print('===============================')
                print("count:",count,item)
                gather_info(item)
    wb.save(excelfile)


