import requests
import os
import json
import pandas as pd
from bs4 import BeautifulSoup
import time


# 模擬 AJAX 的 API URL 
api_url = "https://www.costco.com.tw/rest/v2/taiwan/products/search"  

# 添加必要的請求參數和標頭
params = {
    "fields": "FULL",
    "query": ":BazaarVoiceRating-desc:bazaarVoiceAverageRatingFacet:4-5:bazaarVoiceAverageRatingFacet:5:bazaarVoiceAverageRatingFacet:3-4",
    "pageSize": 48,
    "sort": "BazaarVoiceRating-desc",
    "category": "Coupon",
    "lang": "zh_TW",
    "curr": "TWD",
    "currentPage": 0 
}



def download_img(url, save_path):
    response = requests.get(url)

    with open(save_path, "wb") as file:
        file.write(response.content)



def fetch_data(url,params):
    global bargain_list
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Accept": "application/json"  # 確保接收 JSON 格式
    }
    # 發送 GET 請求
    response = requests.get(url, headers=headers, params=params)

    # 確認請求成功
    if response.status_code == 200:
        data = response.json()  # 解析 JSON 資料
        products = data.get('products', [])  # 根據 API 返回的 JSON 結構調整
        
        dir_name = "Costco_img"
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        for product in products:  #商品資料
            name = product.get("name")
            price = product.get("price", {'value':"售完"}).get("value")
            couponDiscount = product.get("couponDiscount", {'discountValue':"N/A"}).get("discountValue","N/A")
            currency = product.get("price", {}).get("currencyIso")
            rating = product.get("averageRating", "無評價")
            
            # 抓取圖片 URL
            images = product.get("images", [])
            image_url = images[0].get("url") if images else "無圖片"
            
            """
            print(f"商品名稱: {name}")
            print(f"價格: {price} {currency}")
            print(f"評價分數: {rating}")
            print(f"圖片 URL: {image_url}\n")
            """
            
            #下載圖片
            image_url = 'https://www.costco.com.tw'+image_url
            download_img(image_url, f"{dir_name}/{name}.jpg")  #下載圖片
            

            bargain_data = [name,price,couponDiscount,rating,image_url ]
            bargain_list.append(bargain_data)

        
        #自動換頁
        if params["currentPage"] >= data.get('pagination').get("totalPages", 1) - 1:
            #輸出excel
            bargain_df = pd.DataFrame(bargain_list, columns = ["Name",f"Price({currency})", "Discount", 'Rating','Image'])
            bargain_df.to_excel('Costco on-sale.xlsx', index = False, engine= 'openpyxl')
            print(bargain_list)

        else:
            params["currentPage"] += 1
            time.sleep(2)
            print(params["currentPage"])
            fetch_data(url,params)
            

        

    else:
        print(f"請求失敗，狀態碼: {response.status_code}")

if __name__ == "__main__":
    bargain_list = []
    fetch_data(api_url,params)
