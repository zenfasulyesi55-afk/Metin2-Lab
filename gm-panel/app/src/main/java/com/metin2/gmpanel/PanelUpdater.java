package com.metin2.gmpanel;
import android.app.*; import android.content.*; import android.net.*; import android.os.*; import android.provider.*; import android.view.*; import android.widget.*; import org.json.*; import java.io.*; import java.net.*;
public class PanelUpdater {
  public static void attach(final Activity a, LinearLayout r, final TextView tv) {
    final Button b = new Button(a);
    b.setText("YENI PANEL GUNCELLEMESI HAZIR - KUR");
    b.setTextColor(-1); b.setBackgroundColor(0xFFD97706); b.setVisibility(View.GONE);
    int i = r.indexOfChild(tv);
    r.addView(b, i >= 0 ? i + 1 : 2);
    b.setOnClickListener(new View.OnClickListener() {
      public void onClick(View v) { install(a, b, tv); }
    });
    check(a, b, tv);
  }
  static void check(final Activity a, final Button b, final TextView tv) {
    new Thread(new Runnable() { public void run() { try {
      HttpURLConnection c = (HttpURLConnection) new URL("https://api.github.com/repos/zenfasulyesi55-afk/Metin2-Lab/releases/tags/latest-apks").openConnection();
      c.setRequestProperty("User-Agent", "M2");
      String res = new java.util.Scanner(c.getInputStream()).useDelimiter("\\A").next();
      JSONArray arr = new JSONObject(res).getJSONArray("assets");
      for (int k = 0; k < arr.length(); k++) {
        JSONObject o = arr.getJSONObject(k);
        if ("metin2-gm-panel.apk".equals(o.getString("name"))) {
          String tag = o.getString("updated_at") + o.getLong("size");
          SharedPreferences sp = a.getSharedPreferences("m2u", 0);
          if (!tag.equals(sp.getString("cur", ""))) {
            sp.edit().putString("url", o.getString("browser_download_url")).putString("tag", tag).apply();
            a.runOnUiThread(new Runnable() { public void run() { b.setVisibility(View.VISIBLE); tv.setText("Durum: Yeni panel guncellemesi var!"); }});
          }
        }
      }
    } catch (Throwable ignored) {} }}).start();
  }
  static void install(final Activity a, final Button b, final TextView tv) {
    if (Build.VERSION.SDK_INT >= 26 && !a.getPackageManager().canRequestPackageInstalls()) {
      a.startActivity(new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:" + a.getPackageName())));
      tv.setText("Durum: Kurulum izni verip tekrar basin"); return;
    }
    final SharedPreferences sp = a.getSharedPreferences("m2u", 0);
    final String u = sp.getString("url", "");
    if (u.isEmpty()) return;
    b.setEnabled(false); b.setText("Indiriliyor...");
    new Thread(new Runnable() { public void run() { try {
      File d = new File(a.getCacheDir(), "apk"); d.mkdirs();
      File f = new File(d, "panel-update.apk");
      HttpURLConnection c = (HttpURLConnection) new URL(u).openConnection();
      InputStream in = c.getInputStream(); FileOutputStream out = new FileOutputStream(f);
      byte[] buf = new byte[8192]; int n;
      while ((n = in.read(buf)) != -1) out.write(buf, 0, n);
      out.close(); in.close();
      sp.edit().putString("cur", sp.getString("tag", "")).apply();
      a.runOnUiThread(new Runnable() { public void run() {
        b.setEnabled(true); b.setText("YENI PANEL GUNCELLEMESI HAZIR - KUR");
        Intent it = new Intent(Intent.ACTION_VIEW);
        it.setDataAndType(Uri.parse("content://com.metin2.gmpanel.apkprovider/panel-update.apk"), "application/vnd.android.package-archive");
        it.addFlags(1);
        a.startActivity(it);
      }});
    } catch (Throwable t) {
      a.runOnUiThread(new Runnable() { public void run() { b.setEnabled(true); tv.setText("Hata: " + t); }});
    }}}).start();
  }
}
