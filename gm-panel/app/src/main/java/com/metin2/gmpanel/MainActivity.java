package com.metin2.gmpanel;
import android.app.Activity;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.os.Bundle;
import android.text.InputType;
import android.view.View;
import android.widget.*;
import java.io.*;
import java.net.*;
import java.util.concurrent.*;
public class MainActivity extends Activity {
private EditText edHost, edKey, edNick, edCode, edAcc, edTargetNick, edCustom;
private TextView tvStatus;
private final ExecutorService executor = Executors.newSingleThreadExecutor();
private SharedPreferences prefs;
@Override protected void onCreate(Bundle savedInstanceState) {
super.onCreate(savedInstanceState);
prefs = getSharedPreferences("m2_gm_prefs", MODE_PRIVATE);
ScrollView sv = new ScrollView(this); sv.setBackgroundColor(Color.parseColor("#121418"));
LinearLayout root = new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL); root.setPadding(32, 32, 32, 32); sv.addView(root);
TextView title = new TextView(this); title.setText("MOBILE2-LAB Ozel GM Kontrol Paneli"); title.setTextSize(20); title.setTextColor(Color.parseColor("#FFD54F")); root.addView(title);
tvStatus = new TextView(this); tvStatus.setText("Durum: Hazir (Yerel ve SSH Tuneli: 127.0.0.1)"); tvStatus.setTextColor(Color.parseColor("#81C784")); tvStatus.setPadding(0, 12, 0, 20); root.addView(tvStatus);
edHost = addInput(root, "Sunucu IP (Yerel / SSH Tuneli: 127.0.0.1)", prefs.getString("host", "127.0.0.1"), false, false);
edKey = addInput(root, "Ozel Admin Sifresi (GitHub ADMIN_SECRET)", prefs.getString("key", ""), false, true);
edNick = addInput(root, "Senin Karakter Nickin", prefs.getString("nick", "Test"), false, false);
addSection(root, "Karakter ve Seviye");
addRow(root, new String[]{"Lv. 99", "Lv. 120", "Full HP/SP"}, new String[]{"/level 99", "/level 120", "/r"});
addRow(root, new String[]{"999M Yang", "Gorunmez", "Hiz Full"}, new String[]{"GOLD999", "/inv", "SPEED"});
addRow(root, new String[]{"Skiller P", "At Lv.21", "Temizle"}, new String[]{"SKILLP", "HORSE21", "/purge"});
addSection(root, "Kod ile Esya ve Boss Uretimi");
edCode = addInput(root, "Esya veya Mob Kodu (Orn: 19, 11971, 1093)", "19", true, false);
addRow(root, new String[]{"Esya Ver (/item)", "Boss / Mob Cagir (/m)"}, new String[]{"ITEM_CODE", "MOB_CODE"});
addRow(root, new String[]{"Kraliyet", "Sirius +9", "Azrail", "Mavi Ejder"}, new String[]{"/item 11971", "/item 279", "/m 1093", "/m 2493"});
addSection(root, "Isinlanma ve Hava Durumu");
addRow(root, new String[]{"Kirmizi Koy", "Sari Koy", "Mavi Koy"}, new String[]{"/go a", "/go b", "/go c"});
addRow(root, new String[]{"Gece", "Gunduz", "Kar Yagdir", "Kar Durdur"}, new String[]{"/x 1", "/x 2", "/xmas_snow 1", "/xmas_snow 0"});
addSection(root, "Baskasina GM Yetkisi Ver / Al");
edAcc = addInput(root, "Hedef Kullanici Adi (Hesap)", "", false, false);
edTargetNick = addInput(root, "Hedef Karakter Nicki", "", false, false);
addRow(root, new String[]{"GM Yetkisi Ver", "GM Yetkisi Al"}, new String[]{"ADDGM", "DELGM"});
addSection(root, "Serbest GM Komutu");
edCustom = addInput(root, "Komut (Orn: /notice Merhaba)", "/notice Selam!", false, false);
addRow(root, new String[]{"Komutu Gonder"}, new String[]{"CUSTOM"});
setContentView(sv);
}
private EditText addInput(LinearLayout p, String hint, String def, boolean num, boolean pass) {
TextView l = new TextView(this); l.setText(hint); l.setTextColor(Color.LTGRAY); l.setTextSize(12); p.addView(l);
EditText e = new EditText(this); e.setText(def); e.setTextColor(Color.WHITE); e.setBackgroundColor(Color.parseColor("#1E222A")); e.setPadding(20, 16, 20, 16);
if (num) e.setInputType(InputType.TYPE_CLASS_NUMBER); else if (pass) e.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, -2); lp.setMargins(0, 4, 0, 14); e.setLayoutParams(lp); p.addView(e); return e;
}
private void addSection(LinearLayout p, String t) {
TextView s = new TextView(this); s.setText(t); s.setTextColor(Color.parseColor("#64B5F6")); s.setTextSize(15); s.setPadding(0, 18, 0, 8); p.addView(s);
}
private void addRow(LinearLayout p, String[] labels, final String[] actions) {
LinearLayout row = new LinearLayout(this); row.setOrientation(LinearLayout.HORIZONTAL);
for (int i = 0; i < labels.length; i++) {
final String act = actions[i];
Button btn = new Button(this); btn.setText(labels[i]); btn.setTextSize(12);
LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, -2, 1f); lp.setMargins(4, 4, 4, 4); btn.setLayoutParams(lp);
btn.setOnClickListener(new View.OnClickListener() { public void onClick(View v) { runAction(act); } });
row.addView(btn);
}
p.addView(row);
}
private void runAction(String act) {
String nick = edNick.getText().toString().trim();
if (act.equals("GOLD999")) sendCmds(new String[]{"/set " + nick + " gold 999999999"});
else if (act.equals("SPEED")) sendCmds(new String[]{"/mspd 250", "/aspd 250"});
else if (act.equals("SKILLP")) { int[] sk = {1,2,3,4,5,6,16,17,18,19,20,21,31,32,33,34,35,36,46,47,48,49,50,51,61,62,63,64,65,66,76,77,78,79,80,81,91,92,93,94,95,96,106,107,108,109,110,111}; String[] cmds = new String[sk.length]; for (int i = 0; i < sk.length; i++) cmds[i] = "/setsk " + sk[i] + " 59"; sendCmds(cmds); }
else if (act.equals("HORSE21")) sendCmds(new String[]{"/horse_level " + nick + " 21", "/setsk 131 10"});
else if (act.equals("ITEM_CODE")) sendCmds(new String[]{"/item " + edCode.getText().toString().trim()});
else if (act.equals("MOB_CODE")) sendCmds(new String[]{"/m " + edCode.getText().toString().trim()});
else if (act.equals("ADDGM")) sendCmds(new String[]{"ADDGM " + edAcc.getText().toString().trim() + " " + edTargetNick.getText().toString().trim()});
else if (act.equals("DELGM")) sendCmds(new String[]{"DELGM " + edTargetNick.getText().toString().trim()});
else if (act.equals("CUSTOM")) sendCmds(new String[]{edCustom.getText().toString().trim()});
else sendCmds(new String[]{act});
}
private void sendCmds(final String[] cmds) {
final String host = edHost.getText().toString().trim();
final String key = edKey.getText().toString().trim();
final String nick = edNick.getText().toString().trim();
prefs.edit().putString("host", host).putString("key", key).putString("nick", nick).apply();
executor.execute(new Runnable() { public void run() {
String lastRes = "Gonderildi";
try {
for (String cmd : cmds) {
Socket s = new Socket(); s.connect(new InetSocketAddress(host, 11099), 2500); s.setSoTimeout(3000);
OutputStream os = s.getOutputStream(); os.write((key + "|" + nick + "|" + cmd + "\n").getBytes("UTF-8")); os.flush();
BufferedReader br = new BufferedReader(new InputStreamReader(s.getInputStream(), "UTF-8"));
String res = br.readLine(); if (res != null) lastRes = res; s.close();
}
final String msg = lastRes;
runOnUiThread(new Runnable() { public void run() { tvStatus.setText("Durum: " + msg); } });
} catch (final Exception e) {
runOnUiThread(new Runnable() { public void run() { tvStatus.setText("Baglanti Hatasi (Once oyuna giris yap): " + e.getMessage()); } });
}
} });
}
@Override protected void onDestroy() { executor.shutdownNow(); super.onDestroy(); }
}
