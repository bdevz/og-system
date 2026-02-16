# Skill: Inbound Message Classifier

## Purpose

Classify inbound LinkedIn messages within 15 minutes and route them appropriately: Class A (HOT) to Rick immediately, Class B (WARM) to Rick within 2 hours, Class C (NETWORKING) to accept/log, Class D (SPAM) to ignore, Class E (SUSPICIOUS) to alert human immediately.

## What it does

- Analyzes sender profile (title, company, history)
- Parses message text for keywords, specificity, intent
- Applies deterministic classification rules
- Returns classification, confidence, routing instruction, and opportunity summary
- Logs every classification for audit trail

## Why it matters

Recruiters with real opportunities are time-sensitive. A 15-minute response window can mean the difference between a qualified lead and a missed opportunity. Spam and scams waste time. Trust & Safety alerts require immediate action to protect account.

## How to use it

### Single message classification

```python
from inbound_classifier.message_classifier import classify_message

result = classify_message({
    "message_id": "MSG-1234",
    "profile_id": "P-001",
    "sender_name": "John Smith",
    "sender_title": "Senior Recruiter",
    "sender_company": "TechStaff Inc",
    "message_text": "Hi! We have a Python/AWS role in Boston. Are you available?",
    "timestamp": "2026-02-15T10:30:00Z"
})

print(f"Classification: {result['class_label']}")
print(f"Route to: {result['routing']['route_to']}")
print(f"SLA: {result['routing']['sla_minutes']} minutes")
```

### Batch classification

```python
from inbound_classifier.message_classifier import classify_batch

results = classify_batch([msg1, msg2, msg3, ...])

# Results sorted by priority
for msg in results:
    if msg['routing']['priority'] in ['URGENT', 'CRITICAL']:
        print(f"ACTION REQUIRED: {msg['class_label']} from {msg['sender_context']['name']}")
```

### CLI usage

```bash
# Demo with sample messages
python message_classifier.py

# Single message from JSON
python message_classifier.py single_message.json

# Batch from JSON array
python message_classifier.py message_batch.json
```

## Classification system

### Class A: HOT (Urgent)
**Indicators:**
- Recruiter title (Technical Recruiter, Staffing Manager, etc.)
- **AND** specific tech mention OR availability question
- **AND** Tier 1 or Tier 2 staffing firm OR known good company

**Confidence:** 0.85-1.0

**Example:**
```
"Hi! We have a great Python/AWS role for a senior developer in Boston.
The client is looking for someone who can start immediately. Are you available?"
```

**SLA:** 15 minutes

**Action:** Route to Rick immediately with full sender and opportunity context

---

### Class B: WARM (High)
**Indicators:**
- Recruiter title without strong indicators, OR
- HR title (but not dedicated recruiter), AND
- Opportunity mention (vague role, opportunity, project), OR
- Connection request with opportunity note

**Confidence:** 0.50-0.85

**Example:**
```
"Hi! I'd like to connect. We have some exciting tech opportunities
that might interest you based on your background."
```

**SLA:** 2 hours

**Action:** Queue for Rick evaluation within 2-hour window

---

### Class C: NETWORKING (Low)
**Indicators:**
- Generic connection request, OR
- Industry peer / alumni / group member, OR
- No recruiter/HR signals, no opportunity mention

**Confidence:** 0.50-0.70

**Example:**
```
"Hey! Would love to connect with fellow Python developers.
Let's stay in touch and share industry insights."
```

**SLA:** None (no SLA)

**Action:** Accept and log. No escalation to Rick.

---

### Class D: SPAM (Ignore)
**Indicators:**
- MLM keywords OR
- Insurance mention OR
- Generic sales pitch language, OR
- Mass InMail pattern

**Confidence:** 0.80-0.95

**Example:**
```
"Limited time offer! Get life insurance coverage today.
Don't miss out on this exclusive deal!"
```

**SLA:** None

**Action:** Ignore and log as spam

---

### Class E: SUSPICIOUS (Critical)
**Indicators:**
- LinkedIn Trust & Safety language OR
- Verification/identity confirmation request OR
- Unusual activity warning OR
- Account security alert

**Confidence:** 1.0

**Example:**
```
"Verify your account identity immediately due to unusual activity
detected on your account. Click here to confirm."
```

**SLA:** 5 minutes (CRITICAL)

**Action:** Stop all activity immediately. Alert human and Z. Quarantine profile.

## Input schema

```json
{
  "message_id": "MSG-1234",
  "profile_id": "P-001",
  "sender_name": "John Smith",
  "sender_title": "Senior Technical Recruiter",
  "sender_company": "TechStaff Inc",
  "sender_id": "SEND-5678",
  "message_text": "Hi! We have a Python/AWS role...",
  "timestamp": "2026-02-15T10:30:00Z"
}
```

### Field descriptions

- **message_id**: Unique identifier for the message
- **profile_id**: Which LinkedIn profile received the message
- **sender_name**: Name of the person sending message
- **sender_title**: Their job title
- **sender_company**: Their company
- **sender_id**: Their LinkedIn ID (optional)
- **message_text**: Full text of the message
- **timestamp**: When received (ISO-8601)

## Output schema

```json
{
  "message_id": "MSG-1234",
  "profile_id": "P-001",
  "classification": "A",
  "class_label": "HOT",
  "confidence": 0.92,
  "reasoning": [
    "recruiter_title",
    "specific_tech: Python, AWS",
    "availability_question",
    "tier1_firm"
  ],
  "routing": {
    "route_to": "rick",
    "priority": "URGENT",
    "sla_minutes": 15,
    "action": "evaluate"
  },
  "sender_context": {
    "name": "John Smith",
    "title": "Senior Technical Recruiter",
    "company": "TechStaff Inc",
    "sender_id": "SEND-5678",
    "company_tier": "TIER_1"
  },
  "opportunity_summary": "Python, AWS role, Boston",
  "timestamp": "2026-02-15T10:30:00Z",
  "classified_at": "2026-02-15T10:32:15Z"
}
```

## Keyword lists

### Recruiter titles
recruiter, technical recruiter, it recruiter, talent acquisition, staffing, headhunter, sourcerer, vendor, staffing manager, recruiting consultant, account manager, account executive

### Specific tech/role keywords
Java, Python, C++, C#, JavaScript, TypeScript, React, Angular, Vue, Node.js, Django, Flask, Spring, Docker, Kubernetes, AWS, Azure, GCP, microservices, DevOps, SQL, NoSQL, MongoDB, role, position, opportunity, contract, full time, project

### Availability keywords
available, interested, open to, looking for, seeking, exploring, immediate, asap, start date, notice period, rate, salary

### Tier 1 firms
Cognizant, Infosys, TCS, Wipro, Accenture, Deloitte, PWC, KPMG, IBM, Microsoft, Google, Amazon, JPMorgan, Goldman Sachs

### Tier 2 firms
Stripe, Figma, Databricks, Okta, Twilio, New Relic, Qualcomm, NVIDIA

### MLM keywords
MLM, multi-level marketing, herbalife, amway, younique, monat, rodan, lularoe, itworks

### Insurance keywords
Insurance, life insurance, health insurance, policy, premium, coverage, underwriting, allstate, state farm, progressive

### Sales pitch keywords
Special offer, limited time, exclusive deal, click here, learn more, sign up now, buy now, free trial, money back, guarantee, earn money, work from home, passive income

### Trust & Safety keywords
LinkedIn trust, LinkedIn safety, verification, confirm identity, verify account, unusual activity, unauthorized access, security alert

## Classification algorithm

1. **Check for E (SUSPICIOUS)** - If any Trust & Safety keyword found, return Class E immediately
2. **Check for D (SPAM)** - If MLM, insurance, or sales pitch keywords found, return Class D
3. **Check for A (HOT)** - Score based on recruiter title + (tech OR availability) + (tier1 OR tier2)
   - If score >= 0.7: Return Class A
4. **Check for B (WARM)** - Score based on recruiter/HR + opportunity mention
   - If score >= 0.5: Return Class B
5. **Check for C (NETWORKING)** - If any generic connection/peer/group signals found, return Class C
6. **Default to C** - If no other match, classify as generic networking

## Confidence scoring

- **0.95-1.0**: Very high confidence (recruiter + strong tech + availability + tier1 firm)
- **0.85-0.94**: High confidence (recruiter + tech/availability + tier firm)
- **0.70-0.84**: Medium-high confidence (recruiter with some indicators)
- **0.50-0.69**: Medium confidence (some recruiter signals or opportunity mention)
- **< 0.50**: Low confidence (generic message)

## Opportunity extraction

For Class A and B messages, the classifier extracts:
- **Tech stack**: Matched keywords from message
- **Location**: Extracted geography if mentioned
- **Role level**: Implied from language (junior, mid, senior)
- **Urgency**: Based on keywords like "immediate", "asap", "urgent"

## Batch processing

When classifying multiple messages:
1. Sort results by priority (E > A > B > C > D)
2. Within same priority, sort by confidence (descending)
3. This order tells you what to handle first

## Performance

- Single message: <50ms
- Batch of 100: <5s
- Memory efficient, no database calls

## Error handling

- Missing sender_title: Treated as non-recruiter
- Missing message_text: Classified as low-confidence
- Empty fields: Skipped without error
- Invalid timestamp: Uses current time

## Integration points

- **Inbound Monitor**: Receives new messages and sends to classifier
- **Leroy Core**: Reviews classifications, routes to Rick or alerts
- **Rick**: Receives Class A/B leads within SLA
- **Human/EM**: Receives Class E alerts immediately
- **Logging**: Every classification appended to history

## SLA enforcement

- **Class A (HOT):** Must route to Rick within 15 minutes
- **Class B (WARM):** Must route to Rick within 2 hours
- **Class E (SUSPICIOUS):** Must alert human within 5 minutes
- **Class C/D:** No SLA, process in batch

## Future enhancements

- Machine learning scoring (retrain on historical classifications)
- Reputation tracking (build history per sender)
- Budget/rate mention detection
- Contract length mention detection
- Client confidentiality keywords
