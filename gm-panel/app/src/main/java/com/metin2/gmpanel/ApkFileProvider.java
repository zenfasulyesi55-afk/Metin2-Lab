package com.metin2.gmpanel;
import android.content.*;
import android.database.*;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import java.io.*;

public class ApkFileProvider extends ContentProvider {
    public boolean onCreate() { return true; }
    public String getType(Uri u) { return "application/vnd.android.package-archive"; }
    public Cursor query(Uri u, String[] p, String s, String[] sa, String so) {
        File f = new File(new File(getContext().getCacheDir(), "apk"), "panel-update.apk");
        MatrixCursor c = new MatrixCursor(new String[]{"_display_name", "_size"});
        c.addRow(new Object[]{"panel-update.apk", f.length()});
        return c;
    }
    public ParcelFileDescriptor openFile(Uri u, String m) throws FileNotFoundException {
        File f = new File(new File(getContext().getCacheDir(), "apk"), "panel-update.apk");
        return ParcelFileDescriptor.open(f, ParcelFileDescriptor.MODE_READ_ONLY);
    }
    public Uri insert(Uri u, ContentValues v) { return null; }
    public int delete(Uri u, String s, String[] sa) { return 0; }
    public int update(Uri u, ContentValues v, String s, String[] sa) { return 0; }
}
