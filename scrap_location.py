import time
import pandas as pd
from selenium import webdriver  # 동적크롤링
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def setup_driver():
    """Chrome 드라이버 설정"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 세션 안정성을 위한 추가 옵션
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")  # 이미지 로딩 비활성화로 속도 향상
    # chrome_options.add_argument("--disable-javascript")  # JavaScript 비활성화 (필요시 주석 해제)
    
    # 메모리 사용량 최적화
    chrome_options.add_argument("--memory-pressure-off")
    chrome_options.add_argument("--max_old_space_size=4096")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # 페이지 로드 타임아웃 설정
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(10)
    
    return driver

def search_location(driver, searchloc):
    """카카오맵에서 위치 검색"""
    try:
        # 방법 1: 직접 검색 URL로 접근
        search_url = f"https://map.kakao.com/?q={searchloc}"
        driver.get(search_url)
        
        wait = WebDriverWait(driver, 10)
        
        # 페이지 로딩 대기
        time.sleep(3)
        
        # 검색 결과가 있는지 확인
        try:
            # 장소 탭이 있는지 확인하고 클릭
            place_tab = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="info.main.options"]/li[2]/a')))
            place_tab.click()
            time.sleep(3)
            print("장소 탭 클릭 성공")
            return True
        except Exception as e:
            print(f"장소 탭 클릭 실패, 다른 방법 시도: {e}")
            # 다른 방법으로 장소 탭 찾기
            try:
                place_tabs = driver.find_elements(By.XPATH, "//a[contains(text(), '장소')]")
                if place_tabs:
                    place_tabs[0].click()
                    time.sleep(2)
                    print("장소 탭 클릭 성공 (대안 방법)")
                    return True
                else:
                    print("장소 탭을 찾을 수 없습니다. 검색 결과를 확인해주세요.")
            except Exception as e2:
                print(f"대안 방법도 실패: {e2}")
        
        # 방법 2: 검색창을 통한 검색 (fallback)
        print("직접 URL 접근 실패, 검색창을 통한 검색 시도...")
        try:
            driver.get("https://map.kakao.com/")
            time.sleep(2)
            
            # 검색창 찾기 (여러 가능한 선택자 시도)
            search_selectors = [
                '//*[@id="search.keyword.query"]',
                # '//input[@placeholder*="검색"]',
                # '//input[@name*="query"]',
                # '//input[contains(@class, "search")]'
            ]
            
            search_area = None
            for selector in search_selectors:
                try:
                    search_area = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    print(f"검색창 찾기 성공: {selector}")
                    break
                except:
                    continue
            
            if search_area:
                search_area.clear()
                search_area.send_keys(searchloc)
                time.sleep(1)
                
                # Enter 키로 검색
                search_area.send_keys(Keys.ENTER)
                time.sleep(1)
                
                # 장소 탭 클릭 시도
                try:
                    place_tab = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="info.main.options"]/li[2]/a')))
                    place_tab.click()
                    time.sleep(1)
                    print("검색창을 통한 검색 성공")
                    return True
                except:
                    print("검색창을 통한 검색 후 장소 탭 클릭 실패")
            
        except Exception as e3:
            print(f"검색창을 통한 검색도 실패: {e3}")
        
        return False
        
    except Exception as e:
        print(f"검색 중 오류 발생: {e}")
        return False

def access_direct_url(driver, url):
    """직접 카카오맵 URL로 접근"""
    try:
        print(f"직접 URL로 접근: {url}")
        driver.get(url)
        
        # 페이지 로딩 대기
        time.sleep(3)
        
        # URL이 유효한지 확인 (페이지 제목이나 특정 요소 존재 여부로 판단)
        try:
            # 페이지 제목 확인
            page_title = driver.title
            print(f"페이지 제목: {page_title}")
            
            # 장소 정보가 있는지 확인 (여러 가능한 선택자)
            place_selectors = [
                '//*[@id="mArticle"]//h1',  # 장소명
                '//*[@class="place_details"]',  # 장소 상세 정보
                '//*[@class="place_info"]',  # 장소 정보
                '//*[contains(@class, "place")]'  # 장소 관련 클래스
            ]
            
            place_found = False
            for selector in place_selectors:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    if element:
                        print(f"장소 정보 확인됨: {selector}")
                        place_found = True
                        break
                except:
                    continue
            
            if place_found:
                print("직접 URL 접근 성공")
                return True
            else:
                print("장소 정보를 찾을 수 없습니다. URL을 확인해주세요.")
                return False
                
        except Exception as e:
            print(f"페이지 확인 중 오류: {e}")
            return False
            
    except Exception as e:
        print(f"직접 URL 접근 중 오류 발생: {e}")
        return False

def extract_location_info(driver, room_list):
    """숙소 정보 크롤링"""
    try:
        time.sleep(0.5)
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        room_lists = soup.select('.placelist > .PlaceItem') # 장소 정보를 모두 가져옴
        
        for i, room in enumerate(room_lists):
            try:
                # 이름 추출
                name_elements = room.select('.head_item > .tit_name > .link_name')
                if name_elements:
                    name = name_elements[0].text.strip()
                else:
                    name = "이름 없음"
                
                # 평점 추출
                score_elements = room.select('.rating > .score > em')
                if score_elements:
                    score = score_elements[0].text.strip()
                else:
                    score = "평점 없음"
                
                # 주소 추출
                addr_elements = room.select('.addr > p')
                if addr_elements:
                    addr = addr_elements[0].text.strip()
                    if len(addr) > 3:
                        addr = addr[3:]  # "주소 " 부분 제거
                else:
                    addr = "주소 없음"
                
                # 딕셔너리 형태로 데이터 추가
                data = {
                    '숙소명': name,
                    '평점': score,
                    '주소': addr
                }
                room_list.append(data)
                print(f"추출 완료: {name}")
                
            except Exception as e:
                print(f"숙소 정보 추출 중 오류: {e}")
                continue
                
    except Exception as e:
        print(f"숙소 목록 추출 중 오류: {e}")

def extract_single_place_info(driver, place_info=None):
    """단일 장소 페이지에서 정보 추출 (직접 URL 접근용)"""
    try:
        time.sleep(2)
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # 장소명 추출 (여러 가능한 선택자 시도)
        name_selectors = [
            # '//*[@id="mArticle"]//h1',
            # '//*[@class="place_details"]//h1',
            # '//*[@class="place_info"]//h1',
            '//*[contains(@class, "place")]//h1',
            '//*[@class="tit_location"]',
            '//*[@class="tit_place"]'
        ]
        
        name = "이름 없음"
        for selector in name_selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                if element:
                    name = element.text.strip()
                    print(f"장소명 추출 성공: {name}, Selector: {selector}")
                    break
            except:
                continue
        
        # 평점 추출
        score_selectors = [
            '//*[@class="grade_star"]//em',
            '//*[@id="mainContent"]/div[1]/div[1]/div[2]/div[1]/a/span/span[2]'
        ]
        
        score = "평점 없음"
        for selector in score_selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                if element:
                    score = element.text.strip()
                    print(f"평점 추출 성공: {score}, Selector: {selector}")
                    break
            except:
                continue
        
        # 주소 추출
        addr_selectors = [
            '//*[contains(@class, "address")]',
        ]
        
        addr = "주소 없음"
        for selector in addr_selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                if element:
                    addr = element.text.strip()
                    print(f"주소 추출 성공: {addr}, Selector: {selector}")
                    break
            except:
                continue
        
        # 장소 정보 저장
        place_info = {
            '장소명': name,
            '평점': score,
            '주소': addr
        }
        
        print(f"단일 장소 정보 추출 완료: {name}")
        
        return place_info
        
    except Exception as e:
        print(f"단일 장소 정보 추출 중 오류: {e}")
        return None

def save_to_csv(room_list, filename="kakao_map_data.csv"):
    """데이터를 CSV 파일로 저장"""
    try:
        if not room_list:
            print("저장할 데이터가 없습니다.")
            return
        
        # 모든 데이터가 딕셔너리 형태이므로 바로 DataFrame으로 변환
        df = pd.DataFrame(room_list)
        
        # 컬럼 순서 정리 (선택사항)
        column_order = ['숙소명', '평점', '주소']
        existing_columns = [col for col in column_order if col in df.columns]
        if existing_columns:
            df = df[existing_columns + [col for col in df.columns if col not in existing_columns]]
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"데이터가 {filename}에 저장되었습니다.")
        print(f"총 {len(room_list)}개의 행이 저장되었습니다.")
        print(f"저장된 컬럼: {list(df.columns)}")
        
    except Exception as e:
        print(f"CSV 저장 중 오류: {e}")
        import traceback
        traceback.print_exc()

def main():
    """메인 실행 함수 - 위치 정보 크롤링"""
    driver = None
    room_list = []  # 숙소 정보 저장
    
    try:
        # 드라이버 설정
        driver = setup_driver()
        
        # 검색할 위치 또는 직접 URL 입력
        #searchloc_or_url = input("검색할 위치 또는 직접 URL을 입력하세요 (예: '만선호프' 또는 'https://place.map.kakao.com/8332362'): ")
        searchloc_or_url = '만선호프'

        if searchloc_or_url.startswith('http'):
            # 직접 URL 접근 - 단일 장소 페이지
            if not access_direct_url(driver, searchloc_or_url):
                print("직접 URL 접근에 실패했습니다.")
                return
            
            # 단일 장소 페이지에서 정보 추출
            print("단일 장소 페이지에서 정보를 추출합니다...")
            
            # 세션 유효성 확인 후 추출
            try:
                place_info = extract_single_place_info(driver)
            except Exception as session_error:
                print(f"세션 오류 발생: {session_error}")
                print("드라이버를 재시작하고 다시 시도합니다...")
                
                # 드라이버 재시작
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
                
                driver = setup_driver()
                if not access_direct_url(driver, searchloc_or_url):
                    print("재시작 후에도 URL 접근에 실패했습니다.")
                    return
                
                place_info = extract_single_place_info(driver)
            
            # 장소 정보 저장
            if place_info:
                # URL에서 장소 ID 추출
                import re
                match = re.search(r'/(\d+)$', searchloc_or_url)
                if match:
                    filename = f"place_{match.group(1)}_data.csv"
                else:
                    filename = f"{place_info['장소명'].replace(' ', '_')}_data.csv"
                
                save_to_csv([place_info], filename)
                print(f"장소 정보: {place_info}")
            else:
                print("장소 정보를 추출할 수 없습니다.")
            
        else:
            # 검색 위치 검색 - 검색 결과 페이지
            if not search_location(driver, searchloc_or_url):
                print("검색에 실패했습니다.")
                return
            
            page = 1  # 현재 페이지
            page2 = 1  # 5개 중 몇번째인지(버튼이 5개씩있어서 6번째가 되면 다시 1로 바꿔줘야함)
            
            for i in range(1, 2): # 1 페이지만 처리
                try:
                    page2 += 1
                    print(f"{page} 페이지 처리 중...")
                    
                    # 페이지 버튼 번호(1에서 5 사이 값)
                    if i > 5:
                        xpath = f'/html/body/div[5]/div[2]/div[1]/div[7]/div[6]/div/a[{i-5}]'
                    else:
                        xpath = f'/html/body/div[5]/div[2]/div[1]/div[7]/div[6]/div/a[{i}]'
                    
                    # 페이지 선택
                    try:
                        page_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, xpath))
                        )
                        page_button.click()
                        time.sleep(2)
                    except Exception as e:
                        print(f"페이지 {i} 이동 실패: {e}")
                        break
                    
                    # 숙소 정보 크롤링
                    extract_location_info(driver, room_list)
                    
                    # page2가 5를 넘어가면 다시 1로 바꿔주고 다음 버튼 클릭
                    if page2 > 5:
                        page2 = 1
                        try:
                            next_button = driver.find_element(By.XPATH, '//*[@id="info.search.page.next"]')
                            next_button.click()
                            time.sleep(2)
                        except Exception as e:
                            print(f"다음 페이지 버튼 클릭 실패: {e}")
                            break
                    
                    page += 1
                    
                except Exception as e:
                    print(f"페이지 {i} 처리 중 오류: {e}")
                    break
        
        print('크롤링 완료')
        
        # 데이터 저장
        if searchloc_or_url.startswith('http'):
            # 직접 URL 접근의 경우 이미 위에서 저장됨
            print("직접 URL 접근: 장소 정보가 이미 저장되었습니다.")
        else:
            # 검색 결과의 경우
            print(f"총 {len(room_list)}개의 숙소 정보를 수집했습니다.")
            if room_list:
                filename = f"{searchloc_or_url.replace(' ', '_')}_data.csv"
                save_to_csv(room_list, filename)
        
    except Exception as e:
        print(f"전체 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 드라이버 종료
        if driver:
            try:
                driver.quit()
                print("브라우저가 종료되었습니다.")
            except Exception as quit_error:
                print(f"브라우저 종료 중 오류: {quit_error}")

if __name__ == "__main__":
    main() 