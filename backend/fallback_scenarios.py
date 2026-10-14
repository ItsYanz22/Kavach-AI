"""
Fallback scenario engine for Kavach AI.
Generates realistic, diverse scam scenarios across 25 cybercrime categories when LLM is unavailable.
"""

import random
from datetime import datetime
from typing import Dict, List, Any, Optional


class FallbackScenarioEngine:
    """
    Comprehensive fallback scenario engine covering 25 realistic cybercrime categories.
    Used when Groq is temporarily unavailable or during degraded offline operation.
    """

    TAXONOMY_SCENARIOS: List[Dict[str, Any]] = [
        # 1. UPI Payment & Collect-Request Fraud
        {
            "scenario_type": "upi_fraud",
            "attacker_persona": "PhonePe Automated Refund Executive",
            "message": "Dear PhonePe user, ₹2,450 cashback from your recent Indian Oil fuel transaction is pending credit. To receive funds directly in your bank account, click: safesim.link/phonepe-cashback and approve request.",
            "amount": 2450,
            "danger_label": "🔴 Approve ₹2,450 Refund",
            "tip": "UPI PIN is ONLY entered to deduct money, NEVER to receive or claim cashback.",
            "risk_level": "critical",
            "ui_title": "💸 Pending UPI Cashback Notice",
            "ui_description": "Deceptive collect request disguised as an incoming refund credit.",
            "manipulation_tactics": ["greed", "urgency", "platform impersonation"],
            "conversation_goal": "Trick user into entering UPI PIN on a collect request",
        },
        # 2. Fake KYC & Bank Suspension
        {
            "scenario_type": "bank_kyc_phishing",
            "attacker_persona": "SBI Central Compliance Officer",
            "message": "IMPORTANT: Your SBI Account XXXX8921 YONO service is suspended due to unverified PAN-Aadhaar linking. Update credentials within 24 hrs to avoid total freeze: safesim.link/sbi-yono-kyc",
            "amount": 0,
            "danger_label": "🔴 Update KYC Documents",
            "tip": "Banks never send external link URLs for KYC updates via SMS or WhatsApp.",
            "risk_level": "high",
            "ui_title": "⚠️ SBI YONO KYC Suspension Notice",
            "ui_description": "High-pressure phishing attempt threatening immediate bank account freeze.",
            "manipulation_tactics": ["fear", "authority impersonation", "urgency"],
            "conversation_goal": "Steal NetBanking login credentials and OTP",
        },
        # 3. OTP Theft / Fraud Prevention Impersonation
        {
            "scenario_type": "otp_theft",
            "attacker_persona": "HDFC Card Security Wing",
            "message": "HDFC Alert: An international transaction of $490.00 at Apple US was detected on your debit card. If this wasn't you, call +91-98765-XXXXX immediately to block and reverse the charge.",
            "amount": 41500,
            "danger_label": "🔴 Call & Verify OTP",
            "tip": "Fraud departments never ask you to read back OTPs over the phone to cancel charges.",
            "risk_level": "critical",
            "ui_title": "🚨 HDFC Fraud Alert Notice",
            "ui_description": "Fake transaction alert meant to prompt an urgent panicked phone call to steal OTP.",
            "manipulation_tactics": ["fear", "loss aversion", "urgency"],
            "conversation_goal": "Convince user to read out one-time passwords under the guise of cancellation",
        },
        # 4. Phishing / Credential Harvesting
        {
            "scenario_type": "credential_harvesting",
            "attacker_persona": "IRCTC Ticket Booking Security",
            "message": "Your IRCTC Tatkal train ticket confirmation failed due to session timeout. Immediate reverification required to confirm Seat B2-41: safesim.link/irctc-reverify",
            "amount": 1890,
            "danger_label": "🔴 Re-enter IRCTC Credentials",
            "tip": "Always check the domain name in the address bar before entering passwords or PINs.",
            "risk_level": "high",
            "ui_title": "🚆 IRCTC Tatkal Session Alert",
            "ui_description": "Credential harvester exploiting urgency of Tatkal train confirmation.",
            "manipulation_tactics": ["urgency", "fear of lost booking"],
            "conversation_goal": "Harvest IRCTC login and payment card details",
        },
        # 5. Job & Internship Registration Fee Fraud
        {
            "scenario_type": "job_internship_scam",
            "attacker_persona": "Amazon India HR Coordinator",
            "message": "Congratulations! You have been shortlisted for Amazon Remote Reviewer Role (₹35,000/mo). To secure your employee batch ID and remote laptop kit, deposit refundable security deposit ₹1,999: safesim.link/amazon-onboard",
            "amount": 1999,
            "danger_label": "🔴 Pay Registration Fee ₹1,999",
            "tip": "Legitimate companies never demand upfront fees or equipment security deposits.",
            "risk_level": "high",
            "ui_title": "💼 Amazon Remote Job Offer",
            "ui_description": "Advance fee fraud demanding upfront deposit for a fake work-from-home role.",
            "manipulation_tactics": ["greed", "flattery", "scarcity"],
            "conversation_goal": "Extract upfront advance fee under the guise of refundable kit fee",
        },
        # 6. Recruitment Rating Scam (YouTube / Hotel Task)
        {
            "scenario_type": "hr_recruitment_fraud",
            "attacker_persona": "MNC Digital Marketing Agency Recruiter",
            "message": "Hi! We offer daily part-time payouts of ₹2,500 - ₹5,000 just for liking YouTube videos and rating Google Maps hotels. Start trial now on Telegram: @GlobalTaskSupport_09",
            "amount": 5000,
            "danger_label": "🔴 Join VIP Task Channel",
            "tip": "Task scams pay tiny amounts initially to lure you into 'prepaid investment tasks' later.",
            "risk_level": "high",
            "ui_title": "⭐ YouTube Like & Earn Scam",
            "ui_description": "Pyramid task scam that escalates from small payouts to major extortion.",
            "manipulation_tactics": ["easy money", "low barrier of entry"],
            "conversation_goal": "Draw victim into a fake Telegram task group for upfront investment extortion",
        },
        # 7. Cryptocurrency & High Return Investment Fraud
        {
            "scenario_type": "investment_crypto_fraud",
            "attacker_persona": "CryptoBoost VIP Wealth Manager",
            "message": "📈 AI Algorithmic Trading: Earn guaranteed 18.5% daily compounding returns with our SEBI-licensed automated bot. Minimum ₹5,000 starter deposit: safesim.link/cryptoboost-invest",
            "amount": 5000,
            "danger_label": "🔴 Deposit ₹5,000 for 18% Daily ROI",
            "tip": "No regulated financial entity can guarantee daily double-digit returns.",
            "risk_level": "critical",
            "ui_title": "📈 Guaranteed Crypto ROI Scheme",
            "ui_description": "Classic Ponzi investment lure promising mathematically impossible daily returns.",
            "manipulation_tactics": ["greed", "social proof", "algorithmic hype"],
            "conversation_goal": "Trick user into transferring investment money to an untraceable wallet",
        },
        # 8. Parcel Delivery & Customs Duty Scam
        {
            "scenario_type": "parcel_customs_scam",
            "attacker_persona": "India Post / FedEx International Delivery",
            "message": "IndiaPost Notice: Package #IN-88942 cannot be delivered due to incomplete apartment number and pending custom duty of ₹385. Pay immediately to avoid return: safesim.link/indapost-track",
            "amount": 385,
            "danger_label": "🔴 Pay Custom Clearance ₹385",
            "tip": "Postal services do not withhold everyday deliveries via random SMS payment links.",
            "risk_level": "medium",
            "ui_title": "📦 Undelivered Parcel Customs Alert",
            "ui_description": "Smishing tactic exploiting anticipation of online shopping deliveries.",
            "manipulation_tactics": ["curiosity", "low initial amount", "urgency"],
            "conversation_goal": "Capture debit card CVV on a fake checkout gateway",
        },
        # 9. Digital Arrest & Law Enforcement Threat
        {
            "scenario_type": "digital_arrest_threat",
            "attacker_persona": "CBI Cyber Cell Inspector Deshmukh",
            "message": "COURT NOTICE: A consignment containing illegal narcotics and fake passports registered under your Aadhaar was seized at Mumbai Airport. You are under Digital Arrest. Join Skype verification room or face immediate local arrest.",
            "amount": 50000,
            "danger_label": "🔴 Join Skype Interrogation Room",
            "tip": "Police, CBI, or courts NEVER conduct digital arrests or demand money via video calls.",
            "risk_level": "critical",
            "ui_title": "🚨 Digital Arrest Legal Threat",
            "ui_description": "Extreme intimidation using fake CBI/Police uniforms and warrants over video calls.",
            "manipulation_tactics": ["fear", "extreme authority", "isolation"],
            "conversation_goal": "Coerce victim into transferring 'verification collateral' to scammer bank account",
        },
        # 10. Electricity Bill Disconnection Threat
        {
            "scenario_type": "utility_bill_threat",
            "attacker_persona": "State Electricity Board Officer",
            "message": "URGENT DISCONNECTION: Dear Consumer, your electricity power will be disconnected tonight at 9:30 PM due to unpaid bill of ₹2,840. Immediately contact Electricity Officer Sharma at 98765-XXXXX to clear payment.",
            "amount": 2840,
            "danger_label": "🔴 Pay ₹2,840 Disconnection Avoidance",
            "tip": "Electricity boards never send personal mobile numbers for bill payments with 9:30 PM deadlines.",
            "risk_level": "high",
            "ui_title": "⚡ Electricity Disconnection Notice",
            "ui_description": "Time-pressured utility scam forcing panicked phone calls to fraudulent personal numbers.",
            "manipulation_tactics": ["urgency", "loss of essential service", "panic"],
            "conversation_goal": "Force user into downloading remote control tool or making direct UPI payment",
        },
        # 11. QR Code Marketplace Scam
        {
            "scenario_type": "qr_code_scam",
            "attacker_persona": "Interested OLX Army Officer Buyer",
            "message": "I want to buy your sofa for ₹12,000 immediately without discount. Since I am posted at military cantt, I am sending you a PhonePe QR code. Scan it and enter your PIN to receive the advance payment.",
            "amount": 12000,
            "danger_label": "🔴 Scan QR Code to Receive Money",
            "tip": "Scanning a QR code and entering your PIN ALWAYS debits money from your account.",
            "risk_level": "critical",
            "ui_title": "📷 QR Code 'Receive Money' Scam",
            "ui_description": "Marketplace scam where buyer sends a debit QR code claiming it transfers money to you.",
            "manipulation_tactics": ["trust impersonation", "greed", "confusion"],
            "conversation_goal": "Trick seller into scanning payment QR and entering UPI PIN",
        },
        # 12. Fake Customer Care
        {
            "scenario_type": "fake_customer_care",
            "attacker_persona": "Google Pay Senior Technical Support",
            "message": "Hello Sir, we noticed your ₹3,500 transaction to Zomato failed yesterday. I am from GPay grievance desk. Please download our official quick-fix helper app: safesim.link/gpay-support-apk to process your instant refund.",
            "amount": 3500,
            "danger_label": "🔴 Install Support Assistant App",
            "tip": "Customer care never asks customers to install third-party .apk files or screen-sharing tools.",
            "risk_level": "critical",
            "ui_title": "🎧 Fake GPay Customer Support",
            "ui_description": "Impersonation of fintech customer care offering to 'fix' recent failed transactions.",
            "manipulation_tactics": ["helpfulness", "reassurance", "authority"],
            "conversation_goal": "Convince user to install remote access malware (AnyDesk/TeamViewer)",
        },
        # 13. Social Media Account Recovery Scam
        {
            "scenario_type": "social_account_recovery",
            "attacker_persona": "Meta Copyright Infringement Team",
            "message": "Instagram Notice: Your account violates Community Copyright Guidelines. Your profile will be permanently deleted in 24 hours. Submit objection form to retain your username: safesim.link/meta-copyright-appeal",
            "amount": 0,
            "danger_label": "🔴 Submit Copyright Appeal",
            "tip": "Meta and Instagram notify copyright issues inside the official app settings, never via DM or SMS.",
            "risk_level": "high",
            "ui_title": "📸 Instagram Copyright Strike Alert",
            "ui_description": "Phishing lure targeting creators and social media users with threats of account deletion.",
            "manipulation_tactics": ["fear of loss", "urgency", "brand authority"],
            "conversation_goal": "Steal 2FA codes and Instagram account credentials",
        },
        # 14. Family / Friend Emergency Impersonation
        {
            "scenario_type": "family_emergency_impersonation",
            "attacker_persona": "Distressed College Friend / Police Officer",
            "message": "Bhai, urgent help! I had a car accident near Highway. Police are impounding vehicle and hospital needs advance ₹15,000 for surgery. My GPay is blocked, please send immediately to Dr. Sharma UPI: 98765XXXXX@okicici",
            "amount": 15000,
            "danger_label": "🔴 Transfer Emergency Hospital Advance",
            "tip": "Always independently call the friend or family member on their known number before sending emergency money.",
            "risk_level": "critical",
            "ui_title": "🚑 Urgent Accident Emergency Plea",
            "ui_description": "Emotional extortion using the fabricated emergency of a close acquaintance.",
            "manipulation_tactics": ["panic", "emotional blackmail", "urgency"],
            "conversation_goal": "Extract panic transfer before user can independently verify",
        },
        # 15. Romance & Customs Gift Scam
        {
            "scenario_type": "romance_financial_scam",
            "attacker_persona": "Overseas Online Acquaintance",
            "message": "Darling, I dispatched a surprise package with an iPhone 16 Pro and gold necklace from London for your birthday. The courier company says it is held at Delhi Airport customs for clearance fee ₹8,500. Please pay it today!",
            "amount": 8500,
            "danger_label": "🔴 Pay Customs Gift Clearance ₹8,500",
            "tip": "Customs clearance fees are never paid to personal UPI IDs or private bank accounts.",
            "risk_level": "high",
            "ui_title": "💍 Overseas Gift Customs Clearance",
            "ui_description": "Long-game social manipulation leveraging romantic interest and expensive fabricated gifts.",
            "manipulation_tactics": ["emotional attachment", "curiosity", "guilt"],
            "conversation_goal": "Extract serial customs fees for non-existent parcels",
        },
        # 16. Lottery & KBC Lucky Draw Scam
        {
            "scenario_type": "lottery_reward_scam",
            "attacker_persona": "KBC Official Prize Committee",
            "message": "Dear Winner, Your SIM has won ₹25,00,000 in Kaun Banega Crorepati WhatsApp Lucky Draw! Contact Secretary Rana Pratap at 98765-XXXXX with Lottery Code #KBC-772 to claim. Government GST deposit applies.",
            "amount": 12500,
            "danger_label": "🔴 Claim ₹25 Lakh Lottery",
            "tip": "You cannot win a lottery you never entered. Genuine prizes never require advance tax payments.",
            "risk_level": "high",
            "ui_title": "🎉 KBC 25 Lakh Lucky Draw",
            "ui_description": "Advance fee lottery fraud promising astronomical rewards for a nominal processing fee.",
            "manipulation_tactics": ["extreme greed", "celebrity branding"],
            "conversation_goal": "Collect serial processing fees and government tax deposits",
        },
        # 17. Malicious APK Lure
        {
            "scenario_type": "malicious_apk_lure",
            "attacker_persona": "SBI Reward Points Manager",
            "message": "You have 9,450 unclaimed SBI Reward points worth ₹4,725 expiring tonight. Redeem directly into your savings account by downloading SBI Reward Redeem APK: safesim.link/sbi-rewards.apk",
            "amount": 4725,
            "danger_label": "🔴 Download & Install Reward APK",
            "tip": "Never install .apk files sent via SMS or messaging apps. They intercept SMS and steal OTPs.",
            "risk_level": "critical",
            "ui_title": "🎁 SBI Reward Points Expiry Notice",
            "ui_description": "Malware delivery disguised as an expiring loyalty point redemption app.",
            "manipulation_tactics": ["greed", "urgency", "loss aversion"],
            "conversation_goal": "Install SMS-forwarding malware onto victim's Android smartphone",
        },
        # 18. Tech Support Remote Access Scam
        {
            "scenario_type": "tech_support_scam",
            "attacker_persona": "Microsoft Windows Security Engineer",
            "message": "CRITICAL ALERT: Your Windows machine IP was detected transmitting Trojan.Spyware.32 to Russian servers. Your network will be blacklisted within 30 minutes. Contact Toll-Free: 1800-XXX-XXXX for remote removal.",
            "amount": 6500,
            "danger_label": "🔴 Allow Remote Diagnostics",
            "tip": "Microsoft and Apple never send popups or SMS telling you to call phone numbers for virus removal.",
            "risk_level": "high",
            "ui_title": "💻 Windows Security Trojan Alert",
            "ui_description": "Tech support scareware designed to gain AnyDesk remote control of your computer.",
            "manipulation_tactics": ["technical jargon", "fear", "urgency"],
            "conversation_goal": "Install remote software and manipulate online banking screens",
        },
        # 19. Instant Loan Approval Fraud
        {
            "scenario_type": "instant_loan_fraud",
            "attacker_persona": "Dhani Instant Loan Sanction Desk",
            "message": "Pre-approved Loan of ₹5,00,000 sanctioned at 1% interest rate without CIBIL score. To disburse funds directly to your bank account within 10 minutes, pay refundable file charge ₹1,250: safesim.link/quick-loan",
            "amount": 1250,
            "danger_label": "🔴 Pay Processing Charge ₹1,250",
            "tip": "Legitimate banks deduct loan processing fees from the loan amount itself, never upfront via UPI.",
            "risk_level": "high",
            "ui_title": "💳 ₹5 Lakh Instant Loan Pre-Approval",
            "ui_description": "Predatory lending fraud targeting financially vulnerable individuals with advance fees.",
            "manipulation_tactics": ["financial relief", "zero barrier to entry"],
            "conversation_goal": "Steal upfront advance fees for a non-existent loan",
        },
        # 20. AI Voice Deepfake Scenario
        {
            "scenario_type": "ai_voice_deepfake",
            "attacker_persona": "Synthesized Family Member / College Dean",
            "message": "[VOICE MESSAGE TRANSCRIPT] 'Dad... please don't get angry, I was traveling with friends and our car got into a collision. The police are detaining us unless we settle the vehicle damages for ₹25,000 right now. Please pay this number immediately...'",
            "amount": 25000,
            "danger_label": "🔴 Send ₹25,000 Settlement",
            "tip": "Always establish a family safe-word or call the person back on their trusted phone number.",
            "risk_level": "critical",
            "ui_title": "🎙️ AI Voice Clone Emergency Alert",
            "ui_description": "Cutting-edge voice cloning mimicry simulating extreme family distress.",
            "manipulation_tactics": ["visceral panic", "family affection", "extreme urgency"],
            "conversation_goal": "Bypass rational thinking using voice recognition trust",
        },
        # 21. Business Email Compromise
        {
            "scenario_type": "business_email_compromise",
            "attacker_persona": "Authorized Hardware Supplier Finance Dept",
            "message": "Attention Accounts: Due to annual financial audit, our primary HDFC account is under migration. Please route today's pending vendor invoice payment of ₹78,000 to our updated Axis Bank account: A/C 9190200XXXXX.",
            "amount": 78000,
            "danger_label": "🔴 Update Vendor Bank Details",
            "tip": "Always verify vendor bank account changes via a voice call to a known, established contact.",
            "risk_level": "critical",
            "ui_title": "🏢 Vendor Bank Account Update Notice",
            "ui_description": "Corporate fraud targeting accounts payable by impersonating familiar suppliers.",
            "manipulation_tactics": ["routine authority", "business legitimacy"],
            "conversation_goal": "Redirect invoice settlements into fraudulent accounts",
        },
        # 22. Fake Charity / Emergency Fundraiser
        {
            "scenario_type": "fake_charity_fundraiser",
            "attacker_persona": "SaveChild Emergency Foundation",
            "message": "Baby Aarav (3 yrs) is in ICU fighting acute respiratory failure. His parents cannot afford ventilator charges. Every ₹500 helps save a life. Donate directly via PM-CARES partner UPI: child-icu@upi",
            "amount": 500,
            "danger_label": "🔴 Donate ₹500 to Child Relief",
            "tip": "Verify charity registrations on DARPAN portal before sending donations to private UPI IDs.",
            "risk_level": "medium",
            "ui_title": "❤️ ICU Medical Emergency Appeal",
            "ui_description": "Emotional exploitation using fabricated photographs and stolen patient stories.",
            "manipulation_tactics": ["compassion", "guilt", "urgency"],
            "conversation_goal": "Divert public sympathy donations to fraudulent personal wallets",
        },
        # 23. Marketplace Second-Hand Item Scam
        {
            "scenario_type": "marketplace_olx_scam",
            "attacker_persona": "Eager Second-Hand Buyer",
            "message": "I want to buy your listed laptop immediately. I already sent ₹25,000 via Google Pay, but my banking app shows 'Beneficiary must authenticate with ₹1 trial request to unlock payment'. Check your GPay notification now!",
            "amount": 25000,
            "danger_label": "🔴 Authenticate Trial Request",
            "tip": "You NEVER have to pay money or authenticate collect requests to receive funds on any app.",
            "risk_level": "high",
            "ui_title": "💻 OLX Buyer Payment Unlock Scam",
            "ui_description": "Overpayment/trial request trick where seller is coerced into approving a debit.",
            "manipulation_tactics": ["confusion", "buyer eagerness"],
            "conversation_goal": "Disguise a payment debit request as an incoming deposit authentication",
        },
        # 24. SIM Swap & Telecom KYC Deactivation
        {
            "scenario_type": "sim_swap_telecom",
            "attacker_persona": "Jio-Airtel 5G Network Operations",
            "message": "Telecom Alert: Your SIM card will be deactivated tonight within 6 hours due to pending TRAI 5G KYC verification. To keep service active, reply with your 20-digit SIM barcode number or SMS: SIM 987654321 to 121.",
            "amount": 0,
            "danger_label": "🔴 Submit SIM Verification Details",
            "tip": "Never send SIM verification codes or barcodes. It allows attackers to take over your phone number.",
            "risk_level": "critical",
            "ui_title": "📶 SIM Card Deactivation Notice",
            "ui_description": "SIM swap lure designed to hijack OTPs and mobile banking access.",
            "manipulation_tactics": ["fear of disconnection", "regulatory authority"],
            "conversation_goal": "Execute a fraudulent SIM swap and intercept all future OTPs",
        },
        # 25. Suspicious Login Alert
        {
            "scenario_type": "suspicious_login_alert",
            "attacker_persona": "Google Accounts Identity Protection",
            "message": "Security Alert: An unrecognized device (Windows 11 in Bucharest, Romania) logged into your primary Gmail account. If this was not you, secure your account immediately: safesim.link/google-security-lock",
            "amount": 0,
            "danger_label": "🔴 Secure Google Account Now",
            "tip": "Security alerts in external emails or SMS often link to lookalike phishing domains.",
            "risk_level": "high",
            "ui_title": "🔐 Google Security Breach Alert",
            "ui_description": "Phishing mimicry creating panic about an unauthorized foreign login.",
            "manipulation_tactics": ["panic", "loss of privacy", "urgency"],
            "conversation_goal": "Direct user to fake Google login page to capture password and session token",
        },
    ]

    @classmethod
    def generate_random_scenario(cls, exclude_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate a random fallback scenario, avoiding recent types if possible."""
        available = cls.TAXONOMY_SCENARIOS
        if exclude_types:
            filtered = [s for s in cls.TAXONOMY_SCENARIOS if s.get("scenario_type") not in exclude_types]
            if filtered:
                available = filtered

        scenario = random.choice(available).copy()

        # Build dynamic context-specific action buttons
        danger_label = scenario.get("danger_label", "🔴 Pay Now")
        amount = scenario.get("amount", 0)

        scenario["recommended_actions"] = [
            {"label": danger_label, "action_id": "pay", "type": "danger"},
            {"label": "🔍 Analyse Message", "action_id": "analyze", "type": "cyber"},
            {"label": "🙈 Ignore", "action_id": "ignore", "type": "warning"},
            {"label": "🚫 Block Sender", "action_id": "block", "type": "danger"},
            {"label": "⚠️ Report Scam", "action_id": "report", "type": "secondary"},
        ]

        scenario["await_user_response"] = True
        scenario["next_step"] = "wait_for_user"
        scenario["is_fallback"] = True
        scenario["is_ai_generated"] = False
        scenario["generation_source"] = "fallback"
        scenario["generated_at"] = datetime.utcnow().isoformat()
        scenario["escalation_stage"] = 1

        return scenario

    @classmethod
    def generate_scenario_by_type(cls, scenario_type: str) -> Dict[str, Any]:
        """Generate a specific fallback scenario by type."""
        matching = [s for s in cls.TAXONOMY_SCENARIOS if s.get("scenario_type") == scenario_type]
        if not matching:
            return cls.generate_random_scenario()

        scenario = random.choice(matching).copy()
        danger_label = scenario.get("danger_label", "🔴 Pay Now")

        scenario["recommended_actions"] = [
            {"label": danger_label, "action_id": "pay", "type": "danger"},
            {"label": "🔍 Analyse Message", "action_id": "analyze", "type": "cyber"},
            {"label": "🙈 Ignore", "action_id": "ignore", "type": "warning"},
            {"label": "🚫 Block Sender", "action_id": "block", "type": "danger"},
            {"label": "⚠️ Report Scam", "action_id": "report", "type": "secondary"},
        ]

        scenario["await_user_response"] = True
        scenario["next_step"] = "wait_for_user"
        scenario["is_fallback"] = True
        scenario["is_ai_generated"] = False
        scenario["generation_source"] = "fallback"
        scenario["generated_at"] = datetime.utcnow().isoformat()
        scenario["escalation_stage"] = 1

        return scenario

    @classmethod
    def get_all_scenario_types(cls) -> List[str]:
        """Get all available scenario types."""
        return [s["scenario_type"] for s in cls.TAXONOMY_SCENARIOS]


# Singleton engine instance
fallback_engine = FallbackScenarioEngine()
