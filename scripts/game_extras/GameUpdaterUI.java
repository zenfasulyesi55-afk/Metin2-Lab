package com.metin2.client;
import android.app.*; import android.content.*; import android.graphics.*; import android.net.*; import android.os.*; import android.provider.*; import android.view.*; import android.widget.*; import org.json.*; import java.io.*; import java.net.*;
public class GameUpdaterUI {
  public static View wrap(final Activity a, LinearLayout l, final TextView st) {
    FrameLayout f = new FrameLayout(a);
    final ImageView bg = new ImageView(a); bg.setScaleType(ImageView.ScaleType.CENTER_CROP);
    f.addView(bg, new FrameLayout.LayoutParams(-1, -1));
    l.setBackgroundColor(0x88000000); st.setTextColor(-1);
    f.addView(l, new FrameLayout.LayoutParams(-1, -1));
    final Button b = new Button(a); b.setText("YENI OYUN SURUMU HAZIR - KUR");
    b.setTextColor(-1); b.setBackgroundColor(0xFFD97706); b.setVisibility(View.GONE);
    l.addView(b);
    b.setOnClickListener(new View.OnClickListener() { public void onClick(View v) { install(a, b, st); } });
    slide(a, bg); check(a, b, st); return f;
  }
  static void slide(final Activity a, final ImageView bg) {
    try {
      final String[] fs = a.getAssets().list("splash");
      if (fs == null || fs.length == 0) return;
      final Handler h = new Handler(Looper.getMainLooper());
      final int[] i = {0};
      new Runnable() { public void run() {
        try {
          InputStream in = a.getAssets().open("splash/" + fs[i[0]++ % fs.length]);
          bg.setImageBitmap(BitmapFactory.decodeStream(in)); in.close();
        } catch (Throwable ignored) {}
        if (!a.isFinishing()) h.postDelayed(this, 4000);
      }}.run();
    } catch (Throwable ignored) {}
  }
  static void check(final Activity a, final Button b, final TextView st) {
    new Thread(new Runnable() { public void run() { try {
      HttpURLConnection c = (HttpURLConnection) new URL("https://api.github.com/repos/zenfasulyesi55-afk/Metin2-Lab/releases/tags/latest-apks").openConnection();
      c.setRequestProperty("User-Agent", "M2");
      String res = new java.util.Scanner(c.getInputStream()).useDelimiter("\\A").next();
      JSONArray arr = new JSONObject(res).getJSONArray("assets");
      for (int k = 0; k < arr.length(); k++) {
        JSONObject o = arr.getJSONObject(k);
        if ("metin2-live-base.apk".equals(o.getString("name"))) {
          String tag = o.getString("updated_at") + o.getLong("size");
          SharedPreferences sp = a.getSharedPreferences("m2gu", 0);
          if (!tag.equals(sp.getString("cur", ""))) {
            sp.edit().putString("url", o.getString("browser_download_url")).putString("tag", tag).apply();
            a.runOnUiThread(new Runnable() { public void run() { b.setVisibility(View.VISIBLE); }});
          }
        }
      }
    } catch (Throwable ignored) {} }}).start();
  }
  static void install(final Activity a, final Button b, final TextView st) {
    if (Build.VERSION.SDK_INT >= 26 && !a.getPackageManager().canRequestPackageInstalls()) {
      a.startActivity(new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:" + a.getPackageName())));
      st.setText("Kurulum izni verip tekrar basin"); return;
    }
    final SharedPreferences sp = a.getSharedPreferences("m2gu", 0);
    final String u = sp.getString("url", "");
    if (u.isEmpty()) return;
    b.setEnabled(false); b.setText("Indiriliyor...");
    new Thread(new Runnable() { public void run() { try {
      File d = new File(a.getCacheDir(), "apk"); d.mkdirs();
      File f = new File(d, "game-update.apk");
      InputStream in = new URL(u).openStream();
      FileOutputStream out = new FileOutputStream(f); byte[] buf = new byte[8192]; int n;
      while ((n = in.read(buf)) != -1) out.write(buf, 0, n);
      out.close(); in.close();
      sp.edit().putString("cur", sp.getString("tag", "")).apply();
      a.runOnUiThread(new Runnable() { public void run() {
        b.setEnabled(true); b.setText("YENI OYUN SURUMU HAZIR - KUR");
        Intent it = new Intent(Intent.ACTION_VIEW).setDataAndType(Uri.parse("content://" + a.getPackageName() + ".gameapkprovider/game-update.apk"), "application/vnd.android.package-archive").addFlags(1);
        a.startActivity(it);
      }});
    } catch (final Throwable t) {
      a.runOnUiThread(new Runnable() { public void run() { b.setEnabled(true); st.setText("Hata: " + t); }});
    }}}).start();
  }
}
