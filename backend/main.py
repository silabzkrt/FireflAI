from contextlib import asynccontextmanager
from datetime import datetime, timezone
import threading

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.detection_router import router as detection_router
from api.risk_router import router as risk_router
from api.spread_router import router as spread_router
from api.dispatch_router import router as dispatch_router
from core import constants
from database import models
from database.session import SessionLocal, engine
from services.risk_service import RiskPredictionService

models.Base.metadata.create_all(bind=engine)

risk_service = RiskPredictionService()
RISK_CACHE = {}


def update_risk_cache():
    new_cache = {}
    db = SessionLocal()
    try:
        for h in [0]:
            try:
                points = risk_service.get_turkey_grid_risk(
                    threshold=constants.DEFAULT_GRID_RISK_THRESHOLD,
                    hours_ago=h,
                )
                new_cache[h] = points

                if h == 0 and points:
                    now_utc = datetime.now(timezone.utc)
                    for p in points:
                        lat = p.get("lat") or p.get("latitude")
                        lon = p.get("lon") or p.get("longitude")
                        score = p.get("score") or p.get("risk_level", 0.0)
                        temp = p.get("temp") or p.get("temperature")
                        rh = p.get("rh") or p.get("humidity")
                        ws = p.get("ws") or p.get("wind_speed")

                        if lat is not None and lon is not None:
                            record = models.MeteorologicalRisk(
                                risk_level=float(score),
                                latitude=float(lat),
                                longitude=float(lon),
                                temperature=float(temp) if temp is not None else None,
                                humidity=float(rh) if rh is not None else None,
                                wind_speed=float(ws) if ws is not None else None,
                                risk_point=f"POINT({lon} {lat})",
                                captured_at=now_utc,
                            )
                            db.add(record)
                    db.commit()

            except Exception as e:
                db.rollback()
                print(f"Error updating risk cache for hour {h}: {e}")
    finally:
        db.close()

    global RISK_CACHE
    RISK_CACHE = new_cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        update_risk_cache,
        CronTrigger(minute="0"),
        id="hourly_risk_update",
        replace_existing=True,
    )

    scheduler.start()

    threading.Thread(target=update_risk_cache, daemon=True).start()

    yield

    scheduler.shutdown()


app = FastAPI(title="Ignis Core Wildfire Platform API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    detection_router,
    prefix="/api/v1/detection",
    tags=["Model 1: YOLO Detection"],
)

app.include_router(
    risk_router, 
    prefix="/api/v1/risk", 
    tags=["Model 2: Meteorological Risk"],
)

app.include_router(
    spread_router,
    prefix="/api/v1/spread",
    tags=["Model 3: Fire Spread"],
)

app.include_router(
    dispatch_router,
    prefix="/api/v1/dispatch",
    tags=["Model 4: Dispatch"],
)

import pandas as pd
# Test with extreme high-risk inputs
test_dict = {
    "Temperature": [40.0],
    "RH": [15.0],
    "Ws": [35.0],
    "Wind_Direction": [180.0],
    "Rain": [0.0],
    "Rain_3D_Sum": [0.0],
    "Rain_7D_Sum": [0.0],
    "Temp_3D_Max": [42.0],
    "RH_3D_Mean": [20.0],
    "Dryness_Index": [2.66],
    "VPD": [6.0],
    "Surface_Temp": [45.0],
    "Soil_Temp": [35.0],
    "Soil_Moisture": [0.05],
    "Dew_Point": [5.0],
    "Pressure": [1010.0],
    "Evapotranspiration": [0.5],
    "is_day": [1],
    "month_sin": [-0.866],
    "month_cos": [-0.5],
    "hour_sin": [0.0],
    "hour_cos": [1.0],
    "NDVI": [0.2],
    "Fuel_Type_Conifer": [1.0],
    "Resin_Ignition_Potential": [0.8],
    "Nearest_Fire_Dist_KM": [0.5],
    "Wind_Fire_Vector_Alignment": [10.0]
}
test_df = pd.DataFrame(test_dict)
print("EXTREME TEST PREDICTION:", risk_service.model.predict_proba(test_df)[:, 1][0] * 100)

@app.get("/")
def root():
    return {"status": "online", "system": "Ignis Core Wildfire Platform API"}