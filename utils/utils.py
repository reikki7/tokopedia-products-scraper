import time
import re
from urllib.parse import urlparse

def is_valid_url(url):
    """
    Check if a URL is valid
    
    Args:
        url: URL string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def clean_price_text(price_text, currency="Rp"):
    """
    Clean and convert price text to integer
    
    Args:
        price_text: Raw price text from webpage
        currency: Currency symbol to remove
        
    Returns:
        int: Cleaned price as integer, 0 if parsing fails
    """
    try:
        if currency in price_text:
            cleaned = price_text.replace(currency, "").replace(".", "").replace(",", "").strip()
            return int(cleaned)
    except:
        pass
    return 0


def clean_rating_text(rating_text, decimal_separator=","):
    """
    Clean and convert rating text to float
    
    Args:
        rating_text: Raw rating text from webpage
        decimal_separator: Decimal separator used in the text
        
    Returns:
        float: Cleaned rating as float, 0.0 if parsing fails
    """
    try:
        if rating_text:
            cleaned = rating_text.replace(decimal_separator, ".").strip()
            return float(cleaned)
    except:
        pass
    return 0.0


def clean_sold_count(sold_text):
    """
    Clean sold count text
    
    Args:
        sold_text: Raw sold count text from webpage
        
    Returns:
        str: Cleaned sold count text
    """
    try:
        cleaned = sold_text.replace("terjual", "").replace("Terjual", "").strip()
        return cleaned if cleaned else "N/A"
    except:
        return "N/A"


def ensure_absolute_url(url, base_url):
    """
    Ensure URL is absolute
    
    Args:
        url: URL to check
        base_url: Base URL to prepend if relative
        
    Returns:
        str: Absolute URL
    """
    if not url or url == "N/A":
        return "N/A"
    
    if not url.startswith('http'):
        return base_url + url
    
    return url


def format_timestamp(timestamp_format="%Y%m%d_%H%M%S"):
    """
    Generate formatted timestamp string
    
    Args:
        timestamp_format: Format string for timestamp
        
    Returns:
        str: Formatted timestamp
    """
    return time.strftime(timestamp_format)


def extract_rating_from_aria(aria_label):
    """
    Extract rating number from aria-label text
    
    Args:
        aria_label: Aria label text containing rating
        
    Returns:
        float: Extracted rating or None if not found
    """
    try:
        match = re.search(r"bintang\s*(\d+)", aria_label.lower())
        if match:
            return float(match.group(1))
    except:
        pass
    return None


def clean_html_to_text(html_content, separator="\n"):
    """
    Convert HTML content to clean text
    
    Args:
        html_content: Raw HTML content
        separator: Separator for line breaks
        
    Returns:
        str: Cleaned text content
    """
    from bs4 import BeautifulSoup
    
    try:
        # Replace common HTML line breaks with separator
        cleaned_html = html_content.replace("<br>", separator) \
                                  .replace("<br/>", separator) \
                                  .replace("<br />", separator)
        
        # Parse with BeautifulSoup and extract text
        soup = BeautifulSoup(cleaned_html, "html.parser")
        return soup.get_text(separator=separator).strip()
    except:
        return ""


def validate_product_data(product_data):
    """
    Validate that product data contains required fields
    
    Args:
        product_data: Dictionary containing product information
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ['title', 'new_price', 'old_price', 'image_url', 'rating', 'sold_count', 'product_url']
    
    if not isinstance(product_data, dict):
        return False
    
    # Check if all required fields exist
    for field in required_fields:
        if field not in product_data:
            return False
    
    # Check if title is meaningful (not N/A and has reasonable length)
    if product_data['title'] == "N/A" or len(product_data['title']) < 3:
        return False
    
    return True


def safe_element_text(element, default="N/A"):
    """
    Safely extract text from a web element
    
    Args:
        element: Selenium web element
        default: Default value if extraction fails
        
    Returns:
        str: Extracted text or default value
    """
    try:
        text = element.text.strip()
        return text if text else default
    except:
        return default


def safe_element_attribute(element, attribute, default="N/A"):
    """
    Safely extract attribute from a web element
    
    Args:
        element: Selenium web element
        attribute: Attribute name to extract
        default: Default value if extraction fails
        
    Returns:
        str: Extracted attribute value or default value
    """
    try:
        attr_value = element.get_attribute(attribute)
        return attr_value if attr_value else default
    except:
        return default


def log_progress(current, total, item_name="items", prefix="Processing"):
    """
    Log progress of an operation
    
    Args:
        current: Current item number
        total: Total number of items
        item_name: Name of items being processed
        prefix: Prefix for log message
    """
    percentage = (current / total) * 100 if total > 0 else 0
    print(f"{prefix} {current}/{total} {item_name} ({percentage:.1f}%)")


def create_filename_safe_string(text, max_length=50):
    """
    Create a filename-safe string from text
    
    Args:
        text: Input text
        max_length: Maximum length of output string
        
    Returns:
        str: Filename-safe string
    """
    # Remove or replace problematic characters
    safe_text = re.sub(r'[<>:"/\\|?*]', '_', text)
    safe_text = re.sub(r'\s+', '_', safe_text)  # Replace spaces with underscores
    safe_text = safe_text.strip('_')  # Remove leading/trailing underscores
    
    # Truncate if too long
    if len(safe_text) > max_length:
        safe_text = safe_text[:max_length].rstrip('_')
    
    return safe_text if safe_text else "unnamed"