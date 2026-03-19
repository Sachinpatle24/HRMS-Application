# app/services/experience_service.py
from app.core.logger import get_custom_logger
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

logger = get_custom_logger(app_name="experience_service")


# ============================================================
# Date Token Usability Check
# ============================================================


def _is_unusable_token(date_str):
    """Check if token is unusable (not a date, but not worth warning about)"""
    s = date_str.strip().lower()
    
    # Durations
    if re.match(r"^\d+\s*(year|month|day)s?", s):
        logger.debug(f"Skipped duration token: '{date_str}'")
        return True
    # Single month names
    if re.fullmatch(r"[a-z]{3,9}", s):
        logger.debug(f"Skipped incomplete date (month only): '{date_str}'")
        return True
    # Short numeric noise
    if re.fullmatch(r"[\d\-]+", s) and len(s) <= 5:
        logger.debug(f"Skipped ambiguous numeric token: '{date_str}'")
        return True
    # Academic/noise
    if s in {"-", "n/a", ""} or re.search(r"sgpa|gpa|internship", s):
        logger.debug(f"Skipped noise token: '{date_str}'")
        return True
    
    return False


# ============================================================
# Date Parsing 
# ============================================================


def parse_date(date_str):
    if not date_str or date_str.strip().lower() in {"present", "current", "till today", "till date", "till present", "till now", ""}:
        return datetime.today()

    try:
        original_str = date_str

        if _is_unusable_token(date_str):
            return None
        date_str = date_str.strip()
        
        # Early rejection: ranges, durations, noise
        if any(x in date_str for x in [" - ", "-", " – ", "–", " — ", "—"]):
            logger.debug(f"Range leaked to parse_date: '{original_str}'")
            return None
        
        date_str = (
            date_str
            .replace("'", "'")
            .replace("–", "-")
            .replace("—", "-")
            .replace("(", "")
            .replace(")", "")
            .replace(",", "")
            .replace("’", "'")
            .replace("‘", "'")
        )
        
        # Handle PRESENT/CURRENT keywords
        if date_str.upper() in ["PRESENT", "CURRENT", "TILL PRESENT", "TILL DATE", "TILL NOW"]:
            return datetime.today()
        
        # Remove ordinals
        date_str = re.sub(r'(\d{1,2})(st|nd|rd|th)', r'\1', date_str, flags=re.IGNORECASE)
        # Normalize Sept -> Sep BEFORE removing dots
        date_str = re.sub(r'\bSept\.?', 'Sep', date_str, flags=re.IGNORECASE)
        # Now remove dots
        date_str = date_str.replace(".", "")
        date_str = date_str.upper()

        # Handle "DEC- 2022" format
        if re.match(r"^[A-Z]{3}-\s*\d{4}$", date_str):
            date_str = re.sub(r"([A-Z]{3})-\s*(\d{4})", r"\1 \2", date_str)

        formats = [
            "%B %Y", "%b %Y", "%b'%y", "%B'%y", "%b-%Y", "%B-%Y",
            "%Y-%m-%d", "%Y-%m", "%m/%Y", "%Y/%m", "%Y",
            "%b%y", "%B%y", "%b %y", "%B %y",
            "%d %b %Y", "%d %B %Y",
            "%d/%m/%Y", "%d-%m-%Y", "%d-%b-%Y",
            "%b'%Y", "%b'%y",
            "%d-%B %Y", "%d-%B-%Y",
            "%d-%b %Y", "%d-%b-%Y",
            "%B/%Y", "%b/%Y"
        ]

        if re.match(r"^[A-Z]{3,9}\d{4}$", date_str):
            date_str = re.sub(r"([A-Z]+)(\d{4})", r"\1 \2", date_str)

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Only log if it looks like a real date that failed
        if re.search(r'\d{4}', original_str):
            logger.warning(f"Failed to parse date: '{original_str}'")
        
        return None
    except Exception as e:
        logger.error(f"Error parsing date '{original_str}': {e}")
        return None


# ============================================================
# Extraction Logic
# ============================================================


def extract_dates(exp):
    start_keys = ["startDate", "startdate", "start"]
    end_keys = ["endDate", "enddate", "end"]

    start = ""
    for key in start_keys:
        val = exp.get(key)
        if isinstance(val, str) and val.strip():
            start = val.strip()
            break

    end = ""
    for key in end_keys:
        val = exp.get(key)
        if isinstance(val, str) and val.strip():
            end = val.strip()
            break

    # Handle date ranges in startDate field
    if start and not end:
        for sep in [" - ", "-", " – ", "–", " — ", "—"]:
            if sep in start:
                left, right = start.split(sep, 1)
                start = left.strip()
                end = right.strip()
                break

    if end.lower() in {"present", "current", "till date", "till present", "now"}:
        end = "Present"

    return start, end


# ============================================================
# Experience Math
# ============================================================


def convert_years_months_to_decimal(years, months):
    total_months = years * 12 + months
    return round(total_months / 12, 2)


def format_years_months(years, months):
    parts = []
    if years:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months:
        parts.append(f"{months} month{'s' if months != 1 else ''}")
    return " ".join(parts) if parts else "0 months"


def calculate_total_experience(work_experiences):
    total_years = 0
    total_months = 0
    for exp in work_experiences:
        start_str, end_str = extract_dates(exp)
        start_date = parse_date(start_str)
        end_date = parse_date(end_str) if end_str else datetime.today()
        if not start_date or not end_date:
            continue
        if end_date < start_date:
            logger.warning(f"Invalid interval skipped: {start_str} → {end_str}")
            continue
        diff = relativedelta(end_date, start_date)
        total_years += diff.years
        total_months += diff.months
    total_years += total_months // 12
    remaining_months = total_months % 12
    return convert_years_months_to_decimal(total_years, remaining_months)


def format_total_experience_string(work_experiences):
    total_years = 0
    total_months = 0
    for exp in work_experiences:
        start_str, end_str = extract_dates(exp)
        start_date = parse_date(start_str)
        end_date = parse_date(end_str) if end_str else datetime.today()
        if not start_date or not end_date:
            continue
        if end_date < start_date:
            continue
        diff = relativedelta(end_date, start_date)
        total_years += diff.years
        total_months += diff.months
    total_years += total_months // 12
    remaining_months = total_months % 12
    return format_years_months(total_years, remaining_months)


def format_decimal_experience(decimal_exp: float) -> str:
    years = int(decimal_exp)
    months = round((decimal_exp - years) * 12)

    parts = []
    if years:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months:
        parts.append(f"{months} month{'s' if months != 1 else ''}")

    return " ".join(parts) if parts else "0 months"


def calculate_experience_per_company(work_experiences):
    experiences_decimal = []
    experiences_pretty = []
    for exp in work_experiences:
        start_str, end_str = extract_dates(exp)
        start = parse_date(start_str)
        end = parse_date(end_str) if end_str else datetime.today()
        if not start or not end or end < start:
            continue
        diff = relativedelta(end, start)
        if diff.years == 0 and diff.months == 0:
            continue
        decimal_exp = convert_years_months_to_decimal(diff.years, diff.months)
        pretty_exp = format_years_months(diff.years, diff.months)
        experiences_decimal.append(decimal_exp)
        experiences_pretty.append(pretty_exp)
    return experiences_decimal, experiences_pretty
