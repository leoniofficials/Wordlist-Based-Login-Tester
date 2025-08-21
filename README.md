<b> Wordlist Based Login Tester </b>

Bu proje, wordlist tabanlı brute-force login test aracıdır.
Amaç; siber güvenlik araştırmaları, penetrasyon testleri ve parola güvenliği denemeleri için kullanılabilir.

⚠️ Uyarı: Bu yazılım yalnızca kendi sistemlerinizde ve izinli testlerde kullanılmalıdır.
Başka kişilerin/kurumların sistemlerine izinsiz erişim yasalara aykırıdır.


Dipnot: Sitenin URL'sini değiştirmeniz gerekli kodlardan.

<b> Özellikler

 Wordlist’ten otomatik parola denemesi

 CSRF Token desteği

 Cloudflare engellerini aşmak için cookie desteği

 Gecikme (--delay) parametresi

 Başarılı giriş bulunduğunda otomatik olarak kaydeder. 
 </b>

Kurulum

git clone https://github.com/leoniofficials/Wordlist-Based-Login-Tester

cd wordlist-based-login-tester

pip install -r requirements.txt

Kullanım
Basit kullanım:
python basedwordlist.py --user leoniofficials -P wordlist.txt

Gelişmiş kullanım:
python basedwordlist.py --user leoniofficials -P wordlist.txt --delay 0.5 --csrf csrf_token --error "Yanlış şifre!" --cookies cookies.txt

Parametreler:

--user → Hedef kullanıcı adı

-P / --passlist → Wordlist dosyası (parolalar)

--delay → Her deneme arasında bekleme süresi (saniye)

--csrf → Formda kullanılan CSRF token adı

--error → Hatalı giriş mesajı

--cookies → Daha önce alınmış tarayıcı cookie bilgileri (opsiyonel)

 Örnek Çalışma
GET https://hedefsite.com/login → 200

 Deneniyor: 123456
 
 Başarısız: 123456
 
 Deneniyor: xxxxx
 
 Şifre bulundu: xxxxx


 
