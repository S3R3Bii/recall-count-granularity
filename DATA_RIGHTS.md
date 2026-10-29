# Data reuse and publication boundary

Data provided by the U.S. Food and Drug Administration through the openFDA **food enforcement** endpoint. The official licensing page and terms dedicate content/data to CC0 unless specifically noted, preserve privacy/trademark rights and disclaim endorsement. This study uses only administrative food identifiers, reporting dates and classification labels. It does not use device/GMDN material, adverse-event or patient records, third-party source-paper copies, firm addresses, descriptions or free-text recall reasons.

Complete API responses stay outside Git. Publish only five exact source fields (recall_number, event_id, report_date, classification, product_type) plus year/page/row locators, exact request URLs, timestamps, source/subset hashes and extraction/coverage certificates. Product identifiers are public regulatory identifiers, not identifiers of people. No FDA endorsement is implied.

FDA explicitly says this endpoint should not be used to issue public alerts or to track recall lifecycle status. Its current historical export can contain corrections and expansions. This research compares counting conventions in an internal, hypothetical data-review queue; it makes no public safety alert, medical, causal, prospective or lifecycle claim.

The reviewed independent manuscript can be published with this study. Separate formal-publication projects, including Azure optimization, and third-party papers remain excluded.
