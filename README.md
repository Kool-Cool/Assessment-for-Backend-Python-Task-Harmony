# Backend / AI Engineer Assessment

## Candidate
**Name:** Omkar  
**Email:** omkarjadhav@gmail.com  
**GitHub:** https://github.com/Kool-Cool  
**LinkedIn:** https://www.linkedin.com/in/omkar-jadhav-399158227/

---

# 1. Problem Statement

Design and build a system to extract structured logistics data from unstructured emails using LLMs, ensuring:

- High extraction accuracy across heterogeneous formats  
- Scalable system for high throughput  
- Low cost operation (< $500/month constraint)  
- Observability and monitoring  
- Multilingual support  

---

# 2. System Overview

## High-Level Pipeline

Email Ingestion → Queue (Kafka / SQS) → Worker Fleet (Containerized) → LLM Inference (Groq API) → Schema Validator → NoSQL Storage → Metrics + Monitoring

---

# 3. Core Design

## 3.1 Processing Strategy

- Async queue-based architecture decouples ingestion and processing  
- Horizontally scalable worker pool  
- Backpressure handling via queue depth  
- Batch inference for cost optimization  

---

## 3.2 Extraction Strategy

- Prompt-engineered structured extraction using LLMs  
- Schema-constrained output validation  
- Iterative prompt refinement based on failure cases  
- Hybrid logic:
  - fuzzy matching for port codes  
  - alias resolution for product lines  
  - rule-based overrides for ambiguous routes  

---

## 3.3 Scalability Model

- Stateless workers for horizontal scaling  
- Autoscaling based on queue lag  
- Multi-threading / multi-processing depending on deployment  
- Designed to maintain 5-minute SLA under burst traffic  

---

# 4. Data Storage

- NoSQL (MongoDB / DynamoDB)  
- Stores:
  - raw email  
  - structured extraction output  
  - validation logs  

---

# 5. Performance Metrics

## Classification Metrics

product_line: 1.000 / 1.000  
incoterm: 0.960 / 0.960  
origin_port_code: 0.905 / 0.906  
destination_port_code: 0.740 / 0.815  
is_dangerous: 1.000 / 1.000  

---

## Numeric Metrics

cargo_weight_kg: MAE 0.00 (5%: 1.00, 10%: 1.00)  
cargo_cbm: MAE 0.00 (5%: 1.00, 10%: 1.00)  

---

## End-to-End Accuracy

0.56

---

# 6. Prompt Evolution

## v1
- Accuracy: 5%  
- Issues:
  - incorrect port codes  
  - missing incoterms  
- Example:
  "Chennai" → "INMAA"

---

## v2
- Accuracy: 20%  
- Added UN/LOCODE examples  
- Issues:
  - regional port detection errors  

---

## v4
- Accuracy: 56%  
- Added business rules  
- Remaining edge cases (EMAIL_043 class)

---

# 7. Edge Cases Handled

- Duplicate port reference conflicts → fuzzy matching  
- Product line alias normalization  
- Multi-route ambiguity resolved via prompt rules  

---

# 8. Monitoring & Observability

- Field-level accuracy tracking  
- Record-level accuracy tracking  
- Drift detection across email formats  

Tools:
- Grafana  
- Prometheus  

Alerts:
- Accuracy < 85% triggers alert  
- Debug via:
  - field-level breakdown  
  - input drift detection  
  - prompt regression analysis  

---

# 9. Multilingual Support

## Approach

Option 1: Multilingual LLM  
Option 2: Translation pipeline (Hindi/Mandarin → English)

## Evaluation

- Separate datasets:
  - English  
  - Hindi  
  - Mandarin  

- Track per-language accuracy  

---

# 10. Key Engineering Decisions

- Queue-based architecture for scalability  
- Schema validation layer for structured outputs  
- Iterative prompt optimization  
- Observability-first design  
- Cost-aware batching strategy  

---

# 11. Tradeoffs

- Accuracy vs cost constraints  
- Latency vs throughput  
- Prompt complexity vs maintainability  

---

# 12. Summary

Production-grade LLM extraction system featuring:

- Scalable async architecture  
- Structured output enforcement  
- Prompt iteration lifecycle  
- Monitoring + drift detection  
- Multilingual readiness  