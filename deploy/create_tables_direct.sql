-- Direct SQL Table Creation for DeFi Risk Assessment
-- Run this to create all tables without SQLAlchemy issues

-- Create UUID extension if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Protocols table
CREATE TABLE IF NOT EXISTS protocols (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    contract_address VARCHAR(255),
    category VARCHAR(100),
    chain VARCHAR(50) NOT NULL DEFAULT 'ethereum',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Protocol metrics table
CREATE TABLE IF NOT EXISTS protocol_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    protocol_id UUID NOT NULL REFERENCES protocols(id) ON DELETE CASCADE,
    tvl_usd FLOAT,
    volume_24h_usd FLOAT,
    price_change_24h FLOAT,
    liquidity_usd FLOAT,
    user_count INTEGER,
    transaction_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Risk scores table
CREATE TABLE IF NOT EXISTS risk_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    protocol_id UUID NOT NULL REFERENCES protocols(id) ON DELETE CASCADE,
    risk_score FLOAT NOT NULL,
    risk_level VARCHAR(50) NOT NULL,
    confidence_score FLOAT,
    model_version VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    protocol_id UUID NOT NULL REFERENCES protocols(id) ON DELETE CASCADE,
    alert_type VARCHAR(100) NOT NULL,
    threshold FLOAT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_triggered TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Email subscribers table (without duplicate indexes)
CREATE TABLE IF NOT EXISTS email_subscribers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    high_risk_threshold FLOAT NOT NULL DEFAULT 70.0,
    medium_risk_threshold FLOAT NOT NULL DEFAULT 40.0,
    notify_on_high BOOLEAN NOT NULL DEFAULT TRUE,
    notify_on_medium BOOLEAN NOT NULL DEFAULT TRUE,
    verification_token VARCHAR(100),
    unsubscribe_token VARCHAR(100),
    last_alert_sent TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS ix_protocols_chain ON protocols(chain);
CREATE INDEX IF NOT EXISTS ix_protocols_category ON protocols(category);
CREATE INDEX IF NOT EXISTS ix_protocol_metrics_protocol_id ON protocol_metrics(protocol_id);
CREATE INDEX IF NOT EXISTS ix_risk_scores_protocol_id ON risk_scores(protocol_id);
CREATE INDEX IF NOT EXISTS ix_alerts_user_id ON alerts(user_id);
CREATE INDEX IF NOT EXISTS ix_alerts_protocol_id ON alerts(protocol_id);
CREATE INDEX IF NOT EXISTS ix_email_subscribers_email ON email_subscribers(email);
CREATE INDEX IF NOT EXISTS ix_email_subscribers_active ON email_subscribers(is_active);

-- Grant permissions to defi_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO defi_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO defi_user;





