# Ubiquitous Language

## Core artifact and structure

| Term | Definition | Aliases to avoid |
| --- | --- | --- |
| **Calendar Table** | A generated dataset with one row per calendar date and many derived date attributes for analytics and control logic. | Date Dimension (as primary), Date Table |
| **Calendar Date** | The base date key for one row in the Calendar Table from which all derived fields are computed. | dt row, raw date |
| **Date Attribute** | A computed field derived from Calendar Date that captures period, sequence, or label semantics. | Column, metadata field |
| **Period Key** | A compact numeric identifier for a period such as yearmonth or yearquarter. | Surrogate key, bucket id |

## Business day semantics

| Term | Definition | Aliases to avoid |
| --- | --- | --- |
| **Weekday** | A date that falls on Monday through Friday under the fixed weekend model. | Business day |
| **Holiday Calendar** | A configurable set of holiday rules used to classify dates as holidays. | Static holiday list |
| **Holiday** | A date matched by the active Holiday Calendar rules. | Day off |
| **Workday** | A Weekday that is not a Holiday under the active Holiday Calendar. | Weekday |
| **Workday of Month** | The ordinal count of Workdays elapsed in a month up to and including a date. | Business day index |
| **Workday of Year** | The ordinal count of Workdays elapsed in a year up to and including a date. | Business day index |

## Astronomical and temporal enrichment

| Term | Definition | Aliases to avoid |
| --- | --- | --- |
| **Moon Phase** | The named phase state and numeric index for the moon on a Calendar Date. | Lunar status |
| **Moon Illumination** | The percent of the moon illuminated on a Calendar Date. | Moon brightness |
| **Sunrise UTC** | Sunrise timestamp for the configured coordinates in UTC reference time. | UTC sunrise clock |
| **Sunset UTC** | Sunset timestamp for the configured coordinates in UTC reference time. | UTC sunset clock |
| **Sunlight Duration** | The elapsed daylight time between sunrise and sunset for a date and reference frame. | Day length |
| **Darkness Duration** | The non-daylight duration in a 24-hour day for a date and reference frame. | Night length |

## Generation lifecycle

| Term | Definition | Aliases to avoid |
| --- | --- | --- |
| **Generation Window** | The inclusive start and end date range used to build a Calendar Table run. | Date filter |
| **Calendar Table Run** | One execution of the generator that materializes rows and derived attributes for a Generation Window. | Job, batch |
| **Created On** | The run timestamp captured when the Calendar Table is generated. | Build time |
| **Column Dictionary** | Documentation artifact describing each Calendar Table field and datatype. | Data dictionary (generic), column docs file |

## Relationships

- A **Calendar Table** contains exactly one row per **Calendar Date** in a **Generation Window**.
- A **Calendar Date** maps to many **Date Attributes**.
- A **Holiday Calendar** classifies zero or more **Calendar Date** values as **Holiday**.
- A **Workday** is derived from **Weekday** and **Holiday** classification.
- A **Calendar Table Run** produces one **Calendar Table** output and one **Column Dictionary** output.

## Example dialogue

> **Dev:** "For this report, should we join on the **Calendar Table** or build month fields ad hoc?"
>
> **Domain expert:** "Join on the **Calendar Table** so **Workday of Month** and period keys stay consistent."
>
> **Dev:** "If we expand to another region, does **Holiday** still mean the current US list?"
>
> **Domain expert:** "No, **Holiday** comes from a configurable **Holiday Calendar**, but **Weekday** remains Monday through Friday."
>
> **Dev:** "So **Workday** is still Weekday minus Holiday, just with a different Holiday Calendar?"
>
> **Domain expert:** "Exactly."

## Flagged ambiguities

- "Calendar Table" and "Date Dimension" were both used for the same artifact. Canonical term is **Calendar Table**.
- "Weekday" and "Workday" are often conflated. **Weekday** is calendar-based (Mon-Fri), while **Workday** excludes holidays from the active **Holiday Calendar**.
- "Holiday" previously implied a fixed US rule set in code; domain language now treats it as configurable via **Holiday Calendar**.
