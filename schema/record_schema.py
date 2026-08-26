"""CERD record schema — single source of truth. See tasks/01_schema.md.

DRAFT: finalize in task 01 with team sign-off.
"""
from __future__ import annotations

import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class Condition(str, Enum):
    UV = "UV"
    TEMPERATURE = "temperature"


class Assay(str, Enum):
    CFU = "CFU"
    OD = "OD"
    SPOT_ASSAY = "spot_assay"
    SURVIVAL_CURVE = "survival_curve"
    MICROSCOPY = "microscopy"
    OTHER = "other"


class ResponseType(str, Enum):
    SURVIVAL = "survival"
    GROWTH_RATE = "growth_rate"
    GROWTH_INHIBITION = "growth_inhibition"
    RECOVERY_TIME = "recovery_time"
    EXPRESSION_CHANGE = "expression_change"
    MORPHOLOGY = "morphology"
    OTHER = "other"


class EvidenceLevel(str, Enum):
    MEASURED = "measured"
    INFERRED = "inferred"
    SPECULATED = "speculated"


DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")


class Record(BaseModel):
    record_id: str = Field(pattern=r"^[a-z0-9-]+$")
    organism: str                     # NCBI scientific name
    taxid: int
    strain: Optional[str] = None      # verbatim from paper

    condition: Condition
    # UV fields
    uv_band: Optional[str] = None     # UV-A / UV-B / UV-C
    dose_value: Optional[float] = Field(default=None, ge=0)
    dose_unit: Optional[str] = None   # normalized to J/m2 in task 05
    # temperature fields
    temp_c: Optional[float] = None
    temp_shift: Optional[str] = None  # heat_shock / cold_shock / constant

    exposure_time_s: Optional[float] = Field(default=None, ge=0)
    medium: Optional[str] = None
    growth_phase: Optional[str] = None

    assay: Assay
    response_type: ResponseType
    response_value: Optional[float] = None
    response_unit: Optional[str] = None   # percent / fold_change / ...
    response_direction: Optional[str] = None  # increase / decrease / none

    mechanism_reported: list[str] = Field(default_factory=list)
    evidence_level: EvidenceLevel

    source_doi: Optional[str] = None
    source_pmid: Optional[str] = None
    source_quote: str = Field(max_length=300)

    extracted_by: str = "llm"
    verified_by: Optional[str] = None
    verified_date: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("source_doi")
    @classmethod
    def _doi(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not DOI_RE.match(v):
            raise ValueError(f"invalid DOI: {v}")
        return v

    @model_validator(mode="after")
    def _checks(self) -> "Record":
        if self.source_doi is None and self.source_pmid is None:
            raise ValueError("need source_doi or source_pmid")
        if self.condition == Condition.UV and self.dose_value is None:
            raise ValueError("UV record needs dose_value")
        if self.condition == Condition.TEMPERATURE and self.temp_c is None:
            raise ValueError("temperature record needs temp_c")
        if (
            self.response_unit == "percent"
            and self.response_value is not None
            and not 0 <= self.response_value <= 100
        ):
            raise ValueError("percent response outside [0, 100]")
        return self
