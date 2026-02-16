# LinkedIn Identity Map

Maps real consultants to their marketing LinkedIn profiles. Maintained by Z. Leroy manages profile health; Z tracks the mapping and rotation.

## Format

```
Consultant: [Legal Name] (ID: [internal ID])
+-- Profile 1: [Marketing Name]
|   +-- LinkedIn URL: [url]
|   +-- Ads Power Profile ID: [reference]
|   +-- Proxy: [proxy identifier]
|   +-- Status: Active / Cooldown / Restricted / Dead
|   +-- Last used for application: [date]
|   +-- Application count (last 7 days): [number]
|   +-- Notes: [positioning focus]
+-- Profile 2: ...
```

## Rotation rules
- Don't use the same profile for more than the daily limit per tier.
- Rotate profiles across different job categories when possible.
- If a profile enters cooldown, Z flags it and reassigns to next available.
- Z does NOT fix restricted profiles -- that's Leroy's job.

## Active mappings

(Populated when CRM data is ingested and profiles are assigned)
