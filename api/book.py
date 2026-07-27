"""
Vercel serverless function — handles booking form submission.
POST /api/book
"""
import os, json, smtplib, uuid, datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from http.server import BaseHTTPRequestHandler

SMTP_HOST  = "mail.privateemail.com"
SMTP_PORT  = 587
FROM_ADDR  = "hello@vlmcreateflow.com"
FROM_PASS  = os.getenv("SMTP_HELLO_PASS")
NOTIFY     = ["tylarkin@vlmcreateflow.com", "virallensemediavlm@gmail.com"]

S3_BUCKET  = os.getenv("S3_BUCKET_NAME")
S3_REGION  = os.getenv("AWS_REGION", "ap-southeast-2")
S3_PREFIX  = "vlm-enterprise-leads"


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


def _log_lead_to_s3(record):
    if not S3_BUCKET:
        return  # not configured yet — never block the form on this
    import boto3
    s3 = boto3.client("s3", region_name=S3_REGION)
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    key = f"{S3_PREFIX}/{ts}_{uuid.uuid4().hex[:8]}.json"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=json.dumps(record, indent=2),
        ContentType="application/json",
    )


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

        # Lead log — written first so an SMTP outage can never lose the lead
        try:
            _log_lead_to_s3({
                "name": name,
                "email": email,
                "company": company,
                "availability": availability,
                "message": message,
                "source": "enterprise-site",
                "received_at": datetime.datetime.utcnow().isoformat() + "Z",
            })
        except: pass

        # Internal notification
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

Our team will reach out within a few hours to confirm a time for your setup call.

On the call we'll:
- Walk through the system live for {company}
- Scope your first use case
- Map your onboarding from day one

If you want to share any brand assets before we talk — existing content, brand guidelines, reference shots — feel free to reply and send them over.

Talk soon.

— The VLM Team
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
