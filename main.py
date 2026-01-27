from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        list_path = r"//*[@id='seoul-integrated-board']/table/tbody/tr"

        for i in range(1, 4):
            page.goto("https://www.seoul.go.kr/news/news_notice.do?bbsNo=277&curPage={}".format(i))

            items = page.locator(list_path)

            print(items.count())

            for i in range(items.count()):
                print(items.nth(i).inner_text())

        # Xpath가 // 또는 .. 로 시작하면 Playwright가 자동으로 XPath로 인식한다.
        # text = page.locator("//h1").inner_text()

        # 특정 속성값 가져오기
        # 'Get started' 버트의 링크 주소 가져오기
        # link = page.locator("//a[contains(text(), 'Get started')]").get_attribute("href")

        # 여러 요소 한꺼번에 선택
        # items = page.locator("//ul[contains(@class, 'navbar__items')] /li")
        # for i in range(items.count()):
        #     print(f"메뉴 {i}: {items.nth(i).inner_text()}")

        # 클릭하기
        # XPath를 명시적으로 지정하고 싶을 땐 'xpath=' 접두사 사용 가능
        # page.click("xpath=//a[text()='Docs']")

        browser.close()


if __name__ == "__main__":
    main()
