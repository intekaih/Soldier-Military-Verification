"""SheerID Military Verification Configuration"""

# SheerID API Base URL
SHEERID_BASE_URL = "https://services.sheerid.com"

# Program ID - UPDATE THIS before using
# Get this from the SheerID verification URL: /verify/{PROGRAM_ID}/
PROGRAM_ID = ""

# Military Organizations (US Armed Forces)
ORGANIZATIONS = {
    4070: "Army",
    4073: "Air Force",
    4072: "Navy",
    4071: "Marine Corps",
    4074: "Coast Guard",
    4544268: "Space Force",
}

# Military Status Options
MILITARY_STATUSES = ["ACTIVE_DUTY", "VETERAN", "MILITARY_FAMILY"]

# Metadata - Feature Flags (captured from SheerID frontend)
FLAGS = '{"doc-upload-considerations":"default","doc-upload-may24":"default","doc-upload-redesign-use-legacy-message-keys":false,"docUpload-assertion-checklist":"default","include-cvec-field-france-student":"not-labeled-optional","org-search-overlay":"default","org-selected-display":"default"}'

# Metadata - Privacy Policy Opt-In Text (OpenAI version)
SUBMISSION_OPT_IN = 'By submitting the personal information above, I acknowledge that my personal information is being collected under the <a target="_blank" rel="noopener noreferrer" class="sid-privacy-policy sid-link" href="https://openai.com/policies/privacy-policy/">privacy policy</a> of the business from which I am seeking a discount, and I understand that my personal information will be shared with SheerID as a processor/third-party service provider in order for SheerID to confirm my eligibility for a special offer. Contact OpenAI Support for further assistance at support@openai.com'

# Default HTTP Headers for SheerID API
DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Origin": "https://services.sheerid.com",
    "Referer": "https://services.sheerid.com/",
}
