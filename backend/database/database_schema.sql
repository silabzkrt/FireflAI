DROP TABLE IF EXISTS tactical_dispatch_plans CASCADE;
DROP TABLE IF EXISTS fire_spread_polygons CASCADE;
DROP TABLE IF EXISTS fire_detections CASCADE;
DROP TABLE IF EXISTS meteorological_risks CASCADE;

CREATE TABLE meteorological_risks (
    id SERIAL PRIMARY KEY,
    risk_level FLOAT NOT NULL,
    latitude FLOAT,
    longitude FLOAT,
    temperature FLOAT,
    humidity FLOAT,
    wind_speed FLOAT,
    wind_direction FLOAT,
    risk_point VARCHAR(100) NOT NULL,
    captured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_meteorological_risks_id ON meteorological_risks (id);
CREATE INDEX ix_meteorological_risks_latitude ON meteorological_risks (latitude);
CREATE INDEX ix_meteorological_risks_longitude ON meteorological_risks (longitude);
CREATE INDEX ix_meteorological_risks_captured_at ON meteorological_risks (captured_at);

CREATE TABLE fire_detections (
    id SERIAL PRIMARY KEY,
    class_name VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    latitude FLOAT,
    longitude FLOAT,
    detection_point VARCHAR(100), 
    captured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_fire_detections_id ON fire_detections (id);
CREATE INDEX ix_fire_detections_latitude ON fire_detections (latitude);
CREATE INDEX ix_fire_detections_longitude ON fire_detections (longitude);
CREATE INDEX ix_fire_detections_captured_at ON fire_detections (captured_at);

CREATE TABLE fire_spread_polygons (
    id SERIAL PRIMARY KEY,
    fire_detection_id INTEGER REFERENCES fire_detections(id) ON DELETE SET NULL, 
    latitude FLOAT, 
    longitude FLOAT, 
    spread_area TEXT NOT NULL,
    wind_direction FLOAT,
    wind_speed FLOAT,
    prediction_hours INTEGER,
    spread_probability FLOAT,
    affected_area_hectares FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_fire_spread_polygons_id ON fire_spread_polygons (id);
CREATE INDEX ix_fire_spread_polygons_fire_detection_id ON fire_spread_polygons (fire_detection_id);
CREATE INDEX ix_fire_spread_polygons_latitude ON fire_spread_polygons (latitude);
CREATE INDEX ix_fire_spread_polygons_longitude ON fire_spread_polygons (longitude);
CREATE INDEX ix_fire_spread_polygons_created_at ON fire_spread_polygons (created_at);

CREATE TABLE tactical_dispatch_plans (
    id SERIAL PRIMARY KEY,
    fire_detection_id INTEGER REFERENCES fire_detections(id) ON DELETE SET NULL, 
    latitude FLOAT, 
    longitude FLOAT, 
    incident_caption VARCHAR(500), 
    available_forces VARCHAR(500), 
    tactical_order TEXT NOT NULL,
    spread_area_wkt TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_tactical_dispatch_plans_id ON tactical_dispatch_plans (id);
CREATE INDEX ix_tactical_dispatch_plans_fire_detection_id ON tactical_dispatch_plans (fire_detection_id);
CREATE INDEX ix_tactical_dispatch_plans_latitude ON tactical_dispatch_plans (latitude);
CREATE INDEX ix_tactical_dispatch_plans_longitude ON tactical_dispatch_plans (longitude);
CREATE INDEX ix_tactical_dispatch_plans_created_at ON tactical_dispatch_plans (created_at);