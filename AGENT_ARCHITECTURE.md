# Kavach AI – Agent Architecture Guide

## Overview

This document outlines the modular agent architecture for Kavach AI, transitioning from single-prompt approaches to a specialized, coordinator-based multi-agent system.

---

## Current Architecture (v1)

```
User Input
    ↓
Forensic Agent (Monolithic Prompt)
    ↓
Single Response
```

**Issues:**
- ❌ One giant prompt = inefficient
- ❌ No specialization
- ❌ Hard to route different threat types
- ❌ Poor token efficiency
- ❌ Limited extensibility

---

## Recommended Architecture (v2+)

### System Design

```
┌──────────────────────────────────────────────────┐
│                  COORDINATOR AGENT               │
│  • Classifies threat type & severity             │
│  • Routes to appropriate specialized agents      │
│  • Aggregates responses                          │
└────────┬─────────────────────────────────────────┘
         │
         ├─────────────────────────────────────────┐
         │                                         │
         ↓                                         ↓
┌──────────────────────────┐      ┌──────────────────────────┐
│   INFILTRATOR AGENT      │      │    FORENSIC AGENT        │
│  (Attack Simulator)      │      │  (Scam Analyzer)         │
├──────────────────────────┤      ├──────────────────────────┤
│ Shows HOW the attack     │      │ Explains WHY it's a scam │
│ works via simulation     │      │ • Tactic breakdown       │
│ • Step-by-step demo     │      │ • Red flag analysis      │
│ • Interactive examples  │      │ • Historical context     │
│ • Real attack vectors   │      │ • Confidence scoring     │
└──────────────────────────┘      └──────────────────────────┘
         │                                         │
         └─────────────────────────────────────────┘
                     │
                     ↓
        ┌──────────────────────────┐
        │    MENTOR AGENT          │
        │  (Defense Educator)      │
        ├──────────────────────────┤
        │ Teaches counter-measures │
        │ • Defense strategies     │
        │ • Best practices         │
        │ • Real-world examples    │
        │ • Action items           │
        └──────────────────────────┘
                     │
                     ↓
            ┌─────────────────┐
            │  User Response  │
            │  (Comprehensive │
            │   Education)    │
            └─────────────────┘
```

### Agent Responsibilities

#### 1. Coordinator Agent
**Purpose:** Orchestrate the analysis workflow

```python
class CoordinatorAgent(AgentManager):
    """
    Entry point for threat analysis.
    Classifies threat type and decides which agents to invoke.
    """
    
    def classify_threat(self, user_input: str) -> dict:
        """
        Returns:
        {
            "threat_type": "PHISHING|MALWARE|SCAM|SOCIAL_ENGINEERING|SAFE",
            "severity": "CRITICAL|HIGH|MEDIUM|LOW|NONE",
            "confidence": 0.95,
            "triage_notes": "..."
        }
        """
        pass
    
    def route_analysis(self, threat_data: dict) -> list:
        """Determine which agents to invoke"""
        pass
```

#### 2. Infiltrator Agent
**Purpose:** Demonstrate attack techniques

```python
class InfiltratorAgent(AgentManager):
    """
    Shows HOW attacks work through simulation.
    """
    
    def simulate_attack(self, threat_input: str) -> dict:
        """
        Returns:
        {
            "attack_name": "Phishing Campaign",
            "steps": [
                {"step": 1, "action": "...", "technical_detail": "..."},
                ...
            ],
            "success_factors": ["factor1", "factor2"],
            "typical_payload": "...",
            "example_variations": ["var1", "var2"]
        }
        """
        pass
```

#### 3. Forensic Agent
**Purpose:** Deep technical analysis

```python
class ForensicAgent(AgentManager):
    """
    Analyzes WHAT is being used and WHY it's dangerous.
    """
    
    def analyze_threat(self, threat_input: str) -> dict:
        """
        Returns:
        {
            "classification": "SCAM",
            "confidence": 0.95,
            "tactics_used": [
                {
                    "tactic": "Urgency Creation",
                    "description": "...",
                    "indicator": "Limited time offer",
                    "severity": "HIGH"
                },
                ...
            ],
            "red_flags": ["flag1", "flag2"],
            "similar_campaigns": ["previous_scam_id_1"],
            "historical_context": "..."
        }
        """
        pass
```

#### 4. Mentor Agent
**Purpose:** Educational defense strategies

```python
class MentorAgent(AgentManager):
    """
    Teaches users HOW TO DEFEND against threats.
    """
    
    def teach_defense(self, threat_analysis: dict) -> dict:
        """
        Returns:
        {
            "counter_measures": [
                {
                    "action": "Never click links...",
                    "why": "...",
                    "level": "BEGINNER|INTERMEDIATE|ADVANCED",
                    "impact": "CRITICAL|HIGH"
                },
                ...
            ],
            "best_practices": ["practice1", "practice2"],
            "tools_to_use": ["tool1", "tool2"],
            "action_items": ["item1", "item2"],
            "success_criteria": "..."
        }
        """
        pass
```

---

## Implementation Plan

### Phase 1: Setup (Immediate)

1. Create agent class structure in `backend/agents/`:
   ```
   backend/agents/
   ├── __init__.py
   ├── agent_manager.py (existing)
   ├── coordinator.py       (NEW)
   ├── infiltrator.py       (NEW)
   ├── forensic.py          (NEW)
   └── mentor.py            (NEW)
   ```

2. Create coordinator route in `backend/main.py`:
   ```python
   @app.post("/analyze")
   def analyze_comprehensive(data: MessageInput):
       """Full multi-agent analysis"""
       coordinator = CoordinatorAgent()
       result = coordinator.analyze(data.text)
       return api_response(True, result)
   ```

### Phase 2: Migration (Week 1-2)

1. Keep existing endpoints working (backward compatibility)
2. Add new `/analyze` endpoint (uses multi-agent)
3. Frontend can use either endpoint initially
4. Gradually migrate frontend to new endpoints

### Phase 3: Optimization (Week 2-3)

1. Add caching for threat classifications
2. Implement LLM token counting
3. Add response time metrics
4. Optimize prompts for each agent

---

## Prompt Engineering Guide

### Coordinator Prompt Template

```
You are a threat classification specialist. Your job is to:
1. Read the message
2. Determine threat type
3. Assess severity

Be concise. Return JSON only.

Message: {user_input}

Return:
{{
  "threat_type": "PHISHING|MALWARE|SCAM|SOCIAL_ENGINEERING|SAFE",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW|NONE",
  "confidence": 0.0-1.0,
  "triage_notes": "Why you classified it this way"
}}
```

### Infiltrator Prompt Template

```
You are a red team operator demonstrating attack techniques.
DO NOT provide actual malware or illegal information.
ONLY show how the attack mechanism works educationally.

Show how this attack works:
{threat_analysis}

Return:
{{
  "attack_name": "...",
  "steps": [
    {{"step": 1, "action": "...", "technical_detail": "..."}}
  ],
  "success_factors": ["..."],
  "typical_payload": "...",
  "example_variations": ["..."]
}}
```

### Forensic Prompt Template

```
You are a cybersecurity forensic analyst.
Provide technical, detailed analysis of this threat.

Message: {user_input}

Analyze:
1. Tactics used (What techniques?)
2. Indicators (Red flags? Pattern?)
3. Historical context (Seen before?)
4. Confidence level (0-1)

Return:
{{
  "classification": "SCAM|SAFE|PHISHING|etc",
  "confidence": 0.0-1.0,
  "tactics_used": [
    {{"tactic": "...", "description": "...", "indicator": "...", "severity": "HIGH"}}
  ],
  "red_flags": ["..."],
  "similar_campaigns": ["..."],
  "historical_context": "..."
}}
```

### Mentor Prompt Template

```
You are a cybersecurity educator. The user is learning to defend against threats.

Threat to defend against:
{threat_analysis}

Teach them:
1. What to do (concrete actions)
2. Why to do it (reasoning)
3. Best practices (general principles)
4. Tools (what can help)

Return:
{{
  "counter_measures": [
    {{"action": "...", "why": "...", "level": "BEGINNER", "impact": "CRITICAL"}}
  ],
  "best_practices": ["..."],
  "tools_to_use": ["..."],
  "action_items": ["..."],
  "success_criteria": "..."
}}
```

---

## Implementation Example

### File: `backend/agents/coordinator.py`

```python
from agent_manager import AgentManager
from infiltrator import InfiltratorAgent
from forensic import ForensicAgent
from mentor import MentorAgent
import json

class CoordinatorAgent(AgentManager):
    def __init__(self):
        super().__init__("Coordinator")
        self.infiltrator = InfiltratorAgent()
        self.forensic = ForensicAgent()
        self.mentor = MentorAgent()
    
    def analyze(self, user_input: str) -> dict:
        """Main orchestration method"""
        
        # Step 1: Classify threat
        classification = self._classify(user_input)
        
        # Step 2: Deep forensic analysis
        forensic_analysis = self.forensic.analyze(user_input)
        
        # Step 3: Show attack simulation (if it's a threat)
        infiltrator_data = None
        if classification["threat_type"] != "SAFE":
            infiltrator_data = self.infiltrator.simulate(user_input)
        
        # Step 4: Teach defense
        mentor_data = self.mentor.teach(forensic_analysis, classification)
        
        # Step 5: Aggregate response
        return {
            "classification": classification,
            "forensic_analysis": forensic_analysis,
            "attack_simulation": infiltrator_data,
            "defense_strategies": mentor_data,
            "workflow_complete": True
        }
    
    def _classify(self, user_input: str) -> dict:
        """Classify threat type and severity"""
        prompt = f"""
        Classify this message:
        
        Message: {user_input}
        
        Return JSON:
        {{"threat_type": "PHISHING|MALWARE|SCAM|SOCIAL_ENGINEERING|SAFE",
          "severity": "CRITICAL|HIGH|MEDIUM|LOW|NONE",
          "confidence": 0-1,
          "triage_notes": "..."}}
        """
        
        response = self.send_message(prompt)
        # Parse JSON response
        return json.loads(response)
```

### File: `backend/main.py` (New Endpoint)

```python
@app.post("/analyze")
def comprehensive_analysis(data: MessageInput):
    """Multi-agent comprehensive analysis"""
    try:
        coordinator = CoordinatorAgent()
        result = coordinator.analyze(data.text)
        
        # Log to analytics
        log_agent_output(
            agent_name="Coordinator",
            prompt=data.text[:500],
            response=str(result)[:1000],
            response_time_ms=0,
            metadata={"workflow": "multi-agent"}
        )
        
        return api_response(True, result, "Analysis complete")
    
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Token Efficiency

### Cost Comparison

**Single-Agent (Current):**
```
Input Tokens:   500 (user message + 1 prompt)
Output Tokens:  300
Cost per call:  ~$0.002
```

**Multi-Agent (Optimized):**
```
Coordinator:    200 input  + 50 output
Forensic:       300 input  + 200 output
Infiltrator:    300 input  + 150 output
Mentor:         500 input  + 200 output
─────────────────────────────────────
Total:          1,300 input + 600 output
Cost per call:  ~$0.015 (7.5x more expensive!)
```

### Optimization Strategies

1. **Cache Coordinator Results**
   ```python
   @cache(ttl=3600)
   def classify_threat(user_input):
       # Classification rarely changes
       pass
   ```

2. **Parallel Execution**
   ```python
   import asyncio
   
   async def analyze(user_input):
       forensic_task = asyncio.create_task(forensic.analyze(user_input))
       infiltrator_task = asyncio.create_task(infiltrator.simulate(user_input))
       
       results = await asyncio.gather(forensic_task, infiltrator_task)
       return results
   ```

3. **Smart Routing**
   ```python
   # Don't run Infiltrator for "SAFE" classifications
   if classification["threat_type"] == "SAFE":
       # Skip infiltrator, save tokens
       infiltrator_data = None
   ```

4. **Response Streaming**
   ```python
   @app.post("/analyze-stream")
   async def analyze_streaming(data: MessageInput):
       # Stream responses as they come
       # User sees results incrementally
       pass
   ```

---

## Monitoring & Metrics

### Track These Metrics

```python
metrics = {
    "classification_accuracy": 0.94,
    "avg_response_time_ms": 2500,
    "token_usage": {
        "total_input": 1300,
        "total_output": 600,
        "estimated_cost": 0.015
    },
    "agent_performance": {
        "coordinator": {"time_ms": 400, "tokens": 250},
        "forensic": {"time_ms": 800, "tokens": 500},
        "infiltrator": {"time_ms": 700, "tokens": 450},
        "mentor": {"time_ms": 600, "tokens": 400}
    },
    "threat_distribution": {
        "SCAM": 0.60,
        "PHISHING": 0.20,
        "SAFE": 0.15,
        "OTHER": 0.05
    }
}
```

### Dashboard Query

```python
@app.get("/metrics")
def get_metrics(days: int = 7):
    """Get agent performance metrics"""
    return {
        "period": f"last_{days}_days",
        "metrics": get_analytics_summary(days),
        "agent_status": "all_operational",
        "estimated_monthly_cost": 50
    }
```

---

## Rollout Plan

### Week 1: Setup & Testing
- [ ] Create agent files
- [ ] Implement coordinator
- [ ] Test locally
- [ ] Internal QA

### Week 2: Alpha Deployment
- [ ] Deploy to staging
- [ ] 10% of traffic to `/analyze`
- [ ] Monitor errors & latency
- [ ] Collect metrics

### Week 3: Beta
- [ ] 50% of traffic to `/analyze`
- [ ] Gather user feedback
- [ ] Optimize prompts
- [ ] Improve performance

### Week 4: Full Rollout
- [ ] 100% traffic to new system
- [ ] Deprecate old endpoints (keep for 3 months)
- [ ] Monitor production metrics
- [ ] Plan Phase 2 improvements

---

## Success Criteria

✅ **Accuracy:** >90% threat classification  
✅ **Speed:** <5s end-to-end response  
✅ **Cost:** <$0.02 per analysis  
✅ **User Satisfaction:** >4.5/5 rating  
✅ **System Uptime:** >99.9%  

---

**Document Version:** 1.0  
**Last Updated:** May 15, 2026  
**Status:** Ready for Implementation
