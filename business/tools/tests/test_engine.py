"""Offline checks for council.py and visibility.py. Run through tests/run_all.py."""
import contextlib
import csv
import io
import json
import os
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import council as C  # noqa: E402
import visibility as V  # noqa: E402

SP = Path(os.environ["T"])
V.DATA = SP / "data"
calls = []


def run_main(mod, argv):
    sys.argv = ["x", *argv]
    try:
        mod.main()
        return 0
    except SystemExit as e:
        return e.code


def ok(c, msg):
    print(("PASS " if c else "FAIL ") + msg)


# ---- who counts as "named"
T = V.Target("Denver Roofing Company", "denverroofingco.com")
ok(T.mention("For Denver roofing, the top picks are Acme and Beta.", ["Acme", "Beta"]) == "no", "'Denver roofing' doesn't match Denver Roofing Company")
T = V.Target("Acme Software, Inc.", "acmesoftware.com")
ok(T.mention("Top: Acme, HubSpot and Jobber.", ["Acme", "HubSpot", "Jobber"]) == "yes", "extracted 'Acme' matches Acme Software, Inc.")
ok(T.mention("Top: Acme, HubSpot and Jobber.", []) == "maybe", "short name alone -> maybe (never claimed)")
T = V.Target("Box", "box.com")
ok(T.mention("Use dropbox.com or github.com", []) == "no", "box.com not matched inside dropbox.com")
ok(T.mention("Try www.box.com today", []) == "yes", "www.box.com matched")
T = V.Target("Close", "close.com")
ok(T.mention("Pick something close to your budget.", []) == "no", "'Close' not matched by 'close to'")
ok(V.clean_company("The Limited") == "The Limited", "'The Limited' kept")
ok(V.clean_company("Acme Software, Inc.") == "Acme Software", "legal suffix removed")
ok(V.norm_domain("https://www.AcmeHVAC.com/x?utm_source=openai") == "acmehvac.com", "norm_domain strips www, path, query")
C.available = lambda: {"claude": "missing", "chatgpt": "missing", "gemini": "missing", "perplexity": "missing", "local": "ready"}
b = V.extract_brands("Top picks: Jobber and HubSpot CRM.", "local")
ok(b is not None and "Invented Corp" not in b and "Jobber" in b, f"brand not in the answer is dropped: {b}")

# ---- aggregation
T = V.Target("Acme Dispatch", "acmedispatch.com")
rows = [{"failed": False, "engine": "chatgpt", "question": "q", "mention": "yes", "mentioned": True, "brands": ["HubSpot", "Jobber"], "sources": ["https://g2.com/a?x=1"], "brands_failed": False},
        {"failed": False, "engine": "chatgpt", "question": "q", "mention": "no", "mentioned": False, "brands": ["HubSpot CRM", "Acme Dispatch"], "sources": ["https://www.g2.com/b"], "brands_failed": False}]
agg = V.aggregate(rows, T)
you = [b for b in agg["top_brands"] if b["is_you"]][0]
hub = [b for b in agg["top_brands"] if V.name_key(b["name"]) == "hubspot"]
ok(you["answers"] == agg["mentioned"] == 1, "(you) row equals the headline count")
ok(len(hub) == 1 and hub[0]["answers"] == 2, f"name variants merged: {hub}")
ok(agg["top_sources"] == [{"domain": "g2.com", "answers": 2}], f"cited sites normalized: {agg['top_sources']}")


# ---- snapshot runs against stand-in engines
def fake(engine):
    def f(q):
        calls.append(engine)
        if os.environ.get("ALLFAIL"):
            raise RuntimeError("401 bad key")
        return "Top picks: Jobber, ServiceTitan and Housecall Pro. Arrow → ok", ["https://www.g2.com/x?utm=1"]
    return f


V.ENGINES = {e: fake(e) for e in ("chatgpt", "gemini", "perplexity", "claude")}
V.fetch_site = lambda d: {"ok": True, "title": "t " + d, "description": "", "headings": [], "text": ""}
for k in ("OPENAI_API_KEY", "GEMINI_API_KEY", "PERPLEXITY_API_KEY"):
    os.environ[k] = "test"

calls.clear()
code = run_main(V, ["snapshot", "--brand", "Acme Dispatch", "--domain", "acmedispatch.com", "--compare", "nope/raw.json", "--out", str(SP / "r0")])
ok(code and len(calls) == 0, "bad --compare stops before any paid call")

calls.clear()
code = run_main(V, ["snapshot", "--brand", "Acme Dispatch", "--domain", "acmedispatch.com", "--n", "2", "--out", str(SP / "r1")])
ok(code == 0 and (SP / "r1/report.html").exists(), f"bad findings JSON doesn't crash after the paid run (code={code})")
html = (SP / "r1/report.html").read_bytes().decode("utf-8")
ok("&middot;" in html or "·" in html, "report written as UTF-8")
raw = json.loads((SP / "r1/raw.json").read_text(encoding="utf-8"))
ok(raw["meta"]["runs"] == 2 and len(raw["rows"]) == 2 * 3 * 2, "default snapshot asks each question twice")

os.environ["ALLFAIL"] = "1"
calls.clear()
code = run_main(V, ["snapshot", "--brand", "Acme Dispatch", "--domain", "acmedispatch.com", "--n", "2", "--out", str(SP / "r2")])
ok(code not in (0, None) and not (SP / "r2/report.html").exists(), "a run where every call fails writes no report")
del os.environ["ALLFAIL"]

C.available = lambda: {"claude": "missing", "chatgpt": "ready", "gemini": "missing", "perplexity": "missing", "local": "disabled"}
(SP / "q.txt").write_text("\n".join(f"Q{i}?" for i in range(12)), encoding="utf-8")
calls.clear()
with contextlib.redirect_stderr(io.StringIO()):
    code = run_main(V, ["snapshot", "--brand", "Acme Dispatch", "--domain", "acmedispatch.com", "--questions", str(SP / "q.txt"), "--runs", "3", "--out", str(SP / "r3")])
ok(code == V.COST_GUARD_EXIT and len(calls) == 0, "cost guard counts extraction calls and stops before spending (exit 3)")
C.available = lambda: {"claude": "missing", "chatgpt": "missing", "gemini": "missing", "perplexity": "missing", "local": "ready"}

# ---- lead pipeline on messy input
(SP / "leads.csv").write_text("first name,email,company,website\nA,a@x.com,Acme Plumbing,facebook.com/acmeplumbingerie\nB,b@x.com,Beta Roofing,https://facebook.com/BetaRoofingPA\nC,c@x.com,BadCo,badjson.com\nD,d@x.com,StrCo,strcomp.com\nE,e@x.com,Short\n", encoding="utf-8")
V.fetch_site = lambda d: {"ok": True, "title": d, "description": "", "headings": [], "text": ""}
code = run_main(V, ["enrich", "--in", str(SP / "leads.csv"), "--out", str(SP / "l1.csv")])
st = {r["company"]: r.get("enrich_status") for r in csv.DictReader(open(SP / "l1.csv", encoding="utf-8"))}
ok(code == 0, "enrich survives messy input")
ok(st["Acme Plumbing"].startswith("no own website") and st["Beta Roofing"].startswith("no own website"), "Facebook-page leads flagged, not merged")
ok(st["BadCo"] == "model error" and st["StrCo"] == "model error", "invalid model JSON -> 'model error', no crash")
ok(st["Short"] == "no website", "short row -> 'no website'")

(SP / "p.csv").write_text("first name,email,company,website,buyer_question,domain\nD,d@a.com,\"Acme Software, Inc.\",acmesoftware.com,Best tools?,acmesoftware.com\n", encoding="utf-8")
V.ENGINES["chatgpt"] = lambda q: ("Try Acme, HubSpot and Jobber.", [])
run_main(V, ["probe", "--in", str(SP / "p.csv"), "--out", str(SP / "p2.csv"), "--engine", "chatgpt"])
r = list(csv.DictReader(open(SP / "p2.csv", encoding="utf-8")))[0]
ok(r["mentioned"] == "yes" and r["probe_runs"] == "2" and r["probe_answer"].startswith("Try Acme"), "probe: 2 runs, answer saved, 'Acme' counts")
ok("Acme" not in (r["named_1"], r["named_2"]), "a company is never listed as its own competitor")
(SP / "p3.csv").write_text("first name,email,company,website,buyer_question,domain\nD,d@a.com,Zeta Labs,zeta.io,Best tools?,zeta.io\n", encoding="utf-8")
V.ENGINES["chatgpt"] = lambda q: ("Try Jobber, HubSpot and ServiceTitan.", [])
run_main(V, ["probe", "--in", str(SP / "p3.csv"), "--out", str(SP / "p4.csv"), "--engine", "chatgpt"])
run_main(V, ["firstline", "--in", str(SP / "p4.csv"), "--out", str(SP / "p5.csv")])
r = list(csv.DictReader(open(SP / "p5.csv", encoding="utf-8")))[0]
ok("Invented Corp" not in r["first_line"] and r["segment"] == "not_named" and "It named" in r["first_line"], f"first line uses only names from the real answer: {r['first_line']}")

# ---- council bulk
prompt = str(TOOLS / "prompts" / "classify_reply.txt")
(SP / "day1.csv").write_text("first_name,company,reply_text\nAnna,A,please remove me\nBob,B,what does it cost\n", encoding="utf-8")
run_main(C, ["bulk", "--in", str(SP / "day1.csv"), "--prompt", prompt, "--out", str(SP / "tagged.csv"), "--column", "label"])
(SP / "day2.csv").write_text("first_name,company,reply_text\nCara,C,sure send it\nDan,D,send the report\nEve,E,FAILME\n", encoding="utf-8")
run_main(C, ["bulk", "--in", str(SP / "day2.csv"), "--prompt", prompt, "--out", str(SP / "tagged.csv"), "--column", "label"])
lab = {r["first_name"]: r["label"] for r in csv.DictReader(open(SP / "tagged.csv", encoding="utf-8"))}
ok(lab["Cara"] == "yes" and lab["Dan"] == "yes", f"new day's rows never get old labels: {lab}")
ok(lab["Eve"] == "", "a failed row is left empty for retry, never filled with error text")
(SP / "bad.csv").write_text("First Name,Company,Reply\nX,Y,hi\n", encoding="utf-8")
code = run_main(C, ["bulk", "--in", str(SP / "bad.csv"), "--prompt", prompt, "--out", str(SP / "bad-out.csv"), "--column", "label"])
ok(code and "first_name" in str(code), "bulk refuses when CSV columns don't match the prompt")
print("done")
