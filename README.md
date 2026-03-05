# Soldier Military Verification

> SheerID Military Verification for ChatGPT/OpenAI — Automated 2-step veteran identity verification.

Based on the architecture and API documentation from [PastKing/tgbot-verify](https://github.com/PastKing/tgbot-verify).

## Features

- **2-Step Verification Process**: Implements the full SheerID military verification flow
- **Auto-generated Data**: Names, emails, birth dates, and discharge dates are randomly generated
- **6 Military Branches**: Army, Air Force, Navy, Marine Corps, Coast Guard, Space Force
- **3 Status Types**: VETERAN, ACTIVE_DUTY, MILITARY_FAMILY
- **CLI Interface**: Easy-to-use command line with full argument support

## Installation

```bash
git clone https://github.com/intekaih/Soldier-Military-Verification.git
cd Soldier-Military-Verification
pip install -r requirements.txt
```

## Configuration

Before using, update `PROGRAM_ID` in `config.py`:

```python
PROGRAM_ID = "your_program_id_here"
```

### How to get `verificationId`

1. Open the ChatGPT military discount page in your browser
2. Open DevTools (F12) → Network tab
3. Look for requests to `services.sheerid.com`
4. Find the `verificationId` in the URL parameters

## Usage

```bash
# Basic usage (all info auto-generated)
python main.py --verification-id "YOUR_VERIFICATION_ID"

# Using a full URL
python main.py --url "https://services.sheerid.com/verify/PROG_ID/?verificationId=YOUR_ID"

# Specify military status
python main.py --verification-id "YOUR_ID" --status VETERAN

# Specify organization
python main.py --verification-id "YOUR_ID" --organization 4070

# Full custom info
python main.py --verification-id "YOUR_ID" \
  --status VETERAN \
  --first-name John \
  --last-name Doe \
  --email john.doe@gmail.com \
  --birth-date 1970-05-15 \
  --discharge-date 2020-06-30 \
  --organization 4072
```

## Supported Organizations

| ID | Branch |
|----|--------|
| 4070 | Army |
| 4073 | Air Force |
| 4072 | Navy |
| 4071 | Marine Corps |
| 4074 | Coast Guard |
| 4544268 | Space Force |

## Project Structure

```
├── config.py            # SheerID API configuration, organizations, metadata
├── name_generator.py    # Random name, email, date generators
├── sheerid_verifier.py  # MilitaryVerifier class (2-step verification logic)
├── main.py              # CLI entry point
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## How It Works

```
Step 1: collectMilitaryStatus
    POST /rest/v2/verification/{id}/step/collectMilitaryStatus
    Body: {"status": "VETERAN"}
    → Returns submissionUrl for Step 2

Step 2: collectInactiveMilitaryPersonalInfo
    POST {submissionUrl}
    Body: {firstName, lastName, birthDate, email, organization, dischargeDate, metadata...}
    → Returns verification result
```

## Credits

- Architecture and API documentation based on [PastKing/tgbot-verify](https://github.com/PastKing/tgbot-verify)
- Military verification module (`military/README.md`) from the original repository

## License

MIT License
