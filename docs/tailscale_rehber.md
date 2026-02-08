# Tailscale Exit Node Kurulumu

Bu rehber, **yerel bilgisayarınızın** internetini **sunucu (EC2)** üzerinden gelen istekler için kullandırmayı anlatır. Böylece sunucu, Sahibinden'e bağlanırken sizin ev IP adresinizi kullanır.

## 1. Bilgisayarınızda (Windows) Yapılacaklar

1.  **Tailscale uygulamasını açın.** (Sağ alt köşedeki simge veya başlat menüsü).
2.  Tailscale simgesine sağ tıklayın > **Preferences (Ayarlar)** veya **Exit Node** seçeneğini bulun.
3.  **"Run as Exit Node"** onay kutusunu işaretleyin.
    *   *Not: Bu işlem sırasında Windows "Ağ Paylaşımı" vb. uyarılar verebilir, onaylayın.*
4.  Tailscale Admin Paneline gidin (tarayıcıda): [https://login.tailscale.com/admin/machines](https://login.tailscale.com/admin/machines)
5.  Listede kendi bilgisayarınızı bulun.
6.  Sağ taraftaki **... (üç nokta)** menüsüne tıklayın -> **"Edit route settings"**.
7.  **"Use as exit node"** seçeneğini etkinleştirin (Switch açık olsun).

## 2. Sunucuda (EC2) Yapılacaklar (Scraper Çalışmadan Önce)

Sunucunun sizin bilgisayarınızın internetini kullanması için şu komutu çalıştırmanız gerekir:

```bash
# Sunucuda (SSH ile bağlandıktan sonra):
sudo tailscale up --exit-node=<BILGISAYARINIZIN_TAILSCALE_IPSI_VEYA_ADI> --accept-routes
```

> **Bilgisayarınızın Tailscale IP'sini nasıl bulursunuz?**
> Bilgisayarınızda komut satırını açın (`cmd`) ve `tailscale ip` yazın. Veya Tailscale uygulamasında üstte yazar (örn: `100.x.y.z`).

## 3. Kontrol

Sunucuda şu komutu çalıştırarak IP adresinizin değiştiğini (ev IP'niz olduğunu) doğrulayın:

```bash
curl ifconfig.me
```
Eğer ev IP adresinizi görüyorsanız, işlem tamamdır! Artık scraper sunucuda çalışıp, sizin IP'nizden veri çekecektir.

## 4. Scraper'ı Başlatma

Ayarlar tamamlandıktan sonra sunucuda scraper'ı şu komutla başlatabilirsiniz (arka planda çalışır):

```bash
./run_background_low_load.bat 
# Veya Linux sunucu için:
nohup python3 services/scraper_v2.py --headless > logs/scraper.log 2>&1 &
```
