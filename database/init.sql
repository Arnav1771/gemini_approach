-- Graph Analysis AI Database Schema
-- PostgreSQL database initialization script

-- Create database (run this separately as superuser)
-- CREATE DATABASE graph_analysis;

-- Connect to the graph_analysis database
\c graph_analysis;

-- Create the main table for storing historical graph data
CREATE TABLE IF NOT EXISTS graph_data_history (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(255) NOT NULL, -- e.g., 'Monthly Sales', 'User Signups'
    category VARCHAR(255) NOT NULL,    -- e.g., 'January', 'Q1 2023', 'Product A'
    value NUMERIC NOT NULL,
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source_graph_hash VARCHAR(64) -- A hash of the image file to avoid duplicates
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_metric_name_category ON graph_data_history (metric_name, category);
CREATE INDEX IF NOT EXISTS idx_extracted_at ON graph_data_history (extracted_at);
CREATE INDEX IF NOT EXISTS idx_source_graph_hash ON graph_data_history (source_graph_hash);

-- Insert some sample data for testing
INSERT INTO graph_data_history (metric_name, category, value, source_graph_hash) VALUES
    ('sales', 'January', 100000, 'sample_hash_1'),
    ('sales', 'February', 120000, 'sample_hash_2'),
    ('sales', 'March', 110000, 'sample_hash_3'),
    ('sales', 'April', 135000, 'sample_hash_4'),
    ('sales', 'May', 145000, 'sample_hash_5'),
    ('user_signups', 'Q1 2023', 1200, 'sample_hash_6'),
    ('user_signups', 'Q2 2023', 1350, 'sample_hash_7'),
    ('user_signups', 'Q3 2023', 1100, 'sample_hash_8'),
    ('user_signups', 'Q4 2023', 1450, 'sample_hash_9');

-- Create a view for easy data analysis
CREATE OR REPLACE VIEW latest_metrics AS
SELECT 
    metric_name,
    category,
    value,
    extracted_at,
    ROW_NUMBER() OVER (PARTITION BY metric_name, category ORDER BY extracted_at DESC) as rn
FROM graph_data_history;

-- Function to get historical context for a metric
CREATE OR REPLACE FUNCTION get_metric_history(
    p_metric_name VARCHAR(255),
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    category VARCHAR(255),
    value NUMERIC,
    extracted_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT h.category, h.value, h.extracted_at
    FROM graph_data_history h
    WHERE h.metric_name = p_metric_name
    ORDER BY h.extracted_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
