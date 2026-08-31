# FireflAI: Spread Prediction Model

## 1. Overview
This repository sub-module contains the formulation and inference pipeline for the **FireflAI Spread Prediction Model**. Operating at the intersection of geospatial analytics and localized fluid dynamics approximations, this model projects the imminent propagation trajectory of an active wildfire. Rather than relying on simple radial buffering, the model calculates a dynamic expansion polygon by treating fire propagation as a vector-based spatial projection problem driven by meteorological telemetry.

## 2. Theoretical Architecture & Methodology
The spread calculation utilizes a deterministic spatial expansion algorithm that dynamically shifts the centroid of the initial detection based on prevailing wind vectors. 

The mathematical approach operates on the following principles:
* **Forward Propagation (Wind-Driven):** The primary expansion axis is calculated using the wind speed ($v$) and wind direction ($\theta$). The forward distance ($d$) is determined by $d = (v \times \alpha) \times t$, where $t$ is the prediction window in hours and $\alpha$ is a propagation friction coefficient.
* **Lateral Propagation (Perpendicular Expansion):** Fires do not burn in a straight line; they fan outward. The model calculates a perpendicular dispersion vector ($\theta + \frac{\pi}{2}$) to establish the lateral boundaries of the burn scar, scaling this proportionally to the forward distance.
* **Geospatial Projection:** Distances in kilometers are converted into latitudinal and longitudinal deltas using the Earth's radius ($R \approx 6371$ km) and cosine corrections for spherical geometry, ensuring sub-meter accuracy across different latitudes.

## 3. Inputs and Outputs
**Inputs:**
* `lat` (float): Initial ignition latitude.
* `lon` (float): Initial ignition longitude.
* `wind_speed` (float): Prevailing wind speed (km/h) sourced from meteorological endpoints.
* `wind_dir` (float): Wind direction in degrees.
* `prediction_hours` (int): The temporal window for projection (e.g., 4, 12, or 24 hours).

**Outputs:**
* The model yields a precise geographic boundary structured as a **GeoJSON Polygon** and **Well-Known Text (WKT)** string. This output strictly defines the perimeter of the predicted burn area, ready to be ingested by the Dispatch LLM and rendered on the frontend GIS interface.

## 4. Scientific Evaluation Metrics
To rigorously assess the predictive validity of the generated polygons against historical ground-truth burn scars, the model is evaluated using standard spatial segmentation metrics:
* **Intersection over Union (IoU):** Measures the proportional overlap between the predicted propagation polygon and the actual burned area.
* **Dice Coefficient (F1-Score):** Heavily penalizes false-positive spatial expansions while rewarding accurate geographic overlaps.
* **Hausdorff Distance:** Evaluates the maximum margin of error by measuring the greatest distance between any point on the predicted fire boundary and the actual recorded perimeter.
