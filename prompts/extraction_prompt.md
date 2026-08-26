# CERD extraction prompt (v0.1 — iterate via rejected-record feedback)

Template variables: {json_schema} {few_shot_examples} {paper_text}

---

You are extracting structured stress-response data for a scientific
database. Accuracy over completeness: a missing field is fine, a wrong
value is a failure.

<schema>
{json_schema}
</schema>

<examples>
{few_shot_examples}
</examples>

Extract ALL qualifying data points from the paper below into a JSON array
of records matching the schema.

RULES (violations make the record worthless):

1. One record per (strain × condition level × response_type × timepoint).
   A dose gradient of 5 doses = 5 records.
2. Treatment groups only. The untreated/permissive-condition control
   defines the 100% baseline — never emit the control as a record.
3. Only values readable from text or tables. If a value exists only as an
   unreadable point in a figure, set response_value to null and describe
   the trend in notes. Never estimate numbers off figure axes.
4. source_quote: copy the exact sentence (or table caption) that states
   the values, max 300 characters. Every record must have one.
5. Anything not explicitly stated → null. Do not infer strain, medium, or
   growth phase from "usual practice".
6. Claims from Discussion/Introduction sections, or mechanisms the authors
   propose without measuring → evidence_level: "speculated". Measured
   results → "measured". Derived/calculated by authors → "inferred".
7. Units verbatim from the paper in dose_unit/response_unit — do NOT
   convert units yourself; normalization happens downstream.
8. mechanism_reported: only mechanisms this paper reports for this
   organism/condition, as short canonical phrases ("SOS response",
   "nucleotide excision repair", "HSP expression").
9. If the paper contains no qualifying quantitative data, return [].

Output: the JSON array only. No prose, no code fences.

<paper>
{paper_text}
</paper>
