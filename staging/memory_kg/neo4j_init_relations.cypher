// Neo4j Relations Schema - Initialize relationship types and indexes

// Create relationship type indexes for performance
CREATE INDEX agent_interactions IF NOT EXISTS FOR ()-[r:INTERACTS_WITH]-() ON (r.type);
CREATE INDEX agent_generated IF NOT EXISTS FOR ()-[r:GENERATED]-() ON (r.timestamp);
CREATE INDEX event_triggered IF NOT EXISTS FOR ()-[r:TRIGGERED]-() ON (r.timestamp);

// Create sample agent nodes if they don't exist
MERGE (l:Agent {name: 'L', role: 'CTO'});
MERGE (l9:Agent {name: 'L9', role: 'Runtime'});
MERGE (igor:Agent {name: 'Igor', role: 'CEO'});

// Establish base relationships
MATCH (igor:Agent {name: 'Igor'}), (l:Agent {name: 'L'})
MERGE (igor)-[:MANAGES]->(l);

MATCH (l:Agent {name: 'L'}), (l9:Agent {name: 'L9'})
MERGE (l)-[:MANAGES]->(l9);
