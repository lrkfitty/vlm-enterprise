"""
Vercel serverless function — handles booking form submission.
POST /api/book
"""
import os, json, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from http.server import BaseHTTPRequestHandler

SMTP_HOST  = "mail.privateemail.com"
SMTP_PORT  = 587
FROM_ADDR  = "hello@vlmcreateflow.com"
FROM_PASS  = os.getenv("SMTP_HELLO_PASS", "Vlmcreateflow1!")
NOTIFY     = ["tylarkin@vlmcreateflow.com", "virallensemediavlm@gmail.com"]


def _send(subject, body, to, reply_to=None):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = FROM_ADDR
    msg["To"]      = to
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.attach(MIMEText(body, "plain"))
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(FROM_ADDR, FROM_PASS)
        s.sendmail(FROM_ADDR, to, msg.as_string())


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = json.loads(self.rfile.read(length))

        name         = body.get("name", "")
        email        = body.get("email", "")
        company      = body.get("company", "")
        availability = body.get("availability", "")
        message      = body.get("message", "")
        first        = name.split()[0] if name else "there"

        # Notify Ty
        notify_body = f"""New Setup Call Booking — VLM Enterprise

Name:         {name}
Email:        {email}
Company:      {company}
Availability: {availability}
Message:      {message}
Source:       enterprise.vlmcreateflow.com
"""
        subject = f"Setup Call Request — {name} @ {company}"
        for addr in NOTIFY:
            try: _send(subject, notify_body, addr)
            except: pass

        # Confirm to lead
        confirm_body = f"""Hey {first},

Got your request — you're on the list.

I'll reach out within a few hours to confirm a time for your setup call.

On the call we'll:
- Walk through the system live for {company}
- Scope your first use case
- Map your onboarding from day one

If you want to share any brand assets before we talk — existing content, brand guidelines, reference shots — feel free to reply and send them over.

Talk soon.

— Ty
Viral Lense Media
hello@vlmcreateflow.com
"""
        try: _send("Your VLM setup call — confirmed", confirm_body, email)
        except: pass

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
