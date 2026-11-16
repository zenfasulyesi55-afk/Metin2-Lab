# OpenMT2 Sunucu ve Ağ Protokolü Denetim Raporu (Server Audit)

Bu belge, Metin2 özel sunucu ve istemci ağ mimarisinin offline ve uzak (remote) bağlantı profillerini inceler.

## 1. Sunucu Profilleri
* **Offline Profil:** Tamamen yerel ağda (Local Wi-Fi) veya internet bağımlılığı olmadan çalışabilen çevrimdışı sunucu yapılandırması.
* **Remote Profil:** Uzak VPS sunucuları üzerinden çok oyunculu bağlantı ve veri senkronizasyonu sağlayan altyapı.

## 2. Ağ Protokolü ve Haberleşme
* **TCP/IP Sockets:** İstemci ve sunucu arasındaki anlık veri alışverişi (oyuncu hareketleri, saldırılar, envanter) düşük gecikmeli TCP soketleri üzerinden yürütülür.
* **Paket Yapısı:** Oyun içi işlemler özel başlık (header) ve veri payload formatlarıyla paketlenir.

## 3. Laboratuvar Hedefi
Geliştirme sürecinin ilerleyen aşamalarında, harici VPS maliyeti oluşturmadan testler yapabilmek amacıyla yerel bir çevrimdışı sunucu paketi entegre edilecektir.
