package com.metin2.gmpanel;
import java.util.*;

public class CatalogData {
    public static class Entry {
        public final int vnum; public final String name, cat, tags;
        public final boolean plusable, isMob;
        public Entry(int v, String n, String c, boolean p, boolean m, String t) {
            vnum = v; name = n; cat = c; plusable = p; isMob = m; tags = t;
        }
    }
    public static final List<Entry> ALL = Arrays.asList(
        new Entry(180,"Zehir Kilici","silah",true,false,"zehir kilic 75"),
        new Entry(140,"Muharebe Kilici","silah",true,false,"muho muharebe 65"),
        new Entry(270,"Triton / Sirius Kilici","silah",true,false,"sirius triton 80"),
        new Entry(290,"Dolunay Kilici","silah",true,false,"dolunay doli 30"),
        new Entry(150,"Hortlak Disi Kilici","silah",true,false,"hortlak 65 sura"),
        new Entry(190,"Aslan Kilici","silah",true,false,"aslan 75 sura"),
        new Entry(160,"Su Perisi Kilici","silah",true,false,"su perisi 65"),
        new Entry(170,"Azap Kilici","silah",true,false,"azap 70"),
        new Entry(3160,"Kin Kilici","silah",true,false,"kin 75 cift el"),
        new Entry(3130,"Partizan","silah",true,false,"partizan 65 cift el"),
        new Entry(3210,"Kirmizi Demir Pala (KDP)","silah",true,false,"kdp pala 30"),
        new Entry(1130,"Ejderha Bicagi","silah",true,false,"ejderha bicak 65 ninja"),
        new Entry(1180,"Seytan Kanadi Cakram","silah",true,false,"cakram 75 ninja"),
        new Entry(1170,"Siyah Yaprak Hanceri","silah",true,false,"syh hancer 30"),
        new Entry(2160,"Buyuk Seytan Yayi","silah",true,false,"seytan yayi 75"),
        new Entry(2150,"Geyik Boynuzu Yay","silah",true,false,"gby yay 30"),
        new Entry(5120,"Orkide Cani","silah",true,false,"orkide can 75 saman"),
        new Entry(7140,"Kurtulus Yelpazesi","silah",true,false,"kurtulus yelpaze 65"),
        new Entry(11290,"Siyah Celik Zirh","zirh",true,false,"siyah celik savasci 70"),
        new Entry(11490,"Siyah Ruzgar Takimi","zirh",true,false,"siyah ruzgar ninja 70"),
        new Entry(11690,"Karabuyu Zirhi","zirh",true,false,"karabuyu sura 70"),
        new Entry(11890,"Siyah Elbise","zirh",true,false,"siyah elbise saman 70"),
        new Entry(11280,"Ejderha Tanrisi Zirhi","zirh",true,false,"ejderha tanrisi 61"),
        new Entry(11971,"Kraliyet Zirhi (Savasci)","zirh",false,false,"hwang kraliyet savasci"),
        new Entry(11972,"Kraliyet Zirhi (Ninja)","zirh",false,false,"hwang kraliyet ninja"),
        new Entry(11973,"Kraliyet Zirhi (Sura)","zirh",false,false,"hwang kraliyet sura"),
        new Entry(11974,"Kraliyet Zirhi (Saman)","zirh",false,false,"hwang kraliyet saman"),
        new Entry(12240,"Hayalet Maske Baslik","taki",true,false,"kask savasci 41"),
        new Entry(12360,"Celik Kapson","taki",true,false,"kask ninja 41"),
        new Entry(12500,"Kale Kask","taki",true,false,"kask sura 41"),
        new Entry(12640,"Gunisigi Sapka","taki",true,false,"sapka saman 41"),
        new Entry(13060,"Sahin Kalkan","taki",true,false,"sahin kalkan 61"),
        new Entry(13080,"Kaplan Kalkan","taki",true,false,"kaplan kalkan 61"),
        new Entry(13100,"Aslan Agzi Kalkan","taki",true,false,"aslan agzi kalkan 61"),
        new Entry(13120,"Ejderha Pulu Kalkan","taki",true,false,"ejderha pulu kalkan 61"),
        new Entry(14200,"Cennetin Gozu Bilezik","taki",true,false,"cennet bilezik 54"),
        new Entry(16200,"Cennetin Gozu Kolye","taki",true,false,"cennet kolye 54"),
        new Entry(17100,"Abanoz Kupe","taki",true,false,"abanoz kupe 33"),
        new Entry(17200,"Cennetin Gozu Kupe","taki",true,false,"cennet kupe 54"),
        new Entry(15200,"Anka Ayakkabi","taki",true,false,"anka ayakkabi 55"),
        new Entry(50053,"Asker At Kitabi","esya",false,false,"asker at kitabi"),
        new Entry(25040,"Kutsama Kagidi","esya",false,false,"kutsama arti basma"),
        new Entry(25041,"Buyulu Metal","esya",false,false,"buyulu metal"),
        new Entry(71084,"Efsun Nesnesi","esya",false,false,"efsun nesnesi"),
        new Entry(71085,"Artirma Kagidi","esya",false,false,"artirma kagidi efsun"),
        new Entry(71051,"Kutsama Kuresi (5. Efsun)","esya",false,false,"kutsama kuresi"),
        new Entry(70038,"Cesaret Pelerini","esya",false,false,"cesaret pelerini"),
        new Entry(50513,"Ruh Tasi","esya",false,false,"ruh tasi p skill"),
        new Entry(71001,"Kotu Ruh Kovma","esya",false,false,"kotu ruh bk"),
        new Entry(71094,"Munzevi Tavsiyesi","esya",false,false,"munzevi bk"),
        new Entry(70005,"Tecrube Yuzugu","esya",false,false,"tecrube yuzugu exp"),
        new Entry(70057,"Hirsizin Eldiveni","esya",false,false,"hirsiz eldiveni drop"),
        new Entry(27003,"Kirmizi Iksir (B)","esya",false,false,"kirmizi iksir pot hp"),
        new Entry(27006,"Mavi Iksir (B)","esya",false,false,"mavi iksir pot sp"),
        new Entry(27102,"Yesil Iksir (B)","esya",false,false,"yesil iksir saldiri"),
        new Entry(27105,"Mor Iksir (B)","esya",false,false,"mor iksir hareket"),
        new Entry(50011,"Ayisigi Define Sandigi","esya",false,false,"ayisigi sandik"),
        new Entry(50037,"Altigen Hediye Paketi","esya",false,false,"altigen sandik"),
        new Entry(50096,"Futbol Topu","esya",false,false,"futbol topu"),
        new Entry(50082,"Azrail Sandigi","esya",false,false,"azrail sandik"),
        new Entry(28430,"Delici Tasi +4","tas",false,false,"delici tas"),
        new Entry(28431,"Oldurucu Darbe Tasi +4","tas",false,false,"kritik tas"),
        new Entry(28432,"Tekrar Tasi +4","tas",false,false,"tekrar buyu hizi tas"),
        new Entry(28433,"Savascidan Koruyan +4","tas",false,false,"savasci tas"),
        new Entry(28434,"Ninjadan Koruyan +4","tas",false,false,"ninja tas"),
        new Entry(28435,"Suradan Koruyan +4","tas",false,false,"sura tas"),
        new Entry(28436,"Samandan Koruyan +4","tas",false,false,"saman tas"),
        new Entry(28437,"Canavardan Koruyan +4","tas",false,false,"canavar tas"),
        new Entry(28438,"Korunma Tasi +4","tas",false,false,"korunma blok tas"),
        new Entry(28441,"Yasam Tasi +4","tas",false,false,"yasam hp tas"),
        new Entry(28442,"Savunma Tasi +4","tas",false,false,"savunma tas"),
        new Entry(28443,"Hiz Tasi +4","tas",false,false,"hiz tas"),
        new Entry(1093,"Azrail","mob",false,true,"azrail boss kule"),
        new Entry(2493,"Beran-Setaou (Mavi Ejderha)","mob",false,true,"beran mavi ejderha boss"),
        new Entry(2291,"Kirmizi Ejderha","mob",false,true,"kirmizi ejderha boss"),
        new Entry(1901,"Dokuz Kuyruk","mob",false,true,"dokuz kuyruk boss"),
        new Entry(2206,"Alev Kral","mob",false,true,"alev kral boss"),
        new Entry(1304,"Sari Kaplan Hayaleti","mob",false,true,"sari kaplan boss"),
        new Entry(2091,"Kralice Orumcek","mob",false,true,"kralice orumcek boss"),
        new Entry(691,"Ork Reisi","mob",false,true,"ork reisi boss"),
        new Entry(1192,"Guclu Buz Cadisi","mob",false,true,"buz cadisi boss"),
        new Entry(5001,"Korsan Tanaka","mob",false,true,"korsan tanaka event"),
        new Entry(20358,"Isimsiz Cicekler (OX)","mob",false,true,"isimsiz cicek ox"),
        new Entry(8007,"Kiskanclik Metini (35)","metin",false,true,"metin 35"),
        new Entry(8009,"Golge Metini (45)","metin",false,true,"metin 45"),
        new Entry(8011,"Seytan Metini (55)","metin",false,true,"metin 55"),
        new Entry(8014,"Olum Metini (65)","metin",false,true,"metin 65"),
        new Entry(8024,"Pung-Ma Metini (75)","metin",false,true,"metin 75"),
        new Entry(8026,"Tu-Young Metini (85)","metin",false,true,"metin 85"),
        new Entry(8027,"Jeon-Un Metini (90)","metin",false,true,"metin 90")
    );
    public static String norm(String s) {
        if (s == null) return "";
        return s.toLowerCase(Locale.ROOT).replace('ı','i').replace('İ','i')
            .replace('ş','s').replace('ğ','g').replace('ü','u').replace('ö','o').replace('ç','c');
    }
    public static List<Entry> search(String q, String cat) {
        String nq = norm(q).trim(); List<Entry> out = new ArrayList<Entry>();
        for (Entry e : ALL) {
            if (!"tumu".equals(cat) && !cat.equals(e.cat)) continue;
            if (nq.isEmpty() || norm(e.name).contains(nq) || norm(e.tags).contains(nq) || String.valueOf(e.vnum).contains(nq)) out.add(e);
        }
        return out;
    }
}
