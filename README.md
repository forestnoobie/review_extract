# KakaoMap Scraping Tools

This project contains two separate scraping tools for KakaoMap:

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

### 2. `scrap_review.py` - Review Scraper
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

### Scraping Reviews
```bash
python scrap_review.py
# Enter: "https://place.map.kakao.com/8332362"
```

## Output Files

- Location data: `{search_term}_data.csv` or `place_{id}_data.csv`
- Review data: `place_{id}_reviews.csv`

## Notes

- Both scripts use Chrome WebDriver for automation
- The scripts include error handling and session management
- Review scraping includes automatic expansion of truncated reviews
- Location scraping supports both search and direct URL access 