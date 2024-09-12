import requests
from bs4 import BeautifulSoup
import weasyprint
import os

# Function to fetch the main index of the GitBook and gather all page URLs
def fetch_all_page_urls(gitbook_url):
    response = requests.get(gitbook_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the links from the table of contents or summary (adjust this depending on the structure)
        toc_links = soup.select('a[href]')
        page_urls = []
        for link in toc_links:
            page_url = link['href']
            if page_url.startswith('/'):
                page_url = gitbook_url.rstrip('/') + page_url
            if gitbook_url in page_url:  # Only add valid GitBook pages
                page_urls.append(page_url)
        
        return page_urls
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        return []

# Function to fetch content from a GitBook page
def fetch_gitbook_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the title
        title_tag = soup.find('title')
        title = title_tag.text if title_tag else "GitBook Document"

        # Extract content (try multiple potential content structures)
        content_div = soup.find('div', class_='book-body') or \
                      soup.find('section') or \
                      soup.find('article') or \
                      soup.find('main')  # Add more checks based on your GitBook structure

        if content_div:
            return title, str(content_div)
        else:
            print(f"Could not find content on the page {url}.")
            return title, ""
    else:
        print(f"Failed to fetch the page {url}. Status code: {response.status_code}")
        return "", ""

# Function to convert HTML content to PDF
def convert_to_pdf(html_content, output_pdf):
    weasyprint.HTML(string=html_content).write_pdf(output_pdf)
    print(f"PDF saved to {output_pdf}")

# Main function to fetch and convert all GitBook pages to PDF
def gitbook_to_pdf(gitbook_url, output_pdf):
    # Fetch all page URLs
    page_urls = fetch_all_page_urls(gitbook_url)

    if not page_urls:
        print("No pages found to convert.")
        return

    print(f"Found {len(page_urls)} pages to convert.")

    # Fetch content for each page
    full_content = ""
    for i, page_url in enumerate(page_urls):
        title, content = fetch_gitbook_content(page_url)
        if content:
            full_content += f"<h1>{title}</h1>{content}"
        else:
            print(f"Warning: Content for page {page_url} could not be fetched or was empty.")
        print(f"Fetched and added content from page {i+1}/{len(page_urls)}: {page_url}")

    # Generate full HTML document
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{gitbook_url} - GitBook PDF</title>
    </head>
    <body>
        {full_content}
    </body>
    </html>
    """

    # Convert to PDF
    convert_to_pdf(html_content, output_pdf)

# Ensure output folder exists
if not os.path.exists('output'):
    os.makedirs('output')

# URL of the GitBook page
gitbook_url = "https://www.yourwebsite.com"

# Output PDF file path
output_pdf = "output/copied_gitbook.pdf"

# Run the conversion
gitbook_to_pdf(gitbook_url, output_pdf)
