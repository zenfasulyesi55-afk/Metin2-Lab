package com.metin2.gmpanel;
import android.app.*; import android.content.*; import android.graphics.*;
import android.graphics.drawable.GradientDrawable; import android.os.*;
import android.text.*; import android.view.*; import android.widget.*;
import java.io.*; import java.net.*; import java.util.*; import java.util.concurrent.*;

public class MainActivity extends Activity {
    static final int BG=0xFF0E1117, CARD=0xFF161B24, BORDER=0xFF283142, GOLD=0xFFD4AF37;
    static final int ACC=0xFF1F2A3C, RED=0xFF6B2028, GRN=0xFF1E513B, TXT=0xFFEAF0F8, SUB=0xFF9AA7B8;
    SharedPreferences prefs;
    EditText edHost, edKey, edNick, edTarget, edSearch, edCustom, edNotice, edAutoMsg, edAutoMin;
    TextView tvStatus, tvAutoState; LinearLayout connBox, searchResults, autoListBox;
    View[] pages = new View[6]; Button[] tabBtns = new Button[6];
    String searchCat = "tumu"; int searchPlus = 9, searchQty = 1;
    final Handler ui = new Handler(Looper.getMainLooper());
    final ExecutorService net = Executors.newSingleThreadExecutor();
    static ScheduledExecutorService autoExec; static ScheduledFuture<?> autoTask;
    static boolean autoOn = false; static int autoIdx = 0;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        prefs = getSharedPreferences(PanelDefaults.PREF, MODE_PRIVATE);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL); root.setBackgroundColor(BG);
        LinearLayout hdr = row(); hdr.setBackgroundColor(0xFF121722); hdr.setPadding(dp(12),dp(10),dp(12),dp(8));
        TextView ttl = txt("METIN2 GM KOMUTA MERKEZI", 15, GOLD, true);
        ttl.setLayoutParams(new LinearLayout.LayoutParams(0, -2, 1f));
        Button bConn = pill("Baglanti", ACC, GOLD, new View.OnClickListener(){
            public void onClick(View v){ connBox.setVisibility(connBox.getVisibility()==View.VISIBLE?View.GONE:View.VISIBLE); }});
        hdr.addView(ttl); hdr.addView(bConn); root.addView(hdr);

        tvStatus = txt("Durum: Hazir (" + prefs.getString(PanelDefaults.K_NICK, PanelDefaults.D_NICK) + ")", 12, SUB, false);
        tvStatus.setBackgroundColor(0xFF10151F); tvStatus.setPadding(dp(12),dp(4),dp(12),dp(6)); root.addView(tvStatus); PanelUpdater.attach(this,root,tvStatus);

        connBox = card(); connBox.setVisibility(View.GONE);
        edHost = inp(connBox, "Sunucu IP", prefs.getString(PanelDefaults.K_HOST, PanelDefaults.D_HOST));
        edKey  = inp(connBox, "Admin Sifresi", prefs.getString(PanelDefaults.K_KEY, PanelDefaults.D_KEY));
        edNick = inp(connBox, "GM Nicki", prefs.getString(PanelDefaults.K_NICK, PanelDefaults.D_NICK));
        edTarget = inp(connBox, "Hedef Oyuncu (Bos=Kendin)", "");
        LinearLayout cr = row();
        cr.addView(btnRow("Kaydet", GRN, new View.OnClickListener(){ public void onClick(View v){ saveConn(); tvStatus.setText("Durum: Kaydedildi"); connBox.setVisibility(View.GONE); }}));
        cr.addView(btnRow("Test", ACC, new View.OnClickListener(){ public void onClick(View v){ sendCmds(new String[]{"GETPOS"}); }}));
        connBox.addView(cr); root.addView(connBox);

        HorizontalScrollView hsv = new HorizontalScrollView(this);
        hsv.setHorizontalScrollBarEnabled(false); hsv.setBackgroundColor(0xFF121722);
        LinearLayout tabs = row(); tabs.setPadding(dp(8),dp(6),dp(8),dp(6));
        String[] ns = {"Hizli","Kod Ara","Eventler","Oran & Dunya","Isinlan & Set","Oto Duyuru"};
        for (int i=0;i<6;i++){ final int k=i; tabBtns[i]=pill(ns[i],ACC,TXT,new View.OnClickListener(){ public void onClick(View v){ showTab(k); }}); tabs.addView(tabBtns[i]); }
        hsv.addView(tabs); root.addView(hsv);

        FrameLayout fl = new FrameLayout(this); fl.setLayoutParams(new LinearLayout.LayoutParams(-1, 0, 1f));
        pages[0]=buildQuick(); pages[1]=buildSearch(); pages[2]=buildEvents();
        pages[3]=buildRates(); pages[4]=buildWarpKits(); pages[5]=buildAutoNotice();
        for (View p : pages) fl.addView(p);
        root.addView(fl); setContentView(root); showTab(0);
    }
    void showTab(int idx) {
        for (int i=0;i<6;i++) { pages[i].setVisibility(i==idx?View.VISIBLE:View.GONE); stylePill(tabBtns[i], i==idx?GOLD:ACC, i==idx?0xFF0E1117:TXT); }
    }
    View buildQuick() {
        LinearLayout box = page();
        LinearLayout c1 = sec(box, "KARAKTER HIZLI ISLEMLER");
        grid(c1, new String[]{"999M Yang","Lv.99","Lv.120","HP/SP Full"}, new Runnable[]{
            rCmd("/set %T gold 999999999"), rCmd("/level 99"), rCmd("/level 120"), rCmd("/r") });
        grid(c1, new String[]{"Gorunmez","Hiz 200","Asker At","Kahraman"}, new Runnable[]{
            rCmd("/inv"), rCmd("/set %T mov_speed 200","/set %T att_speed 200"), rCmd("/horse_level %T 21","/i 50053"), rCmd("/set %T align 20000") });
        grid(c1, new String[]{"Temizle","Harita Temizle","Reload All","Reload Quest"}, new Runnable[]{
            rCmd("/purge"), rCmd("/purge all"), rCmd("/reload a"), rCmd("/reload q") });
        LinearLayout c2 = sec(box, "OZEL GM KOMUTU");
        edCustom = inp(c2, "Ornek: /i 189 1 veya /m 1093 1", "");
        c2.addView(btnFull("Komutu Gonder", GOLD, new View.OnClickListener(){ public void onClick(View v){ String s=edCustom.getText().toString().trim(); if(!s.isEmpty()) sendCmds(new String[]{s}); }}));
        return wrapScroll(box);
    }
    View buildSearch() {
        LinearLayout box = page();
        LinearLayout c1 = sec(box, "TURKCE KOD ARAMA (ITEM / MOB / METIN)");
        edSearch = inp(c1, "Ara: zehir kilici, siyah celik, azrail...", "");
        edSearch.addTextChangedListener(new TextWatcher(){
            public void beforeTextChanged(CharSequence s,int a,int b,int c){}
            public void onTextChanged(CharSequence s,int a,int b,int c){ refreshSearch(); }
            public void afterTextChanged(Editable e){}
        });
        HorizontalScrollView ch = new HorizontalScrollView(this); ch.setHorizontalScrollBarEnabled(false);
        LinearLayout cr = row();
        String[][] cats = {{"Tumu","tumu"},{"Silah","silah"},{"Zirh","zirh"},{"Taki","taki"},{"Esya","esya"},{"Tas","tas"},{"Boss","mob"},{"Metin","metin"}};
        for (final String[] ct : cats) cr.addView(pill(ct[0], ACC, TXT, new View.OnClickListener(){ public void onClick(View v){ searchCat=ct[1]; refreshSearch(); }}));
        ch.addView(cr); c1.addView(ch);
        LinearLayout pr = row();
        final Button bP = pill("Seviye: +9", ACC, GOLD, null);
        bP.setOnClickListener(new View.OnClickListener(){ public void onClick(View v){ searchPlus=(searchPlus+1)%10; bP.setText("Seviye: +"+searchPlus); refreshSearch(); }});
        final Button bQ = pill("Adet: 1", ACC, TXT, null);
        bQ.setOnClickListener(new View.OnClickListener(){ public void onClick(View v){ int[] q={1,5,10,50,200}; int i=0; for(int k=0;k<q.length;k++) if(q[k]==searchQty) i=(k+1)%q.length; searchQty=q[i]; bQ.setText("Adet: "+searchQty); }});
        pr.addView(bP); pr.addView(bQ); c1.addView(pr);
        searchResults = new LinearLayout(this); searchResults.setOrientation(LinearLayout.VERTICAL);
        box.addView(searchResults); refreshSearch();
        return wrapScroll(box);
    }
    void refreshSearch() {
        searchResults.removeAllViews();
        List<CatalogData.Entry> ls = CatalogData.search(edSearch==null?"":edSearch.getText().toString(), searchCat);
        for (int i=0; i<Math.min(ls.size(), 40); i++) {
            final CatalogData.Entry e = ls.get(i); final int code = e.plusable ? (e.vnum + searchPlus) : e.vnum;
            LinearLayout r = card(); r.setOrientation(LinearLayout.HORIZONTAL); r.setGravity(Gravity.CENTER_VERTICAL);
            LinearLayout inf = new LinearLayout(this); inf.setOrientation(LinearLayout.VERTICAL); inf.setLayoutParams(new LinearLayout.LayoutParams(0,-2,1f));
            inf.addView(txt(e.name + (e.plusable ? " +"+searchPlus : ""), 13, TXT, true));
            inf.addView(txt("Kod: " + code + " [" + e.cat.toUpperCase(Locale.ROOT) + "]", 11, GOLD, false));
            r.addView(inf);
            r.addView(pill(e.isMob?"Cagir":"Ver", GRN, TXT, new View.OnClickListener(){ public void onClick(View v){ sendCmds(new String[]{(e.isMob?"/m ":"/i ")+code+" "+searchQty}); }}));
            r.addView(pill("Kopyala", ACC, TXT, new View.OnClickListener(){ public void onClick(View v){ copyCode(String.valueOf(code)); }}));
            searchResults.addView(r);
        }
    }
    View buildEvents() {
        LinearLayout box = page();
        LinearLayout ox = sec(box, "OX YARISMASI KONTROL");
        grid(ox, new String[]{"OX Meydani","Isimsiz Cicek"}, new Runnable[]{ rCmd("/go ox"), rCmd("/m 20358") });
        grid(ox, new String[]{"OX Duyuru","OX Giris Ac","OX Bitir"}, new Runnable[]{
            rCmd("/n [OX] OX Yarismasi basliyor! Uriel'den katilin!"),
            rCmd("/e oxevent_status 1","/n [OX] Girisler acildi!"),
            rCmd("/e oxevent_status 0","/n [OX] Yarisma sona erdi!") });
        LinearLayout dr = sec(box, "SANDIK & OZEL DROP EVENTLERI");
        evRow(dr, "Ayisigi Define Sandigi", "drop_moon");
        evRow(dr, "Altigen Hediye Paketi", "drop_hexagonal");
        evRow(dr, "Futbol Topu Eventi", "drop_football");
        evRow(dr, "Yilbasi Corap Eventi", "xmas_sock");
        evRow(dr, "Cadilar Bayrami", "halloween_drop");
        evRow(dr, "Ramazan Eventi", "ramadan_drop");
        evRow(dr, "Paskalya Eventi", "easter_drop");
        dr.addView(btnFull("Korsan Tanaka Eventi (15 Adet)", GOLD, new View.OnClickListener(){ public void onClick(View v){ sendCmds(new String[]{"/m 5001 15","/n [EVENT] Korsan Tanaka istilasi basladi!"}); }}));
        LinearLayout mt = sec(box, "METIN YAGMURU (10 ADET)");
        grid(mt, new String[]{"Lv.45","Lv.65","Lv.85","Lv.90"}, new Runnable[]{
            rCmd("/m 8009 10","/n [EVENT] 45 Lv Metin yagmuru!"), rCmd("/m 8014 10","/n [EVENT] 65 Lv Metin yagmuru!"),
            rCmd("/m 8026 10","/n [EVENT] 85 Lv Metin yagmuru!"), rCmd("/m 8027 10","/n [EVENT] 90 Lv Metin yagmuru!") });
        LinearLayout bs = sec(box, "BOSS EVENTI");
        grid(bs, new String[]{"Azrail","Mavi Ejderha","Kirmizi Ejderha"}, new Runnable[]{
            rCmd("/m 1093 1","/n [BOSS] Azrail cikti!"), rCmd("/m 2493 1","/n [BOSS] Mavi Ejderha cikti!"), rCmd("/m 2291 1","/n [BOSS] Kirmizi Ejderha cikti!") });
        grid(bs, new String[]{"Dokuz Kuyruk","Alev Kral","Buz Cadisi"}, new Runnable[]{
            rCmd("/m 1901 1","/n [BOSS] Dokuz Kuyruk cikti!"), rCmd("/m 2206 1","/n [BOSS] Alev Kral cikti!"), rCmd("/m 1192 1","/n [BOSS] Buz Cadisi cikti!") });
        return wrapScroll(box);
    }
    void evRow(LinearLayout p, final String title, final String flag) {
        LinearLayout r = row(); r.setGravity(Gravity.CENTER_VERTICAL);
        TextView t = txt(title, 12, TXT, false); t.setLayoutParams(new LinearLayout.LayoutParams(0,-2,1f));
        r.addView(t);
        r.addView(pill("Ac", GRN, TXT, new View.OnClickListener(){ public void onClick(View v){ sendCmds(new String[]{"/e "+flag+" 1","/n [EVENT] "+title+" basladi!"}); }}));
        r.addView(pill("Kapat", RED, TXT, new View.OnClickListener(){ public void onClick(View v){ sendCmds(new String[]{"/e "+flag+" 0","/n [EVENT] "+title+" sona erdi."}); }}));
        p.addView(r);
    }
    View buildRates() {
        LinearLayout box = page();
        LinearLayout r1 = sec(box, "TUM BAYRAKLAR ORANLAR (24 SAAT)");
        grid(r1, new String[]{"%250","%500","%1000","Sifirla"}, new Runnable[]{
            rCmd("/priv_empire 0 1 250 24","/priv_empire 0 2 250 24","/priv_empire 0 4 250 24","/n [EVENT] Tum oranlar %250!"),
            rCmd("/priv_empire 0 1 500 24","/priv_empire 0 2 500 24","/priv_empire 0 4 500 24","/n [EVENT] Tum oranlar %500!"),
            rCmd("/priv_empire 0 1 1000 24","/priv_empire 0 2 1000 24","/priv_empire 0 4 1000 24","/n [EVENT] Tum oranlar %1000!"),
            rCmd("/priv_empire 0 1 0 1","/priv_empire 0 2 0 1","/priv_empire 0 4 0 1") });
        LinearLayout w1 = sec(box, "HAVA & ATMOSFER");
        grid(w1, new String[]{"Gece","Gunduz","Kar Ac","Kar Kapat"}, new Runnable[]{ rCmd("/x 1"), rCmd("/x 0"), rCmd("/xmas_snow 1"), rCmd("/xmas_snow 0") });
        grid(w1, new String[]{"Agac Ac","Agac Kapat","Muzik Ac","Muzik Kapat"}, new Runnable[]{ rCmd("/xmas_tree 3"), rCmd("/xmas_tree 0"), rCmd("/xmas_song 1"), rCmd("/xmas_song 0") });
        LinearLayout n1 = sec(box, "ANLIK GM DUYURU");
        edNotice = inp(n1, "Duyuru metni yazin...", "");
        grid(n1, new String[]{"Normal Duyuru (/n)","Buyuk Duyuru (/b)"}, new Runnable[]{
            new Runnable(){ public void run(){ String m=edNotice.getText().toString().trim(); if(!m.isEmpty()) sendCmds(new String[]{"/n "+m}); }},
            new Runnable(){ public void run(){ String m=edNotice.getText().toString().trim(); if(!m.isEmpty()) sendCmds(new String[]{"/b "+m}); }} });
        return wrapScroll(box);
    }
    View buildWarpKits() {
        LinearLayout box = page();
        LinearLayout w = sec(box, "TEK TIK ISINLANMA");
        grid(w, new String[]{"Kirmizi 1","Sari 1","Mavi 1","OX"}, new Runnable[]{ rCmd("/go a"), rCmd("/go b"), rCmd("/go c"), rCmd("/go ox") });
        grid(w, new String[]{"Vadi","Col","Sohan","Doyyum"}, new Runnable[]{ rCmd("/go valley"), rCmd("/go desert"), rCmd("/go snow"), rCmd("/go fire") });
        grid(w, new String[]{"Kule","Orumcek 2","Kizil","Surgun"}, new Runnable[]{ rCmd("/go t"), rCmd("/go spider2"), rCmd("/go redwood"), rCmd("/go ski") });
        LinearLayout k = sec(box, "HAZIR +9 SETLER & PAKETLER");
        grid(k, new String[]{"Savasci +9","Sura +9"}, new Runnable[]{
            rCmd("/i 189 1","/i 11299 1","/i 12249 1","/i 13069 1","/i 14209 1","/i 16209 1","/i 17109 1","/i 15209 1"),
            rCmd("/i 199 1","/i 11699 1","/i 12509 1","/i 13109 1","/i 14209 1","/i 16209 1","/i 17209 1","/i 15209 1") });
        grid(k, new String[]{"Ninja +9","Saman +9"}, new Runnable[]{
            rCmd("/i 1189 1","/i 11499 1","/i 12369 1","/i 13089 1","/i 14209 1","/i 16209 1","/i 17109 1","/i 15209 1"),
            rCmd("/i 5129 1","/i 11899 1","/i 12649 1","/i 13129 1","/i 14209 1","/i 16209 1","/i 17209 1","/i 15209 1") });
        k.addView(btnFull("Efsun + Iksir + Pelerin Paketi", GRN, new View.OnClickListener(){ public void onClick(View v){
            sendCmds(new String[]{"/i 71084 200","/i 71085 200","/i 25040 50","/i 70038 200","/i 27102 200","/i 27105 200"}); }}));
        
        LinearLayout au = sec(box, "OZEL AURA ([OK]Miko)");
        grid(au, new String[]{"Altin-Beyaz Aura AC", "Aura KAPAT"}, new Runnable[]{
            rCmd("MIKOAURA 1"), rCmd("MIKOAURA 0")
        });

        LinearLayout edSec = sec(box, "5 EFSUN + 3 TAS ITEM EDITORU");
        final android.widget.EditText edVnum = new android.widget.EditText(this);
        edVnum.setHint("Item Kodu (orn: 189 Zehir +9)");
        edVnum.setText("189");
        edVnum.setTextColor(0xFFFFFFFF);
        edVnum.setHintTextColor(0xFF999999);
        edVnum.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
        edSec.addView(edVnum);

        final String[] bNames = {"0: Yok","1: Max HP","5: Guc","6: Ceviklik","7: Zeka","8: Canlilik","9: Saldiri Hizi","10: Hareket Hizi","15: Kritik","16: Delici","17: Yari Insan","29: Kilic Sav.","30: Cift El Sav.","31: Bicak Sav.","37: Buyu Hizi","53: Saldiri Deg.","71: Beceri Hasari","72: Ortalama Zarar"};
        final int[] bIds = {0,1,5,6,7,8,9,10,15,16,17,29,30,31,37,53,71,72};
        final android.widget.Spinner[] spB = new android.widget.Spinner[5];
        final android.widget.EditText[] edB = new android.widget.EditText[5];
        for (int i = 0; i < 5; i++) {
            LinearLayout row = new LinearLayout(this);
            row.setOrientation(LinearLayout.HORIZONTAL);
            spB[i] = new android.widget.Spinner(this);
            android.widget.ArrayAdapter<String> ad = new android.widget.ArrayAdapter<String>(this, android.R.layout.simple_spinner_dropdown_item, bNames);
            spB[i].setAdapter(ad);
            edB[i] = new android.widget.EditText(this);
            edB[i].setHint("Deger");
            edB[i].setText("0");
            edB[i].setTextColor(0xFFFFFFFF);
            edB[i].setInputType(android.text.InputType.TYPE_CLASS_NUMBER | android.text.InputType.TYPE_NUMBER_FLAG_SIGNED);
            row.addView(spB[i], new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 2f));
            row.addView(edB[i], new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
            edSec.addView(row);
        }

        final String[] sNames = {"0: Tas Yok","28430: Oldurucu Darbe +4","28431: Kavrama +4","28432: Sogutma +4","28433: Savasci +4","28434: Ninja +4","28435: Sura +4","28436: Saman +4","28437: Canavar +4","28438: Korunma +4","28439: Kurnazlik +4","28440: Sihir +4","28441: Yasam +4","28442: Savunma +4","28443: Hiz +4"};
        final int[] sIds = {0,28430,28431,28432,28433,28434,28435,28436,28437,28438,28439,28440,28441,28442,28443};
        final android.widget.Spinner[] spS = new android.widget.Spinner[3];
        for (int i = 0; i < 3; i++) {
            spS[i] = new android.widget.Spinner(this);
            android.widget.ArrayAdapter<String> ad = new android.widget.ArrayAdapter<String>(this, android.R.layout.simple_spinner_dropdown_item, sNames);
            spS[i].setAdapter(ad);
            edSec.addView(spS[i]);
        }

        edSec.addView(btnFull("5 Efsun + 3 Tasli Item Bas", GRN, new View.OnClickListener(){
            public void onClick(View v){
                String vn = edVnum.getText().toString().trim();
                if (vn.isEmpty()) vn = "189";
                StringBuilder sb = new StringBuilder("MAKEITEM ").append(vn);
                for (int i = 0; i < 5; i++) {
                    String val = edB[i].getText().toString().trim();
                    if (val.isEmpty()) val = "0";
                    sb.append(" ").append(bIds[spB[i].getSelectedItemPosition()]).append(" ").append(val);
                }
                for (int i = 0; i < 3; i++) {
                    sb.append(" ").append(sIds[spS[i].getSelectedItemPosition()]);
                }
                sendCmds(new String[]{sb.toString()});
            }
        }));

        return wrapScroll(box);
    }
    View buildAutoNotice() {
        LinearLayout box = page();
        LinearLayout c1 = sec(box, "OTOMATIK DUYURU (10 DK)");
        tvAutoState = txt(autoOn ? "Durum: AKTIF" : "Durum: DURDURULDU", 13, autoOn ? 0xFF4ADE80 : GOLD, true);
        c1.addView(tvAutoState);
        edAutoMin = inp(c1, "Dakika (Varsayilan 10)", String.valueOf(prefs.getInt("auto_min", 10)));
        edAutoMin.setInputType(InputType.TYPE_CLASS_NUMBER);
        grid(c1, new String[]{"5 Dk","10 Dk","15 Dk","30 Dk"}, new Runnable[]{
            new Runnable(){ public void run(){ edAutoMin.setText("5"); }}, new Runnable(){ public void run(){ edAutoMin.setText("10"); }},
            new Runnable(){ public void run(){ edAutoMin.setText("15"); }}, new Runnable(){ public void run(){ edAutoMin.setText("30"); }} });
        grid(c1, new String[]{"BASLAT","DURDUR","TEST ET"}, new Runnable[]{
            new Runnable(){ public void run(){ startAutoNotice(); }}, new Runnable(){ public void run(){ stopAutoNotice(); }},
            new Runnable(){ public void run(){ sendNextAuto(); }} });
        LinearLayout c2 = sec(box, "DUYURU LISTESI");
        edAutoMsg = inp(c2, "Yeni duyuru yazin...", "");
        c2.addView(btnFull("Listeye Ekle", ACC, new View.OnClickListener(){ public void onClick(View v){
            String m = edAutoMsg.getText().toString().trim(); if(m.isEmpty()) return;
            List<String> ls = loadAutoList(); ls.add(m); saveAutoList(ls); edAutoMsg.setText(""); refreshAutoList();
        }}));
        autoListBox = new LinearLayout(this); autoListBox.setOrientation(LinearLayout.VERTICAL);
        c2.addView(autoListBox); refreshAutoList();
        return wrapScroll(box);
    }
    List<String> loadAutoList() {
        String raw = prefs.getString("auto_msgs", "[DUYURU] Keyifli oyunlar!||[EVENT] Eventler icin takipte kalin!");
        List<String> out = new ArrayList<String>();
        for (String p : raw.split("\\|\\|")) if (!p.trim().isEmpty()) out.add(p.trim());
        return out;
    }
    void saveAutoList(List<String> ls) {
        StringBuilder sb = new StringBuilder();
        for (int i=0;i<ls.size();i++) { if(i>0) sb.append("||"); sb.append(ls.get(i)); }
        prefs.edit().putString("auto_msgs", sb.toString()).apply();
    }
    void refreshAutoList() {
        autoListBox.removeAllViews(); final List<String> ls = loadAutoList();
        for (int i=0;i<ls.size();i++) {
            final int idx = i; LinearLayout r = row(); r.setGravity(Gravity.CENTER_VERTICAL);
            TextView t = txt((i+1)+". "+ls.get(i), 12, TXT, false); t.setLayoutParams(new LinearLayout.LayoutParams(0,-2,1f));
            r.addView(t); r.addView(pill("Sil", RED, TXT, new View.OnClickListener(){ public void onClick(View v){ ls.remove(idx); saveAutoList(ls); refreshAutoList(); }}));
            autoListBox.addView(r);
        }
    }
    void startAutoNotice() {
        stopAutoNotice(); int m = 10;
        try { m = Math.max(1, Integer.parseInt(edAutoMin.getText().toString().trim())); } catch(Exception ignored){}
        prefs.edit().putInt("auto_min", m).apply();
        if (autoExec == null || autoExec.isShutdown()) autoExec = Executors.newSingleThreadScheduledExecutor();
        autoOn = true;
        autoTask = autoExec.scheduleAtFixedRate(new Runnable(){ public void run(){ ui.post(new Runnable(){ public void run(){ sendNextAuto(); }}); }}, 0, m, TimeUnit.MINUTES);
        tvAutoState.setText("Durum: AKTIF (Her " + m + " dk)"); tvAutoState.setTextColor(0xFF4ADE80);
    }
    void stopAutoNotice() {
        autoOn = false; if (autoTask != null) { autoTask.cancel(false); autoTask = null; }
        if (tvAutoState != null) { tvAutoState.setText("Durum: DURDURULDU"); tvAutoState.setTextColor(GOLD); }
    }
    void sendNextAuto() {
        List<String> ls = loadAutoList(); if (ls.isEmpty()) return;
        String msg = ls.get(autoIdx % ls.size()); autoIdx++;
        sendCmds(new String[]{"/n " + msg});
    }
    void saveConn() {
        prefs.edit().putString(PanelDefaults.K_HOST, edHost.getText().toString().trim())
            .putString(PanelDefaults.K_KEY, edKey.getText().toString().trim())
            .putString(PanelDefaults.K_NICK, edNick.getText().toString().trim()).apply();
    }
    Runnable rCmd(final String... cmds) { return new Runnable(){ public void run(){ sendCmds(cmds); }}; }
    void sendCmds(final String[] rawCmds) {
        saveConn();
        final String host = edHost.getText().toString().trim(), key = edKey.getText().toString().trim(), nick = edNick.getText().toString().trim();
        final String tgt = edTarget.getText().toString().trim().isEmpty() ? nick : edTarget.getText().toString().trim();
        tvStatus.setText("Durum: Gonderiliyor...");
        net.execute(new Runnable(){ public void run(){
            String last = "Tamamlandi";
            try {
                for (String rc : rawCmds) {
                    Socket s = new Socket(); s.connect(new InetSocketAddress(host, 11099), 2500); s.setSoTimeout(4000);
                    OutputStream os = s.getOutputStream(); os.write((key+"|"+nick+"|"+rc.replace("%T", tgt)+"\n").getBytes("UTF-8")); os.flush();
                    BufferedReader br = new BufferedReader(new InputStreamReader(s.getInputStream(), "UTF-8"));
                    String res = br.readLine(); if (res != null && !res.isEmpty()) last = res; s.close();
                }
            } catch (Exception e) { last = "Hata: " + e.getMessage(); }
            final String out = last; ui.post(new Runnable(){ public void run(){ tvStatus.setText("Durum: " + out); }});
        }});
    }
    void copyCode(String s) {
        ((android.content.ClipboardManager)getSystemService(Context.CLIPBOARD_SERVICE)).setPrimaryClip(ClipData.newPlainText("vnum", s));
        Toast.makeText(this, "Kopyalandi: " + s, Toast.LENGTH_SHORT).show();
    }
    int dp(int v){ return (int)(v * getResources().getDisplayMetrics().density); }
    LinearLayout page(){ LinearLayout l=new LinearLayout(this); l.setOrientation(LinearLayout.VERTICAL); l.setPadding(dp(10),dp(8),dp(10),dp(16)); return l; }
    ScrollView wrapScroll(View v){ ScrollView sv=new ScrollView(this); sv.addView(v); return sv; }
    LinearLayout row(){ LinearLayout l=new LinearLayout(this); l.setOrientation(LinearLayout.HORIZONTAL); return l; }
    LinearLayout card(){ LinearLayout l=new LinearLayout(this); l.setOrientation(LinearLayout.VERTICAL); l.setPadding(dp(10),dp(8),dp(10),dp(8));
        GradientDrawable g=new GradientDrawable(); g.setColor(CARD); g.setCornerRadius(dp(10)); g.setStroke(dp(1), BORDER); l.setBackground(g);
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2); lp.setMargins(0,0,0,dp(8)); l.setLayoutParams(lp); return l; }
    LinearLayout sec(LinearLayout p, String t){ LinearLayout c=card(); TextView tv=txt(t,12,GOLD,true); tv.setPadding(0,0,0,dp(6)); c.addView(tv); p.addView(c); return c; }
    TextView txt(String s, int sp, int col, boolean b){ TextView t=new TextView(this); t.setText(s); t.setTextSize(sp); t.setTextColor(col); if(b) t.setTypeface(null,Typeface.BOLD); return t; }
    EditText inp(LinearLayout p, String h, String v){ EditText e=new EditText(this); e.setHint(h); e.setText(v); e.setTextColor(TXT); e.setHintTextColor(SUB); e.setTextSize(13); e.setPadding(dp(10),dp(8),dp(10),dp(8));
        GradientDrawable g=new GradientDrawable(); g.setColor(0xFF0E131D); g.setCornerRadius(dp(8)); g.setStroke(dp(1),BORDER); e.setBackground(g);
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2); lp.setMargins(0,0,0,dp(6)); e.setLayoutParams(lp); p.addView(e); return e; }
    Button mkBtn(String s, int bg, View.OnClickListener l){ Button b=new Button(this); b.setText(s); b.setAllCaps(false); b.setTextSize(12); b.setTextColor(bg==GOLD?0xFF0E1117:TXT); b.setTypeface(null,Typeface.BOLD);
        GradientDrawable g=new GradientDrawable(); g.setColor(bg); g.setCornerRadius(dp(8)); b.setBackground(g); b.setPadding(dp(8),dp(6),dp(8),dp(6)); if(l!=null) b.setOnClickListener(l); return b; }
    Button btnRow(String s, int bg, View.OnClickListener l){ Button b=mkBtn(s,bg,l); LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,-2,1f); lp.setMargins(dp(3),dp(3),dp(3),dp(3)); b.setLayoutParams(lp); return b; }
    Button btnFull(String s, int bg, View.OnClickListener l){ Button b=mkBtn(s,bg,l); LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2); lp.setMargins(0,dp(3),0,dp(3)); b.setLayoutParams(lp); return b; }
    Button pill(String s, int bg, int fg, View.OnClickListener l){ Button b=new Button(this); b.setText(s); b.setAllCaps(false); b.setTextSize(12); stylePill(b,bg,fg); b.setPadding(dp(12),dp(6),dp(12),dp(6));
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-2,-2); lp.setMargins(dp(3),dp(2),dp(3),dp(2)); b.setLayoutParams(lp); if(l!=null) b.setOnClickListener(l); return b; }
    void stylePill(Button b, int bg, int fg){ b.setTextColor(fg); GradientDrawable g=new GradientDrawable(); g.setColor(bg); g.setCornerRadius(dp(16)); b.setBackground(g); }
    void grid(LinearLayout p, String[] ls, final Runnable[] acts){ LinearLayout r=row(); for(int i=0;i<ls.length;i++){ final int k=i; r.addView(btnRow(ls[i], ACC, new View.OnClickListener(){ public void onClick(View v){ acts[k].run(); }})); } p.addView(r); }
}
