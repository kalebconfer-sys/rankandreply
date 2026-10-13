"""A stand-in for every AI the tools call (OpenAI-compatible chat API, as Ollama and
Perplexity expose). It answers by recognizing which prompt it received, so the tests
run offline, for free, and give the same result every time.

    python fake_llm.py 11436
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

KNOWN = ["Jobber", "ServiceTitan", "Housecall Pro", "HubSpot CRM", "HubSpot", "Acme", "Acme Dispatch",
         "Denver roofing", "Dropbox"]


def answer(req: dict) -> tuple[str, dict]:
    p = req["messages"][-1]["content"]
    if req.get("search_domain_filter"):  # Perplexity, limited to reddit.com
        assert req["search_domain_filter"] == ["reddit.com"], req
        real = "https://www.reddit.com/r/marketing/comments/2xyz9ab/ai_overviews_killed_our_traffic/"
        return (json.dumps({"threads": [
            {"url": real, "title": "AI overviews killed our traffic", "why": "B2B marketer losing traffic"},
            {"url": "https://www.reddit.com/r/SEO/comments/7fakefake/invented_thread/", "title": "made up", "why": "x"}]}),
            {"search_results": [{"title": "AI overviews killed our traffic", "url": real,
                                 "snippet": "Our B2B site lost 40% of clicks"}]})
    if "List every company" in p:
        ans = p.split("<answer>")[1].split("</answer>")[0].lower()
        return json.dumps({"brands": [k for k in KNOWN if k.lower() in ans] + ["Invented Corp"]}), {}
    if "From this, work out" in p:
        if "badjson" in p:
            return json.dumps({"type": "object", "properties": {"category": {"type": "string"}}}), {}
        if "strcomp" in p:
            return json.dumps({"category": "x", "buyer": "y", "buyer_question": "q?",
                               "competitors": "Erie Air, Smith HVAC", "questions": ["a"]}), {}
        return json.dumps({"category": "field service software", "buyer": "HVAC shops",
                           "buyer_question": "What is the best field service software for a small HVAC company?",
                           "competitors": ["Jobber"], "questions": ["Q1?", "Q2?"]}), {}
    if "findings section" in p:
        return json.dumps({"headline": "h", "summary": "s", "fixes": [{"title": "t", "why": "w"}]}), {}  # no 'how'
    if "You sort replies" in p:
        r = p.split("<reply>")[1].split("</reply>")[0].lower()
        label = "yes" if "send" in r else "no" if ("stop" in r or "remove" in r) else "price" if "cost" in r else "other"
        return label, {}
    if "Classify:" in p:
        buyer = ("ChatGPT" in p or "traffic" in p or "Perplexity" in p or "LLMs" in p) and "pizza" not in p
        return json.dumps({"intent": "buyer" if buyer else "irrelevant", "fit": "high" if buyer else "low",
                           "reason": "test"}), {}
    return "ok", {}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._send({"object": "list", "data": [{"id": "llama3.1:8b", "object": "model", "created": 0, "owned_by": "x"}]})

    def do_POST(self):
        req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if "FAILME" in req["messages"][-1]["content"]:
            return self._send({"error": {"message": "boom"}}, 500)
        text, extra = answer(req)
        self._send({"id": "x", "object": "chat.completion", "created": 0, "model": req["model"],
                    "choices": [{"index": 0, "finish_reason": "stop",
                                 "message": {"role": "assistant", "content": text}}], **extra})


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1])), Handler).serve_forever()
