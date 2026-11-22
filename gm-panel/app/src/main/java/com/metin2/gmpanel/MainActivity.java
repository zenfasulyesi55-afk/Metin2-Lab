package com.metin2.gmpanel;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Bundle;
import android.text.Editable;
import android.text.InputType;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends Activity {
    private EditText edHost, edKey, edNick;
    private EditText edCode, edSearch, edItemVnum, edAcc, edTargetNick, edNewPass;
    private EditText edBuildCode, edBuildCnt, edPosName, edNotice, edCustom;
    private TextView tvStatus;
    private LinearLayout boxConn, boxSearchRes, boxAccList, boxFavList;
    private LinearLayout[] tabPanels = new LinearLayout[5];
    private Button[] tabBtns = new Button[5];
    private Spinner[] spAttr = new Spinner[5];
    private EditText[] edAttrVal = new EditText[5];
    private SharedPreferences prefs;
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private boolean connVisible = false;

    private static final String[] ATTR_LABELS = {
        "0 - (Yok)", "1 - Max HP", "2 - Max SP", "3 - Canlilik (VIT)", "4 - Zeka (INT)",
        "5 - Guc (STR)", "6 - Ceviklik (DEX)", "7 - Saldiri Hizi", "8 - Hareket Hizi",
        "9 - Buyu Hizi", "12 - Zehirleme", "13 - Sersemletme", "15 - Kritik Vurus",
        "16 - Delici Vurus", "17 - Yari Insan", "21 - Olumsuzler", "22 - Seytanlar",
        "23 - HP Absorbe", "27 - Bloklama", "29 - Kilic Sav.", "30 - Ciftel Sav.",
        "31 - Bicak Sav.", "34 - Ok Sav.", "37 - Buyu Sav.", "53 - Saldiri Degeri",
        "63 - Canavar Gucu", "71 - Beceri Hasari", "72 - Ortalama Zarar"
    };
    private static final int[] ATTR_IDS = {
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 15, 16, 17, 21, 22, 23, 27, 29, 30, 31, 34, 37, 53, 63, 71, 72
    };

    private static final String[][] CATALOG = {
        {"19", "Kilic +9", "ITEM"}, {"189", "Zehir Kilici +9", "ITEM"}, {"279", "Sirius (Triton) +9", "ITEM"},
        {"299", "Dolunay Kilici +9", "ITEM"}, {"149", "Muharebe Kilici +9", "ITEM"}, {"3169", "Kin Kilici +9", "ITEM"},
        {"1139", "Seytan Kanadi Cakram +9", "ITEM"}, {"2179", "Buyuk Seytan Yayi +9", "ITEM"},
        {"5129", "Orkide Cani +9", "ITEM"}, {"7169", "Iblisin Yelpazesi +9", "ITEM"},
        {"11971", "Kraliyet Zirhi (Savasci)", "ITEM"}, {"11972", "Kraliyet Zirhi (Ninja)", "ITEM"},
        {"11973", "Kraliyet Zirhi (Sura)", "ITEM"}, {"11974", "Kraliyet Zirhi (Saman)", "ITEM"},
        {"11299", "Siyah Celik Zirh +9", "ITEM"}, {"11499", "Siyah Ruzgar Takimi +9", "ITEM"},
        {"11699", "Karabuyu Zirh +9", "ITEM"}, {"11899", "Siyah Elbise +9", "ITEM"},
        {"13069", "Sahin Kalkan +9", "ITEM"}, {"12249", "Hayalet Maske Baslik +9", "ITEM"},
        {"14209", "Cennetin Gozu Bilezik +9", "ITEM"}, {"16209", "Cennetin Gozu Kolye +9", "ITEM"},
        {"17109", "Abanoz Kupe +9", "ITEM"}, {"15209", "Anka Ayakkabi +9", "ITEM"},
        {"71084", "Efsun Nesnesi", "ITEM"}, {"71085", "Arttirma Kagidi", "ITEM"}, {"70024", "Kutsama Kuresi", "ITEM"},
        {"25041", "Buyulu Metal", "ITEM"}, {"71051", "6-7 Efsun Ekleme", "ITEM"}, {"71052", "6-7 Efsun Degistirme", "ITEM"},
        {"28430", "Kavrama Tasi +4", "ITEM"}, {"28431", "Oldurucu Darbe Tasi +4", "ITEM"}, {"28432", "Canavardan Koruyan +4", "ITEM"},
        {"28433", "Savascidan Koruyan +4", "ITEM"}, {"28434", "Ninjadan Koruyan +4", "ITEM"}, {"28435", "Suradan Koruyan +4", "ITEM"},
        {"28436", "Samandan Koruyan +4", "ITEM"}, {"28441", "Savunma Tasi +4", "ITEM"}, {"28442", "Hiz Tasi +4", "ITEM"},
        {"28443", "Yasam Tasi +4", "ITEM"}, {"71124", "Beyaz Aslan Muhru", "ITEM"}, {"50011", "Ayisigi Define Sandigi", "ITEM"},
        {"1093", "Lusifer (Azrail) Boss", "MOB"}, {"2493", "Beran-Setaou (Mavi Ejder)", "MOB"},
        {"2291", "Kirmizi Ejderha Boss", "MOB"}, {"1192", "Guclu Buz Cadisi", "MOB"},
        {"691", "Ork Reisi Boss", "MOB"}, {"1901", "Dokuz Kuyruk Boss", "MOB"}, {"2091", "Kralice Orumcek", "MOB"},
        {"2598", "Azrail (Katakomb)", "MOB"}, {"8027", "Jeon-Un Metini (90 Lv)", "MOB"}, {"8024", "Pung-Ma Metini (75 Lv)", "MOB"},
        {"20016", "Demirci (Yapi/NPC)", "MOB"}, {"9005", "Depocu (Yapi/NPC)", "MOB"}, {"9003", "Satici (Yapi/NPC)", "MOB"},
        {"20044", "Lonca Silahcisi", "MOB"}, {"20045", "Lonca Zirhcisi", "MOB"}, {"20046", "Lonca Kuyumcusu", "MOB"},
        {"20091", "Seon-Pyeong Aniti", "MOB"}, {"20358", "Cicek / Obje", "MOB"}
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs = getSharedPreferences("m2_owner_panel", MODE_PRIVATE);

        LinearLayout outer = new LinearLayout(this);
        outer.setOrientation(LinearLayout.VERTICAL);
        outer.setBackgroundColor(Color.parseColor("#0F1218"));

        // UST BASLIK + DURUM + BAGLANTI AYARI
        LinearLayout topBar = new LinearLayout(this);
        topBar.setOrientation(LinearLayout.VERTICAL);
        topBar.setPadding(24, 24, 24, 14);
        topBar.setBackgroundColor(Color.parseColor("#161B24"));

        LinearLayout headRow = new LinearLayout(this);
        headRow.setOrientation(LinearLayout.HORIZONTAL);
        headRow.setGravity(Gravity.CENTER_VERTICAL);
        TextView title = new TextView(this);
        title.setText("OYUN SAHIBI PANELI");
        title.setTextColor(Color.parseColor("#FFD166"));
        title.setTextSize(17);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        LinearLayout.LayoutParams tp = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
        title.setLayoutParams(tp);
        headRow.addView(title);

        final Button btnConn = makeSmallBtn("BAGLANTI AYARI", "#2B3548");
        btnConn.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
                connVisible = !connVisible;
                boxConn.setVisibility(connVisible ? View.VISIBLE : View.GONE);
            }
        });
        headRow.addView(btnConn);
        topBar.addView(headRow);

        tvStatus = new TextView(this);
        tvStatus.setText("Durum: Hazir (Karakter: " + prefs.getString("nick", "Test") + ")");
        tvStatus.setTextColor(Color.parseColor("#6EE7B7"));
        tvStatus.setTextSize(12);
        tvStatus.setPadding(0, 8, 0, 8);
        topBar.addView(tvStatus);

        boxConn = new LinearLayout(this);
        boxConn.setOrientation(LinearLayout.VERTICAL);
        boxConn.setVisibility(View.GONE);
        edHost = addInput(boxConn, "Sunucu IP", prefs.getString("host", "127.0.0.1"), false, false);
        edKey = addInput(boxConn, "Admin Sifresi", prefs.getString("key", "CHANGE_ME_LOCAL_ONLY"), false, true);
        edNick = addInput(boxConn, "Sahip Karakter Nicki", prefs.getString("nick", "Test"), false, false);
        Button btnSaveConn = makeSmallBtn("AYARLARI KAYDET", "#1F6F50");
        btnSaveConn.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
                saveConn();
                connVisible = false;
                boxConn.setVisibility(View.GONE);
                tvStatus.setText("Durum: Ayarlar kaydedildi (Nick: " + edNick.getText().toString().trim() + ")");
            }
        });
        boxConn.addView(btnSaveConn);
        topBar.addView(boxConn);

        // 5 SEKME CUBUGU
        LinearLayout tabBar = new LinearLayout(this);
        tabBar.setOrientation(LinearLayout.HORIZONTAL);
        tabBar.setPadding(6, 8, 6, 8);
        tabBar.setBackgroundColor(Color.parseColor("#111620"));
        String[] tabNames = {"KARAKTER", "ESYA/EFSUN", "HESAP/BAN", "YAPI/MAP", "SUNUCU"};
        for (int i = 0; i < 5; i++) {
            final int idx = i;
            Button tb = new Button(this);
            tb.setText(tabNames[i]);
            tb.setTextSize(10);
            tb.setTextColor(Color.WHITE);
            tb.setPadding(4, 16, 4, 16);
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
            lp.setMargins(3, 0, 3, 0);
            tb.setLayoutParams(lp);
            tb.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) { selectTab(idx); }
            });
            tabBtns[i] = tb;
            tabBar.addView(tb);
        }

        outer.addView(topBar);
        outer.addView(tabBar);

        ScrollView sv = new ScrollView(this);
        sv.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));
        LinearLayout contentWrap = new LinearLayout(this);
        contentWrap.setOrientation(LinearLayout.VERTICAL);
        contentWrap.setPadding(22, 16, 22, 48);

        for (int i = 0; i < 5; i++) {
            tabPanels[i] = new LinearLayout(this);
            tabPanels[i].setOrientation(LinearLayout.VERTICAL);
            contentWrap.addView(tabPanels[i]);
        }

        buildTabCharacter(tabPanels[0]);
        buildTabItemAttr(tabPanels[1]);
        buildTabAccounts(tabPanels[2]);
        buildTabBuildMap(tabPanels[3]);
        buildTabServer(tabPanels[4]);

        sv.addView(contentWrap);
        outer.addView(sv);
        setContentView(outer);
        selectTab(0);
    }

    private void selectTab(int idx) {
        for (int i = 0; i < 5; i++) {
            tabPanels[i].setVisibility(i == idx ? View.VISIBLE : View.GONE);
            tabBtns[i].setBackgroundColor(Color.parseColor(i == idx ? "#2563EB" : "#222A38"));
        }
    }

    // ==================== SEKME 1: KARAKTER & PARLAMA ====================
    private void buildTabCharacter(LinearLayout p) {
        addSec(p, "Guc, Seviye ve Olumsuzluk");
        addRow(p, new String[]{"LV. 99", "LV. 120", "FULL HP/SP"}, new String[]{"/level 99", "/level 120", "/r"});
        addRow(p, new String[]{"999M YANG", "SKILLER P", "AT LV. 21"}, new String[]{"GOLD999", "SKILLP", "HORSE21"});
        addRow(p, new String[]{"HIZ FULL", "GORUNMEZ", "KAHRAMAN"}, new String[]{"SPEED", "/inv", "ALIGN_HERO"});
        addRow(p, new String[]{"GOD MODE AC", "GOD MODE KAPA", "STATU FULL"}, new String[]{"GODMODE 1", "GODMODE 0", "STAT_FULL"});
        addRow(p, new String[]{"ENVANTER SIL (/ip)", "ETRAFI TEMIZLE"}, new String[]{"/ip", "/purge"});

        addSec(p, "Karakter Parlama Auralari (Ac / Kapa)");
        addRow(p, new String[]{"ALTIN ZIRH", "MOR KALKAN", "KIRMIZI OFKE"}, new String[]{"GLOW 0", "GLOW 1", "GLOW 2"});
        addRow(p, new String[]{"MAVI KILIC", "KUTSAL ISIK", "ALEV AURA"}, new String[]{"GLOW 3", "GLOW 4", "GLOW 5"});
        addRow(p, new String[]{"GM PARLAMA", "TUMUNU KAPAT"}, new String[]{"GLOW 6", "GLOW -1"});

        addSec(p, "VIP Surekli Parlama & Ozel Efektler");
        addRow(p, new String[]{"VIP ISIK AC", "VIP FISEK AC", "VIP MOR AC"}, new String[]{"PULSE 1", "PULSE 2", "PULSE 4"});
        addRow(p, new String[]{"VIP PARLAMA KAPAT"}, new String[]{"PULSE 0"});
        addRow(p, new String[]{"SEVIYE ISIGI", "HAVAI FISEK", "TOPAC FISEK"}, new String[]{"FX 0", "FX 1", "FX 2"});
        addRow(p, new String[]{"MOR DALGA", "KRITIK SIMSEK", "MAVI ENERJI"}, new String[]{"FX 3", "FX 4", "FX 5"});

        addSec(p, "Hizli Donusum (/poly)");
        addRow(p, new String[]{"AZRAIL OL", "MAVI EJDER OL", "NORMAL DON"}, new String[]{"/poly 1093", "/poly 2493", "/poly 0"});
    }

    // ==================== SEKME 2: ESYA & 5 EFSUNLU URETICI ====================
    private void buildTabItemAttr(LinearLayout p) {
        addSec(p, "5 Efsunlu Ozel Esya Uretici");
        edItemVnum = addInput(p, "Esya Kodu (Orn: 189 Zehir, 11971 Kraliyet)", "189", true, false);

        for (int i = 0; i < 5; i++) {
            LinearLayout row = new LinearLayout(this);
            row.setOrientation(LinearLayout.HORIZONTAL);
            row.setPadding(0, 4, 0, 4);

            Spinner sp = new Spinner(this);
            ArrayAdapter<String> ad = new ArrayAdapter<String>(this, android.R.layout.simple_spinner_item, ATTR_LABELS) {
                @Override public View getView(int pos, View cv, ViewGroup pr) {
                    TextView tv = (TextView) super.getView(pos, cv, pr);
                    tv.setTextColor(Color.WHITE); tv.setTextSize(12); return tv;
                }
                @Override public View getDropDownView(int pos, View cv, ViewGroup pr) {
                    TextView tv = (TextView) super.getDropDownView(pos, cv, pr);
                    tv.setTextColor(Color.WHITE); tv.setBackgroundColor(Color.parseColor("#1E2430"));
                    tv.setPadding(18, 16, 18, 16); tv.setTextSize(13); return tv;
                }
            };
            sp.setAdapter(ad);
            sp.setBackgroundColor(Color.parseColor("#1E2430"));
            LinearLayout.LayoutParams slp = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 2.3f);
            slp.setMargins(0, 0, 8, 0);
            sp.setLayoutParams(slp);
            spAttr[i] = sp;
            row.addView(sp);

            EditText ev = new EditText(this);
            ev.setText("0");
            ev.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_SIGNED);
            ev.setTextColor(Color.WHITE);
            ev.setBackgroundColor(Color.parseColor("#1E2430"));
            ev.setPadding(14, 12, 14, 12);
            ev.setTextSize(13);
            ev.setLayoutParams(new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));
            edAttrVal[i] = ev;
            row.addView(ev);
            p.addView(row);
        }

        addRow(p, new String[]{"VS SILAH", "VS ZIRH", "BOSS/FARM", "EDIT 32K"},
               new String[]{"PRESET_VS_W", "PRESET_VS_A", "PRESET_FARM", "PRESET_EDIT"});
        addRow(p, new String[]{"5 EFSUNLU ESYAYI ENVANTERE VER"}, new String[]{"MAKE_ITEM"});

        addSec(p, "Kod Arama Sozlugu (Dokun -> Kodu Doldur)");
        edSearch = addInput(p, "Ara: zehir, celik, kraliyet, efsun, tas, ejder...", "", false, false);
        boxSearchRes = new LinearLayout(this);
        boxSearchRes.setOrientation(LinearLayout.VERTICAL);
        p.addView(boxSearchRes);
        edSearch.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int a, int b, int c) {}
            @Override public void onTextChanged(CharSequence s, int a, int b, int c) { refreshSearch(s.toString()); }
            @Override public void afterTextChanged(Editable s) {}
        });

        addSec(p, "Hizli Kod ile Esya / Boss");
        edCode = addInput(p, "Esya veya Mob Kodu", "19", true, false);
        addRow(p, new String[]{"ESYA VER (/item)", "BOSS / MOB CAGIR (/m)"}, new String[]{"ITEM_CODE", "MOB_CODE"});

        addSec(p, "Hazir Paketler & Sinif Setleri");
        addRow(p, new String[]{"200x EFSUN", "200x ARTTIRMA", "KUTSAMA KURESI"}, new String[]{"/i 71084 200", "/i 71085 200", "/i 70024 50"});
        addRow(p, new String[]{"+4 TAS PAKETI", "SAVASCI SET", "NINJA SET"}, new String[]{"PACK_STONES", "SET_WAR", "SET_NINJA"});
        addRow(p, new String[]{"SURA SET", "SAMAN SET", "BEYAZ ASLAN"}, new String[]{"SET_SURA", "SET_SHAMAN", "/item 71124"});
    }

    // ==================== SEKME 3: HESAP, SIFRE & BAN ====================
    private void buildTabAccounts(LinearLayout p) {
        addSec(p, "Tum Oyuncu Hesaplari, Sifreler & Karakterler");
        addRow(p, new String[]{"HESAPLARI & SIFRELERI GETIR", "KARAKTERLERI LISTELE"}, new String[]{"LISTACC", "LISTCHARS"});

        boxAccList = new LinearLayout(this);
        boxAccList.setOrientation(LinearLayout.VERTICAL);
        boxAccList.setPadding(4, 6, 4, 6);
        p.addView(boxAccList);

        addSec(p, "Hesap Yonetimi (Ban, Sifre, Silme, GM)");
        edAcc = addInput(p, "Hedef Hesap Adi (Listeden dokunabilirsin)", "", false, false);
        edTargetNick = addInput(p, "Hedef Karakter Nicki", "", false, false);
        edNewPass = addInput(p, "Yeni Sifre (Sadece sifre degistirirken)", "", false, false);

        addRow(p, new String[]{"HESABI BANLA", "BANI AC", "SIFRE DEGISTIR"}, new String[]{"ACT_BAN", "ACT_UNBAN", "ACT_SETPASS"});
        addRow(p, new String[]{"GM YETKISI VER", "GM YETKISI AL", "HESABI SIL"}, new String[]{"ADDGM", "DELGM", "ACT_DELACC"});

        addSec(p, "Canli Oyuncu Mudahale (Hedef Nick)");
        addRow(p, new String[]{"OYUNDAN AT (/dc)", "SUSTUR 10 DK", "YANINA CEK"}, new String[]{"PL_DC", "PL_MUTE", "PL_PULL"});
        addRow(p, new String[]{"YANINA GIT", "DONDUR (/stun)", "OLDUR (/kill)"}, new String[]{"PL_WARP", "PL_STUN", "PL_KILL"});
    }

    // ==================== SEKME 4: YAPI & HARITA ====================
    private void buildTabBuildMap(LinearLayout p) {
        addSec(p, "Anlik Yapi / Obje / NPC Koyma & Kaldirma");
        edBuildCode = addInput(p, "Yapi / NPC / Obje Kodu (Orn: 20016 Demirci)", "20016", true, false);
        edBuildCnt = addInput(p, "Adet", "1", true, false);
        addRow(p, new String[]{"BULUNDUGUM YERE KOY", "YAKINDAKILERI SIL (/purge)"}, new String[]{"BUILD_PLACE", "/purge"});

        addRow(p, new String[]{"DEMIRCI", "DEPOCU", "SATICI"}, new String[]{"/m 20016", "/m 9005", "/m 9003"});
        addRow(p, new String[]{"SILAHCI", "ZIRHCI", "SIMYACI"}, new String[]{"/m 9001", "/m 9002", "/m 20001"});
        addRow(p, new String[]{"ISINLAYICI", "LONCA SILAH", "LONCA ZIRH"}, new String[]{"/m 9012", "/m 20044", "/m 20045"});
        addRow(p, new String[]{"LONCA KUYUMCU", "SEHIR BEKCISI", "ANIT / HEYKEL"}, new String[]{"/m 20046", "/m 11000", "/m 20091"});

        addSec(p, "Genis Isinlanma Menusu");
        addRow(p, new String[]{"KIRMIZI KOY", "SARI KOY", "MAVI KOY"}, new String[]{"/go a", "/go b", "/go c"});
        addRow(p, new String[]{"VADI", "COL", "SOHAN DAGI"}, new String[]{"/go t", "/go d", "/go s"});
        addRow(p, new String[]{"DOYYUMHWAN", "SEYTAN KULESI", "KIZIL ORMAN"}, new String[]{"/go f", "/go dt", "/go red"});
        addRow(p, new String[]{"ORUMCEK ZIND.", "SURGUN MAG."}, new String[]{"/go spider", "/go grotto"});

        addSec(p, "Favori Konumlarim (Koordinat Kaydet)");
        edPosName = addInput(p, "Konum Adi (Orn: Boss Meydani)", "Gizli Nokta", false, false);
        addRow(p, new String[]{"BULUNDUGUM YERI KAYDET", "FAVORILERI TEMIZLE"}, new String[]{"SAVE_POS", "CLEAR_POS"});
        boxFavList = new LinearLayout(this);
        boxFavList.setOrientation(LinearLayout.VERTICAL);
        p.addView(boxFavList);
        renderFavs();
    }

    // ==================== SEKME 5: SUNUCU & EVENT ====================
    private void buildTabServer(LinearLayout p) {
        addSec(p, "Drop Oranlari (% EXP / YANG / ESYA)");
        addRow(p, new String[]{"%200 TUM DROP", "%500 TUM DROP"}, new String[]{"DROP_200", "DROP_500"});
        addRow(p, new String[]{"%1000 TUM DROP", "DROPLARI KAPAT"}, new String[]{"DROP_1000", "DROP_0"});

        addSec(p, "Boss & Metin Yagmuru");
        addRow(p, new String[]{"5x AZRAIL", "5x MAVI EJDER", "5x 90 METIN"}, new String[]{"/m 1093 5", "/m 2493 5", "/m 8027 5"});
        addRow(p, new String[]{"3x KIRMIZI EJDER", "5x BUZ CADISI", "TEMIZLE (/purge)"}, new String[]{"/m 2291 3", "/m 1192 5", "/purge"});

        addSec(p, "Hava & Atmosfer");
        addRow(p, new String[]{"GECE", "GUNDUZ", "KAR YAGDIR", "KAR DURDUR"}, new String[]{"/x 1", "/x 2", "/xmas_snow 1", "/xmas_snow 0"});

        addSec(p, "Duyuru & Serbest GM Komutu");
        edNotice = addInput(p, "Duyuru Metni", "Event basliyor!", false, false);
        addRow(p, new String[]{"BUYUK DUYURU (/b)", "SOHBET DUYURU (/n)"}, new String[]{"BIG_NOTICE", "NORM_NOTICE"});
        edCustom = addInput(p, "Serbest GM Komutu (Orn: /poly 1093)", "/n Selam!", false, false);
        addRow(p, new String[]{"SERBEST KOMUTU GONDER"}, new String[]{"CUSTOM"});
    }

    // ==================== YARDIMCI UI FONKSIYONLARI ====================
    private void addSec(LinearLayout p, String t) {
        TextView tv = new TextView(this);
        tv.setText(t);
        tv.setTextColor(Color.parseColor("#60A5FA"));
        tv.setTextSize(13);
        tv.setTypeface(Typeface.DEFAULT_BOLD);
        tv.setPadding(0, 18, 0, 6);
        p.addView(tv);
    }

    private EditText addInput(LinearLayout p, String hint, String def, boolean num, boolean pass) {
        TextView lbl = new TextView(this);
        lbl.setText(hint);
        lbl.setTextColor(Color.parseColor("#9CA3AF"));
        lbl.setTextSize(11);
        lbl.setPadding(0, 6, 0, 2);
        p.addView(lbl);

        EditText e = new EditText(this);
        e.setText(def);
        e.setTextColor(Color.WHITE);
        e.setBackgroundColor(Color.parseColor("#1E2430"));
        e.setPadding(18, 14, 18, 14);
        e.setTextSize(13);
        if (num) e.setInputType(InputType.TYPE_CLASS_NUMBER);
        if (pass) e.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
        p.addView(e);
        return e;
    }

    private Button makeSmallBtn(String text, String hexColor) {
        Button b = new Button(this);
        b.setText(text);
        b.setTextSize(11);
        b.setTextColor(Color.WHITE);
        b.setBackgroundColor(Color.parseColor(hexColor));
        b.setPadding(18, 12, 18, 12);
        return b;
    }

    private void addRow(LinearLayout p, String[] labels, final String[] actions) {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setPadding(0, 4, 0, 4);
        for (int i = 0; i < labels.length; i++) {
            final String act = actions[i];
            Button btn = new Button(this);
            btn.setText(labels[i]);
            btn.setTextSize(11);
            btn.setTextColor(Color.WHITE);
            btn.setBackgroundColor(Color.parseColor(act.equals("ACT_DELACC") || act.equals("ACT_BAN") ? "#7F1D1D" :
                (act.equals("MAKE_ITEM") || act.equals("LISTACC") || act.equals("BUILD_PLACE") ? "#1D4ED8" : "#2D3544")));
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
            lp.setMargins(3, 2, 3, 2);
            btn.setLayoutParams(lp);
            btn.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) { handleAction(act); }
            });
            row.addView(btn);
        }
        p.addView(row);
    }

    private void setPreset(int[] idxs, int[] vals) {
        for (int i = 0; i < 5; i++) {
            spAttr[i].setSelection(idxs[i]);
            edAttrVal[i].setText(String.valueOf(vals[i]));
        }
        tvStatus.setText("Durum: Hazir efsun sablonu dolduruldu, simdi ESYAYI VER butonuna bas.");
    }

    private void refreshSearch(String q) {
        boxSearchRes.removeAllViews();
        String low = q.trim().toLowerCase();
        if (low.length() < 2) return;
        int shown = 0;
        for (final String[] item : CATALOG) {
            if (item[0].contains(low) || item[1].toLowerCase().contains(low)) {
                Button b = new Button(this);
                b.setText("[" + item[2] + "] " + item[0] + " - " + item[1]);
                b.setTextSize(11);
                b.setTextColor(Color.parseColor("#E5E7EB"));
                b.setBackgroundColor(Color.parseColor("#1B2230"));
                b.setGravity(Gravity.LEFT | Gravity.CENTER_VERTICAL);
                b.setPadding(16, 10, 16, 10);
                b.setOnClickListener(new View.OnClickListener() {
                    @Override public void onClick(View v) {
                        edCode.setText(item[0]);
                        if (item[2].equals("ITEM")) edItemVnum.setText(item[0]);
                        else edBuildCode.setText(item[0]);
                        tvStatus.setText("Durum: Secildi -> " + item[0] + " (" + item[1] + ")");
                    }
                });
                boxSearchRes.addView(b);
                if (++shown >= 8) break;
            }
        }
    }

    private void renderFavs() {
        boxFavList.removeAllViews();
        String raw = prefs.getString("fav_pos", "");
        if (raw.isEmpty()) return;
        String[] entries = raw.split(";");
        for (String en : entries) {
            final String[] parts = en.split("=");
            if (parts.length != 2) continue;
            Button b = makeSmallBtn("ISINLAN -> " + parts[0] + " (" + parts[1] + ")", "#1E3A5F");
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            lp.setMargins(0, 4, 0, 4);
            b.setLayoutParams(lp);
            b.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) { sendCmds(new String[]{"/warp " + parts[1]}); }
            });
            boxFavList.addView(b);
        }
    }

    private void saveConn() {
        prefs.edit()
            .putString("host", edHost.getText().toString().trim())
            .putString("key", edKey.getText().toString().trim())
            .putString("nick", edNick.getText().toString().trim())
            .apply();
    }

    // ==================== KOMUT YONETICISI ====================
    private void handleAction(String act) {
        saveConn();
        if (act.equals("GOLD999")) sendCmds(new String[]{"/set " + getNick() + " gold 999999999"});
        else if (act.equals("SPEED")) sendCmds(new String[]{"/a " + getNick() + " mov_speed 200", "/a " + getNick() + " att_speed 200"});
        else if (act.equals("ALIGN_HERO")) sendCmds(new String[]{"/set " + getNick() + " align 20000"});
        else if (act.equals("STAT_FULL")) sendCmds(new String[]{"/a " + getNick() + " str 90", "/a " + getNick() + " con 90", "/a " + getNick() + " iq 90", "/a " + getNick() + " dex 90"});
        else if (act.equals("HORSE21")) sendCmds(new String[]{"/horse_level " + getNick() + " 21", "/item 50053"});
        else if (act.equals("SKILLP")) {
            int[] sk = {1,2,3,4,5,6,16,17,18,19,20,21,31,32,33,34,35,36,46,47,48,49,50,51,61,62,63,64,65,66,76,77,78,79,80,81,91,92,93,94,95,96,106,107,108,109,110,111};
            String[] cmds = new String[sk.length];
            for (int i = 0; i < sk.length; i++) cmds[i] = "/setsk " + sk[i] + " 59";
            sendCmds(cmds);
        }
        else if (act.equals("PRESET_VS_W")) setPreset(new int[]{14, 12, 13, 5, 9}, new int[]{15, 15, 15, 12, 20});
        else if (act.equals("PRESET_VS_A")) setPreset(new int[]{1, 19, 20, 21, 23}, new int[]{3000, 15, 15, 15, 15});
        else if (act.equals("PRESET_FARM")) setPreset(new int[]{27, 25, 12, 13, 10}, new int[]{55, 20, 15, 15, 8});
        else if (act.equals("PRESET_EDIT")) setPreset(new int[]{27, 26, 14, 12, 25}, new int[]{100, 100, 500, 500, 500});
        else if (act.equals("MAKE_ITEM")) {
            StringBuilder sb = new StringBuilder("MAKEITEM ");
            sb.append(edItemVnum.getText().toString().trim());
            for (int i = 0; i < 5; i++) {
                int aid = ATTR_IDS[spAttr[i].getSelectedItemPosition()];
                String val = edAttrVal[i].getText().toString().trim();
                if (val.isEmpty()) val = "0";
                sb.append(" ").append(aid).append(" ").append(val);
            }
            sendCmds(new String[]{sb.toString()});
        }
        else if (act.equals("ITEM_CODE")) sendCmds(new String[]{"/item " + edCode.getText().toString().trim()});
        else if (act.equals("MOB_CODE")) sendCmds(new String[]{"/m " + edCode.getText().toString().trim()});
        else if (act.equals("PACK_STONES")) sendCmds(new String[]{"/i 28430", "/i 28431", "/i 28432", "/i 28433", "/i 28434", "/i 28435", "/i 28436", "/i 28441", "/i 28442", "/i 28443"});
        else if (act.equals("SET_WAR")) sendCmds(new String[]{"/i 11971", "/i 279", "/i 13069", "/i 12249", "/i 14209", "/i 16209", "/i 17109", "/i 15209"});
        else if (act.equals("SET_NINJA")) sendCmds(new String[]{"/i 11972", "/i 1139", "/i 2179", "/i 13069", "/i 14209", "/i 16209", "/i 17109", "/i 15209"});
        else if (act.equals("SET_SURA")) sendCmds(new String[]{"/i 11973", "/i 279", "/i 13069", "/i 14209", "/i 16209", "/i 17109", "/i 15209"});
        else if (act.equals("SET_SHAMAN")) sendCmds(new String[]{"/i 11974", "/i 5129", "/i 7169", "/i 13069", "/i 14209", "/i 16209", "/i 15209"});
        else if (act.equals("ACT_BAN")) {
            String a = edAcc.getText().toString().trim();
            String n = edTargetNick.getText().toString().trim();
            if (a.isEmpty()) { tvStatus.setText("Hata: Hesap adi girin."); return; }
            if (!n.isEmpty()) sendCmds(new String[]{"BAN " + a, "/dc " + n});
            else sendCmds(new String[]{"BAN " + a});
        }
        else if (act.equals("ACT_UNBAN")) {
            String a = edAcc.getText().toString().trim();
            if (a.isEmpty()) { tvStatus.setText("Hata: Hesap adi girin."); return; }
            sendCmds(new String[]{"UNBAN " + a});
        }
        else if (act.equals("ACT_SETPASS")) {
            String a = edAcc.getText().toString().trim();
            String pw = edNewPass.getText().toString().trim();
            if (a.isEmpty() || pw.isEmpty()) { tvStatus.setText("Hata: Hesap adi ve yeni sifre girin."); return; }
            sendCmds(new String[]{"SETPASS " + a + " " + pw});
        }
        else if (act.equals("ACT_DELACC")) {
            final String a = edAcc.getText().toString().trim();
            if (a.isEmpty()) { tvStatus.setText("Hata: Silinecek hesap adini girin."); return; }
            new AlertDialog.Builder(this)
                .setTitle("Hesabi Kalici Sil")
                .setMessage("'" + a + "' hesabi ve tum karakterleri kalici silinsin mi?")
                .setPositiveButton("SIL", new DialogInterface.OnClickListener() {
                    @Override public void onClick(DialogInterface d, int w) { sendCmds(new String[]{"DELACC " + a}); }
                })
                .setNegativeButton("IPTAL", null).show();
        }
        else if (act.equals("ADDGM")) sendCmds(new String[]{"ADDGM " + edAcc.getText().toString().trim() + " " + edTargetNick.getText().toString().trim()});
        else if (act.equals("DELGM")) sendCmds(new String[]{"DELGM " + edTargetNick.getText().toString().trim()});
        else if (act.equals("PL_DC")) sendCmds(new String[]{"/dc " + edTargetNick.getText().toString().trim()});
        else if (act.equals("PL_MUTE")) sendCmds(new String[]{"/block_chat " + edTargetNick.getText().toString().trim() + " 600"});
        else if (act.equals("PL_PULL")) sendCmds(new String[]{"/transfer " + edTargetNick.getText().toString().trim()});
        else if (act.equals("PL_WARP")) sendCmds(new String[]{"/warp " + edTargetNick.getText().toString().trim()});
        else if (act.equals("PL_STUN")) sendCmds(new String[]{"/stun " + edTargetNick.getText().toString().trim()});
        else if (act.equals("PL_KILL")) sendCmds(new String[]{"/kill " + edTargetNick.getText().toString().trim()});
        else if (act.equals("BUILD_PLACE")) {
            String c = edBuildCode.getText().toString().trim();
            String cnt = edBuildCnt.getText().toString().trim();
            sendCmds(new String[]{"/m " + c + (cnt.isEmpty() || cnt.equals("1") ? "" : " " + cnt)});
        }
        else if (act.equals("SAVE_POS")) sendCmds(new String[]{"GETPOS"});
        else if (act.equals("CLEAR_POS")) { prefs.edit().remove("fav_pos").apply(); renderFavs(); tvStatus.setText("Durum: Favoriler temizlendi."); }
        else if (act.equals("DROP_200")) sendCmds(new String[]{"/priv_empire 0 1 200 24", "/priv_empire 0 2 200 24", "/priv_empire 0 3 200 24", "/priv_empire 0 4 200 24"});
        else if (act.equals("DROP_500")) sendCmds(new String[]{"/priv_empire 0 1 500 24", "/priv_empire 0 2 500 24", "/priv_empire 0 3 500 24", "/priv_empire 0 4 500 24"});
        else if (act.equals("DROP_1000")) sendCmds(new String[]{"/priv_empire 0 1 1000 24", "/priv_empire 0 2 1000 24", "/priv_empire 0 3 1000 24", "/priv_empire 0 4 1000 24"});
        else if (act.equals("DROP_0")) sendCmds(new String[]{"/priv_empire 0 1 0 1", "/priv_empire 0 2 0 1", "/priv_empire 0 3 0 1", "/priv_empire 0 4 0 1"});
        else if (act.equals("BIG_NOTICE")) sendCmds(new String[]{"/b " + edNotice.getText().toString().trim()});
        else if (act.equals("NORM_NOTICE")) sendCmds(new String[]{"/n " + edNotice.getText().toString().trim()});
        else if (act.equals("CUSTOM")) sendCmds(new String[]{edCustom.getText().toString().trim()});
        else sendCmds(new String[]{act});
    }

    private String getNick() { return edNick.getText().toString().trim(); }

    private void sendCmds(final String[] cmds) {
        final String host = edHost.getText().toString().trim();
        final String key = edKey.getText().toString().trim();
        final String nick = getNick();
        tvStatus.setText("Durum: Gonderiliyor...");
        executor.execute(new Runnable() {
            @Override public void run() {
                String lastRes = "Tamamlandi";
                try {
                    for (String cmd : cmds) {
                        Socket s = new Socket();
                        s.connect(new InetSocketAddress(host, 11099), 2500);
                        s.setSoTimeout(4000);
                        OutputStream os = s.getOutputStream();
                        os.write((key + "|" + nick + "|" + cmd + "\n").getBytes("UTF-8"));
                        os.flush();
                        BufferedReader br = new BufferedReader(new InputStreamReader(s.getInputStream(), "UTF-8"));
                        String res = br.readLine();
                        if (res != null) lastRes = res;
                        s.close();
                    }
                    final String msg = lastRes;
                    runOnUiThread(new Runnable() {
                        @Override public void run() { handleServerReply(msg); }
                    });
                } catch (final Exception e) {
                    runOnUiThread(new Runnable() {
                        @Override public void run() {
                            tvStatus.setText("Baglanti Hatasi (Oyuna giris yap): " + e.getMessage());
                        }
                    });
                }
            }
        });
    }

    private void handleServerReply(String msg) {
        if (msg.startsWith("OK_LIST::") || msg.startsWith("OK_CHARS::")) {
            final boolean isAcc = msg.startsWith("OK_LIST::");
            String body = msg.substring(isAcc ? 9 : 10);
            String[] rows = body.split(";;");
            boxAccList.removeAllViews();
            TextView hdr = new TextView(this);
            hdr.setText(isAcc ? "ID | Hesap | Sifre | Durum | SilmeKodu (Dokun = Sec)" : "Karakter | Lv | Yang | HesapID (Dokun = Sec)");
            hdr.setTextColor(Color.parseColor("#FBBF24"));
            hdr.setTextSize(11);
            hdr.setPadding(4, 6, 4, 6);
            boxAccList.addView(hdr);

            for (final String r : rows) {
                Button rb = new Button(this);
                rb.setText(r);
                rb.setTextSize(11);
                rb.setAllCaps(false);
                rb.setTextColor(Color.WHITE);
                rb.setBackgroundColor(Color.parseColor(r.contains("BLOCK") ? "#581C1C" : "#1B2230"));
                rb.setGravity(Gravity.LEFT | Gravity.CENTER_VERTICAL);
                rb.setPadding(14, 10, 14, 10);
                LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
                lp.setMargins(0, 2, 0, 2);
                rb.setLayoutParams(lp);
                rb.setOnClickListener(new View.OnClickListener() {
                    @Override public void onClick(View v) {
                        String[] cols = r.split("\\|");
                        if (isAcc && cols.length >= 2) {
                            edAcc.setText(cols[1].trim());
                            tvStatus.setText("Secili hesap: " + cols[1].trim());
                        } else if (!isAcc && cols.length >= 1) {
                            edTargetNick.setText(cols[0].trim());
                            tvStatus.setText("Secili karakter: " + cols[0].trim());
                        }
                    }
                });
                boxAccList.addView(rb);
            }
            tvStatus.setText("Durum: " + rows.length + " kayit listelendi.");
        } else if (msg.startsWith("OK_POS::")) {
            String coords = msg.substring(8).trim();
            String name = edPosName.getText().toString().trim().replace(";", "").replace("=", "");
            if (name.isEmpty()) name = "Konum";
            String cur = prefs.getString("fav_pos", "");
            String next = cur.isEmpty() ? (name + "=" + coords) : (cur + ";" + name + "=" + coords);
            prefs.edit().putString("fav_pos", next).apply();
            renderFavs();
            tvStatus.setText("Durum: Favori konum kaydedildi -> " + name + " (" + coords + ")");
        } else {
            tvStatus.setText("Durum: " + msg);
        }
    }

    @Override
    protected void onDestroy() {
        executor.shutdownNow();
        super.onDestroy();
    }
}
