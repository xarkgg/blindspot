import shutil, os, json, sys
sys.path.insert(0, ".")
from harness import *
SRC = os.path.abspath("fixture-nas/home/xark"); WORK = os.path.abspath("work/xark")
shutil.rmtree("work", ignore_errors=True); shutil.copytree(SRC, WORK)
VAULT = WORK + "/Vault"; RULES = ["ID scans live only in Vault", "No screenshots of passwords"]
out = []
def section(t, body): out.append(f"\n\n========== {t} ==========\n{body}")

# T1 full audit
log, r1 = run([WORK], vault=VAULT, house_rules=RULES, label="T1")
section("T1 full audit", json.dumps(log["states"]) + "\n\n" + report(r1))
# T2 empty + missing folder
log, r = run([WORK + "/Music", WORK + "/DoesNotExist"], label="T2"); section("T2 empty/inaccessible scope", log["result"])
# T3 V4 expert fails
log, r = run([WORK], vault=VAULT, house_rules=RULES, fail=("V4",), label="T3"); section("T3 V4 failed", json.dumps(log["states"]) + "\n" + "\n".join(l for l in report(r).splitlines() if "Not audited" in l or "V4-" in l) )
# T4 verification drops a finding whose file vanished between pass and verify
import harness
orig = harness.verify
def flaky(v, h):
    if "IMG_2290" in h["file"]: return False, "file missing"
    return orig(v, h)
harness.verify = flaky
log, r = run([WORK], vectors=("V1",), label="T4"); harness.verify = orig
section("T4 unverified finding dropped", report(r))
# T5 user approves fixes: move V1/V2 High+ files to Vault, then re-run
for f in r1["findings"]:
    if f["v"] in ("V1","V2") and f["sev"] in ("Critical","High"):
        shutil.move(f["file"], VAULT + "/" + os.path.basename(f["file"]))
log, r5 = run([WORK], vault=VAULT, house_rules=RULES, previous=r1["findings"], label="T5")
section("T5 re-run after approved fixes", report(r5))
open("test-results.md","w").write("".join(out)); print("".join(out))
