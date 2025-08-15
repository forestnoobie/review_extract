import time
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re

def setup_driver():
    """Chrome 드라이버 설정"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-extensions")
    
    # User-Agent 설정
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 자동화 탐지 방지
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    except Exception as e:
        print(f"드라이버 설정 중 오류: {e}")
        return None

def access_user_review_url(driver, url):
    """사용자 리뷰 페이지 URL에 접근"""
    try:
        print(f"URL에 접근합니다: {url}")
        driver.get(url)
        time.sleep(5)
        
        # 페이지 로딩 확인
        wait = WebDriverWait(driver, 15)
        
        # 페이지가 로드되었는지 확인
        try:
            # 다양한 요소를 확인하여 페이지 로딩 완료 판단
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print("페이지 로딩 완료")
            return True
        except:
            print("페이지 로딩 실패")
            return False
            
    except Exception as e:
        print(f"URL 접근 중 오류: {e}")
        return False

def extract_reviews_from_current_page(driver):
    """현재 페이지에서 리뷰 추출 (단일 페이지)"""
    try:
        print("현재 페이지에서 리뷰를 추출합니다...")
        
        # 페이지 로딩 대기
        time.sleep(3)
        
        # HTML 가져오기 및 파싱
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # 리뷰 데이터를 저장할 리스트
        reviews_data = []
        
        # other.review ID를 가진 요소 찾기
        other_review_element = soup.find(id="other.review")
        if other_review_element:
            print("other.review 엘리먼트를 찾았습니다.")
            
            # ul 태그 안의 li 요소들 찾기
            ul_element = other_review_element.find('ul')
            if ul_element:
                li_items = ul_element.find_all('li')
                print(f"총 {len(li_items)}개의 리뷰 항목을 찾았습니다.")
                
                for i, li_item in enumerate(li_items):
                    print(f"\n--- 리뷰 {i+1} 추출 중 ---")
                    
                    # 리뷰 정보 초기화
                    review_info = {
                        'restaurant_name': "장소명 없음",
                        'rating': "별점 없음", 
                        'date': "날짜 없음",
                        'review_text': "리뷰 텍스트 없음"
                    }
                    
                    # 1. 장소명/식당명 추출
                    restaurant_name = "장소명 없음"
                    place_selectors = ['strong'
                    ]
                    
                    for selector in place_selectors:
                        try:
                            place_element = li_item.select_one(selector)
                            if place_element:
                                place_text = place_element.get_text(strip=True)
                                if place_text and len(place_text) > 1:
                                    restaurant_name = place_text
                                    print(f"장소명 추출: {restaurant_name}")
                                    break
                        except:
                            continue

                    review_info['restaurant_name'] = restaurant_name

                    # 2. 별점/평점 추출 - 사용자 제공 XPath 패턴: //*[@id="other.review"]/ul/li[1]/div[2]/span[1]/em
                    rating = "별점 없음"
                    
                    try:
                        # div[2]/span[1]/em 패턴 찾기
                        divs = li_item.find_all('div')
                        if len(divs) >= 2:  # div[2] 존재하는지 확인
                            second_div = divs[1]  # div[2] (0-based index)
                            spans = second_div.find_all('span')
                            if len(spans) >= 1:  # span[1] 존재하는지 확인
                                first_span = spans[0]  # span[1] (0-based index)
                                em_element = first_span.find('em')
                                if em_element:
                                    rating_text = em_element.get_text(strip=True)
                                    # 숫자와 점이 포함된 평점 찾기
                                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                                    if rating_match:
                                        rating = rating_match.group(1)
                                        print(f"XPath 패턴으로 평점 추출: {rating}")
                    except:
                        pass
                    
                    # 백업 방법: 일반적인 평점 선택자들
                    if rating == "별점 없음":
                        rating_selectors = [
                            '.starred_grade', '.grade_star', '.star_rating', '.rating',
                            '[class*="star"]', '[class*="grade"]', '[class*="rating"]',
                            '.score', '[class*="score"]', 'em'
                        ]
                        
                        for selector in rating_selectors:
                            try:
                                rating_element = li_item.select_one(selector)
                                if rating_element:
                                    rating_text = rating_element.get_text(strip=True)
                                    # 숫자와 점이 포함된 평점 찾기 (예: 4.5, 5, 3.2)
                                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                                    if rating_match and float(rating_match.group(1)) <= 5:
                                        rating = rating_match.group(1)
                                        break
                            except:
                                continue

                    review_info['rating'] = rating

                    # 3. 날짜 추출
                    date = "날짜 없음"
                    date_selectors = [
                        '.date', '.time', '[class*="date"]', '[class*="time"]',
                        'time', 'span', '.txt_date'
                    ]
                    
                    for selector in date_selectors:
                        try:
                            date_element = li_item.select_one(selector)
                            if date_element:
                                date_text = date_element.get_text(strip=True)
                                # 날짜 패턴 찾기 (YYYY.MM.DD, YYYY-MM-DD, YYYY/MM/DD 등)
                                date_patterns = [
                                    r'\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2}',
                                    r'\d{2}[.\-/]\d{1,2}[.\-/]\d{1,2}',
                                    r'\d{1,2}[.\-/]\d{1,2}'
                                ]
                                for pattern in date_patterns:
                                    date_match = re.search(pattern, date_text)
                                    if date_match:
                                        date = date_match.group()
                                        print(f"날짜 추출: {date}")
                                        break
                                if date != "날짜 없음":
                                    break
                        except:
                            continue

                    review_info['date'] = date

                    # 4. 리뷰 텍스트 추출
                    review_text = "리뷰 텍스트 없음"
                    
                    # 모든 텍스트를 가져와서 가장 긴 것을 리뷰로 판단
                    all_text_elements = [ 'p'
                        ]
                        
                    longest_text = ""
                    
                    for selector in all_text_elements:
                        try:
                            element = li_item.select_one(selector)
                            element_text = element.get_text(strip=True)
                            print("element", element)
                        except:
                            continue
                        
                        # 필터링 조건
                        if (len(element_text) > len(longest_text) and
                            len(element_text) > 10 and  # 최소 길이
                            element_text != restaurant_name and  # 장소명 제외
                            element_text != rating and  # 평점 제외
                            element_text != date and  # 날짜 제외
                            not re.match(r'^\d+\.?\d*$', element_text) and  # 순수 숫자 제외
                            not re.search(r'^\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2}$', element_text)):  # 날짜 형식 제외
                            longest_text = element_text
                    
                    if longest_text:
                        review_text = longest_text
                        print(f"리뷰 텍스트 추출: {review_text[:50]}...")
                    
                    review_info['review_text'] = review_text
                    
                    # 유효한 데이터가 있는 경우만 추가
                    if (review_info['restaurant_name'] != "장소명 없음" or 
                        review_info['review_text'] != "리뷰 텍스트 없음"):
                        reviews_data.append(review_info)
                        print(f"✓ 리뷰 {i+1} 추출 완료")
                    else:
                        print(f"✗ 리뷰 {i+1} 스킵 (유효한 데이터 없음)")
        
        print(f"현재 페이지에서 총 {len(reviews_data)}개의 리뷰를 추출했습니다.")
        return reviews_data
        
    except Exception as e:
        print(f"현재 페이지 리뷰 추출 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_available_page_numbers(driver):
    """현재 페이지에서 사용 가능한 페이지 번호들 확인"""
    try:
        available_pages = []
        
        # 페이지네이션 영역에서 모든 페이지 번호 찾기 (사용자 제공 XPath 기반)
        page_elements = driver.find_elements(By.XPATH, '//*[@id="other.review.page"]//a')
        
        for element in page_elements:
            try:
                element_text = element.text.strip()
                if element_text.isdigit():
                    page_num = int(element_text)
                    if element.is_displayed() and element.is_enabled():
                        available_pages.append(page_num)
            except:
                continue
        
        available_pages.sort()
        return available_pages
        
    except Exception as e:
        print(f"페이지 번호 확인 중 오류: {e}")
        return []

def click_next_page_button(driver):
    """다음 페이지 버튼 클릭 (>>, 다음, next 등)"""
    try:
        print("다음 페이지 버튼을 찾는 중...")
        
        # 다음 페이지 버튼을 찾기 위한 다양한 선택자
        next_button_selectors = [
            '//*[@id="other.review.page"]//a[contains(text(), "다음")]',
            '//*[@id="other.review.page"]//a[contains(text(), "Next")]',
            '//*[@id="other.review.page"]//a[contains(text(), ">>")]',
            '//*[@id="other.review.page"]//a[contains(text(), ">")]',
            '//*[@id="other.review.page"]//a[contains(@class, "next")]',
            '//*[@id="other.review.page"]//button[contains(text(), "다음")]',
            '//*[@id="other.review.page"]//button[contains(@class, "next")]',
            '//*[contains(@class, "page")]//a[contains(text(), "다음")]',
            '//*[contains(@class, "page")]//a[contains(text(), ">>")]'
        ]
        
        for selector in next_button_selectors:
            try:
                next_button = driver.find_element(By.XPATH, selector)
                if next_button and next_button.is_displayed() and next_button.is_enabled():
                    # 버튼이 비활성화되어 있는지 확인
                    button_class = next_button.get_attribute('class') or ''
                    if 'disabled' not in button_class.lower():
                        print(f"다음 페이지 버튼을 찾았습니다: {selector}")
                        driver.execute_script("arguments[0].click();", next_button)
                        time.sleep(3)
                        print("다음 페이지 버튼 클릭 완료")
                        return True
            except:
                continue
        
        print("다음 페이지 버튼을 찾을 수 없습니다.")
        return False
        
    except Exception as e:
        print(f"다음 페이지 버튼 클릭 중 오류: {e}")
        return False

def go_to_next_page(driver, target_page_number):
    """특정 페이지 번호로 이동"""
    try:
        print(f"페이지 {target_page_number}로 이동을 시도합니다...")
        
        # 페이지네이션 영역 찾기 (사용자 제공 XPath: //*[@id="other.review.page"]/div)
        pagination_selectors = [
            '//*[@id="other.review.page"]',
            '//*[@id="other.review.page"]/div',
            '//*[contains(@class, "page")]',
            '//div[contains(@class, "paging")]'
        ]
        
        for selector in pagination_selectors:
            try:
                pagination_container = driver.find_element(By.XPATH, selector)
                
                # 정확한 페이지 번호 찾기
                page_buttons = pagination_container.find_elements(By.TAG_NAME, "a")
                
                for button in page_buttons:
                    try:
                        button_text = button.text.strip()
                        if button_text == str(target_page_number):
                            if button.is_displayed() and button.is_enabled():
                                print(f"페이지 {target_page_number} 버튼을 찾았습니다.")
                                driver.execute_script("arguments[0].click();", button)
                                time.sleep(3)
                                print(f"페이지 {target_page_number}로 이동 완료")
                                return True
                    except:
                        continue
                        
            except:
                continue
        
        print(f"페이지 {target_page_number} 버튼을 찾을 수 없습니다.")
        return False
        
    except Exception as e:
        print(f"페이지 이동 중 오류: {e}")
        return False

def extract_user_reviews_with_pagination(driver):
    """사용자 리뷰 페이지에서 모든 페이지의 리뷰 추출 - 페이지네이션 지원"""
    try:
        print("사용자 리뷰를 추출합니다...")
        
        # 페이지 로딩 대기
        wait = WebDriverWait(driver, 15)
        
        # 모든 페이지의 리뷰를 저장할 리스트
        all_reviews_data = []
        current_page = 1
        max_pages = 50  # 최대 페이지 수 제한 (무한 루프 방지)
        
        while current_page <= max_pages:
            print(f"\n=== 페이지 {current_page} 처리 중 ===")
            
            # 현재 사용 가능한 페이지 번호들 확인
            available_pages = get_available_page_numbers(driver)
            print(f"사용 가능한 페이지: {available_pages}")
            
            # 현재 페이지의 리뷰 추출
            current_page_reviews = extract_reviews_from_current_page(driver)
            
            if current_page_reviews:
                all_reviews_data.extend(current_page_reviews)
                print(f"페이지 {current_page}에서 {len(current_page_reviews)}개 리뷰 추출")
            else:
                print(f"페이지 {current_page}에서 리뷰를 찾을 수 없습니다.")
            
            # 다음 페이지로 이동
            next_page = current_page + 1
            
            # 다음 페이지가 사용 가능한 페이지 목록에 있는지 확인
            if available_pages and next_page not in available_pages:
                print(f"페이지 {next_page}는 현재 보이는 페이지 목록에 없습니다.")
                print(f"현재 보이는 마지막 페이지: {max(available_pages) if available_pages else current_page}")
                
                # 더 많은 페이지가 있는지 확인하기 위해 "다음" 버튼 클릭 시도
                print("더 많은 페이지를 로드하기 위해 '다음' 버튼을 클릭합니다...")
                if click_next_page_button(driver):
                    print("다음 페이지 세트로 이동했습니다. 새로운 페이지를 확인합니다...")
                    time.sleep(3)
                    
                    # 새로운 페이지 목록 확인
                    new_available_pages = get_available_page_numbers(driver)
                    print(f"새로 로드된 페이지: {new_available_pages}")
                    
                    if new_available_pages and next_page in new_available_pages:
                        print(f"페이지 {next_page}가 새로 로드된 페이지 목록에 있습니다.")
                        # 현재 페이지를 다음 페이지로 설정하고 계속 진행
                        current_page = next_page
                        continue
                    elif new_available_pages:
                        # 새로 로드된 페이지 중 첫 번째 페이지로 이동
                        first_new_page = min(new_available_pages)
                        print(f"새로 로드된 첫 번째 페이지 {first_new_page}로 이동합니다.")
                        if go_to_next_page(driver, first_new_page):
                            current_page = first_new_page
                            continue
                        else:
                            print("새로 로드된 페이지로 이동할 수 없습니다.")
                            break
                    else:
                        print("새로 로드된 페이지가 없습니다. 모든 페이지를 처리했습니다.")
                        break
                else:
                    print("더 이상 다음 페이지가 없습니다. 모든 페이지를 처리했습니다.")
                    break
            else:
                # 일반적인 경우: 다음 페이지가 현재 보이는 목록에 있음
                if not go_to_next_page(driver, next_page):
                    print("더 이상 다음 페이지가 없습니다.")
                    break
                
                current_page += 1
                time.sleep(3)  # 페이지 로딩 대기
        
        print(f"\n총 {len(all_reviews_data)}개의 리뷰를 {current_page-1}개 페이지에서 추출했습니다.")
        return all_reviews_data
        
    except Exception as e:
        print(f"사용자 리뷰 추출 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return [{'review_text': '오류 발생', 'restaurant_name': '오류', 'rating': '오류', 'date': '오류'}]

def save_user_reviews_to_csv(reviews_data, filename="user_reviews_data.csv"):
    """사용자 리뷰 데이터를 CSV 파일로 저장"""
    try:
        if not reviews_data:
            print("저장할 데이터가 없습니다.")
            return
        
        # data 폴더가 없으면 생성
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # 파일 경로 설정
        file_path = os.path.join(data_dir, filename)
        
        # DataFrame 생성
        df = pd.DataFrame(reviews_data)
        
        # CSV 파일로 저장
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"데이터가 {file_path}에 저장되었습니다.")
        print(f"총 {len(reviews_data)}개의 행이 저장되었습니다.")
        print(f"저장된 컬럼: {list(df.columns)}")
        
    except Exception as e:
        print(f"CSV 저장 중 오류: {e}")
        import traceback
        traceback.print_exc()

def main():
    """메인 실행 함수"""
    driver = None
    
    try:
        # 드라이버 설정
        driver = setup_driver()
        if not driver:
            print("드라이버 설정에 실패했습니다.")
            return
        
        # 사용자 리뷰 페이지 URL 입력
        user_review_url = input("카카오맵 사용자 리뷰 페이지 URL을 입력하세요 (예: https://map.kakao.com/?target=other&tab=review&mapuserid=771022966): ")
        # 테스트용
        #user_review_url = "https://map.kakao.com/?target=other&tab=review&mapuserid=771022966"
        
        if not user_review_url.startswith('http'):
            print("올바른 URL을 입력해주세요.")
            return
        
        # URL에서 사용자 ID 추출
        import re
        user_id_match = re.search(r'mapuserid=(\d+)', user_review_url)
        user_id = user_id_match.group(1) if user_id_match else "unknown"
        
        # URL 접근
        if not access_user_review_url(driver, user_review_url):
            print("URL 접근에 실패했습니다.")
            return
        
        # 페이지네이션을 포함한 리뷰 추출
        try:
            reviews_data = extract_user_reviews_with_pagination(driver)
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
            if not access_user_review_url(driver, user_review_url):
                print("재시작 후에도 URL 접근에 실패했습니다.")
                return
            
            reviews_data = extract_user_reviews_with_pagination(driver)
        
        # 리뷰 데이터 저장
        if reviews_data and isinstance(reviews_data, list) and len(reviews_data) > 0:
            filename = f"user_{user_id}_reviews_all_pages.csv"
            save_user_reviews_to_csv(reviews_data, filename)
            print(f"총 {len(reviews_data)}개의 사용자 리뷰를 저장했습니다.")
        else:
            print("추출된 리뷰 데이터가 없습니다.")
        
        print('사용자 리뷰 크롤링 완료')
        
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