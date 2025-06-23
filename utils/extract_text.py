def is_two_column_page(page):
    """
    Heuristically determines if a page is two-column by comparing
    the number of characters on the left and right halves of the page.
    """
    chars = page.chars
    width = page.width

    # Separate characters into left and right halves based on x position
    left_chars = [c for c in chars if c["x0"] < width / 2]
    right_chars = [c for c in chars if c["x0"] >= width / 2]

    total = len(left_chars) + len(right_chars)
    if total == 0:
        return False  # No text found on page

    # Calculate what percentage of text is in each half
    left_ratio = len(left_chars) / total
    right_ratio = len(right_chars) / total

    # If both sides have roughly equal content (35–65%), assume two-column
    return 0.35 < left_ratio < 0.65 and 0.35 < right_ratio < 0.65


def extract_single_column_text(page):
    """
    Extracts all the text from a single-column page.
    This is the default behavior for most PDFs.
    """
    text = page.extract_text()
    return text if text else ''


def extract_two_column_text(page):
    """
    Extracts text from both the left and right columns of a two-column page,
    then combines them in top-to-bottom reading order.
    """
    width = page.width
    height = page.height

    # Define bounding boxes for left and right halves of the page
    left_bbox = (0, 0, width / 2, height)
    right_bbox = (width / 2, 0, width, height)

    # Crop and extract text from each column
    left_text = page.within_bbox(left_bbox).extract_text()
    right_text = page.within_bbox(right_bbox).extract_text()

    combined = ''
    if left_text:
        combined += left_text + '\n'
    if right_text:
        combined += right_text + '\n'

    return combined


def extract_mixed_layout_lines(pdf):
    all_lines = []

    for i, page in enumerate(pdf.pages):
        page_num = i + 1
        chars = page.chars
        if not chars or len(chars) < 20:
            continue

        width = page.width
        height = page.height

        # Zones
        header_zone = (0, height * 0.75, width, height)
        middle_zone_left = (0, height * 0.2, width / 2, height * 0.75)
        middle_zone_right = (width / 2, height * 0.2, width, height * 0.75)
        footer_zone = (0, 0, width, height * 0.2)

        # Detect layout
        mid_chars = [c for c in chars if height * 0.2 <= c['top'] <= height * 0.75]
        left_chars = [c for c in mid_chars if c["x0"] < width / 2]
        right_chars = [c for c in mid_chars if c["x0"] >= width / 2]

        total = len(left_chars) + len(right_chars)
        is_two_col = 0.35 < len(left_chars)/total < 0.65 if total else False

        # Extract from zones
        def add_lines(bbox, col_label):
            text = page.within_bbox(bbox).extract_text()
            if text:
                for line in text.split("\n"):
                    all_lines.append({
                        "text": line.strip(),
                        "page": page_num,
                        "column": col_label
                    })

        add_lines(header_zone, "header")
        if is_two_col:
            add_lines(middle_zone_left, "left")
            add_lines(middle_zone_right, "right")
        else:
            add_lines((0, height * 0.2, width, height * 0.75), "full")
        add_lines(footer_zone, "footer")

    return all_lines



