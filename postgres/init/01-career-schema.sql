-- Core Career Schema v1.0
-- Generated from src/shared/schemas/career.yaml

CREATE TABLE IF NOT EXISTS competency_markers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('not_started', 'in_progress', 'completed')) DEFAULT 'not_started',
    evidence_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    level INTEGER NOT NULL CHECK (level BETWEEN 0 AND 5) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS skill_markers (
    skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
    marker_id UUID REFERENCES competency_markers(id) ON DELETE CASCADE,
    PRIMARY KEY (skill_id, marker_id)
);

CREATE TABLE IF NOT EXISTS user_profiles (
    username TEXT PRIMARY KEY,
    skills JSONB DEFAULT '[]'::JSONB,
    goals JSONB DEFAULT '[]'::JSONB,
    achievements JSONB DEFAULT '[]'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_markers_status ON competency_markers(status);
CREATE INDEX idx_skills_level ON skills(level);
CREATE INDEX idx_user_profiles_created ON user_profiles(created_at);

COMMENT ON TABLE competency_markers IS 'Career competency evidence markers';
COMMENT ON TABLE skills IS 'User skill levels with markers';
