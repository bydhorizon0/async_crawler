from playwright.sync_api import  sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False
        )
        page = browser.new_page()
        page.goto("https://playwright.dev/")
        
        # Xpath가 // 또는 .. 로 시작하면 Playwright가 자동으로 XPath로 인식한다.
        text = page.locator("//h1").inner_text()
        
        # 특정 속성값 가져오기
        # 'Get started' 버트의 링크 주소 가져오기
        link = page.locator("//a[contains(text(), 'Get started')]").get_attribute("href")
        
        # 여러 요소 한꺼번에 선택
        items = page.locator("//ul[contains(@class, 'navbar__items')] /li")
        for i in range(items.count()):
            print(f"메뉴 {i}: {items.nth(i).inner_text()}")
            
        # 클릭하기
        # XPath를 명시적으로 지정하고 싶을 땐 'xpath=' 접두사 사용 가능
        page.click("xpath=//a[text()='Docs']")
        
        browser.close()
    
    
if __name__ == "__main__":
    main()