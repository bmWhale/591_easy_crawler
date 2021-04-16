from bs4 import BeautifulSoup
import requests
import re
import signal
import time

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
    print("共", total_items, "間房子;共", total_pages,"頁");
    return 206, 7

def gather_info(ws, url):
    soup1 = ""
    result = ""
    for i in range(0,3):
        try:
            result = requests.get(url,headers={'User-Agent': 'Chrome/35.0.1916.47'})
        except:
            continue

        if result.status_code != 200:
            continue

        try:
            soup1 = BeautifulSoup(result.content, 'html.parser')
            break
        except:
            print("result: ", result.content);
            print("retry url: ", url, "times: ", i);
            if i == 2:
                print("錯誤：網頁載入失敗")
                return
            else:
                break
    if not soup1:
        print("錯誤：網頁載入失敗")
        return

    try:
        price = soup1.find('span', class_='price-num').text
    except:
        price = ""

    try:
        addrs = soup1.find_all('div', class_='house-info-addr')
    except:
        addrs = []

    try:
        house_name = soup1.find('h1', class_='house-info-name').text
    except:
        house_name = ""

    #try:
    #    floors_key = soup1.find_all('div', class_='house-info-sub')
    #except:
    #    floors_key = []
    try:
        detail_list_lv1 = soup1.find_all('ul', class_='detail-list-lv1')
    except:
        detail_list_lv1 = []
    #try:
    #    detail_list_lv2 = soup1.find_all('ul', class_='detail-list-lv2')
    #except:
    #    detail_list_lv2 = []

    name = "永慶房屋"

    try:
      phone = soup1.find("a", class_="belt-item-tel").text
    except:
      phone = ""

    #try:
    #  remark = soup1.find("span", class_="ins").text
    #except:
    #  remark = ""

    try:
      detail = soup1.find("div", class_="ins").text
    except:
      detail = ""

    print("總價："+ re.sub(r"\s+", "", price), "萬")
    print("地址： "+ re.sub(r"\s+", "", house_name))
    for s in addrs:
        print("地址：" + re.sub(r"\s+", "", s.text))

    for s in detail_list_lv1:
        if "建物坪數" in s.text:
            #print("格局：" + re.sub(r"\s+", "", s.text))
            subs = s.text.split("建物坪數")[1]
            t1 = subs.split("主建物小計")[0]
            subs = subs.split("主建物小計")[1]
            t2 = subs.split("共同使用小計")[0]
            subs = subs.split("共同使用小計")[1]
            t3 = subs.split("附屬建物小計")[0]
            t4 = subs.split("附屬建物小計")[1]
            print("格局1：建物坪數"+re.sub(r"\s+", "",t1));
            print("格局2：主建物小計"+re.sub(r"\s+", "",t2));
            print("格局3：共同使用小計"+re.sub(r"\s+", "",t3));
            print("格局4：附屬建物小計"+re.sub(r"\s+", "",t4));
        elif "房(室)" in s.text or "電梯" in s.text :
            print("格局：" + re.sub(r"\s+", "", s.text))
        elif "車位" in s.text and "房貸" not in s.text:
            print("格局：" + re.sub(r"\s+", "", s.text))

    print("姓名：" + name)
    print("電話：" + re.sub(r"\s+", "", phone))
    #print("訊息：" + remark)
    print("詳情：" + re.sub(r"\s+", "", detail))
    ws.append([name, re.sub(r"\s+", "", phone), re.sub(r"\s+", "", detail)])

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
            #items, pages = get_total_items(init_url)
            items, pages = 206, 2
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
        url = init_url + "?pg="+str(i+1)
        print('----第',i+1,'頁----------')
        print("目標網址:", url)
        for j in range(1,10):
            s = HTMLSession()
            r = s.get(url)
            r.html.render(sleep = 1, timeout = 100)
            #products = r.html.xpath('/html/body/main/div[2]/ul/li[1]', first=True)
            products = r.html.xpath('/html/body/main/div[2]/ul', first=True)
            if not products:
                print("錯誤：找不到任何網址!")
                continue
            print("共找到",len(products.absolute_links),"間房子")
            if len(products.absolute_links) > 0:
                for item in products.absolute_links:
                    if 'buy.yungching.com.tw' in item and 'vrmode=1' not in item:
                        count = count + 1
                        print('===============================')
                        print("第",count,"間")
                        print("房子的網址:", item)
                        gather_info(ws, item)
                    else:
                        print('===============================')
                        print("其他的網址:", item)
                break
            else:
                print('錯誤網址: ', url, '重試')
    wb.save(output_file_name)

if __name__ == '__main__':
    # -------- configurable parameter -------- #
    url = "https://buy.yungching.com.tw/region/%E6%96%B0%E7%AB%B9%E7%B8%A3-%E7%AB%B9%E5%8C%97%E5%B8%82_c/500-1500_price/3-3_rmp/%E9%9B%BB%E6%A2%AF%E5%A4%A7%E5%BB%88_type/"
    output_file_name = 'yungching_output.xlsx'
    # ---------------------------------------- #
    main(output_file_name, url)
    print('完成!')
