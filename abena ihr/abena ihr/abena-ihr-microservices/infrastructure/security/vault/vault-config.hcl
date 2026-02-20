# Abena IHR Vault Configuration
# Secure secret management for healthcare microservices

# Storage backend
storage "raft" {
  path = "/vault/data"
  node_id = "node-1"
  
  retry_join {
    leader_api_addr = "https://vault-0.vault-internal:8200"
    leader_ca_cert_file = "/vault/userconfig/vault-ha-tls/vault.ca"
    leader_client_cert_file = "/vault/userconfig/vault-ha-tls/vault.crt"
    leader_client_key_file = "/vault/userconfig/vault-ha-tls/vault.key"
  }
  
  retry_join {
    leader_api_addr = "https://vault-1.vault-internal:8200"
    leader_ca_cert_file = "/vault/userconfig/vault-ha-tls/vault.ca"
    leader_client_cert_file = "/vault/userconfig/vault-ha-tls/vault.crt"
    leader_client_key_file = "/vault/userconfig/vault-ha-tls/vault.key"
  }
  
  retry_join {
    leader_api_addr = "https://vault-2.vault-internal:8200"
    leader_ca_cert_file = "/vault/userconfig/vault-ha-tls/vault.ca"
    leader_client_cert_file = "/vault/userconfig/vault-ha-tls/vault.crt"
    leader_client_key_file = "/vault/userconfig/vault-ha-tls/vault.key"
  }
}

# Listener configuration
listener "tcp" {
  address = "0.0.0.0:8200"
  tls_disable = false
  tls_cert_file = "/vault/userconfig/vault-ha-tls/vault.crt"
  tls_key_file = "/vault/userconfig/vault-ha-tls/vault.key"
  tls_client_ca_file = "/vault/userconfig/vault-ha-tls/vault.ca"
  tls_require_and_verify_client_cert = true
}

# API configuration
api_addr = "https://vault.abena-ihr.com:8200"
cluster_addr = "https://vault-0.vault-internal:8201"

# UI configuration
ui = true
disable_mlock = true

# Telemetry configuration
telemetry {
  prometheus_retention_time = "24h"
  disable_hostname = true
}

# Seal configuration (for production, use AWS KMS or Azure Key Vault)
seal "shamir" {
  secret_shares = 5
  secret_threshold = 3
}

# Audit logging
audit "file" {
  path = "/vault/logs/audit.log"
  format = "json"
  log_raw = false
  hmac_accessor = false
}

# Logging configuration
log_level = "info"
log_format = "json"

# Default lease TTL
default_lease_ttl = "1h"
max_lease_ttl = "24h"

# Cluster configuration
cluster_name = "abena-ihr-vault"
cluster_cipher_suites = "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"

# Auto-unseal configuration (for production)
# seal "awskms" {
#   region = "us-east-1"
#   kms_key_id = "alias/abena-ihr-vault"
# }

# HA configuration
ha_storage "raft" {
  path = "/vault/ha"
  node_id = "node-1"
  
  retry_join {
    leader_api_addr = "https://vault-0.vault-internal:8200"
    leader_ca_cert_file = "/vault/userconfig/vault-ha-tls/vault.ca"
    leader_client_cert_file = "/vault/userconfig/vault-ha-tls/vault.crt"
    leader_client_key_file = "/vault/userconfig/vault-ha-tls/vault.key"
  }
}

# Plugin directory
plugin_directory = "/vault/plugins"

# Entropy augmentation
entropy "seal" {
  mode = "augmentation"
}

# Performance standby configuration
performance_standby = true

# Service registration
service_registration "kubernetes" {
  namespace = "vault"
  pod_name = "vault-0"
  pod_ip = "10.0.0.1"
}

# Auto-auth configuration
auto_auth {
  method "kubernetes" {
    mount_path = "auth/kubernetes"
    config = {
      role = "abena-ihr-vault"
    }
  }
  
  method "approle" {
    mount_path = "auth/approle"
    config = {
      role_id_file_path = "/vault/userconfig/vault-approle/role-id"
      secret_id_file_path = "/vault/userconfig/vault-approle/secret-id"
    }
  }
}

# Sink configuration
sink "file" {
  config = {
    path = "/vault/userconfig/vault-token/token"
  }
}

# Template configuration for dynamic secrets
template {
  source = "/vault/userconfig/vault-templates/database-creds.tpl"
  destination = "/vault/userconfig/vault-secrets/database-creds.json"
  command = "restart"
}

# Vault policies for healthcare services
# Admin policy
path "sys/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

path "auth/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

path "secret/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Patient engagement service policy
path "secret/patient-engagement/*" {
  capabilities = ["read", "list"]
}

path "secret/database/patient-engagement" {
  capabilities = ["read"]
}

path "secret/redis/patient-engagement" {
  capabilities = ["read"]
}

# Clinical decision support service policy
path "secret/clinical-decision-support/*" {
  capabilities = ["read", "list"]
}

path "secret/database/clinical-decision-support" {
  capabilities = ["read"]
}

path "secret/ai-models/*" {
  capabilities = ["read"]
}

# Data ingestion service policy
path "secret/data-ingestion/*" {
  capabilities = ["read", "list"]
}

path "secret/database/data-ingestion" {
  capabilities = ["read"]
}

path "secret/kafka/*" {
  capabilities = ["read"]
}

# Privacy security service policy
path "secret/privacy-security/*" {
  capabilities = ["read", "list"]
}

path "secret/encryption-keys/*" {
  capabilities = ["read"]
}

path "secret/certificates/*" {
  capabilities = ["read"]
}

# Telemedicine service policy
path "secret/telemedicine/*" {
  capabilities = ["read", "list"]
}

path "secret/webrtc/*" {
  capabilities = ["read"]
}

path "secret/video-storage/*" {
  capabilities = ["read"]
}

# Blockchain service policy
path "secret/blockchain/*" {
  capabilities = ["read", "list"]
}

path "secret/hyperledger/*" {
  capabilities = ["read"]
}

# Analytics engine service policy
path "secret/analytics-engine/*" {
  capabilities = ["read", "list"]
}

path "secret/database/analytics-engine" {
  capabilities = ["read"]
}

# Science intelligence service policy
path "secret/science-intelligence/*" {
  capabilities = ["read", "list"]
}

path "secret/research-data/*" {
  capabilities = ["read"]
}

# Unified data service policy
path "secret/unified-data/*" {
  capabilities = ["read", "list"]
}

path "secret/database/unified-data" {
  capabilities = ["read"]
}

# Auth service policy
path "secret/auth-service/*" {
  capabilities = ["read", "list"]
}

path "secret/jwt-keys/*" {
  capabilities = ["read"]
}

path "secret/oauth/*" {
  capabilities = ["read"]
}

# Provider workflow service policy
path "secret/provider-workflow/*" {
  capabilities = ["read", "list"]
}

path "secret/database/provider-workflow" {
  capabilities = ["read"]
}

# Monitoring and logging policies
path "secret/monitoring/*" {
  capabilities = ["read", "list"]
}

path "secret/logging/*" {
  capabilities = ["read", "list"]
}

# Infrastructure policies
path "secret/kubernetes/*" {
  capabilities = ["read", "list"]
}

path "secret/istio/*" {
  capabilities = ["read", "list"]
}

path "secret/nginx/*" {
  capabilities = ["read", "list"]
}

# Backup and disaster recovery
path "secret/backup/*" {
  capabilities = ["read", "list"]
}

path "secret/disaster-recovery/*" {
  capabilities = ["read", "list"]
}

# Healthcare compliance policies
path "secret/hipaa/*" {
  capabilities = ["read", "list"]
}

path "secret/gdpr/*" {
  capabilities = ["read", "list"]
}

path "secret/compliance/*" {
  capabilities = ["read", "list"]
}

# Audit and logging
path "sys/audit/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "sys/audit" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Health check
path "sys/health" {
  capabilities = ["read"]
}

# Metrics
path "sys/metrics" {
  capabilities = ["read"]
}

# Leader
path "sys/leader" {
  capabilities = ["read"]
}

# Replication status
path "sys/replication/*" {
  capabilities = ["read"]
}

# Mounts
path "sys/mounts/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "sys/mounts" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Policies
path "sys/policies/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "sys/policies" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Tokens
path "auth/token/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

path "auth/token" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

# Kubernetes auth
path "auth/kubernetes/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "auth/kubernetes" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# AppRole auth
path "auth/approle/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "auth/approle" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# LDAP auth
path "auth/ldap/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "auth/ldap" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# OIDC auth
path "auth/oidc/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "auth/oidc" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Database secrets engine
path "database/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# PKI secrets engine
path "pki/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Transit secrets engine
path "transit/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# SSH secrets engine
path "ssh/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# AWS secrets engine
path "aws/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Azure secrets engine
path "azure/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# GCP secrets engine
path "gcp/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Kubernetes secrets engine
path "kubernetes/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Nomad secrets engine
path "nomad/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# RabbitMQ secrets engine
path "rabbitmq/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Terraform secrets engine
path "terraform/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Vault agent configuration
agent {
  # Vault agent configuration
  exit_after_auth = false
  pid_file = "/vault/agent.pid"
  
  # Auto-auth configuration
  auto_auth {
    method "kubernetes" {
      mount_path = "auth/kubernetes"
      config = {
        role = "abena-ihr-vault"
      }
    }
  }
  
  # Template configuration
  template {
    source = "/vault/userconfig/vault-templates/database-creds.tpl"
    destination = "/vault/userconfig/vault-secrets/database-creds.json"
    command = "restart"
  }
  
  # Cache configuration
  cache {
    use_auto_auth_token = true
  }
  
  # Sink configuration
  sink "file" {
    config = {
      path = "/vault/userconfig/vault-token/token"
    }
  }
} 