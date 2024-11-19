from bs4 import BeautifulSoup


async def extract_text_from_message(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition'))
            if content_type == 'text/plain' and 'attachment' not in content_disposition:
                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                break
            elif content_type == 'text/html' and 'attachment' not in content_disposition:
                html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                soup = BeautifulSoup(html, 'html.parser')
                body = soup.get_text(separator=' ', strip=True)
                break
    else:
        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
    return body