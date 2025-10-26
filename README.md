<<<<<<< HEAD
# Pico API Server

A lightweight API server for managing Kubernetes Sandbox environments with transparent SSH/SFTP proxy support.

## Features

- **Session Management**: RESTful API for creating, listing, and deleting sandbox sessions
- **Kubernetes Integration**: Automatically manages Sandbox CRD lifecycle
- **HTTP CONNECT Tunnel**: Transparent proxy for SSH/SFTP traffic to sandbox pods
- **Authentication**: JWT Bearer token authentication support
- **TLS Support**: Optional HTTPS for secure communication

## Quick Start

### Option 1: Deploy to Kubernetes (Recommended)

```bash
# Build Docker image
make docker-build

# For kind cluster
make kind-load

# Deploy to Kubernetes
make k8s-deploy

# Check status
kubectl get pods -n pico-apiserver
make k8s-logs

# Port forward for testing
kubectl port-forward -n pico-apiserver svc/pico-apiserver 8080:8080
```

See [k8s/README.md](k8s/README.md) for detailed deployment instructions.

### Option 2: Local Development

```bash
# Build binary
make build

# Run locally (no Kubernetes required for testing)
./bin/pico-apiserver --port=8080

# Or with Kubernetes
./bin/pico-apiserver \
  --port=8080 \
  --kubeconfig=$HOME/.kube/config \
  --namespace=sandboxes
```

### Test

```bash
# Health check
curl http://localhost:8080/health

# Create session (requires Kubernetes)
curl -X POST http://localhost:8080/v1/sessions \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/json" \
  -d '{"ttl": 3600, "image": "python:3.11"}'
```

## Architecture

```
Client → REST API → pico-apiserver → Kubernetes API → Sandbox CRD
                                                             ↓
                                                  agent-sandbox controller
                                                             ↓
                                                         Pod created
```

### HTTP CONNECT Tunnel

```
Client <--HTTP CONNECT--> pico-apiserver <--TCP/SSH--> Sandbox Pod
```

The server acts as a transparent proxy:
1. Client sends `CONNECT /v1/sessions/{id}/tunnel HTTP/1.1`
2. Server connects to sandbox pod SSH service
3. Server hijacks HTTP connection
4. Server returns `200 Connection Established`
5. Bidirectional transparent data forwarding begins

## API Endpoints

### Sessions

- `POST /v1/sessions` - Create session
- `GET /v1/sessions` - List sessions
- `GET /v1/sessions/{id}` - Get session details
- `DELETE /v1/sessions/{id}` - Delete session

### Tunnel

- `CONNECT /v1/sessions/{id}/tunnel` - Establish SSH/SFTP tunnel

### Health

- `GET /health` - Health check (no auth required)

## Python SDK Usage

```python
from sdk.sandbox_sessions_sdk import SessionsClient, SessionSSHClient

# Create session
with SessionsClient(api_url='http://localhost:8080/v1', bearer_token='token') as client:
    session = client.create_session(ttl=3600)
    print(f"Session: {session.session_id}")

# Use SSH through tunnel
with SessionSSHClient(
    api_url='http://localhost:8080/v1',
    bearer_token='token',
    session_id=session.session_id,
    username='sandbox'
) as ssh:
    result = ssh.run_command('ls -la')
    print(result['stdout'])
```

## Configuration

### Command Line Options

| Flag             | Default   | Description                             |
| ---------------- | --------- | --------------------------------------- |
| `--port`         | `8080`    | API server port                         |
| `--kubeconfig`   | `""`      | Path to kubeconfig (empty = in-cluster) |
| `--namespace`    | `default` | Kubernetes namespace                    |
| `--ssh-username` | `sandbox` | SSH username for pods                   |
| `--ssh-port`     | `22`      | SSH port on pods                        |
| `--enable-tls`   | `false`   | Enable HTTPS                            |
| `--tls-cert`     | `""`      | TLS certificate file                    |
| `--tls-key`      | `""`      | TLS key file                            |
| `--jwt-secret`   | `""`      | JWT secret (empty = skip auth)          |
=======
# kmetis-sdk

# Project Overview

This repository contains a Python SDK for managing Kubernetes sandboxes (Pods). The SDK provides functionality to create, manage, and interact with sandbox environments running in a Kubernetes cluster.

# Code Architecture
>>>>>>> kmetis/main

## Project Structure

```
<<<<<<< HEAD
agent-box/
├── cmd/pico-apiserver/          # Entry point
├── pkg/pico-apiserver/          # Core implementation
│   ├── apiserver.go            # Server, routing, middleware
│   ├── tunnel.go               # ⭐ HTTP CONNECT tunnel & proxy
│   ├── handlers.go             # REST API handlers
│   ├── k8s_client.go           # Kubernetes client
│   ├── session.go              # Session management
│   ├── auth.go                 # Authentication
│   ├── config.go               # Configuration
│   └── utils.go                # Utilities
├── sdk/                         # Python SDK (reference)
├── api-spec/                    # OpenAPI specification
└── Makefile                     # Build system
```

## Development Status

### ✅ Completed (Framework)

- HTTP server and routing
- Session management API
- HTTP CONNECT tunnel handling
- Transparent TCP proxy
- Kubernetes client wrapper
- Authentication middleware
- Build system

### 🚧 TODO (Requires Debugging)

- Kubernetes Sandbox CRD integration (adjust to actual spec)
- Pod IP retrieval and labeling
- Session TTL cleanup
- JWT authentication implementation
- Pod readiness waiting
- Error handling improvements
- Unit tests

## Dependencies

- `github.com/gorilla/mux` - HTTP routing
- `github.com/google/uuid` - UUID generation
- `golang.org/x/crypto/ssh` - SSH client
- `k8s.io/client-go` - Kubernetes client
- `k8s.io/apimachinery` - Kubernetes API machinery

## References

- API Spec: `api-spec/sandbox-api-spec.yaml`
- Python SDK: `sdk/sandbox_sessions_sdk.py`
- Agent Sandbox: https://github.com/kubernetes-sigs/agent-sandbox

## License

Apache 2.0

## Contributing

Contributions welcome! This is a framework implementation that requires:
1. Integration with actual agent-sandbox CRD
2. Production-ready authentication
3. Comprehensive testing
4. Performance optimization

## Notes

- Current implementation uses placeholder Sandbox CRD structure
- JWT validation needs proper implementation
- Production deployments should verify SSH host keys
- Session cleanup requires background goroutine implementation

=======
sandbox_sdk/  
├── models/                   # Data models
│   ├── pod_templates.py      # Custom exception classes for handling various error conditions:
│   ├── sandbox_info.py       # Sandbox instance, pod states, and execution result
│   └── models.py  
├── providers/                # Implementation providers  
│   ├── kubernetes/           # K8s implementations  
│   │   ├── client.py         # Low-level K8s client  
│   │   ├── lifecycle.py      # Pod lifecycle manager and related resource manager
│   └── ssh/                  # SSH implementations  
│       ├── client.py         # Low-level SSH client  
│       └── process.py        # Command/transfer manager  
├── services/                 # Domain services  
│   ├── resource_tracker.py   # tracker of resources during sandbox-related operations  
│   ├── log.py                # Enhanced logging service  
│   └── exceptions.py         # exceptions for various error conditions  
├── constants.py              # Constants used for sandbox management
├── sandbox.py                # sandbox core functionality
└── example.py                # example sandbox usage scenarios
```

The SDK is organized into several modules:

1\. \*\*Main SDK (`sandbox.py`)\*\*: The primary `Sandbox` class that implements all core functionality:

&nbsp;  - `create\_sandbox`: Creates a Kubernetes Pod with SSH configured

&nbsp;  - `delete\_sandbox`: Deletes a sandbox Pod

&nbsp;  - `execute\_command`: Executes commands in a sandbox via SSH

&nbsp;  - `upload\_file`: Uploads files to a sandbox via SFTP

&nbsp;  - `download\_file`: Downloads files from a sandbox via SFTP

2\. \*\*SSH Manager (`providers/ssh/process.py`)\*\*: Manages SSH connections with session pooling to optimize connections and reduce overhead.

3\. \*\*Exceptions (`exceptions.py`)\*\*: Custom exception classes for handling various error conditions:

4\. \*\*Logging(`services/log.py`)\*\*:  Provides hierarchical logging mechanisms for debugging specific components, setting different log levels for different modules, analyzing log flows through the system, and maintaining clean separation of concerns in logs.

# Dependencies

\- `kubernetes`: Kubernetes Python client (v27.2.0)

\- `paramiko`: SSH and SFTP library (v3.4.0)

\- `python-dotenv`: Environment variable management (v1.0.0)

# Development Commands

## Installation

```bash
pip install -e .

\# or

pip install kubernetes paramiko python-dotenv
```

## Running the Example

```bash
python example.py
```

## Running Tests

```bash
pytest
```

# Key Implementation Details

1\. \*\*Kubernetes Integration\*\*: The SDK uses the official Kubernetes Python client to interact with the cluster, supporting both in-cluster and kubeconfig authentication.

2\. \*\*SSH Session Management\*\*: Implements connection pooling to reuse SSH connections for multiple operations on the same sandbox. Sessions are cached with automatic cleanup based on timeouts.

3\. \*\*Caching\*\*: Uses in-memory caching with thread-safe locking to reduce Kubernetes API calls for frequently accessed sandbox information including IP addresses and SSH ports.

4\. \*\*Error Handling\*\*: Comprehensive custom exception hierarchy for different failure modes with descriptive error messages.

5\. \*\*Thread Safety\*\*: Implements proper locking mechanisms for shared resources using threading.Lock.

6\. \*\*Logging\*\*: Uses Python's standard logging module for debugging and monitoring.

7\. \*\*Port Management\*\*: SSH port information is stored in the cache along with IP addresses and retrieved dynamically rather than hardcoded. Defaults to port "22" for container SSH access.

8\. \*\*Configuration\*\*: Environment variables can be loaded from a .env file for configuration including namespace, SSH username, port, and timeout settings.
>>>>>>> kmetis/main
