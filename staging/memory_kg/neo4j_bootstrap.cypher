// Neo4j Bootstrap Schema - Foundational Constraints & Indexes

// Node Labels
CREATE CONSTRAINT IF NOT EXISTS FOR (n:L1Record) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (n:MACEvent) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (n:MetaEvent) REQUIRE n.id IS UNIQUE;

// Indexes
CREATE INDEX l1_timestamp IF NOT EXISTS FOR (n:L1Record) ON (n.timestamp);
CREATE INDEX mac_timestamp IF NOT EXISTS FOR (n:MACEvent) ON (n.timestamp);
CREATE INDEX meta_timestamp IF NOT EXISTS FOR (n:MetaEvent) ON (n.timestamp);

// Constellation Ontology Base
CREATE CONSTRAINT IF NOT EXISTS FOR (a:Agent) REQUIRE a.name IS UNIQUE;
CREATE INDEX agent_role IF NOT EXISTS FOR (a:Agent) ON (a.role);

