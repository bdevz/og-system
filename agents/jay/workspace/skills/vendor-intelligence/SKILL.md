# Vendor Intelligence skill

Classifies vendors and maintains vendor knowledge base.

## Script

### vendor_classifier.py
Classifies a vendor into tier (1/2/3/unknown) and returns known information. Accepts vendor name, returns tier + performance metrics.

Call `classify_vendor(vendor_name)` to get tier and known info.

**Vendor Tiers:**
- **Tier 1:** Top-tier established vendors (Insight Global, Robert Half, TEKsystems, Infosys, Cognizant, TCS, Wipro, Accenture)
- **Tier 2:** Regional specialists and growing vendors with good track records
- **Tier 3:** Small vendors and body shops with higher risk
- **Unknown:** Vendors not yet in knowledge base

**Output includes:**
- Tier classification
- Response rate (% of submissions that get response)
- Ghost rate (% of submissions with no follow-up after 14 days)
- Known clients
- Placement count
- Confidence of classification

## Knowledge base
Maintains vendor-database.md as the source of truth. Updated from submission outcomes and manual research.

## Rules
- Never modify vendor classifications without data.
- Unknown vendors trigger escalation to EM for manual research.
- Tier 1 vendors get +1.5 confidence boost in scoring.
- Tier 3 vendors get -1.0 confidence penalty in scoring.
- Ghost rate threshold: >50% = likely dead/inactive vendor.
- Update vendor-database.md weekly based on submission outcomes.
