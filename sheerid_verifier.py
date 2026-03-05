"""SheerID Military Verification - 2-Step Process"""
import re
import random
import logging
import httpx

import config
from name_generator import NameGenerator, generate_email, generate_birth_date, generate_discharge_date

logger = logging.getLogger(__name__)


class MilitaryVerifier:
    """
    SheerID Military Verification Handler.
    
    Implements the 2-step military verification process:
    Step 1: collectMilitaryStatus - Set military status (VETERAN/ACTIVE_DUTY/MILITARY_FAMILY)
    Step 2: collectInactiveMilitaryPersonalInfo - Submit personal information
    """

    def __init__(self, verification_id, status="VETERAN"):
        """
        Initialize the Military Verifier.

        Args:
            verification_id (str): The SheerID verification ID
            status (str): Military status - VETERAN, ACTIVE_DUTY, or MILITARY_FAMILY
        """
        if status not in config.MILITARY_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {config.MILITARY_STATUSES}")

        self.verification_id = verification_id
        self.status = status
        self.client = httpx.Client(headers=config.DEFAULT_HEADERS, timeout=30.0)

    def __del__(self):
        """Cleanup HTTP client"""
        try:
            self.client.close()
        except Exception:
            pass

    @staticmethod
    def parse_verification_id(url):
        """Extract verificationId from a SheerID URL."""
        # Try query parameter: ?verificationId=XXX
        match = re.search(r'verificationId=([a-f0-9]+)', url)
        if match:
            return match.group(1)

        # Try path-based UUID pattern
        match = re.search(r'/([a-f0-9]{24,})', url)
        if match:
            return match.group(1)

        return None

    def _sheerid_request(self, method, url, body=None):
        """Make an HTTP request to SheerID API."""
        try:
            if method.upper() == "POST":
                response = self.client.post(url, json=body)
            elif method.upper() == "GET":
                response = self.client.get(url)
            elif method.upper() == "DELETE":
                response = self.client.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            try:
                data = response.json()
            except Exception:
                data = {"raw": response.text}

            return data, response.status_code

        except httpx.TimeoutException:
            logger.error(f"Request timeout: {url}")
            return {"error": "Request timeout"}, 0
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return {"error": str(e)}, 0
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"error": str(e)}, 0

    def collect_military_status(self):
        """Step 1: Submit military status to SheerID."""
        url = f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectMilitaryStatus"
        body = {"status": self.status}

        logger.info(f"Step 1/2: Submitting military status '{self.status}'...")
        logger.info(f"  URL: {url}")

        data, status_code = self._sheerid_request("POST", url, body)

        if status_code != 200:
            logger.error(f"Step 1 failed (HTTP {status_code}): {data}")
            return None

        if data.get("currentStep") == "error":
            error_ids = ", ".join(data.get("errorIds", ["Unknown error"]))
            logger.error(f"Step 1 error: {error_ids}")
            return None

        submission_url = data.get("submissionUrl")
        current_step = data.get("currentStep")

        logger.info(f"  ✅ Step 1 complete!")
        logger.info(f"  Current step: {current_step}")
        logger.info(f"  Submission URL: {submission_url}")

        return submission_url

    def collect_personal_info(self, submission_url, first_name, last_name, birth_date,
                               email, organization_id, organization_name, discharge_date):
        """Step 2: Submit personal information to SheerID."""
        body = {
            "firstName": first_name,
            "lastName": last_name,
            "birthDate": birth_date,
            "email": email,
            "phoneNumber": "",
            "organization": {
                "id": organization_id,
                "name": organization_name
            },
            "dischargeDate": discharge_date,
            "locale": "en-US",
            "country": "US",
            "metadata": {
                "marketConsentValue": False,
                "refererUrl": "",
                "verificationId": self.verification_id,
                "flags": config.FLAGS,
                "submissionOptIn": config.SUBMISSION_OPT_IN
            }
        }

        logger.info(f"Step 2/2: Submitting personal information...")
        logger.info(f"  Name: {first_name} {last_name}")
        logger.info(f"  Email: {email}")
        logger.info(f"  Birth Date: {birth_date}")
        logger.info(f"  Organization: {organization_name} (ID: {organization_id})")
        logger.info(f"  Discharge Date: {discharge_date}")

        data, status_code = self._sheerid_request("POST", submission_url, body)

        if status_code != 200:
            logger.error(f"Step 2 failed (HTTP {status_code}): {data}")
        elif data.get("currentStep") == "error":
            error_ids = ", ".join(data.get("errorIds", ["Unknown error"]))
            logger.error(f"Step 2 error: {error_ids}")
        else:
            logger.info(f"  ✅ Step 2 complete!")
            logger.info(f"  Current step: {data.get('currentStep')}")

        return data, status_code

    def verify(self, first_name=None, last_name=None, birth_date=None,
               email=None, organization_id=None, discharge_date=None):
        """Run the full 2-step military verification process."""
        logger.info("=" * 60)
        logger.info("  Military Verification - SheerID")
        logger.info("=" * 60)
        logger.info(f"Verification ID: {self.verification_id}")
        logger.info(f"Military Status: {self.status}")
        logger.info("")

        # Auto-generate missing information
        if not first_name or not last_name:
            name = NameGenerator.generate()
            first_name = first_name or name["first_name"]
            last_name = last_name or name["last_name"]

        if not email:
            email = generate_email()
        if not birth_date:
            birth_date = generate_birth_date()
        if not discharge_date:
            discharge_date = generate_discharge_date()

        # Pick random organization if not specified
        if not organization_id:
            organization_id = random.choice(list(config.ORGANIZATIONS.keys()))

        organization_name = config.ORGANIZATIONS.get(organization_id)
        if not organization_name:
            return {
                "success": False,
                "message": f"Unknown organization ID: {organization_id}. Valid IDs: {list(config.ORGANIZATIONS.keys())}",
                "current_step": None,
                "verification_id": self.verification_id,
                "data": None
            }

        # ---- Step 1: Collect Military Status ----
        submission_url = self.collect_military_status()
        if not submission_url:
            return {
                "success": False,
                "message": "Step 1 failed: Could not get submission URL",
                "current_step": "collectMilitaryStatus",
                "verification_id": self.verification_id,
                "data": None
            }

        logger.info("")

        # ---- Step 2: Collect Personal Info ----
        data, status_code = self.collect_personal_info(
            submission_url=submission_url,
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            email=email,
            organization_id=organization_id,
            organization_name=organization_name,
            discharge_date=discharge_date
        )

        success = status_code == 200 and data.get("currentStep") != "error"
        current_step = data.get("currentStep") if isinstance(data, dict) else None

        logger.info("")
        logger.info("=" * 60)
        if success:
            logger.info("  ✅ VERIFICATION SUBMITTED SUCCESSFULLY")
        else:
            logger.info("  ❌ VERIFICATION FAILED")
        logger.info("=" * 60)

        return {
            "success": success,
            "message": "Verification submitted successfully" if success else f"Verification failed (HTTP {status_code})",
            "current_step": current_step,
            "verification_id": self.verification_id,
            "data": data
        }
