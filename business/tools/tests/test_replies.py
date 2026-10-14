"""Offline checks for replies.py: the reply buckets and the T1 timing rule. Run through tests/run_all.py."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import replies as R  # noqa: E402

ET = R.ET


def ok(c, msg):
    print(("PASS " if c else "FAIL ") + msg)


ok(R.classify("Sure, send it over.") == "SEND_IT", "send it")
ok(R.classify("No thanks.") == "NO", "'no thanks' beats 'thanks'")
ok(R.classify("Thanks, but not interested") == "NO", "'not interested' beats 'interested'")
ok(R.classify("How much does it cost?") == "PRICE", "price question")
ok(R.classify("Who are you and is this a bot?") == "WHAT", "who-are-you question")
ok(R.classify("Call me at (814) 555-0100") == "CALL", "a phone number is a call")
ok(R.classify("I am out of the office until Monday") == "AUTO", "auto-reply dropped")
ok(R.classify("Not sure. Yes, send it") == "SEND_IT", "'not sure' doesn't hide a yes")
ok(R.classify("x", sender="mailer-daemon@googlemail.com") == "BOUNCE", "bounce by sender")
ok(R.classify("Interesting.\n\nOn Wed, Oct 14, 2026 at 9:02 AM Kaleb wrote:\n> send it?") == "OTHER",
   "quoted 'send it' from our own email is ignored")
ok(R.when(dt.datetime(2026, 10, 14, 11, 0, tzinfo=ET)) == "end of day today", "Wed 11 AM: today")
ok(R.when(dt.datetime(2026, 10, 14, 15, 0, tzinfo=ET)) == "noon tomorrow", "Wed 3 PM: tomorrow")
ok(R.when(dt.datetime(2026, 10, 16, 15, 0, tzinfo=ET)) == "noon Monday", "Fri 3 PM: Monday")
ok(R.when(dt.datetime(2026, 10, 17, 10, 0, tzinfo=ET)) == "noon Monday", "Saturday: Monday")
ok("you'll have it by noon tomorrow" in R.T1.format(first_name="Ari", when="noon tomorrow"), "T1 fills in")
ok(R.own_words("Stop\n\nOn Tue, Sep 29, 2026, 9:37 AM Kaleb Confer <k@example.com>\nwrote:\n> hi") == "Stop",
   "a wrapped 'On ... wrote:' line is stripped")
ok(R.classify("Click the link below to instantly become a trusted sender.") == "AUTO", "challenge-response mail dropped")
ok(R.classify("Interested", sender="noreply@example.com") == "AUTO", "no-reply sender dropped")
ok(R.body_text({"body": {"text": "", "html": "<p>Send <b>it</b></p>"}}) == " Send  it  ", "html body falls back to text")
ok(R.classify("Just send me the fixes, skip the report.") == "FIXES", "'send me the fixes' is FIXES, not SEND_IT")
ok(R.classify("Did you even read my site? This looks like AI.") == "SKEPTIC", "skeptic")
item = {"timestamp_created": "2026-10-14T13:00:00.000Z", "from_address_email": "a@example.com", "subject": "Re: x",
        "body": {"text": "How much?"}, "step": "0_0_0"}
page = R.render(item, "PRICE", {"first_name": "Ari", "company_name": "Acme"}, dt.datetime(2026, 10, 14, 11, 0, tzinfo=ET))
ok("Hi Ari, the check is free" in page and "{" not in page.split("## Send")[1], "PRICE file carries the filled-in draft")
page = R.render(item, "NO", {"first_name": "Ari", "company_name": "Acme"}, dt.datetime(2026, 10, 14, 11, 0, tzinfo=ET))
ok("Nothing to send" in page, "NO file says send nothing")
print("done")
