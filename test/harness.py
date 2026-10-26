"""Local dry-run harness for the blindspot Skill.

Stands in for the NAS experts with local tools (tesseract OCR, pdftotext, sha256)
so the Skill's orchestration logic (vectors, evidence format, verification,
severity rubric, house rules, empty/failed handling, re-run diff) can be exercised.
It does NOT prove runtime behaviour on UGOS; real experts use UGREEN's own AI.
"""
import hashlib, json, os, re, shutil, subprocess, sys, datetime as dt

TODAY = dt.date(2026, 10, 24)
IMG = (".png", ".jpg", ".jpeg")

# ---------- simulated experts ----------
def ocr(p):
    return subprocess.run(["tesseract", p, "-", "--psm", "6"], capture_output=True, text=True).stdout

def pdftext(p):
    return subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True).stdout

def mask_secret(s):
    s = s.strip(); return s[:2] + "******" + s[-2:]

def mask_num(s):
    return "*" * max(4, len(s) - 4) + s[-4:]

def walk(scope):
    out = []
    for root, _, files in os.walk(scope):
        for f in files: out.append(os.path.join(root, f))
    return sorted(out)

def file_agent_inventory(scopes):
    res = {}
    for s in scopes:
        if not os.path.isdir(s):
            res[s] = {"status": "inaccessible"}; continue
        fs = walk(s)
        if not fs:
            res[s] = {"status": "empty"}; continue
        cats = {}
        for f in fs:
            ext = os.path.splitext(f)[1].lower()
            c = "images" if ext in IMG else "documents" if ext == ".pdf" else "other"
            cats.setdefault(c, [0, 0]); cats[c][0] += 1; cats[c][1] += os.path.getsize(f)
        res[s] = {"status": "ok", "files": len(fs), "bytes": sum(os.path.getsize(f) for f in fs), "by_category": cats}
    return res

SECRET_RULES = [
    ("crypto recovery phrase", r"(recovery|seed)\s*phrase", "phrase"),
    ("Wi-Fi password", r"wi-?fi[\s\S]*password\s*:\s*(\S+)", "pw"),
    ("password", r"password\s*:\s*(\S+)", "pw"),
    ("one-time code", r"\b(otp|verification code)\b\D*(\d{4,8})", "code"),
]

def photo_agent_v1(scopes):
    hits = []
    for s in scopes:
        for f in walk(s):
            if not f.lower().endswith(IMG): continue
            t = ocr(f)
            for kind, rx, mode in SECRET_RULES:
                m = re.search(rx, t, re.I)
                if not m: continue
                if mode == "phrase":
                    words = re.findall(r"\b[a-z]{3,}\b", t.split(m.group(0))[-1])
                    excerpt = f"{len(words)}-word phrase" if len(words) >= 12 else None
                    if not excerpt: continue
                else:
                    excerpt = mask_secret(m.group(m.lastindex))
                hits.append({"file": f, "what": kind, "evidence": excerpt, "date": dt.date.fromtimestamp(os.path.getmtime(f)).isoformat()})
                break
    return hits

ID_RULES = [("passport", r"\bpassport\b", r"passport\s*no\W*([A-Z0-9]{6,})"),
            ("national ID card", r"identity card|\bNIN\b", r"NIN\W*(\d{6,})"),
            ("bank statement", r"bank statement", r"account\s*(?:no|number)\W*(\d{6,})")]

def classify_id(text):
    for kind, rx, numrx in ID_RULES:
        if re.search(rx, text, re.I):
            n = re.search(numrx, text, re.I)
            exp = re.search(r"expiry\W*([0-9]{1,2} [A-Z]{3} \d{4})", text, re.I)
            return kind, (mask_num(n.group(1)) if n else None), (exp.group(1) if exp else None)
    return None

def v2_identity(scopes, include_photos=True):
    hits = []
    for s in scopes:
        for f in walk(s):
            if f.lower().endswith(".pdf"): t = pdftext(f)
            elif include_photos and f.lower().endswith(IMG): t = ocr(f)
            else: continue
            c = classify_id(t)
            if c: hits.append({"file": f, "what": c[0], "evidence": f"number {c[1]}" + (f", expires {c[2]}" if c[2] else ""), "date": c[2] or ""})
    return hits

MONTHS = {m: i for i, m in enumerate(["january","february","march","april","may","june","july","august","september","october","november","december"], 1)}
def pdate(s):
    d, m, y = s.split(); return dt.date(int(y), MONTHS[m.lower()], int(d))
DATE = r"(\d{1,2} [A-Z][a-z]+ \d{4})"

def orig_key(f): return ("copy" in os.path.basename(f).lower(), os.path.getmtime(f), f)
def docs(scopes):
    return [(f, pdftext(f)) for f in sorted((f for s in scopes for f in walk(s) if f.lower().endswith(".pdf")), key=orig_key)]

def v3_contracts(scopes):
    hits = []
    for f, t in docs(scopes):
        if not re.search(r"agreement|lease|contract", t, re.I) or re.search(r"\binvoice\b", t, re.I): continue
        flat = " ".join(t.split())
        end = re.search(r"End date:\s*" + DATE, flat)
        if not end: continue
        end = pdate(end.group(1))
        auto = bool(re.search(r"renews automatically", flat, re.I))
        notice = re.search(r"at least (\d+) days", flat)
        deadline = end - dt.timedelta(days=int(notice.group(1))) if (auto and notice) else end
        newp = re.search(r"rent of (NGN [\d,]+)", flat)
        rec = {"file": f, "end": end.isoformat(), "auto_renew": auto, "deadline": deadline.isoformat()}
        days = (deadline - TODAY).days
        if days <= 90:
            what = f"auto-renews {end.isoformat()}" + (f" at {newp.group(1)}/month" if newp else "") if auto else f"ends {end.isoformat()}"
            hits.append({"file": f, "what": what, "evidence": f"notice deadline {deadline.isoformat()} ({days} days left)" if auto else f"{days} days left", "date": deadline.isoformat(), "days": days})
    return hits

def amount(s): return int(s.replace(",", ""))

def v4_money(scopes):
    ds = docs(scopes); hits = []
    contracts = {}
    for f, t in ds:
        flat = " ".join(t.split())
        if re.search(r"agreement|lease", flat, re.I) and not re.search(r"\binvoice\b", flat, re.I):
            party = re.search(r"(?:Landlord|Provider):\s*([A-Z][\w ]+?Ltd)", flat)
            amt = re.search(r"(?:Monthly rent|Monthly fee):\s*NGN ([\d,]+)", flat)
            if party and amt: contracts[party.group(1)] = (f, amount(amt.group(1)))
    seen = {}
    for f, t in ds:
        flat = " ".join(t.split())
        m = re.search(r"Invoice (\S+) From:\s*([A-Z][\w ]+?Ltd)", flat)
        if not m: continue
        num, party = m.groups(); total = amount(re.search(r"Total due: NGN ([\d,]+)", flat).group(1))
        key = (num, total)
        if key in seen:
            hits.append({"file": f, "what": f"duplicate invoice {num}", "evidence": f"same number and amount as {os.path.basename(seen[key])}", "date": ""}); continue
        seen[key] = f
        if party not in contracts:
            hits.append({"file": f, "what": "invoice with no matching contract", "evidence": party, "date": ""}); continue
        cf, expected = contracts[party]
        if total != expected:
            hits.append({"file": f, "what": f"overcharge vs {os.path.basename(cf)}", "evidence": f"expected NGN {expected:,}, invoiced NGN {total:,}", "date": "", "delta": total - expected})
    return hits

def v5_dupes(scopes):
    groups = {}
    for s in scopes:
        for f in walk(s):
            groups.setdefault(hashlib.sha256(open(f, "rb").read()).hexdigest(), []).append(f)
    for g in groups.values(): g.sort(key=orig_key)
    out = []
    for g in groups.values():
        if len(g) > 1:
            sz = os.path.getsize(g[0]); out.append({"files": g, "size": sz, "recoverable": sz * (len(g) - 1)})
    return out

# ---------- skill logic under test ----------
def severity(v, h, vault):
    if v == "V1" and vault and h["file"].startswith(vault): return "Low"
    if v == "V1": return "Critical" if "recovery phrase" in h["what"] or "card" in h["what"] else "High"
    if v == "V2": return "Info" if vault and h["file"].startswith(vault) else "High"
    if v in ("V3", "V4"): return "Medium"
    return "Low"

def verify(v, h):
    """Step 4: second focused read of the single file."""
    if not os.path.exists(h["file"]): return False, "file missing"
    if v == "V1":
        t = ocr(h["file"]); ok = any(re.search(rx, t, re.I) for _, rx, _ in SECRET_RULES)
    else:
        t = ocr(h["file"]) if h["file"].lower().endswith(IMG) else pdftext(h["file"]); ok = classify_id(t) is not None
    return ok, ("confirmed" if ok else "not confirmed")

def run(scopes, vectors=("V1","V2","V3","V4","V5"), vault=None, house_rules=(), fail=(), previous=None, label="run"):
    log = {"label": label, "states": {}}
    inv = file_agent_inventory(scopes)
    live = [s for s, r in inv.items() if r["status"] == "ok"]
    if not live:
        log["result"] = "STOP: no files found in scope (" + ", ".join(f"{s}: {r['status']}" for s, r in inv.items()) + "). Nothing changed."
        return log, None
    agents = {"V1": lambda: photo_agent_v1(live), "V2": lambda: v2_identity(live), "V3": lambda: v3_contracts(live), "V4": lambda: v4_money(live), "V5": lambda: v5_dupes(live)}
    findings, not_audited, unverified = [], [], []
    for v in vectors:
        if v in fail:
            log["states"][v] = "failed"; not_audited.append(v); continue
        res = agents[v](); log["states"][v] = "completed" + ("" if res else " (empty result)")
        if v == "V5":
            v4files = {f["file"] for f in findings if f["v"] == "V4" and "duplicate" in f["what"]}
            for g in res:
                if any(x in v4files for x in g["files"]):
                    for f in findings:
                        if f["file"] in g["files"] and "duplicate" in f["what"]: f["evidence"] += f"; {g['recoverable']/1024:.0f} KB recoverable"; f["rec"] = g["recoverable"]
                    continue
                findings.append({"v": v, "sev": "Low", "file": g["files"][0], "what": f"{len(g['files'])} identical copies", "evidence": f"{g['recoverable']/1024:.0f} KB recoverable; copies: " + ", ".join(os.path.relpath(x, live[0]) for x in g["files"][1:]), "pass": "single-pass", "rec": g["recoverable"]})
            continue
        for h in res:
            sev = severity(v, h, vault)
            f = {"v": v, "sev": sev, **h, "pass": "single-pass"}
            if sev in ("Critical", "High"):
                ok, why = verify(v, h)
                if not ok: unverified.append((h["file"], why)); continue
                f["pass"] = "verified"
            findings.append(f)
    order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}
    findings.sort(key=lambda f: (order[f["sev"]], f["pass"] != "verified", f.get("days", 9999), -f.get("rec", 0)))
    counters = {}
    for f in findings:
        counters[f["v"]] = counters.get(f["v"], 0) + 1; f["id"] = f"{f['v']}-{counters[f['v']]:02d}"
    rules = []
    for r in house_rules:
        if r == "ID scans live only in Vault":
            if "V2" not in log["states"] or log["states"]["V2"] == "failed": rules.append((r, "Not checked"))
            else:
                b = [f["id"] for f in findings if f["v"] == "V2" and f["sev"] != "Info"]; rules.append((r, "Broken (" + ", ".join(b) + ")" if b else "Holding"))
        elif r == "No screenshots of passwords":
            if log["states"].get("V1", "failed") == "failed": rules.append((r, "Not checked"))
            else:
                b = [f["id"] for f in findings if f["v"] == "V1"]; rules.append((r, "Broken (" + ", ".join(b) + ")" if b else "Holding"))
    return log, {"scopes": scopes, "inv": inv, "findings": findings, "not_audited": not_audited, "unverified": unverified, "rules": rules, "previous": previous}

def report(r):
    base = r["scopes"][0]
    c = {}
    for f in r["findings"]: c[f["sev"]] = c.get(f["sev"], 0) + 1
    rec = sum(f.get("rec", 0) for f in r["findings"])
    L = [f"# Blindspot report — {TODAY.isoformat()}", f"Scope: {', '.join(os.path.basename(s) or s for s in r['scopes'])}", "",
         "**Verdict:** " + ", ".join(f"{c[k]} {k}" for k in ["Critical","High","Medium","Low","Info"] if k in c) + f". {rec/1024:.0f} KB recoverable.", "",
         "| ID | Severity | File | Found | Evidence | Pass |", "|---|---|---|---|---|---|"]
    for f in r["findings"]:
        L.append(f"| {f['id']} | {f['sev']} | {os.path.relpath(f['file'], base)} | {f['what']} | {f['evidence']} | {f['pass']} |")
    if r["rules"]:
        L += ["", "**House rules**"] + [f"- {a}: {b}" for a, b in r["rules"]]
    if r["not_audited"]: L += ["", "**Not audited:** " + ", ".join(r["not_audited"]) + " (expert returned failed)"]
    if r["unverified"]: L += ["", "**Could not verify:** " + "; ".join(f"{os.path.relpath(a, base)} ({b})" for a, b in r["unverified"])]
    if r["previous"] is not None:
        key = lambda f: (f["v"], os.path.basename(f["file"]), f["what"])
        order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}
        prev = {key(f): f for f in r["previous"]}; cur = {key(f): f for f in r["findings"]}
        down = [f"{cur[k]['id']} ({prev[k]['sev']} to {cur[k]['sev']})" for k in cur if k in prev and order[cur[k]["sev"]] > order[prev[k]["sev"]]]
        still = [cur[k]["id"] for k in cur if k in prev and cur[k]["sev"] == prev[k]["sev"]]
        L += ["", "**Since last scan**",
              "- New: " + (", ".join(cur[k]["id"] for k in cur if k not in prev) or "none"),
              "- Resolved: " + (", ".join(prev[k]["id"] for k in prev if k not in cur) or "none"),
              "- Downgraded: " + (", ".join(down) or "none"),
              "- Still open: " + (", ".join(still) or "none")]
    return "\n".join(L)
