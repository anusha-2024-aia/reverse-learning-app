import re
from typing import Dict, List, Any, Optional

# Registry mapping topic names to required core concepts and evidence aliases
TOPIC_CONCEPTS_REGISTRY: Dict[str, List[Dict[str, Any]]] = {
    # System Design Basics
    "client-server architecture": [
        {"concept": "Client", "aliases": ["client", "browser", "frontend", "user agent", "mobile app"]},
        {"concept": "Server", "aliases": ["server", "backend", "web server", "application server", "host"]},
        {"concept": "Request", "aliases": ["request", "http request", "client request", "get request", "post request"]},
        {"concept": "Response", "aliases": ["response", "http response", "server response", "payload", "json response"]},
        {"concept": "HTTP/HTTPS Protocol", "aliases": ["http", "https", "protocol", "transport layer"]},
        {"concept": "Statelessness", "aliases": ["stateless", "statelessness", "no session state", "independent requests"]}
    ],
    "load balancing": [
        {"concept": "Load Balancer", "aliases": ["load balancer", "lb", "reverse proxy", "nginx", "haproxy"]},
        {"concept": "Traffic Distribution", "aliases": ["distribute traffic", "distribution", "balancing load", "routing requests"]},
        {"concept": "Algorithms", "aliases": ["round robin", "least connections", "ip hash", "weighted"]},
        {"concept": "Health Checks", "aliases": ["health check", "heartbeat", "unhealthy node", "monitoring"]},
        {"concept": "High Availability", "aliases": ["high availability", "ha", "redundancy", "failover", "zero downtime"]}
    ],
    "database design (sql vs nosql)": [
        {"concept": "Relational (SQL)", "aliases": ["sql", "relational", "tables", "rows", "columns", "postgresql", "mysql"]},
        {"concept": "Non-Relational (NoSQL)", "aliases": ["nosql", "document store", "key value", "mongodb", "dynamodb"]},
        {"concept": "ACID Properties", "aliases": ["acid", "atomicity", "consistency", "isolation", "durability", "transactions"]},
        {"concept": "BASE / Eventual Consistency", "aliases": ["base", "eventual consistency", "cap theorem", "availability"]},
        {"concept": "Schema & Joins", "aliases": ["schema", "foreign key", "joins", "normalization", "structured"]}
    ],
    "caching strategies": [
        {"concept": "Cache Layer", "aliases": ["cache", "caching", "in-memory", "redis", "memcached"]},
        {"concept": "Cache Hit / Miss", "aliases": ["cache hit", "cache miss", "hit ratio"]},
        {"concept": "Eviction Policies", "aliases": ["lru", "lfu", "ttl", "eviction", "time to live", "expiration"]},
        {"concept": "Caching Patterns", "aliases": ["cache-aside", "write-through", "write-back", "read-through"]}
    ],
    "message queues": [
        {"concept": "Message Queue / Broker", "aliases": ["message queue", "mq", "broker", "rabbitmq", "kafka", "sqs"]},
        {"concept": "Producer & Consumer", "aliases": ["producer", "consumer", "publisher", "subscriber", "pub sub"]},
        {"concept": "Asynchronous Processing", "aliases": ["async", "asynchronous", "decoupling", "background task", "job queue"]},
        {"concept": "Message Delivery & Persistence", "aliases": ["acknowledgment", "ack", "at least once", "idempotency", "persistence"]}
    ],

    # Python Fundamentals
    "variables & data types": [
        {"concept": "Variables", "aliases": ["variable", "assignment", "naming", "reference"]},
        {"concept": "Data Types", "aliases": ["data type", "type", "primitive", "object"]},
        {"concept": "Numbers (int / float)", "aliases": ["int", "integer", "float", "number", "numeric"]},
        {"concept": "Strings (str)", "aliases": ["str", "string", "character", "quotes", "text"]},
        {"concept": "Booleans (bool)", "aliases": ["bool", "boolean", "true", "false", "logical"]},
        {"concept": "Mutability", "aliases": ["mutable", "immutable", "reassignment", "id"]}
    ],
    "lists & tuples": [
        {"concept": "Lists", "aliases": ["list", "array", "mutable sequence", "square brackets"]},
        {"concept": "Tuples", "aliases": ["tuple", "immutable sequence", "parentheses"]},
        {"concept": "Indexing & Slicing", "aliases": ["index", "indexing", "slice", "slicing", "zero based"]},
        {"concept": "List Methods", "aliases": ["append", "extend", "pop", "insert", "remove", "sort"]},
        {"concept": "Immutability vs Mutability", "aliases": ["immutable", "mutable", "modify", "read-only"]}
    ],
    "dictionaries & sets": [
        {"concept": "Dictionaries (dict)", "aliases": ["dict", "dictionary", "key-value", "hash map", "keys", "values"]},
        {"concept": "Sets (set)", "aliases": ["set", "unique", "unordered", "union", "intersection", "curly braces"]},
        {"concept": "Hashing & Keys", "aliases": ["hash", "hashable", "lookup", "o(1)"]},
        {"concept": "Dictionary Operations", "aliases": ["get", "items", "update", "pop", "dictionary methods"]}
    ],
    "functions & lambda": [
        {"concept": "Function Definition", "aliases": ["def", "function", "parameters", "arguments", "return"]},
        {"concept": "Scope & Namespace", "aliases": ["scope", "global", "local", "legb", "nonlocal"]},
        {"concept": "Lambda Expressions", "aliases": ["lambda", "anonymous function", "inline function", "one line"]},
        {"concept": "Default & Keyword Arguments", "aliases": ["default argument", "kwargs", "args", "keyword args"]}
    ],
    "loops & conditionals": [
        {"concept": "Conditional Logic", "aliases": ["if", "elif", "else", "conditional", "boolean condition"]},
        {"concept": "For Loops", "aliases": ["for loop", "iteration", "iterable", "range"]},
        {"concept": "While Loops", "aliases": ["while loop", "condition loop", "infinite loop"]},
        {"concept": "Loop Control (break/continue)", "aliases": ["break", "continue", "pass", "loop control"]}
    ],
    "exception handling": [
        {"concept": "Try-Except Blocks", "aliases": ["try", "except", "catch", "exception handling"]},
        {"concept": "Finally & Else", "aliases": ["finally", "else block", "cleanup"]},
        {"concept": "Raising Exceptions", "aliases": ["raise", "throw", "custom exception", "error message"]},
        {"concept": "Built-in Exceptions", "aliases": ["valueerror", "typeerror", "keyerror", "indexerror", "baseexception"]}
    ],
    "list comprehensions": [
        {"concept": "Comprehension Syntax", "aliases": ["list comprehension", "brackets", "concise loop"]},
        {"concept": "Filtering (if condition)", "aliases": ["filter", "if clause", "conditional comprehension"]},
        {"concept": "Transformation", "aliases": ["map", "expression", "transform items"]},
        {"concept": "Performance Benefits", "aliases": ["c speed", "faster than loop", "pythonic", "readability"]}
    ],
    "decorators & closures": [
        {"concept": "Decorators", "aliases": ["decorator", "@", "wrapper", "higher order function"]},
        {"concept": "Closures", "aliases": ["closure", "nested function", "enclosing scope", "free variable"]},
        {"concept": "Function Arguments Pass-through", "aliases": ["*args", "**kwargs", "functools.wraps", "signature"]}
    ]
}


def normalize_text(text: str) -> str:
    """
    Normalizes text by converting to lowercase, replacing punctuation with spaces,
    and collapsing extra whitespace.
    """
    if not text:
        return ""
    # Replace non-alphanumeric characters (except spaces) with space
    clean = re.sub(r'[^\w\s]', ' ', text.lower())
    # Collapse multiple spaces
    return re.sub(r'\s+', ' ', clean).strip()


def get_concepts_for_topic(topic_name: str) -> List[Dict[str, Any]]:
    """
    Retrieves required concepts for a topic name. If exact topic name is not found,
    attempts case-insensitive matching or fallback concept extraction.
    """
    if not topic_name:
        return []
    
    key = topic_name.strip().lower()
    if key in TOPIC_CONCEPTS_REGISTRY:
        return TOPIC_CONCEPTS_REGISTRY[key]
    
    # Partial match check
    for reg_key, concepts in TOPIC_CONCEPTS_REGISTRY.items():
        if reg_key in key or key in reg_key:
            return concepts
            
    # Fallback: Extract words from topic name as default concepts if not registered
    words = [w for w in re.split(r'\W+', topic_name) if len(w) > 3]
    fallback_concepts = []
    for word in words[:4]:
        fallback_concepts.append({
            "concept": word.capitalize(),
            "aliases": [word.lower()]
        })
    return fallback_concepts


def calculate_concept_coverage(explanation: str, topic_name: str, required_concepts: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Calculates deterministic Concept Coverage % for a given student explanation.
    
    Returns:
      {
        "required_count": int,
        "covered_count": int,
        "coverage_percentage": float | None,
        "covered_concepts": list[str],
        "missing_concepts": list[str],
        "details": list[dict] # [{"concept": str, "covered": bool, "matched_evidence": str|None}]
      }
    """
    if required_concepts is None:
        required_concepts = get_concepts_for_topic(topic_name)
        
    required_count = len(required_concepts)
    
    # Handle zero required concepts safety
    if required_count == 0:
        return {
            "required_count": 0,
            "covered_count": 0,
            "coverage_percentage": None,
            "covered_concepts": [],
            "missing_concepts": [],
            "details": []
        }
        
    normalized_explanation = normalize_text(explanation)
    
    covered_concepts = []
    missing_concepts = []
    details = []
    
    # Empty explanation check
    if not normalized_explanation:
        for c in required_concepts:
            concept_name = c["concept"]
            missing_concepts.append(concept_name)
            details.append({
                "concept": concept_name,
                "covered": False,
                "matched_evidence": None
            })
        return {
            "required_count": required_count,
            "covered_count": 0,
            "coverage_percentage": 0.0,
            "covered_concepts": [],
            "missing_concepts": missing_concepts,
            "details": details
        }
        
    # Check each required concept against normalized explanation
    for item in required_concepts:
        concept_name = item["concept"]
        aliases = item.get("aliases", [concept_name.lower()])
        
        matched_evidence = None
        for alias in aliases:
            norm_alias = normalize_text(alias)
            if not norm_alias:
                continue
                
            # Regex word-boundary search to avoid partial word false positives
            pattern = r'\b' + re.escape(norm_alias) + r'\b'
            if re.search(pattern, normalized_explanation):
                matched_evidence = norm_alias
                break
                
        if matched_evidence:
            covered_concepts.append(concept_name)
            details.append({
                "concept": concept_name,
                "covered": True,
                "matched_evidence": matched_evidence
            })
        else:
            missing_concepts.append(concept_name)
            details.append({
                "concept": concept_name,
                "covered": False,
                "matched_evidence": None
            })
            
    covered_count = len(covered_concepts)
    coverage_percentage = round((covered_count / required_count) * 100.0, 1)
    
    return {
        "required_count": required_count,
        "covered_count": covered_count,
        "coverage_percentage": coverage_percentage,
        "covered_concepts": covered_concepts,
        "missing_concepts": missing_concepts,
        "details": details
    }
