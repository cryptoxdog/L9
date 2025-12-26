# config_loader Module Spec

Generated: 2025-12-17 00:23:23

Citations: 60

---

<think>
This is a detailed request for comprehensive research on configuration management in Python applications, particularly for a theoretical "L9" system architecture. The user wants me to generate a deep research report (10,000+ words) covering:

1. Pydantic Settings v2
2. Python-dotenv patterns
3. YAML configuration loading
4. 12-Factor App principles
5. FastAPI lifespan integration
6. Fail-fast patterns

The user also mentions they want a Module-Spec-v2.5 YAML output at the end, but the primary goal based on the instructions is a comprehensive research report.

Let me plan the structure:
1. Title and executive summary
2. Pydantic Settings v2 deep dive
3. Python-dotenv patterns and best practices
4. YAML configuration management
5. 12-Factor App methodology
6. FastAPI lifespan integration for configuration
7. Fail-fast patterns and validation strategies
8. Integrating PostgreSQL, Redis, and structured logging
9. Production architecture recommendations
10. Conclusion with the Module-Spec YAML

I need to make sure this is well-researched, citing the provided sources, and reaches at least 10,000 words. Let me start writing.
</think>

# Production-Ready Configuration Management Architecture: A Comprehensive L9 System Specification

This report provides an exhaustive examination of configuration management patterns for production-grade Python systems, synthesizing research on Pydantic Settings v2, environment variable management, YAML loading strategies, and fail-fast validation patterns. The analysis culminates in a complete Module-Spec-v2.5 for a Tier 0 configuration loader component suitable for sophisticated distributed systems requiring PostgreSQL, Redis, and structured logging integration.

## Pydantic Settings v2: Typed Configuration Foundation

The modern era of Python application development demands sophisticated configuration management that transcends simple dictionary lookups or environment variable parsing[1][4]. Pydantic Settings v2 represents a paradigm shift in how Python applications approach configuration by providing declarative, type-safe access to environment variables and configuration files through an elegant inheritance-based API. The foundation of this capability rests on the `BaseSettings` class, which extends Pydantic's BaseModel with environment variable binding capabilities[1][4].

When a model inherits from `BaseSettings`, the model initializer attempts to determine values for any fields not passed as keyword arguments by reading from the environment[1][4]. This automatic environment variable discovery eliminates boilerplate code and establishes a single source of truth for configuration. Default values continue to be used when matching environment variables are not set, ensuring backward compatibility and graceful degradation[1][4]. The beauty of this approach lies in its simplicity: developers define configuration as a class with typed fields, and Pydantic handles the complexity of environment variable parsing, type coercion, and validation.

Environment variable naming conventions in Pydantic Settings follow predictable rules that enable seamless integration with both development and production environments. By default, the environment variable name matches the field name exactly[1][4]. However, this behavior can be modified through the `env_prefix` configuration setting, allowing all environment variables to be prefixed with a common string, such as `my_prefix_`[1][4]. For a field named `auth_key` with an `env_prefix` of `my_prefix_`, Pydantic will read from the environment variable `my_prefix_auth_key`[1][4]. This prefix-based approach supports multiple independent configurations running on the same system, a critical requirement for containerized deployments where multiple services may run on shared infrastructure.

Case sensitivity represents another important configuration dimension. By default, environment variable names are case-insensitive, meaning both `REDIS_HOST` and `redis_host` would match a field named `redis_host`[1][4]. This permissive default accommodates the varied naming conventions found across different operating systems and shell environments. However, when strict case sensitivity is required, the `case_sensitive` configuration option can be set to `True`, enforcing exact matches between environment variable names and field names[1][4]. This level of control proves essential in scenarios where configuration precision is paramount or when interfacing with legacy systems employing strict naming conventions.

Pydantic Settings v2 introduces sophisticated handling of nested models, enabling hierarchical configuration structures that mirror real-world application architectures. When defining nested models, each submodel must inherit from `pydantic.BaseModel`, not `BaseSettings`[1]. The powerful aspect of this design emerges when combining nested models with environment variable parsing through the `env_nested_delimiter` configuration option[1]. Setting `env_nested_delimiter='__'` enables parsing of environment variables like `SUB_MODEL__V1=json-1` into nested structures, where double underscores represent hierarchical boundaries[1]. This pattern supports both flat environment variable listings and deeply nested configuration objects, providing flexibility across deployment scenarios.

Complex field types present particular challenges in configuration management. Lists, sets, dictionaries, and custom objects require special handling beyond simple string parsing. Pydantic Settings addresses this through JSON parsing: when a field type is identified as complex, the environment variable value is treated as a JSON-encoded string[2]. For example, passing `NUMBERS='[1, 2, 3]'` results in automatic parsing into a Python list[2]. This JSON-based approach provides powerful expressiveness while maintaining backward compatibility with systems unable to handle structured environment variable data.

Validation of configuration occurs during model instantiation, and Pydantic Settings v2 provides granular control over when and how validation is applied[1]. By default, default values are not validated unless explicitly configured through the `validate_default` parameter[1]. This design decision reflects the principle that developers control default values in code and should not be constrained by validation rules applied to user input. However, when defaults represent configuration that could be invalid, setting `validate_default=False` prevents unnecessary validation overhead[1].

Field validators in Pydantic v2 support sophisticated patterns through the `mode` parameter, enabling validators to run before (`mode='before'`) or after (`mode='after'`) Pydantic's internal parsing[31][34]. Before validators operate on raw input and can transform values before type coercion occurs[31][34]. After validators operate on already-parsed values and can enforce business logic constraints[31][34]. Custom validators further support context passing through the `info` parameter, enabling dynamic validation logic based on other field values or external state[31][34].

## Environment Variable Precedence and python-dotenv Integration

The twelve-factor application methodology establishes configuration best practices that have become industry standard[8][57]. This framework explicitly mandates that applications store configuration in environment variables, emphasizing that configuration varies substantially across deploys while code remains constant[8][57]. Environment variables represent a language- and OS-agnostic standard superior to configuration files scattered throughout projects or constants hardcoded into source code[8][57]. The critical insight is that environment variables enable configuration changes between deployment environments without code modification or recompilation.

Python-dotenv provides the mechanism for integrating `.env` files into applications while respecting the twelve-factor principle that environment variables take precedence over file-based configuration[6][53]. By default, `load_dotenv()` reads key-value pairs from a `.env` file and adds them to `os.environ`, but crucially, it does not override environment variables already set[6][53]. This default behavior implements the sensible principle that explicitly set environment variables represent more specific configuration than defaults stored in files[6][53].

Understanding precedence hierarchy proves critical for avoiding configuration confusion in production systems. The recommended precedence order, from highest to lowest, should be: explicitly set environment variables from the deployment platform, followed by `.env` file values, followed by hardcoded defaults in code[6][53]. This ordering ensures that system-level configuration takes precedence over development convenience files. When multiple `.env` files exist, they can be loaded in priority order, with later values overriding earlier ones, though this advanced pattern requires careful documentation to prevent maintainability issues[6][53].

The python-dotenv package supports multiple advanced loading patterns that enable sophisticated configuration management. The `dotenv_values()` function returns a dictionary of parsed values without modifying `os.environ`, enabling read-only access to `.env` file contents[6][53]. This pattern proves useful when application code needs to inspect configuration files without affecting the global environment state. Variable expansion features enable interpolation of environment variables within `.env` files using POSIX-style syntax, allowing configuration values to reference other values[6][53].

Encoding specification when loading `.env` files requires careful attention to character encoding requirements. The `env_file_encoding` parameter defaults to `'utf-8'`[6][53], supporting international characters and preventing encoding-related failures in multilingual environments. File handling follows context manager semantics, ensuring proper resource cleanup even when parsing fails or exceptions occur[6][53]. The `stream` parameter accepts both file paths and file-like objects, including `io.StringIO` instances, enabling programmatic configuration generation and testing scenarios[6][53].

Practical configuration management often requires orchestrating multiple configuration sources with clear precedence rules. A common pattern merges configuration from shared defaults, environment-specific files, and explicit environment variables through dictionary unpacking[6][53]. This approach enables teams to maintain centralized shared configuration, environment-specific overrides, and machine-specific adjustments without conflicts. Documentation of this layering becomes essential, as engineers must understand the precedence order to debug configuration issues effectively.

## YAML Configuration Loading and Safe Deserialization

YAML files provide human-readable configuration format increasingly adopted in modern applications[10][15][23]. Unlike JSON or XML, YAML emphasizes readability through minimal syntax, supporting comments, multi-line strings, and nested structures without excessive punctuation[10][15][23]. YAML's comprehensiveness makes it suitable for complex configuration scenarios involving multiple levels of nesting, lists of dictionaries, and mixed data types[10][15][23].

PyYAML implements YAML parsing for Python, providing both `yaml.load()` and `yaml.safe_load()` functions with critical security implications[7][10]. The fundamental distinction separates convenience from safety: `yaml.load()` deserializes arbitrary Python objects including functions and classes, enabling code execution vulnerabilities equivalent to pickle-based deserialization attacks[7]. Production code must use `yaml.safe_load()` exclusively, which recognizes only standard YAML tags representing simple Python objects like dictionaries, lists, and strings[7][10].

Safe YAML loading restricts deserialization to the following types: mappings (dictionaries), sequences (lists), strings, numbers, booleans, and null values[7][10]. This restriction eliminates the attack surface entirely by preventing instantiation of arbitrary classes or execution of arbitrary functions. When applications require custom type support, PyYAML provides mechanisms to mark custom classes as safe through the `yaml.YAMLObject` base class and explicit `yaml_loader` configuration[7]. This allows application-specific types to be safely deserialized while maintaining protections against untrusted input.

YAML parsing errors warrant special handling in production systems. Malformed YAML syntax, encoding issues, or file access failures should be caught and logged with sufficient context for debugging. The `yaml.YAMLError` exception and its subclasses provide type-specific error information, enabling precise error handling and user-friendly error messages[7]. In configuration loaders, YAML parsing errors should trigger application startup failure with explicit error reporting, preventing silent configuration misinterpretation.

File handling for YAML configuration follows standard Python patterns with specific considerations for encoding and error recovery. Opening YAML files with explicit encoding specification prevents platform-specific encoding issues[10]. Using context managers ensures file handles are properly closed regardless of success or failure, preventing resource leaks in long-running applications. When YAML files reference multiple documents using `---` delimiters, applications must either parse the first document and ignore others or explicitly handle multiple document sequences[10].

## 12-Factor Application Configuration Principles

The twelve-factor methodology provides proven guidance for building resilient, scalable applications suitable for modern cloud deployments[8][11][57]. This framework explicitly recognizes configuration as everything that varies between deployment environments: database connection strings, API credentials, service endpoints, and per-deploy values like hostnames[8][57]. The critical principle mandates strict separation of configuration from code, establishing that a codebase should be committable to version control without compromising credentials or environment-specific values.

Configuration should never be grouped into named environments like "development," "test," and "production." Instead, twelve-factor applications treat each configuration value as an independent control, independently managed for each deployment[8][57]. This granular approach scales smoothly as projects expand to multiple deployments—adding new staging environments, feature branch deployments, or per-developer sandboxes does not require code changes or complex environment configuration logic.

Environment variables represent the ideal mechanism for implementing twelve-factor configuration because they are language- and OS-agnostic, easy to change between deploys without requiring code modification, and unlikely to be accidentally committed to version control[8][57]. While configuration files offer some advantages over hardcoded constants, they still suffer from fragmentation across directories and formats, accidental commit risks, and language-specific semantics that complicate polyglot systems.

The hierarchical precedence for configuration values should flow from code defaults (lowest priority) through increasingly specific configuration layers to explicitly set environment variables (highest priority). This ensures that team default values, environment-specific settings, and local overrides coexist without conflicts[8][57]. Applications should fail immediately if required configuration is missing, rather than attempting to infer reasonable defaults or continuing with partial configuration. This fail-fast approach shifts configuration errors from runtime obscurity to startup visibility, enabling rapid detection and correction.

## FastAPI Application Startup Configuration and Lifespan Events

Modern web frameworks including FastAPI provide lifecycle hooks enabling applications to execute initialization logic before processing requests and cleanup logic after processing completes[9][12][55]. These hooks prove essential for loading expensive resources, establishing database connections, validating configuration, and preparing runtime state. FastAPI implements this pattern through the lifespan parameter, an async context manager controlling application startup and shutdown[9][12][55].

The lifespan pattern replaces earlier `@app.on_event("startup")` and `@app.on_event("shutdown")` decorators with a unified mechanism providing explicit connection between startup and shutdown logic[9][12][55]. This architecture enables resource management patterns where startup prepares a resource and shutdown releases it, maintaining shared state between the two phases through the context manager scope[9][12][55].

Configuration validation and initialization should occur during application startup, before the application begins serving requests. This ensures that configuration errors surface immediately when the application starts rather than during request handling. Loading expensive resources like machine learning models or database connection pools during startup prevents repeated initialization overhead on every request[9][12][55]. Logging initialization and configuration summary information during startup aids debugging and supports operational transparency.

Testing applications with lifespan events requires special consideration. The `TestClient` context manager can wrap the application, triggering lifespan startup before tests execute and lifespan shutdown after tests complete[12][58]. This enables comprehensive testing of initialization logic, configuration validation, and resource management in isolated test environments.

## Fail-Fast Patterns and ValidationError Handling

Production applications demand immediate notification of configuration errors rather than silent degradation or runtime failures. Pydantic's `ValidationError` exception provides detailed information about validation failures, including field locations, error types, and contextual messages[13][16]. Custom error messages enhance clarity by replacing cryptic validation error codes with human-readable descriptions explaining what configuration values are invalid and why[13].

Applications should catch `ValidationError` during configuration loading and either render detailed error information or re-raise with enhanced context. Catching exceptions enables custom formatting suitable for operational environments, while preserving stack traces for debugging. The `.errors()` method on `ValidationError` instances returns a list of dictionaries containing error details: field location, error type, validation message, and problematic input value[13][16].

Configuration validation should occur synchronously during application startup before initializing other systems. This ensures that no partial or incorrect state propagates to subsequent initialization phases. When validation fails, applications should log the specific configuration problems and exit with non-zero status code, triggering deployment platform alerts and preventing continued operation in an invalid state[14].

Structured logging frameworks enable rich context recording during configuration validation and startup. Rather than printing unstructured error messages, applications should record configuration validation errors with structured fields including timestamp, service name, configuration keys, error messages, and any relevant context[26][29]. This structured data enables subsequent search, analysis, and alerting through centralized logging infrastructure.

## PostgreSQL and Redis Integration with Configuration Management

Production L9 systems commonly employ PostgreSQL for persistent data storage with pgvector extensions enabling vector similarity searches[21][24]. Redis serves as a high-performance cache layer supporting session data, temporary state, and real-time analytics[47][56][59]. Configuration management must account for connections to both systems, handling connection string specifications, authentication credentials, pool sizing, and timeout parameters.

PostgreSQL connection configuration requires specification of host, port, user credentials, database name, and optional SSL settings. Connection URIs in `postgresql://user:password@host:port/database` format provide compact specification of all parameters[45]. The asyncpg library for asynchronous PostgreSQL connections accepts connection parameters through either DSN strings or individual keyword arguments[45]. Pool sizing parameters control the number of cached prepared statements and connection reuse behavior, directly impacting application performance under load[45].

Redis configuration similarly requires host and port specification, with optional authentication credentials, database selection, and protocol version preference[47][59]. Sentinel-based Redis deployments add complexity by requiring sentinel host addresses, master service names, and quorum specifications[56][59]. The configuration loader must support both direct Redis connections and Sentinel-mediated high-availability deployments without introducing deployment-specific complexity into application code.

## Structured Logging Integration with Configuration

Structured logging frameworks like structlog provide production-grade logging suitable for cloud-native deployments and comprehensive observability[26][29]. Rather than rendering log entries as unstructured text strings, structured logging separates concerns into key-value pairs that remain machine-processable throughout the logging pipeline[26][29]. Configuration initialization should log structured records including configuration source (environment variables, `.env` file, YAML, defaults), validation results, connection pool initialization, and any warnings or errors encountered[26][29].

Structlog configuration during application startup should establish log level settings derived from environment variables or configuration files, timestamp formatting for operational systems, and output formatting suitable for deployment environment. Development environments may benefit from human-readable console output, while production systems typically write structured JSON records to centralized logging infrastructure[26][29].

## Production Architecture: Complete Configuration Loader Module

Drawing together the preceding research domains, a production-grade configuration loader must integrate Pydantic Settings for type-safe configuration, python-dotenv for `.env` file support, YAML loading with safe deserialization, FastAPI lifespan integration, PostgreSQL and Redis connection management, structured logging, and comprehensive fail-fast validation. This component functions as Tier 0 infrastructure, loading before any other application module and establishing the foundation for all subsequent initialization.

The configuration loader architecture follows these principles: configuration is immutable after initial validation, supporting safe sharing across application threads; all configuration values are strongly typed through Pydantic models, eliminating runtime type uncertainties; missing required configuration triggers immediate startup failure with explicit error reporting; environment variables take precedence over file-based configuration; and configuration changes between deployments require no code modifications or recompilation.

Nested Pydantic models represent logical configuration subsystems: database connectivity parameters grouped in a `DatabaseConfig` model, Redis parameters in a `CacheConfig` model, logging parameters in a `LoggingConfig` model, and application-specific parameters in appropriate submodels. The top-level `ApplicationConfig` model composes these subsystems, providing unified access to all configuration.

Environment variable naming follows a hierarchical pattern where nested model fields are prefixed with their model name, for example `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USER`, `REDIS_HOST`, and `REDIS_PORT`. This pattern enables deployment systems to configure each subsystem independently through environment variable assignment. The configuration loader parses these variables, validates them, and exposes them through typed Python objects ensuring compile-time safety in static type checkers and runtime safety through validation.

Configuration validation occurs in the FastAPI lifespan startup phase, before any request processing. Validation failures immediately trigger application startup errors, preventing deployment of misconfigured instances. Upon successful validation, configuration objects are made available to request handlers through dependency injection, ensuring consistent access patterns throughout the application.

## Advanced Configuration Patterns for Distributed Systems

Large-scale systems commonly require different configuration for different deployment phases or processing modes. Configuration layering enables this by composing multiple configuration sources with explicit precedence: hardcoded application defaults, optional `.env` file configuration, YAML file configuration, and finally environment variable overrides. This pattern supports development workflows where `.env` files store development-specific settings, deployment automation where YAML files define per-environment configuration, and runtime overrides through environment variables.

Secret management represents a critical dimension of production configuration. Sensitive values like database passwords, API keys, and authentication tokens should never be stored in code or committed to version control. Python-dotenv supports `.env` files excluded from version control through `.gitignore` patterns, enabling local development with real credentials without exposing them to version control systems[43][46]. Production systems should retrieve secrets from dedicated secret management services like AWS Secrets Manager, Azure Key Vault, or HashiCorp Vault through secure credential supply chains[43][46].

Configuration change management requires careful orchestration in long-running systems. Applications may need to reload configuration without full restarts, though this complexity should be avoided when possible. When configuration reloading is necessary, strict validation and atomic updates prevent transitioning to partially-updated or invalid configuration states. Immutable configuration objects prove essential for thread-safe configuration access during reload operations.

## Synthesis and Implementation Guidance

Configuration management forms the foundation of production applications, directly impacting reliability, security, and operational effectiveness. Successful implementations separate configuration concerns from application logic, provide type-safe access to all configuration values, validate configuration at startup before any processing begins, and maintain clear precedence hierarchies when multiple configuration sources exist.

Pydantic Settings v2 provides the ideal foundation for typed configuration management, enabling developers to define configuration as Python classes with validation rules and automatic environment variable binding. Integration with python-dotenv adds support for convenient `.env` file loading during development while maintaining production-grade precedence semantics. YAML configuration files support complex scenarios requiring hierarchical structures, while structured logging enables operational visibility into configuration and initialization processes.

The twelve-factor methodology guides architectural decisions, particularly the principle that configuration should vary between deployments while code remains constant. FastAPI lifespan events provide hooks for configuration validation and resource initialization at precisely the right time in application startup. PostgreSQL and Redis integration requires careful configuration to establish performant connections while maintaining security and reliability.

Fail-fast philosophy demands that configuration errors surface immediately during startup rather than appearing as obscure runtime failures hours or days later. This principle drives immediate validation of all configuration at application startup, detailed error reporting that guides rapid correction, and explicit notification to deployment platforms when configuration prevents application startup.

---

# Module-Spec-v2.5: config_loader

```yaml
---
module_spec_version: '2.5'
module_id: config_loader
module_name: Configuration Loader
module_tier: 0
module_category: core_infrastructure

description: >
  Tier 0 core infrastructure module providing environment and YAML configuration
  management with comprehensive validation. Loads before all other L9 modules,
  establishing typed access to application configuration via Pydantic Settings v2.
  Implements fail-fast validation, ensuring invalid configuration prevents startup
  with explicit error reporting suitable for operational visibility.

dependencies:
  module_dependencies: []
  external_dependencies:
    - pydantic>=2.5.0
    - pydantic-settings>=2.1.0
    - python-dotenv>=1.0.0
    - PyYAML>=6.0.0
    - structlog>=24.1.0

interfaces:
  provided:
    - config_provider:
        description: >
          Exposes validated application configuration through strongly-typed
          Pydantic models. Configuration is immutable after validation and
          safely shareable across application threads.
        methods:
          - get_config() -> ApplicationConfig
          - get_database_config() -> DatabaseConfig
          - get_cache_config() -> CacheConfig
          - get_logging_config() -> LoggingConfig
          - validate_config() -> ValidationResult
  required: []

configuration:
  environment_variables:
    - DATABASE_HOST: { type: string, default: "localhost", required: false }
    - DATABASE_PORT: { type: integer, default: 5432, required: false }
    - DATABASE_USER: { type: string, required: true }
    - DATABASE_PASSWORD: { type: string, required: true, sensitive: true }
    - DATABASE_NAME: { type: string, default: "l9_core", required: false }
    - DATABASE_POOL_SIZE: { type: integer, default: 20, required: false }
    - DATABASE_MAX_OVERFLOW: { type: integer, default: 10, required: false }
    - DATABASE_ECHO: { type: boolean, default: false, required: false }
    - DATABASE_SSL_MODE: { type: string, default: "prefer", required: false }
    - REDIS_HOST: { type: string, default: "localhost", required: false }
    - REDIS_PORT: { type: integer, default: 6379, required: false }
    - REDIS_DB: { type: integer, default: 0, required: false }
    - REDIS_PASSWORD: { type: string, required: false, sensitive: true }
    - REDIS_SENTINEL_HOSTS: { type: string, required: false }
    - REDIS_SENTINEL_SERVICE_NAME: { type: string, default: "mymaster", required: false }
    - LOG_LEVEL: { type: string, default: "INFO", required: false }
    - LOG_FORMAT: { type: string, default: "json", required: false }
    - LOG_OUTPUT: { type: string, default: "stdout", required: false }
    - APPLICATION_ENV: { type: string, default: "development", required: false }
    - APPLICATION_DEBUG: { type: boolean, default: false, required: false }
    - ENABLE_VECTORDB: { type: boolean, default: true, required: false }

  dotenv_support:
    enabled: true
    file_path: ".env"
    encoding: "utf-8"
    override_existing: false
    search_upward: true

  yaml_support:
    enabled: true
    safe_loading_only: true
    supported_formats:
      - application/yaml
      - application/x-yaml

lifespan_integration:
  startup:
    - load_environment_variables
    - load_dotenv_files
    - parse_yaml_configuration
    - validate_all_configuration
    - initialize_structured_logging
    - health_check_prerequisites
    - log_configuration_summary
  shutdown:
    - flush_logging
    - close_configuration_resources

validation:
  fail_on_error: true
  detailed_error_reporting: true
  validation_errors:
    - invalid_type: "Configuration value cannot be coerced to required type"
    - missing_required: "Required configuration environment variable not set"
    - invalid_format: "Configuration value does not match expected format"
    - out_of_range: "Configuration numeric value exceeds valid range"
    - invalid_url: "Configuration URL is malformed or uses unsupported scheme"

security:
  secret_handling:
    - never_log_secrets: true
    - mask_sensitive_values: true
    - validate_secret_permissions: true
    - support_secret_rotation: true
  credential_sources:
    - environment_variables_only: true
    - external_secret_managers: ["aws_secrets", "azure_keyvault", "vault"]
    - dotenv_for_development_only: true
    - no_hardcoded_secrets: true

database_configuration:
  connection_string_format: "postgresql+asyncpg://user:password@host:port/database"
  connection_parameters:
    host:
      type: string
      description: "PostgreSQL server hostname or IP address"
      required: true
      environment_variable: "DATABASE_HOST"
    port:
      type: integer
      description: "PostgreSQL server port"
      default: 5432
      environment_variable: "DATABASE_PORT"
      range: [1024, 65535]
    user:
      type: string
      description: "PostgreSQL database user"
      required: true
      environment_variable: "DATABASE_USER"
    password:
      type: string
      description: "PostgreSQL database password"
      required: true
      environment_variable: "DATABASE_PASSWORD"
      sensitive: true
    database:
      type: string
      description: "PostgreSQL database name"
      default: "l9_core"
      environment_variable: "DATABASE_NAME"
    pool_size:
      type: integer
      description: "Maximum number of database connections in pool"
      default: 20
      environment_variable: "DATABASE_POOL_SIZE"
      range: [5, 100]
    max_overflow:
      type: integer
      description: "Maximum overflow connections beyond pool_size"
      default: 10
      environment_variable: "DATABASE_MAX_OVERFLOW"
      range: [0, 50]
    echo:
      type: boolean
      description: "Enable SQL query logging for debugging"
      default: false
      environment_variable: "DATABASE_ECHO"
    ssl_mode:
      type: string
      description: "SSL connection mode: disable, allow, prefer, require, verify-ca, verify-full"
      default: "prefer"
      environment_variable: "DATABASE_SSL_MODE"
      valid_values: ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]
  pgvector_extension:
    enabled: true
    required_version: "0.5.0"
    dimensions_supported: [1024]
    operations: ["cosine_distance", "l2_distance", "inner_product"]

cache_configuration:
  backend: redis
  connection_parameters:
    host:
      type: string
      description: "Redis server hostname or IP address"
      default: "localhost"
      environment_variable: "REDIS_HOST"
    port:
      type: integer
      description: "Redis server port"
      default: 6379
      environment_variable: "REDIS_PORT"
      range: [1024, 65535]
    db:
      type: integer
      description: "Redis database number"
      default: 0
      environment_variable: "REDIS_DB"
      range: [0, 15]
    password:
      type: string
      description: "Redis password for authentication"
      required: false
      environment_variable: "REDIS_PASSWORD"
      sensitive: true
  sentinel_support:
    enabled: true
    hosts:
      type: string
      description: "Comma-separated sentinel hosts"
      environment_variable: "REDIS_SENTINEL_HOSTS"
      format: "host1:26379,host2:26379,host3:26379"
    service_name:
      type: string
      description: "Redis service name in Sentinel configuration"
      default: "mymaster"
      environment_variable: "REDIS_SENTINEL_SERVICE_NAME"
    quorum:
      type: integer
      description: "Sentinel quorum for failover decisions"
      default: 2
      range: [1, 5]
  connection_pooling:
    min_idle: 2
    max_size: 50
    connection_timeout_ms: 5000
    idle_timeout_ms: 300000

logging_configuration:
  framework: structlog
  processors:
    - add_log_level
    - add_timestamp
    - add_service_name
    - json_renderer
  log_level:
    type: string
    default: "INFO"
    environment_variable: "LOG_LEVEL"
    valid_values: ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
  output_format:
    type: string
    default: "json"
    environment_variable: "LOG_FORMAT"
    valid_values: ["json", "text", "syslog"]
  output_destination:
    type: string
    default: "stdout"
    environment_variable: "LOG_OUTPUT"
    valid_values: ["stdout", "stderr", "file", "syslog"]
  context_fields:
    - service_name
    - version
    - environment
    - request_id
    - user_id
    - correlation_id

application_configuration:
  environment:
    type: string
    default: "development"
    environment_variable: "APPLICATION_ENV"
    valid_values: ["development", "staging", "production"]
  debug_mode:
    type: boolean
    default: false
    environment_variable: "APPLICATION_DEBUG"
  enable_vector_database:
    type: boolean
    default: true
    environment_variable: "ENABLE_VECTORDB"
  enable_http_client_pooling:
    type: boolean
    default: true
  http_client_timeout_seconds:
    type: integer
    default: 30
    range: [5, 300]
  max_workers_for_async_tasks:
    type: integer
    default: 10
    range: [1, 100]

output:
  exports:
    config_instance:
      type: ApplicationConfig
      description: "Fully validated application configuration object"
    database_url:
      type: string
      description: "Validated PostgreSQL connection URL"
    redis_url:
      type: string
      description: "Validated Redis connection URL"
    logger_instance:
      type: structlog.BoundLogger
      description: "Configured structured logger"
  metrics:
    - config_load_duration_ms
    - config_validation_duration_ms
    - config_error_count
    - missing_required_variables_count

error_handling:
  validation_errors:
    behavior: fail_fast
    reporting: detailed
    logging: structured_json
  missing_required_configuration:
    behavior: startup_failure
    exit_code: 1
    notification: "Alert deployment platform"
  partial_configuration_detected:
    behavior: log_warning
    action: continue_with_defaults
  configuration_reload:
    enabled: false
    reason: "Immutable configuration prevents runtime updates"

testing:
  fixtures:
    valid_config

---

## Sources

1. https://docs.pydantic.dev/latest/concepts/pydantic_settings/
2. https://github.com/pydantic/pydantic-settings/issues/331
3. https://github.com/theskumar/python-dotenv/issues/5
4. https://docs.pydantic.dev/2.2/usage/pydantic_settings/
5. https://docs.pydantic.dev/latest/concepts/models/
6. https://pypi.org/project/python-dotenv/
7. https://pyyaml.org/wiki/PyYAMLDocumentation
8. https://12factor.net/config
9. https://fastapi.tiangolo.com/advanced/events/
10. https://www.freecodecamp.org/news/how-to-work-with-yaml-in-python-a-guide-with-examples/
11. https://12factor.net
12. https://fastapi.tiangolo.com/advanced/testing-events/
13. https://docs.pydantic.dev/latest/errors/errors/
14. https://tech.preferred.jp/en/blog/working-with-configuration-in-python/
15. https://www.cloudbees.com/blog/yaml-tutorial-everything-you-need-get-started
16. https://docs.pydantic.dev/latest/errors/validation_errors/
17. https://docs.python.org/3/c-api/init_config.html
18. https://yaml.org
19. https://docs.pydantic.dev/latest/concepts/pydantic_settings/
20. https://docs.ultralytics.com/guides/model-yaml-config/
