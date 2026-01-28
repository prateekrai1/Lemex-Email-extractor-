# Lemex-Email-extractor (LLM-Powered Freight Email Extraction)

## Overview

This project implements an LLM-powered email extraction system for freight forwarding pricing enquiries. The objective is to extract structured shipment information from unstructured emails and evaluate accuracy against a provided ground truth dataset.

The final solution combines **LLM-based raw extraction** with **deterministic post-processing logic** to handle domain-specific noise (especially port names and abbreviations).

**Final overall accuracy on provided dataset:** **91.43%**

## Setup Instructions

```bash
pip install -r requirements.txt
python extract.py      # Generates output.json
python evaluate.py     # Prints accuracy metrics
```
## Approach Summary


## Prompt Evolution
### v1-Basic Extraction
#### Accuracy 28%

Description:
Initial prompt asking the LLM to extract structured fields directly.

Issues observed:
1. Port codes often missing or incorrect

2. LLM returned raw port names instead of UN/LOCODEs

3. Product line accuracy extremely low

Example failures:

```EMAIL_004: destination extracted as "Chennai" instead of INMAA```

```EMAIL_012: "SHA" not recognized as Shanghai```

### v2 – Explicit Business Rules

Accuracy: ~~61%

Changes:

1. Added explicit business rules to the prompt

2. Listed valid incoterms

3. Clarified India import/export logic

Remaining issues:

1. Port abbreviations ```(SHA, MAA, SIN)``` still failed

2. Multi-word ports like "Xingang / Tianjin" inconsistent

3. Product line failures due to unresolved ports

Example:
```EMAIL_017: origin extracted as "SHA" but failed downstream resolution```

### v3 – Shift Logic Out of the Prompt

Accuracy: 91.43%

Key realization:
Prompt tuning alone cannot reliably normalize real-world port mentions.

Changes:

1. Simplified prompt to extract raw facts only

2. Moved normalization into deterministic Python logic

Implemented a robust PortResolver:

1. Alias mapping (SHA → CNSHA, MAA → INMAA)

2. Substring matching

3. India fallback rules

4. Canonicalized port names using port_codes_reference.json

This shift eliminated most remaining errors and generalized well to unseen data.


Final results from ```evaluate.py```:
```bash
OVERALL ACCURACY: 91.43%

product_line             : 88%
origin_port_code         : 86%
destination_port_code    : 96%
incoterm                 : 96%
cargo_weight_kg          : 82%
cargo_cbm                : 92%
is_dangerous             : 100%
```
