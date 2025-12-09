-- ============================================================
--  L9 CONSTELLATION MEMORY SCHEMA (Single File Migration)
--  L1 (L - CTO Memory), MAC (Multi-Agent Coordination),
--  META (System-Level / Constellation Meta-Governance)
-- ============================================================

-- ========================
-- L1 MEMORY TABLES
-- ========================

CREATE TABLE IF NOT EXISTS l_directives (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz DEFAULT now(),
    directive jsonb NOT NULL,
    source text NOT NULL,
    priority integer DEFAULT 1,
    context_window jsonb,
    checksum text
);

CREATE TABLE IF NOT EXISTS l_reasoning_patterns (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz DEFAULT now(),
    directive_hash text,
    reasoning_mode text,
    pattern_type text,
    pattern_signature jsonb,
    effectiveness_score float,
    autonomy_level_required integer DEFAULT 1,
    source text,
    notes text
);

CREATE TABLE IF NOT EXISTS l_evaluations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz DEFAULT now(),
    evaluation jsonb NOT NULL,
    result jsonb,
    confidence float,
    category text,
    notes text
);

CREATE TABLE IF NOT EXISTS l_decision_register (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz DEFAULT now(),
    decision text NOT NULL,
    rationale text,
    alternatives_considered jsonb,
    risk_profile jsonb,
    predicted_outcomes jsonb,
    confidence float,
    governance_passed boolean DEFAULT false,
    final_action text
);

CREATE TABLE IF NOT EXISTS l_execution_trace (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz DEFAULT now(),
    directive jsonb,
    module_invoked text,
    module_version text,
    latency_ms integer,
    error_flag boolean DEFAULT false,
    output_excerpt text,
    checksum text,
    event_type text
);

CREATE TABLE IF NOT EXISTS l_memory_buffer (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz DEFAULT now(),
    content jsonb,
    content_type text,
    retention_policy text DEFAULT 'short_term'
);

CREATE TABLE IF NOT EXISTS l_drift_monitor (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz DEFAULT now(),
    drift_type text,
    drift_signal jsonb,
    severity integer,
    corrective_action text,
    status text
);

CREATE TABLE IF NOT EXISTS l_autonomy_history (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz DEFAULT now(),
    previous_level integer,
    new_level integer,
    reason text,
    approved_by text
);

-- ========================
-- MAC MEMORY TABLES
-- ========================

CREATE TABLE IF NOT EXISTS mac_agent_registry (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz DEFAULT now(),
    agent_name text NOT NULL,
    agent_role text,
    capabilities jsonb,
    health_status text,
    autonomy_level integer DEFAULT 1
);

CREATE TABLE IF NOT EXISTS mac_message_bus (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz DEFAULT now(),
    source_agent text,
    target_agent text,
    interaction_type text,
    payload jsonb,
    success boolean DEFAULT true,
    latency_ms integer,
    notes text
);

CREATE TABLE IF NOT EXISTS mac_task_delegations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz DEFAULT now(),
    delegator text,
    delegate text,
    task jsonb,
    status text,
    deadline timestamptz,
    result jsonb
);

CREATE TABLE IF NOT EXISTS mac_coordination_graph (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz DEFAULT now(),
    source_agent text,
    target_agent text,
    relation_type text,
    weight float,
    metadata jsonb
);

CREATE TABLE IF NOT EXISTS mac_constellation_links (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz DEFAULT now(),
    source_agent text,
    target_agent text,
    interaction_type text,
    payload jsonb,
    latency_ms integer,
    success boolean,
    notes text
);

-- ========================
-- META MEMORY TABLES
-- ========================

CREATE TABLE IF NOT EXISTS meta_constitution (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz DEFAULT now(),
    rule_name text,
    rule_body jsonb,
    version text,
    active boolean DEFAULT true
);

CREATE TABLE IF NOT EXISTS meta_invariants (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz DEFAULT now(),
    invariant_name text,
    invariant_value jsonb,
    version text,
    description text
);

CREATE TABLE IF NOT EXISTS meta_incident_log (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz DEFAULT now(),
    severity text,
    category text,
    description text,
    metadata jsonb,
    resolved boolean DEFAULT false,
    resolved_by text
);

CREATE TABLE IF NOT EXISTS meta_audit_log (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz DEFAULT now(),
    audit_type text,
    agent text,
    finding jsonb,
    severity integer,
    recommended_action text
);

CREATE TABLE IF NOT EXISTS meta_ontology (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz DEFAULT now(),
    entity_type text,
    schema jsonb,
    version text,
    notes text
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================

-- L1 INDEXES
CREATE INDEX IF NOT EXISTS idx_l_directives_timestamp 
    ON l_directives (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_l_reasoning_patterns_mode 
    ON l_reasoning_patterns (reasoning_mode);

CREATE INDEX IF NOT EXISTS idx_l_execution_trace_event 
    ON l_execution_trace (event_type);

CREATE INDEX IF NOT EXISTS idx_l_execution_trace_error 
    ON l_execution_trace (error_flag);

CREATE INDEX IF NOT EXISTS idx_l_drift_monitor_severity 
    ON l_drift_monitor (severity DESC);

-- MAC INDEXES
CREATE INDEX IF NOT EXISTS idx_mac_message_bus_agents 
    ON mac_message_bus (source_agent, target_agent);

CREATE INDEX IF NOT EXISTS idx_mac_task_delegations_status 
    ON mac_task_delegations (status);

CREATE INDEX IF NOT EXISTS idx_mac_coordination_graph_relation 
    ON mac_coordination_graph (relation_type);

-- META INDEXES
CREATE INDEX IF NOT EXISTS idx_meta_incident_log_severity 
    ON meta_incident_log (severity DESC);

CREATE INDEX IF NOT EXISTS idx_meta_constitution_active 
    ON meta_constitution (active);

CREATE INDEX IF NOT EXISTS idx_meta_audit_log_agent 
    ON meta_audit_log (agent);

-- ============================================================
-- END OF MIGRATION PACK
-- ============================================================

