from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

print("--- 테스트 시작: 셀레니움으로 구글 열기 ---")

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True) # 테스트를 위해 창이 닫히지 않게 설정

try:
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)

    print("드라이버 실행 성공. 구글 사이트로 이동합니다...")
    driver.get("https://www.google.com")

    print("구글 페이지 로딩 성공!")
    print("--- 10초 후 프로그램이 종료됩니다 (브라우저 창은 그대로 유지됩니다) ---")
    time.sleep(10)

except Exception as e:
    print("\n!!! 테스트 중 오류 발생 !!!")
    print(e)