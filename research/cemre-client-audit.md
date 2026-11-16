# Cemre Android İstemci Teknik Denetim Raporu (Client Audit)

Bu belge, `https://github.com/cemreefe/metin2-android` deposundan alınan C++ tabanlı Android istemci mimarisinin teknik analizini içerir.

## 1. Mimari Yapı ve Bileşenler
* **C++ Katmanı:** Oyun motorunun temel döngüsü, pencere yönetimi ve bellek optimizasyonu C++ ile yazılmıştır.
* **JNI (Java Native Interface):** Java tabanlı Android uygulama kabuğu ile C++ çekirdeği arasındaki köprü JNI katmanı üzerinden sağlanmaktadır.
* **Grafik Motoru:** Android cihazlarda donanımsal hızlandırma için **OpenGL ES 3.0** API'si kullanılmaktadır.
* **Derleme Hedefi:** Yalnızca 64-bit işlemciler hedef alınarak **`arm64-v8a`** ABI mimarisine göre yapılandırılmıştır.

## 2. Derleme Gereksinimleri
* **NDK:** Sürüm `25.2.9519653` gerektirir.
* **CMake:** Yerel C++ kütüphanelerini derlemek için `3.22.1` sürümü kullanılır.
* **Gradle:** Android Gradle Plugin `8.1.1` ve Gradle Wrapper `8.13` standartlarına tam uyumludur.

## 3. Güvenlik ve Lisans Notu
Oyunun orijinal varlıkları (pack, ses, model ve doku dosyaları) telif hakları nedeniyle istemci APK paketine gömülmemelidir. Sadece motor ikilileri (binaries) ve kaynak kod altyapısı bu laboratuvar ortamında derlenmektedir.
