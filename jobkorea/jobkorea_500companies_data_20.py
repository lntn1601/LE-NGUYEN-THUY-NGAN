
import pandas as pd
from bs4 import BeautifulSoup
from requests import get
import time

def find_item_value(keys, values, item):
    try:
        index = keys.index(item)
        if 0 <= index < len(values):
            return values[index]
        else:
            return ""
    except:
        return ""

def get_detail_info(detail_soup, corp_name=""):
    items = ["자본금", "매출액", "설립일", "대표자"]

    key_elements = detail_soup.select(
        "table.table-basic-infomation-primary > tbody > tr.field > th.field-label")
    value_elements = detail_soup.select(
        "table.table-basic-infomation-primary > tbody > tr.field > td.field-value")

    key_list = [ key.get_text(strip=True) for key in key_elements ]
    value_list = [ value.get_text(strip=True) for value in value_elements ]

    print(f"🔍 [{corp_name}] KEYs: {key_list}")
    print(f"📎 VALUEs: {value_list}")

    capital = find_item_value(key_list, value_list, "자본금")
    sales = find_item_value(key_list, value_list, "매출액")
    foundation_date = find_item_value(key_list, value_list, "설립일")
    ceo = find_item_value(key_list, value_list, "대표자")

    return (capital, sales, foundation_date, ceo)

def get_jobkorea_data(corp_name_list, page_no=1):
    jobkorea_data = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    for idx, corp_name in enumerate(corp_name_list, 1):
        print(f"▶️ [{idx}/{len(corp_name_list)}] {corp_name} 처리 중...")
        capital = sales = ceo = foundation_date = ""
        corp_type = corp_location = corp_industry = ""
        try:
            url = f"https://www.jobkorea.co.kr/Search/?stext={corp_name}&tabType=corp&Page_No={page_no}"
            response = get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            flex_containers = soup.find_all("div", class_="Flex_display_flex__i0l0hl2 Flex_direction_row__i0l0hl3 Flex_justify_space-between__i0l0hlf")

            # ❗️Không break sớm — quét tất cả kết quả (công ty mẹ + con)
            for container in flex_containers:
                inner_flex = container.find("div", class_="Flex_display_flex__i0l0hl2 Flex_gap_space12__i0l0hls Flex_direction_row__i0l0hl3")
                if not inner_flex:
                    continue

                spans = inner_flex.find_all("span", class_="Typography_variant_size14__344nw27")
                if len(spans) < 3:
                    continue

                if len(spans) == 3:
                    corp_type, corp_location, corp_industry = [spans[i].get_text(strip=True) for i in range(3)]
                else:
                    corp_type, corp_location, corp_industry = [spans[i].get_text(strip=True) for i in range(1, 4)]

                parent = container.find_parent("div", class_="Flex_display_flex__i0l0hl2 Flex_gap_space4__i0l0hly Flex_direction_column__i0l0hl4")
                if not parent:
                    continue

                a_tag = parent.find('a', href=True)
                if not a_tag:
                    continue

                href = a_tag['href']
                if not href.startswith("http"):
                    href = "https://www.jobkorea.co.kr" + href

                text = a_tag.get_text(strip=True)
                print("🔗 링크:", href)

                detail_response = get(href, headers=headers, timeout=10)
                detail_soup = BeautifulSoup(detail_response.text, "html.parser")
                capital, sales, foundation_date, ceo = get_detail_info(detail_soup, corp_name)

                jobkorea_data.append({
                    "기업명": corp_name,
                    "상세명": text,
                    "기업형태": corp_type,
                    "지역": corp_location,
                    "업종": corp_industry,
                    "자본금": capital,
                    "매출액": sales,
                    "대표자": ceo,
                    "설립일": foundation_date
                })
                time.sleep(1)
        except Exception as e:
            print(f"❌ 오류 발생 ({corp_name}):", e)
            continue

    return pd.DataFrame(jobkorea_data)

if __name__ == "__main__":
    corp_name_list = pd.read_excel("500companies.xlsx")["기업명"].dropna().unique().tolist()
    test_data = get_jobkorea_data(corp_name_list[:15])
    test_data.to_csv("jobkorea_data_20.csv", index=False, encoding="utf-8-sig")
    print(test_data.head())
