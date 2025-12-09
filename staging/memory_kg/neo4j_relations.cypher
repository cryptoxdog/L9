// Neo4j Relations Schema - Agent Communication & Event Tracking

// Agent → Agent communication
MATCH (s:Agent {name:$source}), (t:Agent {name:$target})
MERGE (s)-[:INTERACTS_WITH {type:$interaction}]->(t);

// L1 Events → Agents
MATCH (a:Agent {name:$agent})
MERGE (a)-[:GENERATED]->(l:L1Record {id:$id});

