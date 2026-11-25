#!/usr/bin/env python3
import os, re, sqlite3
_orig_sc = sqlite3.connect
sqlite3.connect = lambda *a, **k: (lambda c: (c.create_function("m2_enum_text", -1, lambda *x: x[0] if x else None), c.create_function("m2_set_text", -1, lambda *x: x[0] if x else None), c.execute("PRAGMA ignore_check_constraints=ON"), c)[-1])(_orig_sc(*a, **k))
ADMIN_SECRET = (os.environ.get("ADMIN_SECRET") or "").strip() or "CHANGE_ME_LOCAL_ONLY"
ADMIN_SECRET_CPP = ADMIN_SECRET.replace("\\", "\\\\").replace('"', '\\"')
db_path = "/tmp/m2serverpack/server/sqlite-seed/common.sqlite3"
con = sqlite3.connect(db_path) if os.path.exists(db_path) else None
cur = con.cursor() if con else None
hcols = [r[1] for r in cur.execute("PRAGMA table_info(gmhost)").fetchall()] if cur else []
cur.execute("DELETE FROM gmhost") if hcols else None
cur.execute("INSERT INTO gmhost (" + hcols[0] + ") VALUES (?)", ("127.0.0.1",)) if hcols else None
ginfo = cur.execute("PRAGMA table_info(gmlist)").fetchall() if cur else []
gcols = [r[1] for r in ginfo]
gvals = [1 if ("id" in r[1].lower() and r[5] == 1) else ("test" if "account" in r[1].lower() else ("Test" if "name" in r[1].lower() else ("127.0.0.1" if "contact" in r[1].lower() else ("ALL" if "server" in r[1].lower() else ("IMPLEMENTOR" if "authority" in r[1].lower() else ""))))) for r in ginfo]
cur.execute("DELETE FROM gmlist") if gcols else None
cur.execute("INSERT INTO gmlist (" + ",".join(gcols) + ") VALUES (" + ",".join(["?"] * len(gcols)) + ")", gvals) if gcols else None
gvals2 = [2 if ("id" in r[1].lower() and r[5] == 1) else ("admin" if "account" in r[1].lower() else ("[OK]Miko" if "name" in r[1].lower() else ("127.0.0.1" if "contact" in r[1].lower() else ("ALL" if "server" in r[1].lower() else ("IMPLEMENTOR" if "authority" in r[1].lower() else ""))))) for r in ginfo]
cur.execute("INSERT INTO gmlist (" + ",".join(gcols) + ") VALUES (" + ",".join(["?"] * len(gcols)) + ")", gvals2) if gcols else None
con.commit() if con else None
con.close() if con else None
# M2_RENAME_OK_MIKO_V2
_miko_roots = ["/tmp/m2serverpack", "/tmp/m2stage", "/tmp/m2dev-server", "client-src"]
_miko_db_cnt = 0
_miko_ren_cnt = 0
_miko_found = []
for _root in _miko_roots:
    if not os.path.exists(_root):
        continue
    for _r, _d, _fs in os.walk(_root):
        for _fn in _fs:
            _fp = os.path.join(_r, _fn)
            if not os.path.isfile(_fp):
                continue
            try:
                with open(_fp, "rb") as _fh:
                    _hdr = _fh.read(16)
            except Exception:
                continue
            if _hdr == b"SQLite format 3\x00":
                _miko_db_cnt += 1
                _miko_found.append(_fp)
                try:
                    os.chmod(_fp, 0o644)
                except Exception:
                    pass
                try:
                    _sc = sqlite3.connect(_fp)
                    _tbls = [x[0] for x in _sc.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
                    for _t in _tbls:
                        _tl = _t.lower()
                        if _tl == "player":
                            _cols = [c[1] for c in _sc.execute('PRAGMA table_info("' + _t + '")').fetchall()]
                            if any(c.lower() == "name" for c in _cols):
                                _cur = _sc.execute(
                                    'UPDATE "' + _t + '" SET name=? WHERE LOWER(REPLACE(TRIM(CAST(name AS TEXT)), char(0), \'\')) IN (\'[sa]admin\',\'[tl]admin\',\'[ok]admin\') OR LOWER(CAST(name AS TEXT)) LIKE \'%]admin%\'',
                                    ("[OK]Miko",),
                                )
                                if _cur.rowcount > 0:
                                    _miko_ren_cnt += _cur.rowcount
                                    print("OK: MIKO_PLAYER_RENAME", _fp, "rows=", _cur.rowcount)
                        elif _tl == "gmlist":
                            _cols = [c[1] for c in _sc.execute('PRAGMA table_info("' + _t + '")').fetchall()]
                            _cm = {c.lower(): c for c in _cols}
                            if "mname" in _cm and "mauthority" in _cm:
                                _cur = _sc.execute(
                                    'UPDATE "' + _t + '" SET "' + _cm["mname"] + '"=?, "' + _cm["mauthority"] + '"=? WHERE LOWER(CAST("' + _cm["mname"] + '" AS TEXT)) LIKE \'%]admin%\'' + (' OR LOWER(CAST("' + _cm["maccount"] + '" AS TEXT))=\'admin\'' if "maccount" in _cm else ''),
                                    ("[OK]Miko", "IMPLEMENTOR"),
                                )
                                if _cur.rowcount > 0:
                                    print("OK: MIKO_GMLIST_RENAME", _fp, "rows=", _cur.rowcount)
                    _sc.commit()
                    _sc.close()
                except Exception as _ex:
                    print("WARN: MIKO_DB_ERR", _fp, _ex)
            elif _fn.lower().endswith(".sql") and os.path.getsize(_fp) < 20_000_000:
                try:
                    _txt = open(_fp, "r", encoding="utf-8", errors="ignore").read()
                    if any(k in _txt for k in ("[SA]Admin", "[TL]Admin", "[OK]Admin")):
                        for k in ("[SA]Admin", "[TL]Admin", "[OK]Admin"):
                            _txt = _txt.replace(k, "[OK]Miko")
                        open(_fp, "w", encoding="utf-8").write(_txt)
                        _miko_ren_cnt += 1
                        print("OK: MIKO_SQL_RENAME", _fp)
                except Exception as _ex:
                    print("WARN: MIKO_SQL_ERR", _fp, _ex)
print("OK: MIKO_SCAN_DONE sqlite=", _miko_db_cnt, "renamed=", _miko_ren_cnt)
if _miko_ren_cnt == 0:
    print("WARN: MIKO_FOUND_DBS:", _miko_found[:12])
# END_M2_RENAME_OK_MIKO_V2



main_cpp = "/tmp/m2dev-server-src/src/game/main.cpp"
ms = open(main_cpp, "r", encoding="utf-8", errors="ignore").read()
m = re.search(r"(?m)^[ \t]*(?:static[ \t]+)?void[ \t]+heartbeat[ \t]*\([^;{}]*\)[ \t\r\n]*\{", ms)
assert m is not None, "main.cpp icinde heartbeat tanimi bulunamadi!"
hdr = ["", "// M2_ADM_HEADERS", "#include <thread>", "#include <mutex>", "#include <queue>", "#include <chrono>", "#include <string>", "#include <memory>", "#include <utility>", "#include <type_traits>", "#include <cstring>", "#include <cstdio>", "#include <cstdlib>", "#include <sys/socket.h>", "#include <netinet/in.h>", "#include <arpa/inet.h>", "#include <unistd.h>", ""]
b = [""]
b.append('#include "config.h"')
b.append('#include "db.h"')
b.append('#include "char.h"')
b.append('#include "char_manager.h"')
b.append('#include "cmd.h"')
# M2_OWNER_V2: affect.h ve packet.h sembollerini derleme aninda guvenli tara
_m2_aff_src = ""
for _fp in ("/tmp/m2dev-server-src/src/game/affect.h", "/tmp/m2dev-server-src/src/common/length.h"):
    if os.path.exists(_fp): _m2_aff_src += open(_fp, "r", encoding="utf-8", errors="ignore").read()
_m2_pkt_src = ""
for _fp in ("/tmp/m2dev-server-src/src/game/packet.h", "/tmp/m2dev-server-src/src/game/char.h"):
    if os.path.exists(_fp): _m2_pkt_src += open(_fp, "r", encoding="utf-8", errors="ignore").read()
def _pick_sym(src, names, fallback):
    for n in names:
        if re.search(r"\b" + n + r"\b", src): return n
    return fallback
_g_syms = [
    _pick_sym(_m2_aff_src, ["AFF_CHEONGEUN"], "AFF_NONE"),
    _pick_sym(_m2_aff_src, ["AFF_HEUKSIN"], "AFF_NONE"),
    _pick_sym(_m2_aff_src, ["AFF_JEONGWIHON"], "AFF_NONE"),
    _pick_sym(_m2_aff_src, ["AFF_GEOMGYEONG"], "AFF_NONE"),
    _pick_sym(_m2_aff_src, ["AFF_HOSIN", "AFF_BOHO"], "AFF_NONE"),
    _pick_sym(_m2_aff_src, ["AFF_FIRE"], "AFF_NONE"),
    _pick_sym(_m2_aff_src, ["AFF_YMIR", "AFF_CHINA_FIREWORK"], "AFF_NONE"),
]
_fx_syms = [
    _pick_sym(_m2_pkt_src, ["SE_LEVELUP"], "0"),
    _pick_sym(_m2_pkt_src, ["SE_CHINA_FIREWORK"], "0"),
    _pick_sym(_m2_pkt_src, ["SE_SPIN_TOP"], "0"),
    _pick_sym(_m2_pkt_src, ["SE_DXUP_PURPLE", "SE_SUCCESS"], "0"),
    _pick_sym(_m2_pkt_src, ["SE_CRITICAL", "SE_PENETRATE"], "0"),
    _pick_sym(_m2_pkt_src, ["SE_SPUP_BLUE", "SE_HPUP_RED"], "0"),
]
b.append('#include "item.h"')
b.append('#include "item_manager.h"')
b.append('#include "affect.h"')
b.append('#include "packet.h"')
b.append('#include "desc.h"')

b.extend(hdr)
b.append("struct M2AdminReq { std::string nick, cmd, reply; bool done; M2AdminReq() : done(false) {} };")
b.append("static std::mutex g_m2_adm_mtx;")
b.append("static std::queue<std::shared_ptr<M2AdminReq>> g_m2_adm_q;")
b.append("template <typename T> static typename std::enable_if<std::is_pointer<T>::value>::type m2_adm_release(T p) { delete p; }")
b.append("template <typename T> static typename std::enable_if<!std::is_pointer<T>::value>::type m2_adm_release(const T&) {}")
b.append('static void m2_adm_exec_sql(const char* query) { auto res = DBManager::instance().DirectQuery("%s", query); m2_adm_release(res); }')
b.append("static SQLMsg* m2_adm_raw(SQLMsg* p) { return p; }")
b.append("template <typename T> static auto m2_adm_raw(T& p) -> decltype(p.get()) { return p.get(); }")
b.append("static std::string m2_adm_esc(const std::string& in) { std::string o; for (char c : in) { if (c == 39) { o += (char)39; o += (char)39; } else if (c >= 32 && c != 59) o += c; } return o; }")
b.append("static bool m2_adm_find_db(const char* fname, char* out, size_t sz) {")
b.append('  const char* envs[] = { std::getenv("M2_DB_DIR"), std::getenv("SQLITE_DB_DIR") };')
b.append('  for (int i = 0; i < 2; ++i) { if (envs[i] && envs[i][0]) { std::snprintf(out, sz, "%s/%s", envs[i], fname); if (::access(out, F_OK) == 0) return true; } }')
b.append('  const char* dirs[] = { ".", "db", "../db", "../../db", "../../../db", "sqlite-seed", "../sqlite-seed", "../../sqlite-seed" };')
b.append('  for (int i = 0; i < 8; ++i) { std::snprintf(out, sz, "%s/%s", dirs[i], fname); if (::access(out, F_OK) == 0) return true; }')
b.append("  return false;")
b.append("}")
b.append("static int m2_adm_query_rows(const char* query, int cols, std::string& out, int maxRows) {")
b.append('  auto res = DBManager::instance().DirectQuery("%s", query);')
b.append("  SQLMsg* msg = m2_adm_raw(res); int cnt = 0;")
b.append("  if (msg && msg->Get() && msg->Get()->pSQLResult) {")
b.append("    MYSQL_ROW row;")
b.append("    while (cnt < maxRows && (row = mysql_fetch_row(msg->Get()->pSQLResult))) {")
b.append('      if (!out.empty()) out += ";;";')
b.append('      for (int i = 0; i < cols; ++i) { if (i > 0) out += " | "; out += (row[i] ? row[i] : "-"); }')
b.append("      ++cnt;")
b.append("    }")
b.append("  }")
b.append("  m2_adm_release(res); return cnt;")
b.append("}")
b.append("static std::string g_m2_adm_pulse_nick;")
b.append("static int g_m2_adm_pulse_fx = 0;")
b.append("static std::string g_m2_adm_god_nick;")
b.append("static int g_m2_adm_pclk = 0;")
b.append("static const EAffectBits g_m2_adm_glows[7] = { " + ", ".join(_g_syms) + " };")
b.append("static const int g_m2_adm_fxs[6] = { " + ", ".join(_fx_syms) + " };")
# M2_MIKO_AURA_V1
_miko_affs = [
    _pick_sym(_m2_aff_src, ["AFF_CHEONGEUN"], "AFF_NONE"),
    _pick_sym(_m2_aff_src, ["AFF_HOSIN"], "AFF_NONE"),
    _pick_sym(_m2_aff_src, ["AFF_BOHO"], "AFF_NONE"),
    _pick_sym(_m2_aff_src, ["AFF_YMIR", "AFF_CHINA_FIREWORK"], "AFF_NONE"),
]
_miko_fx_gold = _pick_sym(_m2_pkt_src, ["SE_LEVELUP"], "0")
_miko_fx_white = _pick_sym(_m2_pkt_src, ["SE_SUCCESS", "SE_CRITICAL", "SE_DXUP_PURPLE"], "0")
b.append("static const EAffectBits g_m2_miko_affs[4] = { " + ", ".join(_miko_affs) + " };")
b.append("static const int g_m2_miko_fx_gold = " + _miko_fx_gold + ";")
b.append("static const int g_m2_miko_fx_white = " + _miko_fx_white + ";")
b.append("static bool g_m2_miko_aura_on = true;")
b.append("static int g_m2_miko_phase = 0;")
b.append("static void m2_miko_apply_aura(LPCHARACTER ch, bool on) {")
b.append("  if (!ch) return;")
b.append("  for (int k = 0; k < 4; ++k) {")
b.append("    if (on) { if (!ch->FindAffect(590 + k) && g_m2_miko_affs[k] != AFF_NONE) ch->AddAffect(590 + k, POINT_NONE, 0, g_m2_miko_affs[k], 86400, 0, true); }")
b.append("    else { ch->RemoveAffect(590 + k); }")
b.append("  }")
b.append("}")


b.append("static bool m2_adm_is_owner(const char* s) { if (!s) return false; bool t=(s[0]=='t'||s[0]=='T')&&(s[1]=='e'||s[1]=='E')&&(s[2]=='s'||s[2]=='S')&&(s[3]=='t'||s[3]=='T')&&s[4]==0; bool a=(s[0]=='a'||s[0]=='A')&&(s[1]=='d'||s[1]=='D')&&(s[2]=='m'||s[2]=='M')&&(s[3]=='i'||s[3]=='I')&&(s[4]=='n'||s[4]=='N')&&s[5]==0; return t || a; }")
b.append("static bool m2_adm_db(char* out, size_t sz) {")
b.append('const char* envs[] = { std::getenv("M2_DB_DIR"), std::getenv("SQLITE_DB_DIR") };')
b.append('for (int i = 0; i < 2; ++i) { if (envs[i] && envs[i][0]) { std::snprintf(out, sz, "%s/common.sqlite3", envs[i]); if (::access(out, F_OK) == 0) return true; } }')
b.append('const char* cands[] = { "common.sqlite3", "db/common.sqlite3", "../db/common.sqlite3", "../../db/common.sqlite3", "../../../db/common.sqlite3" };')
b.append('for (int i = 0; i < 4; ++i) { if (::access(cands[i], F_OK) == 0) { std::snprintf(out, sz, "%s", cands[i]); return true; } }')
b.append("return false;")
b.append("}")
b.append("static void m2_adm_clean(const std::string& s, char* d, size_t sz) {")
b.append("size_t j = 0;")
b.append("for (size_t i = 0; i < s.size() && j + 1 < sz; ++i) {")
b.append("unsigned char c = (unsigned char)s[i];")
b.append("if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_') d[j++] = (char)c;")
b.append("}")
b.append("d[j] = 0;")
b.append("}")
b.append("static void m2_adm_set_reply(const std::shared_ptr<M2AdminReq>& req, const std::string& msg) { std::lock_guard<std::mutex> lk(g_m2_adm_mtx); req->reply = msg; req->done = true; }")
b.append("static void m2_adm_thread() {")
b.append("int srv = ::socket(AF_INET, SOCK_STREAM, 0);")
b.append("if (srv < 0) return;")
b.append("int opt = 1;")
b.append("::setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &opt, (socklen_t)sizeof(opt));")
b.append("struct sockaddr_in addr;")
b.append("std::memset(&addr, 0, sizeof(addr));")
b.append("addr.sin_family = AF_INET;")
b.append("addr.sin_port = htons(11099);")
b.append("addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);")
b.append("if (::bind(srv, (const struct sockaddr*)&addr, (socklen_t)sizeof(addr)) < 0) { ::close(srv); return; }")
b.append("::listen(srv, 16);")
b.append("while (true) {")
b.append("int cl = ::accept(srv, NULL, NULL);")
b.append("if (cl < 0) { std::this_thread::sleep_for(std::chrono::milliseconds(50)); continue; }")
b.append("char buf[1024];")
b.append("ssize_t n = ::recv(cl, buf, sizeof(buf) - 1, 0);")
b.append("if (n > 0) {")
b.append("buf[n] = 0;")
b.append("std::string line(buf);")
b.append("while (!line.empty() && (line.back() == '\\n' || line.back() == '\\r')) line.pop_back();")
b.append("size_t p1 = line.find('|');")
b.append("size_t p2 = (p1 != std::string::npos) ? line.find('|', p1 + 1) : std::string::npos;")
b.append('if (p1 == std::string::npos || p2 == std::string::npos || line.substr(0, p1) != "' + ADMIN_SECRET_CPP + '") {')
b.append('const char* err = "ERR: Yetkisiz erisim\\n";')
b.append("::send(cl, err, std::strlen(err), 0);")
b.append("} else {")
b.append("auto req = std::make_shared<M2AdminReq>();")
b.append("req->nick = line.substr(p1 + 1, p2 - p1 - 1);")
b.append("req->cmd = line.substr(p2 + 1);")
b.append("{ std::lock_guard<std::mutex> lk(g_m2_adm_mtx); g_m2_adm_q.push(req); }")
b.append('std::string out = "OK: Kuyruga alindi";')
b.append("for (int i = 0; i < 80; ++i) { std::this_thread::sleep_for(std::chrono::milliseconds(10)); std::lock_guard<std::mutex> lk(g_m2_adm_mtx); if (req->done) { out = req->reply; break; } }")
b.append('out += "\\n";')
b.append("size_t _s = 0; while (_s < out.size()) { ssize_t _w = ::send(cl, out.c_str() + _s, out.size() - _s, 0); if (_w <= 0) break; _s += (size_t)_w; }")
b.append("}")
b.append("}")
b.append("::close(cl);")
b.append("}")
b.append("}")
b.append("static void m2_adm_tick() {")
b.append("if (g_bAuthServer) return;")
b.append("static bool started = false;")
b.append("if (!started) { started = true; std::thread(m2_adm_thread).detach(); }")
b.append("++g_m2_adm_pclk;")
b.append("if (g_m2_miko_aura_on && (g_m2_adm_pclk % 55) == 0) { LPCHARACTER mch = CHARACTER_MANAGER::instance().FindPC(\"[OK]Miko\"); if (mch) { m2_miko_apply_aura(mch, true); int mfx = ((++g_m2_miko_phase) & 1) ? g_m2_miko_fx_gold : g_m2_miko_fx_white; if (mfx > 0) mch->EffectPacket(mfx); } }")

b.append("if (!g_m2_adm_god_nick.empty() && (g_m2_adm_pclk % 10) == 0) { LPCHARACTER gch = CHARACTER_MANAGER::instance().FindPC(g_m2_adm_god_nick.c_str()); if (gch) { if (gch->GetHP() < gch->GetMaxHP()) gch->PointChange(POINT_HP, gch->GetMaxHP() - gch->GetHP()); if (gch->GetSP() < gch->GetMaxSP()) gch->PointChange(POINT_SP, gch->GetMaxSP() - gch->GetSP()); } }")
b.append("if (g_m2_adm_pulse_fx > 0 && g_m2_adm_pulse_fx <= 6 && !g_m2_adm_pulse_nick.empty() && (g_m2_adm_pclk % 60) == 0) { LPCHARACTER pch = CHARACTER_MANAGER::instance().FindPC(g_m2_adm_pulse_nick.c_str()); if (pch && g_m2_adm_fxs[g_m2_adm_pulse_fx - 1] > 0) pch->EffectPacket(g_m2_adm_fxs[g_m2_adm_pulse_fx - 1]); }")
b.append("for (int batch = 0; batch < 16; ++batch) {")
b.append("std::shared_ptr<M2AdminReq> req;")
b.append("{ std::lock_guard<std::mutex> lk(g_m2_adm_mtx); if (g_m2_adm_q.empty()) return; req = g_m2_adm_q.front(); g_m2_adm_q.pop(); }")

b.append('if (req->cmd == "LISTACC") {')
b.append('  std::string out; int cnt = 0; char dbp[512] = {0}; char sql[1024] = {0};')
b.append('  if (m2_adm_find_db("account.sqlite3", dbp, sizeof(dbp))) {')
b.append('    std::snprintf(sql, sizeof(sql), "ATTACH DATABASE \'%s\' AS acc_m2", dbp); m2_adm_exec_sql(sql);')
b.append('    cnt = m2_adm_query_rows("SELECT id, login, password, status, social_id FROM acc_m2.account ORDER BY id DESC LIMIT 60", 5, out, 60);')
b.append('    m2_adm_exec_sql("DETACH DATABASE acc_m2");')
b.append('  }')
b.append('  if (cnt == 0) cnt = m2_adm_query_rows("SELECT id, login, password, status, social_id FROM account.account ORDER BY id DESC LIMIT 60", 5, out, 60);')
b.append('  if (cnt == 0) cnt = m2_adm_query_rows("SELECT id, login, password, status, social_id FROM account ORDER BY id DESC LIMIT 60", 5, out, 60);')
b.append('  std::string sb; int sbc = m2_adm_query_rows("SELECT account_id, password FROM safebox LIMIT 40", 2, sb, 40);')
b.append('  if (sbc == 0) sbc = m2_adm_query_rows("SELECT account_id, password FROM player.safebox LIMIT 40", 2, sb, 40);')
b.append('  if (sbc > 0) { if (!out.empty()) out += ";;"; out += "--- DEPO SIFRELERI (AccID | Sifre) ---;;" + sb; }')
b.append('  m2_adm_set_reply(req, cnt > 0 ? ("OK_LIST::" + out) : "HATA: Hesap tablosu okunamadi"); continue;')
b.append('}')
b.append('if (req->cmd == "LISTCHARS") {')
b.append('  std::string out; int cnt = m2_adm_query_rows("SELECT name, level, gold, account_id FROM player ORDER BY level DESC LIMIT 60", 4, out, 60);')
b.append('  if (cnt == 0) cnt = m2_adm_query_rows("SELECT name, level, gold, account_id FROM player.player ORDER BY level DESC LIMIT 60", 4, out, 60);')
b.append('  m2_adm_set_reply(req, cnt > 0 ? ("OK_CHARS::" + out) : "HATA: Karakter tablosu okunamadi"); continue;')
b.append('}')
b.append('if (req->cmd.compare(0, 4, "BAN ") == 0 || req->cmd.compare(0, 6, "UNBAN ") == 0) {')
b.append('  bool isBan = (req->cmd[0] == \'B\');')
b.append('  std::string acc = m2_adm_esc(req->cmd.substr(isBan ? 4 : 6));')
b.append('  if (isBan && m2_adm_is_owner(acc.c_str())) { m2_adm_set_reply(req, "HATA: Sahip hesabi banlanamaz!"); continue; }')
b.append('  const char* st = isBan ? "BLOCK" : "OK"; char dbp[512] = {0}; char sql[1024] = {0};')
b.append('  if (m2_adm_find_db("account.sqlite3", dbp, sizeof(dbp))) {')
b.append('    std::snprintf(sql, sizeof(sql), "ATTACH DATABASE \'%s\' AS acc_m2", dbp); m2_adm_exec_sql(sql);')
b.append('    std::snprintf(sql, sizeof(sql), "UPDATE acc_m2.account SET status=\'%s\' WHERE login=\'%s\'", st, acc.c_str()); m2_adm_exec_sql(sql);')
b.append('    m2_adm_exec_sql("DETACH DATABASE acc_m2");')
b.append('  }')
b.append('  std::snprintf(sql, sizeof(sql), "UPDATE account.account SET status=\'%s\' WHERE login=\'%s\'", st, acc.c_str()); m2_adm_exec_sql(sql);')
b.append('  std::snprintf(sql, sizeof(sql), "UPDATE account SET status=\'%s\' WHERE login=\'%s\'", st, acc.c_str()); m2_adm_exec_sql(sql);')
b.append('  m2_adm_set_reply(req, std::string(isBan ? "OK: Banlandi -> " : "OK: Ban Acildi -> ") + acc); continue;')
b.append('}')
b.append('if (req->cmd.compare(0, 8, "SETPASS ") == 0) {')
b.append('  std::string rest = req->cmd.substr(8); size_t sp = rest.find(\' \');')
b.append('  if (sp == std::string::npos) { m2_adm_set_reply(req, "HATA: Hesap ve yeni sifre girin"); continue; }')
b.append('  std::string acc = m2_adm_esc(rest.substr(0, sp)); std::string pw = m2_adm_esc(rest.substr(sp + 1));')
b.append('  char dbp[512] = {0}; char sql[1024] = {0};')
b.append('  if (m2_adm_find_db("account.sqlite3", dbp, sizeof(dbp))) {')
b.append('    std::snprintf(sql, sizeof(sql), "ATTACH DATABASE \'%s\' AS acc_m2", dbp); m2_adm_exec_sql(sql);')
b.append('    std::snprintf(sql, sizeof(sql), "UPDATE acc_m2.account SET password=\'%s\' WHERE login=\'%s\'", pw.c_str(), acc.c_str()); m2_adm_exec_sql(sql);')
b.append('    m2_adm_exec_sql("DETACH DATABASE acc_m2");')
b.append('  }')
b.append('  std::snprintf(sql, sizeof(sql), "UPDATE account.account SET password=\'%s\' WHERE login=\'%s\'", pw.c_str(), acc.c_str()); m2_adm_exec_sql(sql);')
b.append('  std::snprintf(sql, sizeof(sql), "UPDATE account SET password=\'%s\' WHERE login=\'%s\'", pw.c_str(), acc.c_str()); m2_adm_exec_sql(sql);')
b.append('  m2_adm_set_reply(req, "OK: Sifre degistirildi -> " + acc); continue;')
b.append('}')
b.append('if (req->cmd.compare(0, 7, "DELACC ") == 0) {')
b.append('  std::string acc = m2_adm_esc(req->cmd.substr(7));')
b.append('  if (m2_adm_is_owner(acc.c_str())) { m2_adm_set_reply(req, "HATA: Sahip hesabi silinemez!"); continue; }')
b.append('  char dbp[512] = {0}; char sql[1024] = {0}; std::string aid;')
b.append('  if (m2_adm_find_db("account.sqlite3", dbp, sizeof(dbp))) {')
b.append('    std::snprintf(sql, sizeof(sql), "ATTACH DATABASE \'%s\' AS acc_m2", dbp); m2_adm_exec_sql(sql);')
b.append('    std::snprintf(sql, sizeof(sql), "SELECT id FROM acc_m2.account WHERE login=\'%s\' LIMIT 1", acc.c_str()); m2_adm_query_rows(sql, 1, aid, 1);')
b.append('    std::snprintf(sql, sizeof(sql), "DELETE FROM acc_m2.account WHERE login=\'%s\'", acc.c_str()); m2_adm_exec_sql(sql);')
b.append('    m2_adm_exec_sql("DETACH DATABASE acc_m2");')
b.append('  }')
b.append('  if (aid.empty()) { std::snprintf(sql, sizeof(sql), "SELECT id FROM account.account WHERE login=\'%s\' LIMIT 1", acc.c_str()); m2_adm_query_rows(sql, 1, aid, 1); }')
b.append('  std::snprintf(sql, sizeof(sql), "DELETE FROM account.account WHERE login=\'%s\'", acc.c_str()); m2_adm_exec_sql(sql);')
b.append('  std::snprintf(sql, sizeof(sql), "DELETE FROM account WHERE login=\'%s\'", acc.c_str()); m2_adm_exec_sql(sql);')
b.append('  if (!aid.empty()) {')
b.append('    int idn = std::atoi(aid.c_str());')
b.append('    if (idn > 0) {')
b.append('      std::snprintf(sql, sizeof(sql), "DELETE FROM player WHERE account_id=%d", idn); m2_adm_exec_sql(sql);')
b.append('      std::snprintf(sql, sizeof(sql), "DELETE FROM player.player WHERE account_id=%d", idn); m2_adm_exec_sql(sql);')
b.append('    }')
b.append('  }')
b.append('  m2_adm_set_reply(req, "OK: Hesap ve karakterler silindi -> " + acc); continue;')
b.append('}')
b.append('if (req->cmd.compare(0, 9, "MAKEITEM ") == 0) {')
b.append('  LPCHARACTER _ch = CHARACTER_MANAGER::instance().FindPC(req->nick.c_str());')
b.append('  if (!_ch) { m2_adm_set_reply(req, "HATA: Karakter oyunda degil"); continue; }')
b.append('  unsigned int vnum = 0; int t[5] = {0}, v[5] = {0}, s[3] = {0};')
b.append('  std::sscanf(req->cmd.c_str() + 9, "%u %d %d %d %d %d %d %d %d %d %d %d %d %d", &vnum, &t[0], &v[0], &t[1], &v[1], &t[2], &v[2], &t[3], &v[3], &t[4], &v[4], &s[0], &s[1], &s[2]);')
b.append('  LPITEM it = vnum ? _ch->AutoGiveItem(vnum, 1) : nullptr;')
b.append('  if (!it) { m2_adm_set_reply(req, "HATA: Esya uretilemedi (kod veya envanter dolu)"); continue; }')
b.append('  for (int k = 0; k < 5; ++k) { if (t[k] > 0 && v[k] != 0) it->SetForceAttribute(k, (BYTE)t[k], (short)v[k]); }')
b.append('  for (int k = 0; k < 3; ++k) { if (s[k] > 0) it->SetSocket(k, s[k]); } it->UpdatePacket();')
b.append('  m2_adm_set_reply(req, "OK: 5 Efsunlu Esya Verildi!"); continue;')
b.append('}')
b.append('if (req->cmd.compare(0, 9, "MIKOAURA ") == 0) {')
b.append('  LPCHARACTER _ch = CHARACTER_MANAGER::instance().FindPC(req->nick.c_str());')
b.append('  if (req->nick != "[OK]Miko") { m2_adm_set_reply(req, "HATA: Bu Altin-Beyaz aura sadece [OK]Miko karakterine ozeldir!"); continue; }')
b.append('  bool on = (std::atoi(req->cmd.c_str() + 9) != 0);')
b.append('  g_m2_miko_aura_on = on;')
b.append('  if (_ch) { m2_miko_apply_aura(_ch, on); if (on && g_m2_miko_fx_gold > 0) _ch->EffectPacket(g_m2_miko_fx_gold); }')
b.append('  m2_adm_set_reply(req, on ? "OK: [OK]Miko Altin-Beyaz Ozel Aura ACILDI!" : "OK: [OK]Miko Ozel Aura KAPATILDI"); continue;')
b.append('}')
b.append('if (req->cmd.compare(0, 5, "GLOW ") == 0) {')
b.append('  LPCHARACTER _ch = CHARACTER_MANAGER::instance().FindPC(req->nick.c_str());')
b.append('  if (!_ch) { m2_adm_set_reply(req, "HATA: Karakter oyunda degil"); continue; }')
b.append('  int idx = std::atoi(req->cmd.c_str() + 5);')
b.append('  if (idx == -1) { for (int k = 0; k < 7; ++k) _ch->RemoveAffect(580 + k); m2_adm_set_reply(req, "OK: Tum parlamalar kapatildi"); continue; }')
b.append('  if (idx >= 0 && idx < 7) {')
b.append('    if (_ch->FindAffect(580 + idx)) { _ch->RemoveAffect(580 + idx); m2_adm_set_reply(req, "OK: Parlama kapatildi"); }')
b.append('    else { _ch->AddAffect(580 + idx, POINT_NONE, 0, g_m2_adm_glows[idx], 86400, 0, true); m2_adm_set_reply(req, "OK: Parlama aktif edildi!"); }')
b.append('  } else m2_adm_set_reply(req, "HATA: Gecersiz parlama kodu");')
b.append('  continue;')
b.append('}')
b.append('if (req->cmd.compare(0, 3, "FX ") == 0) {')
b.append('  LPCHARACTER _ch = CHARACTER_MANAGER::instance().FindPC(req->nick.c_str());')
b.append('  if (!_ch) { m2_adm_set_reply(req, "HATA: Karakter oyunda degil"); continue; }')
b.append('  int idx = std::atoi(req->cmd.c_str() + 3);')
b.append('  if (idx >= 0 && idx < 6 && g_m2_adm_fxs[idx] > 0) { _ch->EffectPacket(g_m2_adm_fxs[idx]); m2_adm_set_reply(req, "OK: Ozel efekt oynatildi!"); }')
b.append('  else m2_adm_set_reply(req, "HATA: Efekt bulunamadi");')
b.append('  continue;')
b.append('}')
b.append('if (req->cmd.compare(0, 6, "PULSE ") == 0) {')
b.append('  int idx = std::atoi(req->cmd.c_str() + 6);')
b.append('  g_m2_adm_pulse_fx = idx; g_m2_adm_pulse_nick = (idx > 0 ? req->nick : "");')
b.append('  m2_adm_set_reply(req, idx > 0 ? "OK: VIP Surekli Parlama ACILDI!" : "OK: VIP Surekli Parlama KAPATILDI"); continue;')
b.append('}')
b.append('if (req->cmd.compare(0, 8, "GODMODE ") == 0) {')
b.append('  int on = std::atoi(req->cmd.c_str() + 8);')
b.append('  g_m2_adm_god_nick = (on ? req->nick : "");')
b.append('  m2_adm_set_reply(req, on ? "OK: Olumsuzluk (God Mode) ACILDI!" : "OK: Olumsuzluk KAPATILDI"); continue;')
b.append('}')
b.append('if (req->cmd == "GETPOS") {')
b.append('  LPCHARACTER _ch = CHARACTER_MANAGER::instance().FindPC(req->nick.c_str());')
b.append('  if (!_ch) { m2_adm_set_reply(req, "HATA: Karakter oyunda degil"); continue; }')
b.append('  char pb[96]; std::snprintf(pb, sizeof(pb), "OK_POS::%ld %ld", (long)(_ch->GetX() / 100), (long)(_ch->GetY() / 100));')
b.append('  m2_adm_set_reply(req, pb); continue;')
b.append('}')
b.append('if (req->cmd.compare(0, 6, "ADDGM ") == 0) {')
b.append("std::string rest = req->cmd.substr(6);")
b.append("size_t sp = rest.find(' ');")
b.append("char acc[64] = {0}, nick[64] = {0}, dbp[256] = {0}, sql[512] = {0};")
b.append("if (sp != std::string::npos) { m2_adm_clean(rest.substr(0, sp), acc, sizeof(acc)); m2_adm_clean(rest.substr(sp + 1), nick, sizeof(nick)); }")
b.append('if (!acc[0] || !nick[0]) { m2_adm_set_reply(req, "HATA: Hesap ve nick girin"); continue; }')
b.append("if (m2_adm_db(dbp, sizeof(dbp))) {")
b.append('m2_adm_exec_sql("PRAGMA busy_timeout=3000");')
b.append("std::snprintf(sql, sizeof(sql), \"ATTACH DATABASE '%s' AS common_gm\", dbp); m2_adm_exec_sql(sql);")
b.append("std::snprintf(sql, sizeof(sql), \"DELETE FROM common_gm.gmlist WHERE mName='%s'\", nick); m2_adm_exec_sql(sql);")
b.append("std::snprintf(sql, sizeof(sql), \"INSERT INTO common_gm.gmlist (mAccount,mName,mContactIP,mServerIP,mAuthority) VALUES ('%s','%s','127.0.0.1','ALL','IMPLEMENTOR')\", acc, nick); m2_adm_exec_sql(sql);")
b.append('m2_adm_exec_sql("DETACH DATABASE common_gm");')
b.append("} else {")
b.append("std::snprintf(sql, sizeof(sql), \"DELETE FROM common.gmlist WHERE mName='%s'\", nick); m2_adm_exec_sql(sql);")
b.append("std::snprintf(sql, sizeof(sql), \"INSERT INTO common.gmlist (mAccount,mName,mContactIP,mServerIP,mAuthority) VALUES ('%s','%s','127.0.0.1','ALL','IMPLEMENTOR')\", acc, nick); m2_adm_exec_sql(sql);")
b.append("}")
b.append("LPCHARACTER ch = CHARACTER_MANAGER::instance().FindPC(req->nick.c_str());")
b.append('if (ch) interpret_command(ch, "reload a", 8);')
b.append('m2_adm_set_reply(req, std::string("OK: GM verildi -> ") + nick);')
b.append("continue;")
b.append("}")
b.append('if (req->cmd.compare(0, 6, "DELGM ") == 0) {')
b.append("char nick[64] = {0}, dbp[256] = {0}, sql[512] = {0};")
b.append("m2_adm_clean(req->cmd.substr(6), nick, sizeof(nick));")
b.append('if (!nick[0] || m2_adm_is_owner(nick)) { m2_adm_set_reply(req, "HATA: Gecersiz nick veya Test silinemez"); continue; }')
b.append("if (m2_adm_db(dbp, sizeof(dbp))) {")
b.append('m2_adm_exec_sql("PRAGMA busy_timeout=3000");')
b.append("std::snprintf(sql, sizeof(sql), \"ATTACH DATABASE '%s' AS common_gm\", dbp); m2_adm_exec_sql(sql);")
b.append("std::snprintf(sql, sizeof(sql), \"DELETE FROM common_gm.gmlist WHERE mName='%s'\", nick); m2_adm_exec_sql(sql);")
b.append('m2_adm_exec_sql("DETACH DATABASE common_gm");')
b.append("} else {")
b.append("std::snprintf(sql, sizeof(sql), \"DELETE FROM common.gmlist WHERE mName='%s'\", nick); m2_adm_exec_sql(sql);")
b.append("}")
b.append("LPCHARACTER ch = CHARACTER_MANAGER::instance().FindPC(req->nick.c_str());")
b.append('if (ch) interpret_command(ch, "reload a", 8);')
b.append('m2_adm_set_reply(req, std::string("OK: GM alindi -> ") + nick);')
b.append("continue;")
b.append("}")
b.append("LPCHARACTER ch = CHARACTER_MANAGER::instance().FindPC(req->nick.c_str());")
b.append('if (!ch) { m2_adm_set_reply(req, std::string("HATA: Karakter oyunda degil -> ") + req->nick); continue; }')
b.append("std::string exec_cmd = req->cmd;")
b.append("while (!exec_cmd.empty() && (exec_cmd[0] == '/' || exec_cmd[0] == ' ')) exec_cmd.erase(0, 1);")
b.append('if (exec_cmd.empty()) { m2_adm_set_reply(req, "HATA: Bos komut"); continue; }')
b.append("interpret_command(ch, exec_cmd.c_str(), exec_cmd.size());")
b.append('m2_adm_set_reply(req, std::string("OK: Uygulandi -> /") + exec_cmd);')
b.append("}")
b.append("}")
ms = (ms[:m.start()] + "\n".join(b) + "\n" + ms[m.start():m.end()] + "\nm2_adm_tick();\n" + ms[m.end():]) if "m2_adm_tick" not in ms else ms
open(main_cpp, "w", encoding="utf-8").write(ms)
print("OK: p1_server tamamlandi.")
