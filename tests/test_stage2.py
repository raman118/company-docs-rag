import os
import fitz
import pytest

print("--- Stage 2: Create Sample Docs ---")

def test_stage2():
    docs_dir = "./data/sample_docs/"
    os.makedirs(docs_dir, exist_ok=True)

    hr_policy = """HR POLICY DOCUMENT v2.1
Section 1: Leave Policy
Employees are entitled to 18 days of paid annual leave per year.
Sick leave is capped at 10 days per calendar year.
Maternity leave is 26 weeks as per company policy.

Section 2: Work Hours
Standard work hours are 9 AM to 6 PM Monday to Friday.
Remote work is allowed up to 2 days per week with manager approval.

Section 3: Reimbursements
Travel reimbursement requires receipts submitted within 7 days of travel.
Maximum meal allowance is Rs. 500 per day during business travel.
"""

    tech_manual = """TECHNICAL INFRASTRUCTURE MANUAL
Section 1: VPN Access
All employees must use Cisco AnyConnect VPN when accessing internal systems remotely.
VPN credentials are issued by the IT department within 2 business days of joining.

Section 2: Password Policy
Passwords must be at least 12 characters long.
Passwords expire every 90 days.
Do not reuse last 5 passwords.

Section 3: Software Requests
New software installations must be approved via the IT helpdesk portal.
Approval typically takes 3 to 5 business days.
"""

    faq_pdf_content = """PRODUCT FAQ
Q: What is the refund policy?
A: Refunds are processed within 5 to 7 business days of request approval.

Q: How do I contact support?
A: Email support@company.com or call 1800-XXX-XXXX between 10 AM and 5 PM IST.
"""

    try:
        with open(os.path.join(docs_dir, "hr_policy.txt"), "w") as f:
            f.write(hr_policy)
        
        with open(os.path.join(docs_dir, "tech_manual.txt"), "w") as f:
            f.write(tech_manual)
        
        # Create PDF
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), faq_pdf_content)
        doc.save(os.path.join(docs_dir, "sample.pdf"))
        doc.close()
        
        print("Sample docs creation: PASS")
    except Exception as e:
        pytest.fail(f"Sample docs creation: FAIL ({e})")
