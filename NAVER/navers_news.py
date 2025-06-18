# curl "https://openapi.naver.com/v1/search/news.xml?query=%EC%A3%BC%EC%8B%9D&display=10&start=1&sort=sim" \
# -H "X-Naver-Client-Id: {애플리케이션 등록 시 발급받은 클라이언트 아이디 값}" \
# -H "X-Naver-Client-Secret: {애플리케이션 등록 시 발급받은 클라이언트 시크릿 값}" -v

# Naver News API 발급 주소
# 1일 25,000건 제한
# https://developers.naver.com/main/

# Documentation: https://developers.naver.com/docs/serviceapi/search/news/news.md#%EB%89%B4%EC%8A%A4
# 네이버 API 신청 현황 : https://developers.naver.com/apps/#/list


# 클라이언트 아이디 값
# 64g43aYmdLhFMenUVVVZ

# 클라이언트 시크릿 값
# LrXCNWZHsp

# 요청 코드 예시
# curl "https://openapi.naver.com/v1/search/news.json?query=LG&display=10&start=1&sort=sim" -H "X-Naver-Client-Id: CFN_cKg1htsqD1xqkA0k" -H "X-Naver-Client-Secret: 52E_v8ylTA" -v

# curl https://openapi.naver.com/v1/search/news.json?query=%EC%A3%BC%EC%8B%9D&display=10&start=1&sort=sim \
#     -H "X-Naver-Client-Id: CFN_cKg1htsqD1xqkA0k" \
#     -H "X-Naver-Client-Secret: 52E_v8ylTA" -v

# Python 코드로 네이버 뉴스 API 호출 구현
import requests
import urllib.parse
import json
import os
import re
from datetime import datetime
import pandas as pd

# API KEY
client_id = "CFN_cKg1htsqD1xqkA0k"
client_secret = "52E_v8ylTA"

# Đọc danh sách công ty từ Excel (lấy 10 công ty đầu tiên)
excel_path = "500companies.xlsx"
df_companies = pd.read_excel(excel_path)
company_list = df_companies["기업명"].dropna().unique().tolist()

# Hàm gọi API
def fetch_news(company_name, display=5):
    encoded_query = urllib.parse.quote(company_name)
    url = f"https://openapi.naver.com/v1/search/news.json?query={encoded_query}&display={display}&start=1&sort=sim"

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "User-Agent": "Mozilla/5.0",
    }

    try:
        response = requests.get(url, headers=headers)
        print(f"[{company_name}] Status: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.text)
            news_items = data.get("items", [])
            print(f"총 검색 결과: {data['total']}개")
            for item in news_items:
                item["company"] = company_name
                item["title"] = re.sub(r"<.*?>", "", item["title"])
                item["description"] = re.sub(r"<.*?>", "", item["description"])
            return news_items
        else:
            print(f"❌ Error: {response.status_code} for {company_name}")
            return []
    except Exception as e:
        print(f"❌ Exception with {company_name}: {e}")
        return []

 # 검색 결과 출력
all_news = []
for idx, company in enumerate(company_list, 1):
    print(f"[{idx}/{len(company_list)}] Fetching: {company}")
    news = fetch_news(company)
    all_news.extend(news)

  # 검색 결과 데이터프레임으로 변환
if all_news:
    df_news = pd.DataFrame(all_news)
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"naver_news_all_companies_{current_time}.csv"
    
    # HTML 태그 제거 및 텍스트 정리
    if "title" in df_news.columns:
        # 모든 HTML 태그를 정규식으로 제거
        df_news["title"] = df_news["title"].apply(lambda x: re.sub(r"<.*?>", "", x))
        df_news["description"] = df_news["description"].apply(lambda x: re.sub(r"<.*?>", "", x))

    # os.path를 사용하여 경로 생성
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(output_dir, file_name)
    df_news.to_csv(file_name, index=False, encoding="utf-8-sig")
    print(f"\n✅ 데이터가 저장되었습니다: {file_name}")
else:
    print("❗ 데이터가 없습니다.")
    
# XML 형식으로 요청하려면 아래 URL을 사용
# url = f"https://openapi.naver.com/v1/search/news.xml?query={encoded_query}&display=10&start=1&sort=sim"


