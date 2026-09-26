"""Generate the sample PDFs in sample_docs/ (already committed, so you only need
this to regenerate them). Company and content are fictional.

Usage: python -m scripts.make_sample_pdfs
"""
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

OUT = Path(__file__).resolve().parent.parent / "sample_docs"
COMPANY = "Brightwater Analytics"

DOCS: dict[str, tuple[str, list[list[tuple[str, str]]]]] = {
    "brightwater-employee-handbook.pdf": (
        "Employee Handbook",
        [
            [
                ("Welcome", f"This handbook explains how we work at {COMPANY}. It applies to all full-time and "
                 "part-time employees. Contractors should refer to their individual agreements. Where this "
                 "handbook and local employment law differ, local law takes precedence."),
                ("Working hours", "Our core collaboration hours are 10:00 to 15:00 in each employee's local time "
                 "zone. Outside core hours, employees may arrange their schedule freely as long as they work an "
                 "average of 40 hours per week for full-time roles. Meetings should not be scheduled outside "
                 "core hours without the attendee's agreement."),
                ("Probation", "New employees complete a 90-day probation period. During probation, either party "
                 "may end employment with one week of written notice. A review meeting with the line manager "
                 "takes place at day 45 and again at day 85."),
            ],
            [
                ("Paid time off", "Full-time employees receive 25 days of paid time off per calendar year, in "
                 "addition to public holidays. Part-time employees receive a pro-rated amount. Up to 5 unused "
                 "days may be carried over into the first quarter of the following year; any remaining unused "
                 "days expire on 31 March."),
                ("Requesting leave", "Leave requests of three days or more must be submitted in the HR portal at "
                 "least two weeks in advance. Requests shorter than three days need at least two working days "
                 "of notice. Managers should respond to requests within three working days."),
                ("Sick leave", "Employees receive up to 10 days of paid sick leave per year. For absences longer "
                 "than three consecutive days, a doctor's note is required. Please notify your manager before "
                 "10:00 on the first day of absence."),
                ("Parental leave", "Primary caregivers receive 16 weeks of fully paid parental leave. Secondary "
                 "caregivers receive 6 weeks of fully paid leave, which may be taken in up to three blocks "
                 "within the first year."),
            ],
            [
                ("Remote work", "Brightwater is remote-first. Employees may work from any location within their "
                 "country of employment. Working from another country for more than 30 days in a 12-month "
                 "period requires written approval from HR because of tax and legal implications."),
                ("Equipment", "Each new employee receives a laptop and a one-time home office allowance of 600 "
                 "euros for a desk, chair, monitor or similar equipment. Receipts must be submitted within 60 "
                 "days of purchase. Laptops are replaced every three years."),
                ("Expenses", "Business expenses under 50 euros can be claimed with a receipt and do not need "
                 "pre-approval. Expenses of 50 euros or more require manager approval before purchase. Claims "
                 "must be submitted in the finance portal by the fifth working day of the following month."),
                ("Learning budget", "Every employee has an annual learning budget of 1,000 euros for courses, "
                 "books and conferences related to their role, plus up to 5 working days per year for learning."),
            ],
        ],
    ),
    "brightwater-api-reference.pdf": (
        "Public API Reference v2",
        [
            [
                ("Overview", "The Brightwater API gives programmatic access to datasets, reports and scheduled "
                 "jobs. All endpoints are served over HTTPS from https://api.brightwater.example/v2. Requests "
                 "and responses use JSON encoded in UTF-8."),
                ("Authentication", "Authenticate every request with an API key sent in the Authorization header "
                 "using the Bearer scheme. API keys are created in the dashboard under Settings, then API Keys. "
                 "Each key is scoped to one workspace. Keys can be rotated at any time; the old key keeps working "
                 "for 24 hours after rotation so you can deploy the new one without downtime."),
                ("Environments", "Sandbox keys start with bw_test_ and live keys start with bw_live_. Sandbox data "
                 "is reset every Sunday at 02:00 UTC."),
            ],
            [
                ("Rate limits", "The API allows 120 requests per minute per API key on the Standard plan and 600 "
                 "requests per minute on the Enterprise plan. Report exports are additionally limited to 10 "
                 "concurrent jobs per workspace. When a limit is exceeded the API returns HTTP 429 with a "
                 "Retry-After header that states how many seconds to wait."),
                ("Pagination", "List endpoints are paginated with cursors. Pass the limit parameter (maximum 100, "
                 "default 20) and use the next_cursor value from the response to fetch the following page. A "
                 "null next_cursor means there are no more results."),
                ("Idempotency", "POST requests accept an Idempotency-Key header. If a request with the same key "
                 "is received within 24 hours, the original response is returned instead of performing the "
                 "action again."),
            ],
            [
                ("Endpoints", "GET /datasets lists datasets in the workspace. POST /datasets creates a dataset "
                 "from an uploaded CSV of up to 500 MB. GET /reports/{id} returns report metadata. POST "
                 "/reports/{id}/export starts an asynchronous export and returns a job id. GET /jobs/{id} "
                 "returns job status: queued, running, succeeded or failed."),
                ("Errors", "Errors use standard HTTP status codes and a JSON body with code and message fields. "
                 "400 means the request was invalid, 401 means the API key is missing or invalid, 403 means the "
                 "key lacks permission for the workspace, 404 means the resource does not exist, and 5xx errors "
                 "are safe to retry with exponential backoff."),
                ("Webhooks", "Webhooks notify you when an export job finishes. Each delivery is signed with "
                 "HMAC-SHA256 in the Brightwater-Signature header. Failed deliveries are retried up to 8 times "
                 "over 24 hours."),
            ],
        ],
    ),
    "brightwater-security-policy.pdf": (
        "Information Security Policy",
        [
            [
                ("Purpose", "This policy protects the confidentiality, integrity and availability of Brightwater "
                 "and customer data. It applies to all employees, contractors and systems. Violations may lead "
                 "to disciplinary action."),
                ("Data classification", "Data is classified into four levels. Public data may be shared freely. "
                 "Internal data is for employees only. Confidential data, such as contracts and financial "
                 "reports, is shared on a need-to-know basis. Restricted data, which includes customer datasets "
                 "and credentials, must be encrypted at rest and in transit and must never be copied to personal "
                 "devices."),
            ],
            [
                ("Passwords and authentication", "Passwords must be at least 14 characters long and must be "
                 "stored in the company password manager. Multi-factor authentication is mandatory for email, "
                 "source control, cloud consoles and the HR portal. Hardware security keys are required for "
                 "anyone with production access."),
                ("Access control", "Access follows the principle of least privilege. Production access is "
                 "granted for a maximum of 8 hours at a time through the access request tool and is logged. "
                 "Managers review their team's access rights every quarter."),
                ("Devices", "Company laptops must use full-disk encryption, automatic screen lock after 5 minutes "
                 "of inactivity, and must install security updates within 7 days of release."),
            ],
            [
                ("Incident reporting", "Any suspected security incident, including lost devices, phishing emails "
                 "that were clicked, or data sent to the wrong recipient, must be reported to the security team "
                 "within 1 hour of discovery via the #security-incidents channel or security@brightwater.example. "
                 "Do not try to investigate on your own and do not delete evidence."),
                ("Incident response", "The security team triages every report within 4 hours. Incidents involving "
                 "personal data are assessed by the data protection officer, and where required, the relevant "
                 "authority is notified within 72 hours."),
                ("Training", "All staff complete security awareness training during onboarding and then once a "
                 "year. Simulated phishing exercises are run every quarter."),
            ],
        ],
    ),
}


def build() -> None:
    OUT.mkdir(exist_ok=True)
    styles = getSampleStyleSheet()
    for filename, (title, pages) in DOCS.items():
        story = [Paragraph(f"{COMPANY}: {title}", styles["Title"]),
                 Paragraph("Fictional sample document for demo purposes.", styles["Italic"])]
        for i, sections in enumerate(pages):
            if i:
                story.append(PageBreak())
            for heading, body in sections:
                story += [Paragraph(heading, styles["Heading2"]), Paragraph(body, styles["BodyText"]),
                          Spacer(1, 6)]
        doc = SimpleDocTemplate(str(OUT / filename), pagesize=A4, title=f"{COMPANY}: {title}",
                                author=COMPANY, topMargin=2 * cm, bottomMargin=2 * cm)
        doc.build(story)
        print(f"wrote {OUT / filename}")


if __name__ == "__main__":
    build()
