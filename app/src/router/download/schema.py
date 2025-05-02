from enum import Enum


class EnumDownloadEntity(str, Enum):
    assignments = "assignments"
    agreements = "agreements"
    customers = "customers"
    assets = "assets"
    followup_results = "followup_results"
    customer_history = "customer_history"
    ptp_followup_results = "ptp_followup_results"
