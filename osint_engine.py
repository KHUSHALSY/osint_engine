import asyncio
import aiohttp
import time
import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
client = genai.Client()

TARGETS = {
    "GitHub": {"url": "https://github.com/{}", "type": "status"},
    "Reddit": {"url": "https://www.reddit.com/user/{}/about.json", "type": "reddit_json"},
    "HackerNews": {"url": "https://news.ycombinator.com/user?id={}", "type": "text", "not_found_text": "No such user."},
    "Medium": {"url": "https://medium.com/@{}", "type": "status"},
    "Dev.to": {"url": "https://dev.to/{}", "type": "status"},
    "Keybase": {"url": "https://keybase.io/{}", "type": "status"},
    "DockerHub": {"url": "https://hub.docker.com/u/{}", "type": "status"},
    "Patreon": {"url": "https://www.patreon.com/{}", "type": "status"},
    "Vimeo": {"url": "https://vimeo.com/{}", "type": "status"},
    "SoundCloud": {"url": "https://soundcloud.com/{}", "type": "status"},
    "Figma": {"url": "https://www.figma.com/@{}", "type": "status"},
    "Kaggle": {"url": "https://www.kaggle.com/{}", "type": "status"},
    "Linktree": {"url": "https://linktr.ee/{}", "type": "status"},
    "TryHackMe": {"url": "https://tryhackme.com/p/{}", "type": "status"},
    "HackTheBox": {"url": "https://app.hackthebox.com/users/{}", "type": "status"},
    "Pastebin": {"url": "https://pastebin.com/u/{}", "type": "status"},
    "npm": {"url": "https://www.npmjs.com/~{}", "type": "status"},
    "PyPI": {"url": "https://pypi.org/user/{}/", "type": "status"},
    "Flickr": {"url": "https://www.flickr.com/people/{}/", "type": "status"},
    "Codecademy": {"url": "https://www.codecademy.com/profiles/{}", "type": "status"}
}

async def check_profile(session, platform, data, username):
    url = data["url"].format(username)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    
    if data["type"] == "reddit_json":
        headers["User-Agent"] = "windows:osint-project:v1.0 (by /u/researcher)"
        headers["Accept"] = "application/json"

    try:
        async with session.get(url, headers=headers, timeout=10, ssl=False) as response:
            if data["type"] in ["status", "reddit_json"]:
                if response.status == 200:
                    return platform, True, url
                elif response.status == 404:
                    return platform, False, None
                else:
                    return platform, f"BLOCKED (HTTP {response.status})", None
                    
            elif data["type"] == "text":
                if response.status != 200:
                    return platform, f"BLOCKED (HTTP {response.status})", None
                text = await response.text()
                if data["not_found_text"] in text:
                    return platform, False, None
                return platform, True, url
                
    except asyncio.TimeoutError:
        return platform, "TIMEOUT (Tarpitted)", None
    except Exception as e:
        return platform, f"ERROR ({type(e).__name__})", None

async def fetch_profile_text(session, url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) OSINT-Scraper/1.0"}
    try:
        async with session.get(url, headers=headers, timeout=10, ssl=False) as response:
            if response.status == 200:
                text = await response.text()
                return f"Source: {url}\nContent: {text[:2000]}"
    except:
        return ""
    return ""

def generate_report(username, found_profiles, ai_report):
    if not os.path.exists("reports"):
        os.makedirs("reports")
        
    filename = f"reports/{username}_dossier.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# OSINT Dossier: {username}\n")
        f.write(f"*Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        f.write("## 1. Confirmed Profiles\n")
        for url in found_profiles:
            f.write(f"- {url}\n")
            
        f.write("\n## 2. AI Identity Correlation\n")
        f.write(ai_report)
        f.write("\n")
        
    print(f"\n[+] Full dossier saved to: {filename}")

async def correlate_identities(found_urls, username):
    print("\n[*] Initializing AI Correlation Engine...")
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_profile_text(session, url) for url in found_urls]
        html_dumps = await asyncio.gather(*tasks)

    valid_dumps = [dump for dump in html_dumps if dump]
    
    prompt = f"""
    You are an elite OSINT analyst. We discovered these public accounts for username '{username}': {', '.join(found_urls)}.
    Here is scraped data from those profiles:
    
    {valid_dumps}
    
    Analyze bio text, interests, technical stacks, or linguistic style.
    State the confidence score (0-100%) that these accounts belong to the same person.
    Highlight the specific evidence supporting or disputing this match in under 4 concise sentences.
    """
    
    print("[*] Correlating with gemini-3.5-flash-lite...")
    
    for attempt in range(3):
        try:
            chat = client.chats.create(model='gemini-3.5-flash-lite')
            response = chat.send_message(prompt)
            
            print("\n=== AI CORRELATION REPORT ===")
            print(response.text)
            print("=============================\n")
            
            return response.text 
            
        except errors.ServerError as e:
            if e.code == 503:
                wait_time = 2 ** attempt 
                print(f"[!] Google AI servers are busy. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"\n[!] Unexpected AI Server Error: {e}")
                return None
        except errors.ClientError as e:
            if e.code == 429:
                print("\n[!] QUOTA REACHED: You have exceeded your free tier API limits.")
                return None
            else:
                print(f"\n[!] Unexpected Client Error: {e}")
                return None
                
    print("\n[-] Failed to get an AI report because the servers remained overloaded.")
    return None

async def run_scan(username):
    print(f"\n[*] Initializing asynchronous target scan for: {username}")
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = [check_profile(session, platform, data, username) for platform, data in TARGETS.items()]
        results = await asyncio.gather(*tasks)
    
    print(f"[+] Network sweep of {len(TARGETS)} targets completed in {time.time() - start_time:.2f} seconds.\n")
    
    found_profiles = []
    for platform, status, url in results:
        if status is True:
            print(f"[✓] {platform.ljust(12)}: MATCH FOUND -> {url}")
            found_profiles.append(url)
        elif status is False:
            print(f"[x] {platform.ljust(12)}: Not found")
        else:
            print(f"[!] {platform.ljust(12)}: {status}")
    
    ai_report = None
    if len(found_profiles) > 1:
        ai_report = await correlate_identities(found_profiles, username)
        if ai_report:
            generate_report(username, found_profiles, ai_report)
    elif len(found_profiles) == 1:
        print("\n[-] Only one profile found. No cross-platform correlation possible.")
        ai_report = "Only one profile found. No cross-platform correlation possible."
    else:
        print("\n[-] No matches found across targets.")
        ai_report = "Ghost. No matches found across targets."

    return {
        "username": username,
        "profiles": found_profiles,
        "report": ai_report
    }