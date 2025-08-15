# KakaoMap Scraping Tools

This project contains three separate scraping tools for KakaoMap:

## Files

### 1. `scrap_location.py` - Location Information Scraper
This file handles scraping location information from KakaoMap.

**Features:**
- Search for locations by name
- Extract location information (name, rating, address)
- Support for direct URL access to specific places
- Save location data to CSV files

**Functions:**
- `setup_driver()` - Chrome driver configuration
- `search_location()` - Search for locations on KakaoMap
- `access_direct_url()` - Access specific place URLs directly
- `extract_location_info()` - Extract location info from search results
- `extract_single_place_info()` - Extract info from a single place page
- `save_to_csv()` - Save location data to CSV

**Usage:**
```bash
python scrap_location.py
```

### 2. `scrap_review.py` - Place Review Scraper
This file handles scraping reviews from specific KakaoMap place pages.

**Features:**
- Extract reviews from specific place URLs
- Get user names, ratings, dates, and review text
- Expand "더보기" (more) buttons to get full review content
- Save review data to CSV files

**Functions:**
- `setup_driver()` - Chrome driver configuration
- `access_direct_url()` - Access specific place URLs directly
- `extract_review()` - Extract reviews from place pages
- `save_reviews_to_csv()` - Save review data to CSV

**Usage:**
```bash
python scrap_review.py
```

### 3. `scrap_user_review.py` - User Review Scraper
This file handles scraping all reviews written by a specific user from their KakaoMap profile page.

**Features:**
- Extract all reviews from a specific user's profile
- **Full pagination support** - automatically navigates through all review pages
- Get restaurant names, ratings, dates, and review text for each review
- Handles both numbered page buttons (1, 2, 3...) and "next" button navigation
- Smart page detection and automatic page set loading
- Save all user reviews to a single CSV file

**Functions:**
- `setup_driver()` - Chrome driver configuration
- `access_user_review_url()` - Access user review profile URLs
- `extract_reviews_from_current_page()` - Extract reviews from current page
- `get_available_page_numbers()` - Detect available page numbers
- `click_next_page_button()` - Handle "next" button for loading more page sets
- `go_to_next_page()` - Navigate to specific page numbers
- `extract_user_reviews_with_pagination()` - Main pagination controller
- `save_user_reviews_to_csv()` - Save all user review data to CSV

**Usage:**
```bash
python scrap_user_review.py
# Enter: "https://map.kakao.com/?target=other&tab=review&mapuserid=771022966"
```

## Requirements

Install the required packages:
```bash
pip install -r requirements.txt
```

## Dependencies

- selenium
- pandas
- beautifulsoup4
- webdriver-manager

## Usage Examples

### Scraping Location Information
```bash
python scrap_location.py
# Enter: "만선호프" or "https://place.map.kakao.com/8332362"
```

### Scraping Place Reviews
```bash
python scrap_review.py
# Enter: "https://place.map.kakao.com/8332362"
```

### Scraping User Reviews (with Pagination)
```bash
python scrap_user_review.py
# Enter: "https://map.kakao.com/?target=other&tab=review&mapuserid=771022966"
```

## Output Files

- **Location data**: `{search_term}_data.csv` or `place_{id}_data.csv`
- **Place review data**: `place_{id}_reviews.csv`
- **User review data**: `user_{user_id}_reviews_all_pages.csv`

## Notes

- All scripts use Chrome WebDriver for automation
- The scripts include error handling and session management
- **User review scraping** features advanced pagination support that automatically handles:
  - Numbered page navigation (1, 2, 3, 4, 5...)
  - "Next" button clicking when reaching end of visible pages  
  - Dynamic loading of new page sets
  - Automatic stopping when all pages are processed
- Place review scraping includes automatic expansion of truncated reviews
- Location scraping supports both search and direct URL access
- User review scraping can process **unlimited pages** with intelligent pagination 