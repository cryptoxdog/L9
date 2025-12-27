# AI Negotiation Agents: L9 Technical Integration Specification
## Production Implementation Guide for Memory Substrate, Governance Engine, and Agent Orchestration

**Version:** 1.0  
**Target**: Enterprises using L9 AI OS for autonomous agent deployment  
**Dependencies**: L9 Memory Substrate, Governance Policy Engine, Agent Executor, Tool Registry

---

## 1. MEMORY SUBSTRATE EXTENSIONS FOR NEGOTIATION AGENTS

### 1.1 Negotiation-Specific Schema Additions

The L9 Memory Substrate (PostgreSQL + pgvector + Neo4j) requires extensions to store negotiation-specific data:

#### 1.1.1 PostgreSQL Tables (New)

```sql
-- Core negotiation records
CREATE TABLE negotiations (
  id UUID PRIMARY KEY,
  agent_id UUID NOT NULL REFERENCES agents(id),
  counterparty_id UUID NOT NULL,
  counterparty_name TEXT,
  deal_type VARCHAR(50),  -- 'procurement', 'partnership', 'sales', 'investment'
  deal_value_usd DECIMAL(15, 2),
  negotiation_start_time TIMESTAMP,
  negotiation_end_time TIMESTAMP,
  status VARCHAR(50),  -- 'active', 'closed', 'failed', 'escalated'
  outcome VARCHAR(50),  -- 'deal_closed', 'no_deal', 'escalated_to_human'
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Negotiation events (offers, counteroffers, messages)
CREATE TABLE negotiation_events (
  id UUID PRIMARY KEY,
  negotiation_id UUID NOT NULL REFERENCES negotiations(id),
  event_type VARCHAR(50),  -- 'offer', 'counteroffer', 'tactic', 'message'
  actor VARCHAR(50),  -- 'agent', 'human', 'counterparty'
  timestamp TIMESTAMP,
  content TEXT,  -- Raw offer or message
  parsed_terms JSONB,  -- Structured: {price, delivery_date, payment_terms, warranty, ...}
  tactic_detected VARCHAR(100),  -- 'anchoring', 'flinching', 'nibbling', 'time_pressure', NULL
  confidence FLOAT,  -- Tactic confidence (0-1)
  created_at TIMESTAMP DEFAULT NOW()
);

-- Counterparty profiles (learned over time)
CREATE TABLE counterparty_profiles (
  id UUID PRIMARY KEY,
  counterparty_id UUID,
  counterparty_name TEXT UNIQUE,
  deal_type VARCHAR(50),
  negotiation_history_count INT,
  avg_negotiation_duration_hours FLOAT,
  avg_discount_requested_pct FLOAT,
  preferred_payment_terms_days INT,
  risk_score FLOAT,  -- 0-100, higher = riskier
  key_tactics JSONB,  -- Array of observed tactics
  success_rate FLOAT,  -- % of negotiations that closed
  profile_updated_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Agent decisions and recommendations
CREATE TABLE agent_recommendations (
  id UUID PRIMARY KEY,
  negotiation_id UUID NOT NULL REFERENCES negotiations(id),
  agent_id UUID NOT NULL REFERENCES agents(id),
  recommendation_type VARCHAR(50),  -- 'opening_offer', 'counteroffer', 'tactic', 'escalate'
  recommendation_content JSONB,  -- {offer_price, rationale, confidence, ...}
  human_decision VARCHAR(50),  -- 'accepted', 'rejected', 'modified', 'pending'
  human_feedback TEXT,
  outcome_impact VARCHAR(50),  -- 'positive', 'negative', 'neutral'
  created_at TIMESTAMP DEFAULT NOW()
);

-- Policy violations and escalations
CREATE TABLE policy_violations (
  id UUID PRIMARY KEY,
  negotiation_id UUID REFERENCES negotiations(id),
  agent_id UUID REFERENCES agents(id),
  policy_name TEXT,
  violation_type VARCHAR(50),  -- 'constraint_violation', 'unauthorized_action', 'anomaly'
  severity VARCHAR(50),  -- 'critical', 'high', 'medium', 'low'
  escalated_to VARCHAR(100),  -- Email/ID of escalation target
  resolution VARCHAR(50),  -- 'approved', 'rejected', 'modified'
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### 1.1.2 pgvector Embeddings for Semantic Search

Negotiation agents need semantic search for:
- Finding similar past contracts
- Detecting tactic patterns in language
- Retrieving relevant policies

```sql
-- Contract embeddings (enhanced existing table)
CREATE TABLE contract_embeddings (
  id UUID PRIMARY KEY,
  contract_id UUID REFERENCES contracts(id),
  full_text_embedding VECTOR(1536),  -- OpenAI embedding of full contract
  terms_summary_embedding VECTOR(1536),  -- Embedding of key terms only
  party_embedding VECTOR(1536),  -- Embedding of party info
  embedding_model VARCHAR(100),  -- 'text-embedding-3-large', 'text-embedding-ada-002'
  created_at TIMESTAMP DEFAULT NOW()
);

-- Negotiation message embeddings (for tactic detection)
CREATE TABLE negotiation_message_embeddings (
  id UUID PRIMARY KEY,
  event_id UUID REFERENCES negotiation_events(id),
  message_embedding VECTOR(1536),
  tactic_labels JSONB,  -- Detected tactics via semantic similarity
  created_at TIMESTAMP DEFAULT NOW()
);

-- Policies/constraints (for policy engine retrieval)
CREATE TABLE policy_embeddings (
  id UUID PRIMARY KEY,
  policy_id UUID REFERENCES policies(id),
  policy_text TEXT,
  embedding VECTOR(1536),
  relevance_keywords TEXT[],  -- For hybrid search
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### 1.1.3 Neo4j Knowledge Graph Extensions

Negotiation agents maintain a knowledge graph of:
- Counterparty relationships and negotiation patterns
- Deal precedents and outcome correlations
- Negotiation tactics and counter-tactics
- Organizational policies and constraints

```cypher
-- Node types and relationships for negotiation KG

// Core entities
CREATE CONSTRAINT ON (c:Counterparty) ASSERT c.id IS UNIQUE;
CREATE CONSTRAINT ON (d:Deal) ASSERT d.id IS UNIQUE;
CREATE CONSTRAINT ON (a:Agent) ASSERT a.id IS UNIQUE;
CREATE CONSTRAINT ON (p:Policy) ASSERT p.id IS UNIQUE;

// Counterparty nodes (properties: name, industry, risk_score, preferred_terms, etc.)
CREATE (acme:Counterparty {
  id: 'counterparty_acme',
  name: 'ACME Corp',
  industry: 'Manufacturing',
  risk_score: 35,
  negotiation_count: 12,
  avg_discount_requested: 8.5,
  preferred_payment_days: 45
});

// Deal nodes (properties: value, type, status, terms, outcome)
CREATE (deal1:Deal {
  id: 'deal_001',
  type: 'Procurement',
  value_usd: 250000,
  status: 'closed',
  product: 'Industrial Widgets',
  outcome: 'successful',
  negotiation_duration_hours: 28,
  dispute_reported: false
});

// Tactic nodes (properties: tactic_name, counter_tactic, effectiveness)
CREATE (anchor:Tactic {
  name: 'Anchoring',
  definition: 'Setting first price very high/low to bias negotiation range',
  frequency: 'common',
  counter_tactic: 'Counter-anchor with data-backed position'
});

// Policy nodes (properties: name, constraint, enforcement_level)
CREATE (payment_policy:Policy {
  id: 'policy_payment_terms',
  name: 'Payment Terms Guardrail',
  constraint: 'MAX_DAYS_DUE = 60',
  enforcement: 'hard',
  severity: 'medium'
});

// Relationships
CREATE (acme)-[:NEGOTIATED_DEAL]->(deal1)
CREATE (acme)-[:USED_TACTIC]->(anchor)
CREATE (deal1)-[:SUBJECT_TO]->(payment_policy)
CREATE (anchor)-[:HAS_COUNTER]->(counter_tactic)

// Indices for efficient traversal
CREATE INDEX ON :Counterparty(name);
CREATE INDEX ON :Deal(status);
CREATE INDEX ON :Tactic(name);
CREATE INDEX ON :Policy(enforcement);
```

### 1.2 Ingestion Pipeline for Negotiation Artifacts

Extend the L9 Memory Substrate ingestion to parse and embed:

```python
# Example ingestion flow (L9-compatible)

from l9.memory import MemorySubstrate
from l9.models import PacketEnvelope
import openai
import json

class NegotiationIngestionAgent:
    """
    Ingests past contracts, RFPs, negotiation logs into L9 Memory Substrate.
    """
    
    def __init__(self, memory_substrate: MemorySubstrate):
        self.memory = memory_substrate
        self.embedding_model = "text-embedding-3-large"
    
    def ingest_contract(self, contract_text: str, metadata: dict) -> PacketEnvelope:
        """
        Parse contract, extract terms, embed, store in memory substrate.
        """
        # Extract structured terms using LLM
        extraction_prompt = f"""
        Extract key negotiation terms from this contract:
        {contract_text[:2000]}...
        
        Return JSON with: price, payment_terms_days, delivery_date, warranty_months, 
        liability_cap_pct, counterparty_name, deal_value_usd, product/service
        """
        terms = self._extract_terms_via_llm(extraction_prompt)
        
        # Embed full text and terms summary
        full_embedding = openai.Embedding.create(
            model=self.embedding_model,
            input=contract_text
        )["data"][0]["embedding"]
        
        terms_summary = json.dumps(terms)
        terms_embedding = openai.Embedding.create(
            model=self.embedding_model,
            input=terms_summary
        )["data"][0]["embedding"]
        
        # Create PacketEnvelope for L9 storage
        packet = PacketEnvelope(
            packet_id=f"contract_{metadata['contract_id']}",
            packet_type="negotiation_contract",
            source="ingestion_pipeline",
            timestamp=datetime.now().isoformat(),
            payload={
                "contract_text": contract_text,
                "extracted_terms": terms,
                "party_a": metadata.get("party_a"),
                "party_b": metadata.get("party_b"),
                "deal_value": terms.get("deal_value_usd"),
                "outcome": metadata.get("outcome")  # 'successful', 'disputed', etc.
            },
            embeddings={
                "full_text": full_embedding,
                "terms_summary": terms_embedding
            },
            metadata=metadata,
            lineage={"source": "contract_archive", "ingestion_date": datetime.now().isoformat()}
        )
        
        # Store in memory substrate
        self.memory.store_packet(packet)
        
        # Extract knowledge graph triples (counterparty, deal, outcomes)
        self._update_knowledge_graph(packet, terms)
        
        return packet
    
    def ingest_negotiation_log(self, negotiation_id: str, messages: list, outcome: dict):
        """
        Ingest a completed negotiation: sequence of offers, tactics, final terms.
        """
        # Detect tactics in messages using semantic search + LLM
        tactics_detected = []
        for msg in messages:
            tactic = self._detect_tactic(msg["content"])
            if tactic:
                tactics_detected.append({
                    "message": msg["content"],
                    "tactic": tactic,
                    "actor": msg["actor"]
                })
        
        # Create packet
        packet = PacketEnvelope(
            packet_id=f"negotiation_{negotiation_id}",
            packet_type="negotiation_event_log",
            source="negotiation_system",
            timestamp=datetime.now().isoformat(),
            payload={
                "counterparty": outcome.get("counterparty_name"),
                "deal_type": outcome.get("deal_type"),
                "messages": messages,
                "tactics_detected": tactics_detected,
                "final_terms": outcome.get("final_terms"),
                "negotiation_duration_hours": outcome.get("duration_hours"),
                "outcome": outcome.get("outcome"),  # 'deal_closed', 'no_deal', etc.
                "dispute_reported": outcome.get("dispute_reported", False)
            },
            metadata={
                "counterparty_id": outcome.get("counterparty_id"),
                "deal_value": outcome.get("deal_value"),
                "agent_id": outcome.get("agent_id")
            },
            lineage={"source": "live_negotiation", "outcome_date": datetime.now().isoformat()}
        )
        
        self.memory.store_packet(packet)
        
        # Update counterparty profile in KG
        self._update_counterparty_profile(outcome)
    
    def _extract_terms_via_llm(self, prompt: str) -> dict:
        """Use LLM to extract structured terms."""
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        # Parse JSON response
        terms_str = response["choices"][0]["message"]["content"]
        return json.loads(terms_str)
    
    def _detect_tactic(self, message_text: str) -> str:
        """Detect negotiation tactic in message text."""
        # Semantic search in KG for known tactics
        # Compare message embedding to tactic embeddings
        # Return matching tactic or None
        pass
    
    def _update_knowledge_graph(self, packet: PacketEnvelope, terms: dict):
        """Update Neo4j KG with new contract info."""
        # Create Counterparty node if not exists
        # Create Deal node with properties
        # Link relationships: Counterparty -> Deal, Deal -> Policy, Deal -> Outcome
        pass
    
    def _update_counterparty_profile(self, outcome: dict):
        """Update counterparty profile with new negotiation data."""
        # Query existing profile
        # Update: negotiation_count, avg_discount, risk_score, etc.
        # Recalculate win rate, avg duration
        pass
```

---

## 2. NEGOTIATION STRATEGY ENGINE

### 2.1 Game-Theoretic Solver Integration

The negotiation agent needs a game-theoretic solver to compute optimal strategies:

```python
# game_theoretic_solver.py

from enum import Enum
import numpy as np
from scipy.optimize import linprog
import openai

class NegotiationType(Enum):
    SINGLE_ISSUE = "single_issue"  # Price only
    MULTI_ISSUE = "multi_issue"    # Price, delivery, warranty, etc.
    COALITION = "coalition"         # Multi-party negotiation

class GameTheoreticSolver:
    """
    Computes equilibrium strategies and recommendations for negotiation.
    """
    
    def __init__(self, memory_substrate, llm_model="gpt-4"):
        self.memory = memory_substrate
        self.llm_model = llm_model
    
    def compute_opening_offer(self, 
                             negotiation_context: dict,
                             risk_tolerance: str = "balanced") -> dict:
        """
        Compute opening offer using game theory + RL policy blend.
        
        Inputs:
          - negotiation_context: {deal_type, value, counterparty, historical_discounts, ...}
          - risk_tolerance: 'aggressive', 'balanced', 'conservative'
        
        Outputs:
          - opening_offer: {price, terms, rationale, confidence}
        """
        counterparty = negotiation_context.get("counterparty")
        deal_value = negotiation_context.get("deal_value")
        deal_type = negotiation_context.get("deal_type")
        
        # Step 1: Retrieve similar past deals
        precedent_deals = self.memory.semantic_search(
            query=f"{deal_type} {counterparty} negotiation",
            embedding_type="full_text",
            limit=10
        )
        
        # Step 2: Infer market price distribution from precedents
        prices = [d.get("final_price") for d in precedent_deals if d.get("final_price")]
        if prices:
            price_mean = np.mean(prices)
            price_std = np.std(prices)
        else:
            # No precedents; use heuristic
            price_mean = deal_value
            price_std = deal_value * 0.15
        
        # Step 3: Query counterparty profile from KG
        counterparty_profile = self._query_counterparty_profile(counterparty)
        
        # Step 4: Compute strategic opening offer
        # Using simplified Stackelberg game: we move first (set price); 
        # counterparty responds (accept or counter)
        
        offer_price = self._stackelberg_price(
            price_mean=price_mean,
            price_std=price_std,
            counterparty_profile=counterparty_profile,
            risk_tolerance=risk_tolerance
        )
        
        # Step 5: Formulate rationale via LLM
        rationale = self._generate_rationale(
            offer_price=offer_price,
            precedent_deals=precedent_deals,
            market_data={"mean": price_mean, "std": price_std}
        )
        
        # Step 6: Compute confidence (how likely counterparty accepts?)
        confidence = self._estimate_acceptance_probability(
            offer_price=offer_price,
            counterparty_profile=counterparty_profile
        )
        
        return {
            "offer_price": offer_price,
            "rationale": rationale,
            "confidence": confidence,
            "strategy": f"{risk_tolerance}_stackelberg"
        }
    
    def _stackelberg_price(self, price_mean, price_std, counterparty_profile, risk_tolerance):
        """
        Compute Stackelberg equilibrium price.
        
        Intuition: In a Stackelberg game, the leader (us) commits to a price.
        The follower (counterparty) decides whether to accept.
        We want to maximize our payoff while keeping acceptance probability high.
        
        Strategy depends on risk tolerance:
        - aggressive: price_mean + 1.5 * price_std (high payoff, lower acceptance)
        - balanced: price_mean + 0.5 * price_std (medium)
        - conservative: price_mean - 0.2 * price_std (low payoff, high acceptance)
        """
        multipliers = {
            "aggressive": 1.5,
            "balanced": 0.5,
            "conservative": -0.2
        }
        multiplier = multipliers.get(risk_tolerance, 0.5)
        
        offer_price = price_mean + multiplier * price_std
        
        # Apply fairness constraint (don't go below BATNA)
        batna = self._estimate_batna(counterparty_profile)
        offer_price = max(offer_price, batna)
        
        return offer_price
    
    def _estimate_acceptance_probability(self, offer_price, counterparty_profile):
        """
        Estimate probability counterparty accepts this offer.
        Uses logistic model: P(accept) = 1 / (1 + exp(-k * (offer - reservation)))
        """
        reservation_price = counterparty_profile.get("avg_discount_requested", 0)
        k = 0.1  # Logistic slope parameter
        
        acceptance_prob = 1.0 / (1.0 + np.exp(-k * (offer_price - reservation_price)))
        return float(acceptance_prob)
    
    def compute_counteroffer_response(self, 
                                     counterparty_offer: dict,
                                     negotiation_history: list) -> dict:
        """
        Given a counterparty offer, compute our response: accept, counter, or walk.
        """
        offer_price = counterparty_offer.get("price")
        
        # Detect if counterparty is using anchoring tactic
        tactic = self._detect_tactic_in_offer(counterparty_offer, negotiation_history)
        
        # Estimate counterparty's BATNA
        counterparty_batna = self._estimate_counterparty_batna(negotiation_history)
        
        # Compute optimal response
        if self._should_accept(offer_price, negotiation_history):
            return {"action": "accept", "rationale": "Offer meets our threshold"}
        elif self._should_walk(offer_price, negotiation_history):
            return {"action": "walk", "rationale": "Offer below BATNA; no deal is better"}
        else:
            # Counter
            counter_price = self._compute_counteroffer_price(
                offer_price=offer_price,
                negotiation_history=negotiation_history,
                tactic_detected=tactic
            )
            return {
                "action": "counter",
                "counter_price": counter_price,
                "counter_tactic": self._select_counter_tactic(tactic),
                "rationale": "Offer below target; provide counter"
            }
    
    def _detect_tactic_in_offer(self, offer: dict, history: list) -> str:
        """Detect negotiation tactic in offer."""
        # If first offer is unusually high/low, it's anchoring
        if not history:
            return "anchoring"
        
        # If offer dropped little since last round, nibbling
        last_offer = history[-1].get("price")
        if abs(offer["price"] - last_offer) < 0.02 * last_offer:
            return "nibbling"
        
        # If offer is followed by time pressure, flinching
        if offer.get("deadline_mentioned"):
            return "time_pressure"
        
        return None
    
    def _compute_counteroffer_price(self, offer_price, negotiation_history, tactic_detected):
        """
        Compute counteroffer price based on offer and detected tactic.
        """
        if not negotiation_history:
            batna = self._estimate_batna()
            return batna
        
        # If anchoring detected, counter-anchor closer to fair price
        if tactic_detected == "anchoring":
            return offer_price + 0.15 * offer_price  # Move 15% closer to fair
        
        # Standard concession: move 50% of the gap
        prev_offer = negotiation_history[-1]["price"]
        gap = abs(offer_price - prev_offer)
        counter = offer_price + 0.5 * gap if offer_price < prev_offer else offer_price - 0.5 * gap
        
        return counter
    
    def _should_accept(self, offer_price, negotiation_history) -> bool:
        """Decide whether to accept offer."""
        batna = self._estimate_batna()
        return offer_price >= batna * 0.95  # Accept if within 5% of BATNA
    
    def _should_walk(self, offer_price, negotiation_history) -> bool:
        """Decide whether to walk away."""
        batna = self._estimate_batna()
        negotiation_duration = len(negotiation_history)
        
        # Walk if offer is way below BATNA and we've negotiated many rounds
        return offer_price < batna * 0.8 and negotiation_duration > 5
    
    def _estimate_batna(self) -> float:
        """Estimate our Best Alternative to Negotiated Agreement."""
        # Query KG for alternatives (competitors, substitute products)
        # Return median price of alternatives
        pass
    
    def _estimate_counterparty_batna(self, negotiation_history) -> float:
        """Estimate counterparty's BATNA based on their concession pattern."""
        # If they're making aggressive concessions, their BATNA is weak
        # If they're stalling, BATNA is strong
        pass
    
    def _select_counter_tactic(self, detected_tactic: str) -> str:
        """Select counter-tactic based on detected tactic."""
        counter_tactics = {
            "anchoring": "data_backed_position",
            "time_pressure": "ignore_deadline",
            "flinching": "normalize_offer",
            "nibbling": "bundled_concession"
        }
        return counter_tactics.get(detected_tactic, "collaborative_problem_solving")
    
    def _generate_rationale(self, offer_price, precedent_deals, market_data) -> str:
        """Generate natural language rationale for offer."""
        prompt = f"""
        Explain why this opening offer is strategic:
        - Offer price: ${offer_price}
        - Market average: ${market_data['mean']} (±${market_data['std']})
        - Similar past deals: {len(precedent_deals)} precedents
        
        Generate a 2-sentence rationale suitable for a negotiation email.
        """
        response = openai.ChatCompletion.create(
            model=self.llm_model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
    
    def _query_counterparty_profile(self, counterparty_name: str) -> dict:
        """Query Neo4j for counterparty negotiation profile."""
        query = f"""
        MATCH (c:Counterparty {{name: '{counterparty_name}'}})
        RETURN c.negotiation_count, c.avg_discount_requested, c.risk_score, c.preferred_payment_days
        """
        # Execute against Neo4j and return profile
        pass
```

### 2.2 Reinforcement Learning Policy for Negotiation

The agent's strategy should improve over time based on outcomes:

```python
# negotiation_rl_policy.py

import torch
import torch.nn as nn
from torch.optim import Adam

class NegotiationPolicyNetwork(nn.Module):
    """
    Deep RL policy network for negotiation strategy.
    
    State: Current negotiation context (offer, counterparty profile, history, time)
    Action: Offer price (continuous); acceptance threshold (continuous)
    Reward: Deal value achieved, speed to agreement, fairness score
    """
    
    def __init__(self, state_dim=64, action_dim=2):
        super(NegotiationPolicyNetwork, self).__init__()
        
        self.fc1 = nn.Linear(state_dim, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3_policy = nn.Linear(64, action_dim)  # Mean of offer, acceptance threshold
        self.fc3_value = nn.Linear(64, 1)  # Value function for critic
        
        self.relu = nn.ReLU()
        self.tanh = nn.Tanh()
    
    def forward(self, state):
        x = self.relu(self.fc1(state))
        x = self.relu(self.fc2(x))
        
        # Policy output: offer_price (bounded 0-1), acceptance_threshold (bounded 0-1)
        policy = self.tanh(self.fc3_policy(x))
        
        # Value output: expected future reward
        value = self.fc3_value(x)
        
        return policy, value

class NegotiationAgent:
    """
    Agent using Actor-Critic RL for negotiation strategy optimization.
    """
    
    def __init__(self, state_dim=64, learning_rate=1e-4):
        self.policy = NegotiationPolicyNetwork(state_dim=state_dim)
        self.optimizer = Adam(self.policy.parameters(), lr=learning_rate)
        self.gamma = 0.99  # Discount factor
    
    def select_offer(self, state: torch.Tensor) -> float:
        """
        Given current negotiation state, select offer price.
        """
        with torch.no_grad():
            policy, _ = self.policy(state)
        
        # Unbind: policy outputs normalized offer_price in [0, 1]
        # Scale to realistic range (e.g., [price_min, price_max])
        offer_price = policy[0].item()  # 0-1
        return offer_price
    
    def train_step(self, transitions: list):
        """
        Update policy using collected transitions (s, a, r, s', done).
        """
        states = torch.stack([t["state"] for t in transitions])
        actions = torch.tensor([t["action"] for t in transitions])
        rewards = torch.tensor([t["reward"] for t in transitions])
        next_states = torch.stack([t["next_state"] for t in transitions])
        dones = torch.tensor([t["done"] for t in transitions])
        
        # Compute policy and value
        policies, values = self.policy(states)
        _, next_values = self.policy(next_states)
        
        # TD target: r + gamma * V(s')
        td_targets = rewards + self.gamma * next_values[:, 0] * (1 - dones)
        td_errors = td_targets - values[:, 0]
        
        # Actor loss: policy gradient * advantage
        actor_loss = -torch.mean(policies * td_errors.detach())
        
        # Critic loss: MSE between value and target
        critic_loss = torch.mean(td_errors ** 2)
        
        # Total loss
        loss = actor_loss + critic_loss
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
```

---

## 3. GOVERNANCE POLICY ENGINE FOR NEGOTIATION

### 3.1 Policy Schema & Runtime Evaluation

Extend the L9 Governance Policy Engine with negotiation-specific policies:

```python
# negotiation_policy_engine.py

from enum import Enum
from typing import Dict, List, Tuple
import yaml

class PolicyAction(Enum):
    ALLOW = "allow"
    CONSTRAINT = "constraint"  # Modify to meet constraint
    ESCALATE = "escalate"       # Send to human
    PAUSE = "pause"             # Pause agent

class NegotiationPolicyEngine:
    """
    Deny-by-default policy evaluation for negotiation agents.
    """
    
    def __init__(self, policy_yaml_path: str):
        with open(policy_yaml_path, 'r') as f:
            self.policies = yaml.safe_load(f)
    
    def evaluate_offer(self, offer: dict, context: dict) -> Tuple[PolicyAction, dict]:
        """
        Evaluate proposed offer against all policies.
        
        Returns: (action, explanation)
          - action: ALLOW, CONSTRAINT, ESCALATE, PAUSE
          - explanation: Detailed reason
        """
        results = []
        
        for policy in self.policies.get("policies", []):
            # Evaluate condition
            if self._evaluate_condition(policy["condition"], offer, context):
                results.append({
                    "policy_name": policy["id"],
                    "action": PolicyAction[policy["action"].upper()],
                    "explanation": policy.get("explanation", "")
                })
        
        # Determine final action (highest severity wins)
        action_priority = {PolicyAction.PAUSE: 4, PolicyAction.ESCALATE: 3, 
                          PolicyAction.CONSTRAINT: 2, PolicyAction.ALLOW: 1}
        
        final_result = max(results, key=lambda r: action_priority.get(r["action"], 0))
        
        return final_result["action"], final_result
    
    def _evaluate_condition(self, condition: str, offer: dict, context: dict) -> bool:
        """
        Evaluate policy condition against offer and context.
        Supports:
          - deal_value < 1000000
          - supplier_risk_score > 70
          - payment_terms_days <= 60
          - contract_contains_novel_terms
        """
        # Parse and evaluate condition (simplified)
        # In production, use a proper expression evaluator (e.g., simpleeval)
        
        # Example: "deal_value < 1000000"
        if "deal_value" in condition:
            deal_value = context.get("deal_value", 0)
            return eval(condition.replace("deal_value", str(deal_value)))
        
        if "payment_terms_days" in condition:
            payment_terms = offer.get("payment_terms_days", 0)
            return eval(condition.replace("payment_terms_days", str(payment_terms)))
        
        if "supplier_risk_score" in condition:
            risk_score = context.get("supplier_risk_score", 0)
            return eval(condition.replace("supplier_risk_score", str(risk_score)))
        
        if "contract_contains_novel_terms" in condition:
            novel_terms = context.get("novel_terms_detected", False)
            return novel_terms
        
        return False
    
    def constrain_offer(self, offer: dict, constraint: dict) -> dict:
        """
        Modify offer to meet constraint.
        E.g., if payment_terms > 60, reduce to 60.
        """
        if "MAX_DAYS_DUE" in constraint.get("value", ""):
            max_days = int(constraint["value"].split("=")[-1].strip())
            offer["payment_terms_days"] = min(offer.get("payment_terms_days", 30), max_days)
        
        return offer
    
    def log_violation(self, negotiation_id: str, policy_name: str, violation: dict):
        """Log policy violation to database."""
        # Store in policy_violations table
        pass
```

**Example YAML policy file:**

```yaml
policies:
  - id: "procurement_authorization"
    condition: "deal_value < 1000000"
    action: "ALLOW"
    explanation: "Standard procurement under $1M approved for agent autonomy."
  
  - id: "supplier_risk_check"
    condition: "supplier_risk_score > 70"
    action: "ESCALATE"
    target: "compliance_officer"
    timeout_hours: 2
    explanation: "High-risk supplier requires human review."
  
  - id: "payment_term_guardrail"
    condition: "payment_terms_days > 60"
    action: "CONSTRAINT"
    value: "MAX_DAYS_DUE = 60"
    explanation: "Cash flow policy: max 60 days payment terms."
  
  - id: "liability_cap"
    condition: "liability_cap < deal_value * 0.5"
    action: "CONSTRAINT"
    value: "MIN_LIABILITY_CAP_PCT = 50"
    explanation: "Standard risk management: cap must be ≥ 50% of deal value."
  
  - id: "novel_terms_review"
    condition: "contract_contains_novel_terms"
    action: "ESCALATE"
    target: "legal_team"
    timeout_hours: 2
    explanation: "Novel terms not in precedent contracts require legal review."
  
  - id: "circuit_breaker"
    condition: "escalation_rate > 0.40 OR breach_rate > 0.05"
    action: "PAUSE"
    duration_hours: 24
    explanation: "High escalation/breach rate triggers agent pause for retraining."
```

---

## 4. ORCHESTRATION FOR MULTI-AGENT NEGOTIATION FLEET

### 4.1 Agent Coordinator

When multiple agents negotiate, a coordinator ensures:
- No task duplication
- Conflict resolution
- Knowledge sharing

```python
# agent_coordinator.py

from typing import List, Dict
import uuid

class NegotiationCoordinator:
    """
    Coordinates multiple specialized negotiation agents.
    """
    
    def __init__(self, agents: List['NegotiationAgent']):
        self.agents = {agent.id: agent for agent in agents}
        self.active_negotiations: Dict[str, Dict] = {}  # negotiation_id -> state
    
    def assign_negotiation(self, negotiation_request: dict) -> str:
        """
        Route a negotiation request to the most suitable agent.
        
        Selection criteria:
          - Agent specialization (procurement, partnership, sales)
          - Agent current workload
          - Agent success rate on similar counterparties
        """
        deal_type = negotiation_request.get("deal_type")
        counterparty = negotiation_request.get("counterparty")
        
        # Find agents specialized in this deal type
        suitable_agents = [a for a in self.agents.values() 
                          if deal_type in a.specializations]
        
        if not suitable_agents:
            # Escalate to human
            return self._escalate_to_human(negotiation_request)
        
        # Score agents by workload + success rate
        scores = {}
        for agent in suitable_agents:
            success_rate = agent.success_rate_with_counterparty(counterparty)
            workload = len(self.active_negotiations)  # Simplified
            scores[agent.id] = success_rate - 0.1 * workload
        
        # Assign to highest-scoring agent
        best_agent_id = max(scores, key=scores.get)
        negotiation_id = str(uuid.uuid4())
        
        self.active_negotiations[negotiation_id] = {
            "agent_id": best_agent_id,
            "request": negotiation_request,
            "status": "active"
        }
        
        # Notify agent
        self.agents[best_agent_id].start_negotiation(negotiation_id, negotiation_request)
        
        return negotiation_id
    
    def resolve_agent_conflict(self, conflict: dict):
        """
        When agents disagree (e.g., two want to handle same customer),
        resolve via: priority rules, voting, human escalation.
        """
        agents_involved = conflict.get("agents", [])
        issue = conflict.get("issue")
        
        if len(agents_involved) == 1:
            # One agent wins
            winner = agents_involved[0]
        else:
            # Vote: each agent's weight = success rate
            weights = {a: self.agents[a].success_rate for a in agents_involved}
            winner = max(weights, key=weights.get)
        
        return winner
    
    def share_knowledge(self):
        """
        Periodic sync: agents share learnings (updated opponent models, tactics).
        """
        # Aggregate outcomes across all agents
        all_outcomes = [self.agents[a].recent_outcomes for a in self.agents]
        
        # Update global KG: new tactics, opponent patterns
        self._update_global_knowledge_graph(all_outcomes)
    
    def _escalate_to_human(self, request: dict) -> str:
        """Escalate negotiation to human decision-maker."""
        # Create escalation ticket
        pass
    
    def _update_global_knowledge_graph(self, outcomes: List[Dict]):
        """Update shared KG with new learnings."""
        pass
```

---

## 5. MONITORING & OBSERVABILITY

### 5.1 Audit Trail & Decision Tracing

```python
# audit_trail.py

class AuditTrail:
    """
    Immutable log of all agent decisions, reasoning, and outcomes.
    """
    
    def __init__(self, db):
        self.db = db
    
    def log_recommendation(self, recommendation: dict):
        """Log every recommendation the agent makes."""
        self.db.insert("agent_recommendations", {
            "id": uuid.uuid4(),
            "negotiation_id": recommendation["negotiation_id"],
            "agent_id": recommendation["agent_id"],
            "recommendation_type": recommendation["type"],  # offer, tactic, escalate
            "content": recommendation["content"],
            "confidence": recommendation.get("confidence"),
            "rationale": recommendation.get("rationale"),
            "timestamp": datetime.now()
        })
    
    def log_decision(self, decision: dict):
        """Log human decision on agent recommendation."""
        self.db.insert("human_decisions", {
            "recommendation_id": decision["recommendation_id"],
            "human_decision": decision["decision"],  # accepted, rejected, modified
            "feedback": decision.get("feedback"),
            "timestamp": datetime.now()
        })
    
    def log_outcome(self, outcome: dict):
        """Log deal outcome and agent performance."""
        self.db.insert("negotiation_outcomes", {
            "negotiation_id": outcome["negotiation_id"],
            "agent_id": outcome["agent_id"],
            "final_terms": outcome["final_terms"],
            "dispute_reported": outcome.get("dispute_reported", False),
            "deal_value_achieved": outcome["deal_value"],
            "target_value": outcome["target_value"],
            "performance_vs_target": outcome["deal_value"] / outcome["target_value"],
            "timestamp": datetime.now()
        })
    
    def generate_audit_report(self, negotiation_id: str) -> dict:
        """Generate full audit trail for negotiation."""
        recommendations = self.db.query(
            "SELECT * FROM agent_recommendations WHERE negotiation_id = %s",
            [negotiation_id]
        )
        decisions = self.db.query(
            "SELECT * FROM human_decisions WHERE recommendation_id IN (...)",
            [r["id"] for r in recommendations]
        )
        outcome = self.db.query_one(
            "SELECT * FROM negotiation_outcomes WHERE negotiation_id = %s",
            [negotiation_id]
        )
        
        return {
            "recommendations": recommendations,
            "human_decisions": decisions,
            "outcome": outcome,
            "generated_at": datetime.now()
        }
```

---

## 6. DEPLOYMENT CHECKLIST FOR ENTERPRISES

### Pre-Launch Validation

- [ ] **Data Foundation**
  - [ ] 3+ years of past contracts ingested
  - [ ] Semantic search index built and tested
  - [ ] Knowledge graph populated with >1000 deals
  - [ ] Outcome labels verified (80%+ accuracy)

- [ ] **Agent Development**
  - [ ] Negotiation agents trained on simulated scenarios
  - [ ] Performance benchmarked vs. human negotiators
  - [ ] Personality-aware variants tested
  - [ ] Code coverage >80%, security audit passed

- [ ] **Governance**
  - [ ] Policy engine tested on 50+ policy scenarios
  - [ ] Escalation workflows validated
  - [ ] Circuit breaker tested under stress
  - [ ] Legal review completed; insurance procured

- [ ] **Monitoring**
  - [ ] Audit trail captures all decisions
  - [ ] Dashboard shows real-time agent metrics
  - [ ] Anomaly detection enabled
  - [ ] Alert thresholds configured

- [ ] **Training & Change Management**
  - [ ] 10+ negotiators trained on copilot
  - [ ] Training material ready for scale
  - [ ] Change champion identified per business unit
  - [ ] Communication plan approved

### Go-Live

- [ ] **Phase 1 Pilot**
  - Copilot deployed to 5–10 negotiators
  - Monitor for 6 weeks; measure ROI
  - Collect feedback; iterate

- [ ] **Escalation**
  - Phase 2: Expand copilot + launch fleet
  - Fleet autonomously handles <$200K deals
  - Humans notified of outcomes

- [ ] **Scale**
  - Phase 3: Fleet handles 80%+ of deals
  - Multi-agent orchestration active
  - Cross-deal learning loop operating
  - 3–5 year roadmap initiated

---

## CONCLUSION

This technical specification provides enterprises with a concrete blueprint for deploying AI negotiation agents on the L9 platform. The architecture combines:

1. **Memory Substrate** (PostgreSQL + pgvector + Neo4j) for persistent memory and semantic reasoning
2. **Game-Theoretic Solver** for optimal strategy computation
3. **RL Policy** for continuous improvement
4. **Governance Policy Engine** for safe, policy-compliant autonomy
5. **Multi-Agent Orchestration** for coordinated negotiation at scale
6. **Audit & Monitoring** for explainability and compliance

With careful phasing, strong governance, and continuous learning, enterprises can deploy negotiation agents that enhance human capabilities while maintaining control and trust.

**Key Principle**: Humans remain in authority; AI amplifies capability.