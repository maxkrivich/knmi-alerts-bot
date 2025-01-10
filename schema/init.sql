-- Create enum for severity levels
CREATE TYPE public.alert_severity AS ENUM ('yellow', 'orange', 'red');

-- Create enum for provinces
CREATE TYPE public.province AS ENUM (
    'Drenthe', 'Flevoland', 'Friesland', 'Gelderland', 'Groningen',
    'Limburg', 'Noord-Brabant', 'Noord-Holland', 'Overijssel', 'Utrecht',
    'Zeeland', 'Zuid-Holland', 'Waddenzee', 'IJsselmeergebied',
    'Waddeneilanden'
);

-- Create simplified weather alerts table
CREATE TABLE IF NOT EXISTS public.alerts (
    id SERIAL PRIMARY KEY,
    severity alert_severity NOT NULL,
    region province NOT NULL,
    phenomenon_name TEXT NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    description TEXT
);


-- Create table for users
CREATE TABLE IF NOT EXISTS public.users (
    telegram_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    region province,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    notify_yellow BOOLEAN NOT NULL DEFAULT TRUE,
    notify_orange BOOLEAN NOT NULL DEFAULT TRUE,
    notify_red BOOLEAN NOT NULL DEFAULT TRUE
    -- maybe add notification settings and mute
);
