import os
import fitz
import pytest
from src import config

def test_stage2_sample_docs():
    """Stage 2: Create Sample Documents for Testing"""
    docs_dir = config.SAMPLE_DOCS_DIR
    os.makedirs(docs_dir, exist_ok=True)

    hr_policy = """HR POLICY DOCUMENT v2.1
Section 1: Leave Policy
Employees are entitled to 18 days of paid annual leave per year.
Sick leave is capped at 10 days per calendar year.
Maternity leave is 26 weeks as per company policy.

Section 2: Work Hours
Standard work hours are 9 AM to 6 PM Monday to Friday.
Remote work is allowed up to 2 days per week with manager approval.
"""

    tech_manual = """TECHNICAL INFRASTRUCTURE MANUAL
Section 1: VPN Access
All employees must use Cisco AnyConnect VPN when accessing internal systems remotely.
VPN credentials are issued by the IT department within 2 business days of joining.
"""

    faq_pdf_content = """PRODUCT FAQ
Q: What is the refund policy?
A: Refunds are processed within 5 to 7 business days of request approval.
"""

    try:
        with open(docs_dir / "hr_policy.txt", "w") as f:
            f.write(hr_policy)
        
        with open(docs_dir / "tech_manual.txt", "w") as f:
            f.write(tech_manual)
        
        # Create PDF
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), faq_pdf_content)
        doc.save(docs_dir / "sample.pdf")
        doc.close()
        
    except Exception as e:
        pytest.fail(f"Sample docs creation failed: {e}")
