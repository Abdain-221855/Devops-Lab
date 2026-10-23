# Data dictionary

Descriptions are based on the supplied CSV's column names and observed values. The blank CSV header is represented by pandas as `Unnamed: 0`. Rating labels are ordinal responses; scale endpoints should be interpreted in the context of the source survey.

| Column | Type / observed values | Description and analysis handling |
|---|---|---|
| `Unnamed: 0` | Integer, 0–103,903 | Unique contiguous row index; excluded from model features. |
| `id` | Integer, unique in supplied file | Passenger record identifier; excluded from model features. |
| `Gender` | Male, Female | Passenger-reported gender category; nominal. |
| `Customer Type` | Loyal Customer, disloyal Customer | Customer category; nominal. |
| `Age` | Integer, 7–85 | Passenger age in years; continuous numeric model input. |
| `Type of Travel` | Personal Travel, Business travel | Travel-purpose category; nominal. |
| `Class` | Eco, Eco Plus, Business | Cabin class; nominal, not treated as an ordered numeric quantity. |
| `Flight Distance` | Integer, 31–4,983 | Flight distance as supplied; numeric. |
| `Inflight wifi service` | Integer, 0–5 | In-flight Wi-Fi service rating; ordinal, modeled as standardized numeric. |
| `Departure/Arrival time convenient` | Integer, 0–5 | Convenience rating for departure/arrival time; ordinal, modeled as standardized numeric. |
| `Ease of Online booking` | Integer, 0–5 | Online-booking ease rating; ordinal, modeled as standardized numeric. |
| `Gate location` | Integer, 0–5 | Gate-location rating; ordinal, modeled as standardized numeric. |
| `Food and drink` | Integer, 0–5 | Food and drink rating; ordinal, modeled as standardized numeric. |
| `Online boarding` | Integer, 0–5 | Online-boarding rating; ordinal, modeled as standardized numeric. |
| `Seat comfort` | Integer, 0–5 | Seat-comfort rating; ordinal, modeled as standardized numeric. |
| `Inflight entertainment` | Integer, 0–5 | In-flight entertainment rating; ordinal, modeled as standardized numeric. |
| `On-board service` | Integer, 0–5 | On-board service rating; ordinal, modeled as standardized numeric. |
| `Leg room service` | Integer, 0–5 | Leg-room rating; ordinal, modeled as standardized numeric. |
| `Baggage handling` | Integer, 1–5 | Baggage-handling rating; ordinal, modeled as standardized numeric. |
| `Checkin service` | Integer, 0–5 | Check-in service rating; ordinal, modeled as standardized numeric. |
| `Inflight service` | Integer, 0–5 | In-flight service rating; ordinal, modeled as standardized numeric. |
| `Cleanliness` | Integer, 0–5 | Cleanliness rating; ordinal, modeled as standardized numeric. |
| `Departure Delay in Minutes` | Integer, 0–1,592 | Departure delay in minutes; numeric, right-skewed. |
| `Arrival Delay in Minutes` | Numeric, 0–1,584; 310 missing | Arrival delay in minutes; mean-imputed inside each training-only predictive pipeline. |
| `satisfaction` | `neutral or dissatisfied`, `satisfied` | Binary outcome. Explicit model encoding: `satisfied = 1`, `neutral or dissatisfied = 0`. |
| `TOTAL` | Derived, sum of 14 ratings | Not present in the source CSV. For the paper-table sensitivity model only, sum the 14 ordinal service-rating columns above, excluding `satisfaction`. Not used in the primary baseline because it is a redundant aggregate and may be target-adjacent. |

The paper describes `TOTAL` as the sum of all variables on the five-point satisfaction scale and lists it as a covariate in its original-variable logistic-regression table. The separately evaluated sensitivity model documents this derivation explicitly. It is not a direct sum of the binary target label.
