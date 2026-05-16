"""
Fallback scenario engine for Kavach AI.
Generates realistic scam scenarios when LLM is unavailable.
"""

import random
import json
from datetime import datetime
from typing import Dict, List, Any


class FallbackScenarioEngine:
    """
    Generates production-ready fallback scenarios when LLM fails.
    Database of realistic, educational scam scenarios.
    """
    
    # Phishing scenarios
    PHISHING_SCENARIOS = [
        {
            "scenario_type": "bank_phishing",
            "message": "Dear Customer, Your SBI account YONO access has been disabled due to pending KYC. Click here to verify now to avoid permanent block: sbi-secure-kyc.in/yono",
            "scammer_personality": "THE POLITE PROFESSIONAL",
            "emotional_strategy": "Trust",
            "escalation_stage": 1,
            "amount": 49999,
            "tip": "Banks never send YONO or KYC update links via SMS. Official updates only happen through the official app or branch.",
            "risk_level": "high",
            "ui_title": "⚠️ SBI YONO KYC Alert",
            "ui_description": "Fake banking alert impersonating SBI YONO support.",
        },
        {
            "scenario_type": "upi_fraud",
            "message": "Payment of ₹15,000 to Amazon is SUCCESSFUL. If not done by you, immediately Tap to Cancel and Reverse Transaction: phonepe-refund.net.in/cancel",
            "scammer_personality": "THE URGENT SERVICE EXEC",
            "emotional_strategy": "Urgency",
            "escalation_stage": 1,
            "amount": 15000,
            "tip": "UPI 'Cancel' links are often 'Pay' links in disguise. Never enter your PIN to 'receive' or 'cancel' a payment.",
            "risk_level": "high",
            "ui_title": "⚠️ UPI Transaction Alert",
            "ui_description": "A fake transaction notification designed to trigger panic and a 'cancel' action.",
        },
    ]
    
    # Investment/Financial Fraud
    INVESTMENT_SCENARIOS = [
        {
            "scenario_type": "crypto_investment",
            "message": "🎯 LIMITED: CryptoBoost - Guaranteed 20% daily returns. Invest ₹5000 now: crypto-boom.club/invest",
            "amount": 5000,
            "tip": "No investment offers guaranteed high daily returns - this is a Ponzi scheme",
            "risk_level": "critical",
            "ui_title": "💰 Crypto Investment Scam",
            "ui_description": "Unrealistic returns promise to lure investments",
        },
        {
            "scenario_type": "forex_trading",
            "message": "Millionaire traders are making ₹2L/day with FX Trading. Join our group: forex-masters.site/join",
            "amount": 10000,
            "tip": "Anyone making ₹2L daily wouldn't recruit; that's the scam itself",
            "risk_level": "critical",
            "ui_title": "📈 Forex Trading Scam",
            "ui_description": "Get-rich-quick scheme targeting young adults",
        },
        {
            "scenario_type": "stock_tip",
            "message": "BUY INFY NOW! Stock will go to ₹3000 this week. Tips here: stock-alerts.top/premium",
            "amount": 2999,
            "tip": "No one can predict stock movements - this is insider trading or manipulation",
            "risk_level": "high",
            "ui_title": "📊 Stock Tip Scam",
            "ui_description": "Fake stock trading advice to lure users",
        },
    ]
    
    # Delivery/E-commerce fraud
    DELIVERY_SCENARIOS = [
        {
            "scenario_type": "customs_fee",
            "message": "IndiaPost: Unpaid customs fee ₹450. Pay now: track-package.site/fee",
            "amount": 450,
            "tip": "Postal services never collect fees via links - always call them directly",
            "risk_level": "medium",
            "ui_title": "📦 Fake Delivery Fee",
            "ui_description": "Smishing attack claiming unpaid customs",
        },
        {
            "scenario_type": "flipkart_refund",
            "message": "Flipkart refund pending. Provide bank details: flipkart-refund-portal.com/verify",
            "amount": 0,
            "tip": "E-commerce sites refund to original payment method - they never ask for bank details",
            "risk_level": "high",
            "ui_title": "📱 Flipkart Refund Scam",
            "ui_description": "Fake refund request to steal bank details",
        },
    ]
    
    # Utility/Government impersonation
    UTILITY_SCENARIOS = [
        {
            "scenario_type": "electricity_threat",
            "message": "⚡ URGENT: Your electricity will disconnect at 9 PM due to unpaid bill. Call: +91-9876543210",
            "amount": 12500,
            "tip": "Government agencies never threaten immediate disconnection via SMS",
            "risk_level": "high",
            "ui_title": "⚡ Electricity Disconnection",
            "ui_description": "High-pressure tactic forcing you to call a fake number",
        },
        {
            "scenario_type": "income_tax",
            "message": "⚠️ INCOME TAX ALERT: Unpaid taxes ₹95,000. Clear now: incometax-portal-india.gov.in",
            "amount": 95000,
            "tip": "IT dept sends notices by registered post - not SMS/email",
            "risk_level": "critical",
            "ui_title": "🏛️ Income Tax Scam",
            "ui_description": "Government impersonation for tax extortion",
        },
    ]
    
    # OTP/Authentication fraud
    OTP_SCENARIOS = [
        {
            "scenario_type": "otp_sharing",
            "message": "Google: Someone tried to access your account. Reply with: 123456 to confirm",
            "amount": 0,
            "tip": "NEVER share OTPs - even with official-looking messages",
            "risk_level": "critical",
            "ui_title": "🔐 OTP Phishing",
            "ui_description": "Attempt to steal your authentication codes",
        },
        {
            "scenario_type": "recovery_code",
            "message": "Verify your Instagram. Recovery code needed: 847923. Reply only to this chat.",
            "amount": 0,
            "tip": "Social media never asks for recovery codes via message - that IS the scam",
            "risk_level": "critical",
            "ui_title": "📸 Instagram Recovery Scam",
            "ui_description": "Stealing account recovery codes",
        },
    ]
    
    # Job fraud
    JOB_SCENARIOS = [
        {
            "scenario_type": "work_from_home",
            "message": "🏠 Work from home! Earn ₹500/hour data entry. Register: jobs-now.site/apply Fee: ₹999",
            "amount": 999,
            "tip": "Real jobs don't require upfront fees - that's the scam",
            "risk_level": "medium",
            "ui_title": "💼 Work From Home Scam",
            "ui_description": "Fake job posting to collect registration fees",
        },
        {
            "scenario_type": "interview_fee",
            "message": "Congratulations! You're selected at Google. Pay ₹5000 for interview kit: google-interviews.co/pay",
            "amount": 5000,
            "tip": "Google doesn't charge for interviews - legitimate companies never do",
            "risk_level": "critical",
            "ui_title": "🏢 Google Interview Scam",
            "ui_description": "Company impersonation to extract fees",
        },
    ]
    
    # Romance/Relationship fraud
    ROMANCE_SCENARIOS = [
        {
            "scenario_type": "dating_app",
            "message": "Hi! I really like your profile. Download my photo app: photo-dating.site/app",
            "amount": 0,
            "tip": "Romance scammers build trust then ask for money or steal data",
            "risk_level": "high",
            "ui_title": "💔 Romance Scam",
            "ui_description": "Catfishing to extract money or data",
        },
    ]
    
    # Loan/Credit fraud
    LOAN_SCENARIOS = [
        {
            "scenario_type": "instant_loan",
            "message": "✨ Instant personal loan ₹50,000 approved! No documents needed. Get cash: quick-loan.app/activate",
            "amount": 0,
            "tip": "Banks require documents - no legitimate lender skips this",
            "risk_level": "high",
            "ui_title": "💳 Instant Loan Scam",
            "ui_description": "Fake lending app to collect personal data",
        },
    ]
    
    # Deepfake/Impersonation
    DEEPFAKE_SCENARIOS = [
        {
            "scenario_type": "ceo_fraud",
            "message": "Hi, This is your CEO. Send ₹2,00,000 to this account urgently for acquisition. Don't tell anyone!",
            "amount": 200000,
            "tip": "CEOs never request money via personal messages - verify via official channels",
            "risk_level": "critical",
            "ui_title": "🎭 CEO Impersonation",
            "ui_description": "Business email compromise targeting employees",
        },
    ]
    
    ALL_SCENARIOS = (
        PHISHING_SCENARIOS +
        INVESTMENT_SCENARIOS +
        DELIVERY_SCENARIOS +
        UTILITY_SCENARIOS +
        OTP_SCENARIOS +
        JOB_SCENARIOS +
        ROMANCE_SCENARIOS +
        LOAN_SCENARIOS +
        DEEPFAKE_SCENARIOS
    )
    
    @classmethod
    def generate_random_scenario(cls) -> Dict[str, Any]:
        """Generate a random fallback scenario."""
        scenario = random.choice(cls.ALL_SCENARIOS).copy()
        
        # Add UI components
        scenario["recommended_actions"] = [
            {"label": "💳 Pay Now", "action_id": "pay", "type": "danger"},
            {"label": "🛑 Block & Ignore", "action_id": "ignore", "type": "warning"},
            {"label": "🔍 Analyze Message", "action_id": "analyze", "type": "cyber"},
        ]
        
        scenario["await_user_response"] = True
        scenario["is_fallback"] = True
        scenario["generated_at"] = datetime.utcnow().isoformat()
        
        return scenario
    
    @classmethod
    def generate_scenario_by_type(cls, scenario_type: str) -> Dict[str, Any]:
        """Generate a specific scenario type."""
        matching = [s for s in cls.ALL_SCENARIOS if s.get("scenario_type") == scenario_type]
        
        if not matching:
            return cls.generate_random_scenario()
        
        scenario = random.choice(matching).copy()
        scenario["recommended_actions"] = [
            {"label": "💳 Pay Now", "action_id": "pay", "type": "danger"},
            {"label": "🛑 Block & Ignore", "action_id": "ignore", "type": "warning"},
            {"label": "🔍 Analyze Message", "action_id": "analyze", "type": "cyber"},
        ]
        
        scenario["await_user_response"] = True
        scenario["is_fallback"] = True
        scenario["generated_at"] = datetime.utcnow().isoformat()
        
        return scenario
    
    @classmethod
    def get_all_scenario_types(cls) -> List[str]:
        """Get all available scenario types for learning modules."""
        return list(set([s["scenario_type"] for s in cls.ALL_SCENARIOS]))


# Initialize engine
fallback_engine = FallbackScenarioEngine()
