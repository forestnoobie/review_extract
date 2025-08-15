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

# Location scraping functions moved to scrap_location.py

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

def extract_review(driver):
    """리뷰 추출 함수 - 사용자명, 별점, 날짜, 리뷰 텍스트 추출"""
    try:
        # 페이지 로딩 대기
        wait = WebDriverWait(driver, 10)
        
        # 후기 탭으로 이동 시도 (여러 방법)
        try:
            # 방법 1: 후기 탭 클릭
            review_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '후기')]")))
            review_tab.click()
            time.sleep(3)
            print("후기 탭 클릭 성공")
        except:
            try:
                # 방법 2: 후기 링크 찾기
                review_links = driver.find_elements(By.XPATH, "//a[contains(@href, '#comment')]")
                if review_links:
                    review_links[0].click()
                    time.sleep(3)
                    print("후기 링크 클릭 성공")
                else:
                    print("후기 탭을 찾을 수 없습니다")
            except Exception as e:
                print(f"후기 탭 클릭 실패: {e}")
        
        # 문서 밑으로 스크롤, 추가 후기 확인, 추가로 후기 로딩 되면 다시 스크롤 내리기
        # 연속적으로 스크롤하여 모든 후기를 로드
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scroll_attempts = 15  # 최대 스크롤 시도 횟수
        
        while scroll_attempts < max_scroll_attempts:
            # 페이지 끝까지 스크롤
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # 새로운 높이 계산
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            # 높이가 같으면 더 이상 로드할 내용이 없음
            if new_height == last_height:
                print(f"스크롤 완료: {scroll_attempts + 1}번째 시도 후 더 이상 로드할 내용이 없습니다.")
                break
            
            print(f"스크롤 {scroll_attempts + 1}: 새로운 내용 로드됨 (높이: {last_height} → {new_height})")
            last_height = new_height
            scroll_attempts += 1
        
        if scroll_attempts >= max_scroll_attempts:
            print(f"최대 스크롤 시도 횟수({max_scroll_attempts})에 도달했습니다.")

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # 디버깅을 위해 HTML 저장
        try:
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("디버깅용 HTML 파일 저장됨: debug_page.html")
        except:
            pass
        
        # 리뷰 데이터를 저장할 리스트
        reviews_data = []
        
        # 리뷰 컨테이너 찾기 (info_review 클래스)
        #review_containers = soup.select('.info_review')
        review_containers = soup.select('.inner_review')

        if review_containers:
            print(f"리뷰 컨테이너 발견: {len(review_containers)}개")
            
            # Step 1: Click all "더보기" buttons outside the for loop
            print("모든 더보기 버튼을 클릭하여 리뷰 내용을 펼치는 중...")
            try:
                # JavaScript를 사용하여 모든 더보기 버튼을 한 번에 클릭
                expand_script = """
                var moreButtons = document.querySelectorAll('.btn_more');
                var clickedCount = 0;
                for (var i = 0; i < moreButtons.length; i++) {
                    if (moreButtons[i].textContent.trim() === '더보기') {
                        moreButtons[i].scrollIntoView({behavior: 'smooth', block: 'center'});
                        setTimeout(function(button) {
                            button.click();
                        }, 100 * clickedCount, moreButtons[i]);
                        clickedCount++;
                    }
                }
                return clickedCount;
                """
                
                clicked_count = driver.execute_script(expand_script)
                print(f"총 {clicked_count}개의 더보기 버튼을 클릭했습니다.")
                
                # 모든 버튼이 클릭될 때까지 대기
                wait_time = 4  # 클릭된 버튼 수에 따라 대기 시간 조정
                print(f"내용 확장을 위해 {wait_time}초 대기 중...")
                time.sleep(wait_time)
                
            except Exception as e:
                print(f"더보기 버튼 클릭 중 오류: {e}")
            
            # Step 2: Get updated HTML with all expanded content
            print("업데이트된 페이지에서 리뷰 정보를 추출하는 중...")
            updated_html = driver.page_source
            updated_soup = BeautifulSoup(updated_html, 'html.parser')
            
            # Step 3: Find updated review containers
            updated_review_containers = updated_soup.select('.inner_review')
            
            if updated_review_containers:
                print(f"업데이트된 리뷰 컨테이너 발견: {len(updated_review_containers)}개")
                
                # Step 4: Extract review data from updated containers
                for i, container in enumerate(updated_review_containers):
                    review_info = {}
                    
                    # 1. 사용자 이름 추출 (name_user 클래스)
                    try:
                        name_element = container.select_one('.name_user')
                        if name_element:
                            # screen_out 클래스를 제외한 텍스트만 추출
                            screen_out_elements = name_element.select('.screen_out')
                            for screen_out in screen_out_elements:
                                screen_out.extract()  # screen_out 요소 제거
                            user_name = name_element.get_text(strip=True)
                            review_info['user_name'] = user_name
                            print(f"사용자 이름: {user_name}")
                        else:
                            review_info['user_name'] = "이름 없음"
                    except Exception as e:
                        print(f"사용자 이름 추출 실패: {e}")
                        review_info['user_name'] = "이름 추출 실패"
                    
                    # 2. 별점 추출 (starred_grade 클래스)
                    try:
                        starred_element = container.select_one('.starred_grade')
                        if starred_element:
                            # screen_out 클래스 중에서 별점 숫자를 찾기
                            screen_out_elements = starred_element.select('.screen_out')
                            for screen_out in screen_out_elements:
                                text = screen_out.get_text(strip=True)
                                # 숫자와 점이 포함된 텍스트 찾기 (예: "1.0", "4.5")
                                if any(char.isdigit() for char in text) and '.' in text:
                                    starred_grade = text
                                    review_info['starred_grade'] = starred_grade
                                    print(f"별점: {starred_grade}")
                                    break
                            else:
                                review_info['starred_grade'] = "별점 없음"
                        else:
                            review_info['starred_grade'] = "별점 없음"
                    except Exception as e:
                        print(f"별점 추출 실패: {e}")
                        review_info['starred_grade'] = "별점 추출 실패"
                    
                    # 3. 날짜 추출 (txt_date 클래스)
                    try:
                        date_element = container.select_one('.txt_date')
                        if date_element:
                            txt_date = date_element.get_text(strip=True)
                            review_info['txt_date'] = txt_date
                            print(f"날짜: {txt_date}")
                        else:
                            review_info['txt_date'] = "날짜 없음"
                    except Exception as e:
                        print(f"날짜 추출 실패: {e}")
                        review_info['txt_date'] = "날짜 추출 실패"
                    
                    # 4. 리뷰 텍스트 추출 (desc_review 클래스) - Now with expanded content
                    try:
                        desc_element = container.select_one('.desc_review')
                        if desc_element:
                            review_text = desc_element.get_text(strip=True)
                            review_info['review_text'] = review_text
                            print(f"리뷰 텍스트 (확장됨): {review_text[:100]}...")  # Show first 100 chars
                        else:
                            review_info['review_text'] = "리뷰 텍스트 없음"
                    except Exception as e:
                        print(f"리뷰 텍스트 추출 실패: {e}")
                        review_info['review_text'] = "리뷰 텍스트 추출 실패"
                    
                    reviews_data.append(review_info)
                    print(f"리뷰 데이터 추가 완료: {review_info['user_name']} - {len(review_info['review_text'])}자")
            else:
                print("업데이트된 리뷰 컨테이너를 찾을 수 없습니다.")
        
        print(f"추출된 리뷰 데이터: {reviews_data}")
        return reviews_data
        
    except Exception as e:
        print(f"리뷰 추출 중 오류: {e}")
        # 에러 발생 시 원래 창으로 돌아가기 (세션 유효성 확인)
        try:
            # 현재 창이 유효한지 확인
            current_url = driver.current_url
            print(f"현재 URL: {current_url}")
        except Exception as session_error:
            print(f"세션 오류: {session_error}")
            # 세션이 무효한 경우 새로고침 시도
            try:
                driver.refresh()
                time.sleep(3)
            except:
                pass
        
        print("Added error review: 오류 발생")
        return [{'review_text': '오류 발생'}]

# Location scraping functions moved to scrap_location.py

# Location scraping functions moved to scrap_location.py

def save_reviews_to_csv(reviews_data, filename="reviews_data.csv"):
    """리뷰 데이터를 CSV 파일로 저장"""
    try:
        if not reviews_data:
            print("저장할 리뷰 데이터가 없습니다.")
            return
        
        # 모든 데이터가 딕셔너리 형태이므로 바로 DataFrame으로 변환
        df = pd.DataFrame(reviews_data)
        
        # 컬럼 순서 정리 (선택사항)
        column_order = ['user_name', 'starred_grade', 'txt_date', 'review_text']
        existing_columns = [col for col in column_order if col in df.columns]
        if existing_columns:
            df = df[existing_columns + [col for col in df.columns if col not in existing_columns]]
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"리뷰 데이터가 {filename}에 저장되었습니다.")
        print(f"총 {len(reviews_data)}개의 리뷰가 저장되었습니다.")
        print(f"저장된 컬럼: {list(df.columns)}")
        
    except Exception as e:
        print(f"리뷰 CSV 저장 중 오류: {e}")
        import traceback
        traceback.print_exc()

# Location data saving function moved to scrap_location.py

def main():
    """메인 실행 함수 - 리뷰 크롤링 전용"""
    driver = None
    
    try:
        # 드라이버 설정
        driver = setup_driver()
        
        # 카카오맵 장소 URL 입력
        place_url = input("카카오맵 장소 URL을 입력하세요 (예: https://place.map.kakao.com/8332362): ")
        
        if not place_url.startswith('http'):
            print("올바른 URL을 입력해주세요.")
            return
        
        # 직접 URL 접근
        if not access_direct_url(driver, place_url):
            print("URL 접근에 실패했습니다.")
            return
        
        print("리뷰를 추출합니다...")
        
        # 세션 유효성 확인 후 리뷰 추출
        try:
            reviews_data = extract_review(driver)
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
            if not access_direct_url(driver, place_url):
                print("재시작 후에도 URL 접근에 실패했습니다.")
                return
            
            reviews_data = extract_review(driver)
        
        # 리뷰 데이터 저장
        if reviews_data and isinstance(reviews_data, list):
            # URL에서 장소 ID 추출
            import re
            match = re.search(r'/(\d+)$', place_url)
            if match:
                filename = f"place_{match.group(1)}_reviews.csv"
            else:
                filename = "reviews_data.csv"
            
            save_reviews_to_csv(reviews_data, filename)
            print(f"총 {len(reviews_data)}개의 리뷰를 저장했습니다.")
        else:
            print("리뷰 데이터를 추출할 수 없습니다.")
        
        print('리뷰 크롤링 완료')
        
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