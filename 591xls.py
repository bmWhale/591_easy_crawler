from bs4 import BeautifulSoup
import requests
import re
import signal

from requests_html import HTMLSession
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

def get_total_items(url):
    s = HTMLSession()
    r = s.get(url)
    r.html.render(sleep = 3, timeout = 100)
    if r.status_code != 200:
        return None, None
    soup1 = BeautifulSoup(r.html.html, 'html.parser')
    print('區域：', soup1.find('span', {'class':'areaTxt'}).text)
    houseList_head_title = soup1.find('div', class_='houseList-head-title').text
    print(houseList_head_title);
    total_items = int(''.join(filter(str.isdigit, houseList_head_title)))
    total_pages = int(total_items/30 + 1)
    return total_items, total_pages

def gather_info(ws, url):
    result = requests.get(url,headers={'User-Agent': 'Chrome/35.0.1916.47'})
    if result.status_code != 200:
        return None, None
    soup1 = BeautifulSoup(result.content, 'html.parser')
    price = soup1.find('span', class_='info-price-num').text
    print("總價："+ re.sub(r"\s+", "", price))
    addrs = soup1.find_all('span', class_='info-addr-value')
    for s in addrs:
        print("地址：" + s.text)

    floors_key = soup1.find_all('div', class_='info-floor-key')
    #floors_value = soup1.find_all('div', class_='info-floor-value')
    for s in floors_key:
        print("格局：" + s.text)

    try:
      name = soup1.find("span", class_="info-span-name").text
    except:
      name = ""

    try:
      phone = soup1.find("span", class_="info-host-word").text
    except:
      phone = ""

    try:
      remark = soup1.find("span", class_="info-span-msg").text
    except:
      remark = ""

    try:
      detail = soup1.find("div", class_="info-detail-show").text
    except:
      detail = ""

    print("姓名：" + name)
    print("電話：" + re.sub(r"\s+", "", phone))
    print("訊息：" + remark)
    print("詳情：" + re.sub(r"\s+", "", detail))
    #ws.append([name, re.sub(r"\s+", "", phone), remark])

def exit(signum, frame):
        print('You choose to stop me.')
        exit()

def main(outputfile, init_url):
    signal.signal(signal.SIGINT, exit)
    signal.signal(signal.SIGTERM, exit)
    if not init_url or not outputfile:
        print('參數錯誤：設定網址為空 或 輸出檔名為空')
        return

    print("設定網址:", init_url)
    for i in range(1,3):
        try:
            items, pages = get_total_items(init_url)
            break;
        except:
            print("錯誤：無法獲取總共的房子數");
            items, pages = 0, 0

    if items == 0:
        return
    wb = Workbook()
    ws = wb.active
    ws.append(['姓名', '電話', '訊息'])
    count = 0
    for i in range(pages):
        url = init_url +'&firstRow='+ str(i*30) + '&totalRows='+str(items)
        print('----第',i+1,'頁----------')
        print("目標網址:", url)
        for j in range(1,10):
            s = HTMLSession()
            r = s.get(url)
            r.html.render(sleep = 1, timeout = 100)
            products = r.html.xpath('//*[@id="app"]/div[4]/div[2]/section/div[3]', first=True)
            if not products:
                print("錯誤：找不到任何網址!")
                continue
            print("共找到",len(products.absolute_links),"間房子")
            if len(products.absolute_links) > 0:
                for item in products.absolute_links:
                    if 'sale.591.com.tw' in item:
                        count = count + 1
                        print('===============================')
                        print("第",count,"間")
                        gather_info(ws, item)
                        print("房子的網址:", item)
                    else:
                        print('===============================')
                        print("其他的網址:", item)
                break
            else:
                print('錯誤網址: ', url, '重試')
    wb.save(output_file_name)

if __name__ == '__main__':
    # -------- configurable parameter -------- #
    url = "https://sale.591.com.tw/?shType=list&regionid=5&section=54&kind=9&pattern=3&shape=2&price=500$_1500$"
    output_file_name = '591_output.csv'
    # ---------------------------------------- #
    main(output_file_name, url)
    print('完成!')
