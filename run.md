.venv\Scripts\Activate.ps1

pip install -r requirements.txt

# Crawl a webpage

python main.py crawl --url https://example.com/article

# Extract an Abstract

python main.py abstract --url https://example.com/article

# Generate the Latest 10 Unique News Articles

python main.py news --url https://example.com/ --limit 10