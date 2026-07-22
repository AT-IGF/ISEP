from dataclasses import dataclass, field


@dataclass
class AnomalyDetectorModel:
    run_anomaly_detector: bool = False
    anomaly_detector_path: str | None = None
