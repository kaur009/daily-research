import os
import random
import re
import requests
import io
import urllib.request
import xml.etree.ElementTree as ET
import subprocess
import time
from datetime import datetime, timedelta
from google import genai 
from pypdf import PdfReader

# --- CONFIGURATION ---
CATEGORIES = ['cs.CV', 'cs.AI', 'cs.LG', 'cs.CL', 'cs.RO', 'cs.CR', 'cs.SE']
CATEGORY_NAMES = {
    'cs.CV': 'Computer Vision', 'cs.AI': 'Artificial Intelligence',
    'cs.LG': 'Machine Learning', 'cs.CL': 'NLP', 'cs.RO': 'Robotics',
    'cs.CR': 'Cryptography', 'cs.SE': 'Software Engineering'
}

# --- DECISION ENGINE ---
def decision_engine():
    """
    Decides activity based on a sparse, random pattern.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # Check when we last worked
    last_run_date = ""
    if os.path.exists("run_log.txt"):
        with open("run_log.txt", "r") as f:
            lines = f.readlines()
            if lines:
                # Extract date from last line "[2025-01-09 14:00:00]..."
                last_line = lines[-1]
                match = re.search(r"\[(\d{4}-\d{2}-\d{2})", last_line)
                if match:
                    last_run_date = match.group(1)

    # 1. FORCED REST: If we worked yesterday, 40% chance to force a skip today
    # (This creates the 1-day gaps)
    if last_run_date:
        last_date_obj = datetime.strptime(last_run_date, "%Y-%m-%d")
        days_since_last = (datetime.now() - last_date_obj).days
        
        if days_since_last == 1:
            if random.random() < 0.40:
                print("Taking a rest day after working yesterday.")
                return 0

    # 2. Main Dice Roll (0.0 to 1.0)
    roll = random.random()
    
    # 50% chance to SKIP completely (create gaps)
    if roll < 0.50:
        print(f"Dice Roll ({roll:.2f}): Lazy Day. Skipping.")
        return 0
        
    # 30% chance for NORMAL consistency (1 commit)
    elif roll < 0.80:
        print(f"Dice Roll ({roll:.2f}): Normal Work Day.")
        return 1
        
    # 20% chance for BURST (2-5 commits)
    else:
        burst = random.randint(2, 5)
        print(f"Dice Roll ({roll:.2f}): CRUNCH MODE! Doing {burst} commits.")
        return burst

# --- CORE FUNCTIONS (unchanged) ---

API_KEY = os.environ.get("GEMINI_API_KEY")
client = None
if API_KEY:
    client = genai.Client(api_key=API_KEY)

def git_commit_and_push(paper_title):
    try:
        subprocess.run(["git", "add", "."], check=True)
        commit_message = f"Added notes for: {paper_title[:30]}..."
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Git push successful.")
    except subprocess.CalledProcessError as e:
        print(f"Git Error: {e}")

def log_run(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("run_log.txt", "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def fetch_paper_data():
    category = random.choice(CATEGORIES)
    url = f'http://export.arxiv.org/api/query?search_query=cat:{category}&start=0&max_results=50&sortBy=submittedDate&sortOrder=descending'
    try:
        with urllib.request.urlopen(url) as response:
            root = ET.fromstring(response.read())
        entries = root.findall('{http://www.w3.org/2005/Atom}entry')
        return entries, category
    except Exception as e:
        print(f"ArXiv Error: {e}")
        return None, None

def process_one_paper():
    entries, category = fetch_paper_data()
    if not entries: return False

    random.shuffle(entries)
    for entry in entries:
        title = entry.find('{http://www.w3.org/2005/Atom}title').text.replace('\n', ' ').strip()
        date = entry.find('{http://www.w3.org/2005/Atom}published').text[:10]
        safe_title = re.sub(r'[^\w\-_\. ]', '', title).replace(' ', '_')[:40]
        filename = f"papers/{date}_{safe_title}.md"
        
        if not os.path.exists(filename):
            pdf_link = entry.find('{http://www.w3.org/2005/Atom}id').text.replace("/abs/", "/pdf/") + ".pdf"
            link = entry.find('{http://www.w3.org/2005/Atom}id').text
            
            text = ""
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                resp = requests.get(pdf_link, headers=headers)
                reader = PdfReader(io.BytesIO(resp.content))
                for p in reader.pages[:6]: text += p.extract_text()
            except:
                text = "PDF Extraction failed."

            summary = "AI Summary Unavailable."
            if client and len(text) > 500:
                try:
                    prompt = "Summarize this research paper in Markdown (Problem, Method, Impact):\n" + text[:40000]
                    resp = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                    summary = resp.text
                except Exception as e:
                    summary = f"Gemini Error: {e}"
            
            if not os.path.exists("papers"): os.makedirs("papers")
            content = f"# {title}\n\n- **Category:** {CATEGORY_NAMES.get(category, category)}\n- **Date:** {date}\n- **Link:** {link}\n\n---\n{summary}"
            with open(filename, "w", encoding='utf-8') as f: f.write(content)
            
            log_run(f"Processed: {title}")
            git_commit_and_push(title)
            return True
            
    return False

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    commits_today = decision_engine()
    
    if commits_today > 0:
        print(f"Starting work... Target: {commits_today} papers.")
        for i in range(commits_today):
            success = process_one_paper()
            if success:
                print(f"Commit {i+1}/{commits_today} done.")
                if i < commits_today - 1:
                    wait_time = random.randint(120, 600) # Wait 2-10 mins between bursts
                    print(f"Thinking for {wait_time} seconds...")
                    time.sleep(wait_time)
            else:
                print("Could not find new paper or error occurred.")
    else:
        # We purposely do NOT write to run_log.txt on skip days 
        # so the 'last_run_date' logic sees a gap next time.
        print("Skipped run (Decision Engine).")
