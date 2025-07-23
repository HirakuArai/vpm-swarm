# vpm-swarm
Hyper-Swarm 1B – Phase 0 bootstrap repository.

## Architecture

This repository implements Phase-0 of the Hyper-Swarm system with 5 role cells:
- **Planner**: Planning and coordination
- **Curator**: Content curation and filtering  
- **Archivist**: Data archival and storage
- **Watcher**: Monitoring and observation
- **Synthesizer**: Data synthesis and output generation

## Docker Compose Build & Run

### Prerequisites
- Docker and Docker Compose installed
- Python 3.11+ (for local development)

### Quick Start

1. **Start local registry and build all cells:**
   ```bash
   docker-compose up -d registry
   docker-compose build
   ```

2. **Run all cells:**
   ```bash
   docker-compose up planner curator archivist watcher synthesizer
   ```

3. **Access cells:**
   - Planner: http://localhost:8001
   - Curator: http://localhost:8002  
   - Archivist: http://localhost:8003
   - Watcher: http://localhost:8004
   - Synthesizer: http://localhost:8005

### Testing

Run the smoke test to verify all cells are working:
```bash
pip install pytest requests
python tests/e2e/test_smoke.py
```

Or with pytest:
```bash
pytest tests/e2e/test_smoke.py -v
```

### Kubernetes Deployment

For kind + Knative deployment:
1. Apply the local registry: `kubectl apply -f infra/kind-dev/registry.yaml`
2. Deploy Knative services: `kubectl apply -f infra/k8s/overlays/dev/`

### Development

Each cell is a FastAPI application with async loops. To run a single cell locally:
```bash
cd cells/planner
python main.py
```
