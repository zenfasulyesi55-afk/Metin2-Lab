# Bağımlılık ve Lisans Uygunluk Raporu (Dependency Audit)

Bu belge, MOBILE2-LAB projesinin derleme araçları, bağımlılıkları ve telif/lisans politikalarını belirler.

## 1. Sistem Bağımlılıkları
* **Java:** JDK 17 (Zulu / Temurin dağıtımı)
* **Android SDK:** Platform 33 (`platforms;android-33`) ve Build-Tools `33.0.2`
* **NDK:** Sürüm `25.2.9519653`
* **CMake:** Sürüm `3.22.1`

## 2. Derleme Araçları
* **AGP (Android Gradle Plugin):** `8.1.1`
* **Gradle Wrapper:** `8.13`
* **Hedef Mimariler:** Yalnızca 64-bit arm64 cihazlar (`arm64-v8a`)

## 3. Lisans ve Telif Hakları Politikası
* Webzen ve Gameforge mülkiyetindeki orijinal oyun varlıkları (texture, model, ses, pack dosyaları) projeye ve APK çıktısına dahil edilemez.
* Sadece açık kaynaklı C++ altyapısı ve motor katmanı derlenmektedir.
