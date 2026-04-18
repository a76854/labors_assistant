SHELL := /bin/bash

PROJECT_ROOT := $(CURDIR)
VENV_DIR := $(PROJECT_ROOT)/.venv
VENV_BIN := $(VENV_DIR)/bin
PYTHON := python3
PIP := $(VENV_BIN)/pip
NODE_MAJOR ?= 20

BACKEND_PORT ?= 8000
AGENT_PORT ?= 8001
FRONTEND_PORT ?= 4173

RUN_DIR := $(PROJECT_ROOT)/run
LOG_DIR := $(PROJECT_ROOT)/logs

BACKEND_PID_FILE := $(RUN_DIR)/backend.pid
AGENT_PID_FILE := $(RUN_DIR)/agent.pid
FRONTEND_PID_FILE := $(RUN_DIR)/frontend.pid

.PHONY: help install install-system install-node install-python install-frontend setup build-frontend init-db start start-backend start-agent start-frontend stop stop-backend stop-agent stop-frontend restart status health logs clean

help:
	@echo "Available targets:"
	@echo "  make install         - Install system packages, Node.js, Python venv deps, frontend deps"
	@echo "  make setup           - Prepare runtime dirs and .env file"
	@echo "  make init-db         - Initialize/reset database"
	@echo "  make start           - Start backend, agent, and frontend (preview) in background"
	@echo "  make stop            - Stop backend, agent, and frontend"
	@echo "  make restart         - Restart all services"
	@echo "  make status          - Show service process status"
	@echo "  make health          - Run health checks"
	@echo "  make logs            - Show log file locations"
	@echo ""
	@echo "Ports: backend=$(BACKEND_PORT), agent=$(AGENT_PORT), frontend=$(FRONTEND_PORT)"

install: install-system install-node install-python install-frontend

install-system:
	@set -e; \
	if command -v apt-get >/dev/null 2>&1; then \
		echo "[install-system] Installing OS packages via apt..."; \
		sudo apt-get update; \
		sudo apt-get install -y curl git build-essential python3 python3-dev python3-venv python3-pip ca-certificates libpq-dev pkg-config; \
	else \
		echo "[install-system] apt-get not found. Please install curl/git/build-essential/python3/python3-venv manually."; \
	fi

install-node:
	@set -e; \
	if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then \
		echo "[install-node] Node is already installed: $$(node -v), npm: $$(npm -v)"; \
	else \
		echo "[install-node] Installing Node.js $(NODE_MAJOR).x ..."; \
		curl -fsSL https://deb.nodesource.com/setup_$(NODE_MAJOR).x | sudo -E bash -; \
		sudo apt-get install -y nodejs; \
		echo "[install-node] Installed Node: $$(node -v), npm: $$(npm -v)"; \
	fi

install-python:
	@set -e; \
	echo "[install-python] Creating virtual environment at $(VENV_DIR) ..."; \
	$(PYTHON) -m venv $(VENV_DIR); \
	$(PIP) install --upgrade pip setuptools wheel; \
	$(PIP) install -r requirements-backend.txt || { \
		echo "[install-python] Backend deps install failed. If error mentions psycopg2-binary, run: make install-system then retry."; \
		exit 1; \
	}; \
	$(PIP) install -r agent/requirements.txt; \
	echo "[install-python] Python deps installed in $(VENV_DIR)"

install-frontend:
	@set -e; \
	echo "[install-frontend] Installing frontend packages ..."; \
	cd frontend; \
	if [ -f package-lock.json ]; then npm ci; else npm install; fi

setup:
	@set -e; \
	mkdir -p $(RUN_DIR) $(LOG_DIR) generated_docs storage/db; \
	if [ ! -f .env ] && [ -f .env.example ]; then cp .env.example .env; fi; \
	echo "[setup] Runtime directories are ready"; \
	echo "[setup] Please check .env before starting services"

build-frontend:
	@set -e; \
	echo "[build-frontend] Building frontend ..."; \
	cd frontend; npm run build

init-db:
	@set -e; \
	echo "[init-db] Initializing database ..."; \
	$(VENV_BIN)/python scripts/init_db.py

start: setup build-frontend start-backend start-agent start-frontend
	@echo "[start] All services started"
	@$(MAKE) status

start-backend:
	@set -e; \
	mkdir -p $(RUN_DIR) $(LOG_DIR); \
	if [ -f $(BACKEND_PID_FILE) ] && kill -0 $$(cat $(BACKEND_PID_FILE)) 2>/dev/null; then \
		echo "[start-backend] Already running (PID: $$(cat $(BACKEND_PID_FILE)))"; \
	else \
		echo "[start-backend] Starting backend on :$(BACKEND_PORT) ..."; \
		nohup $(VENV_BIN)/uvicorn backend.main:app --host 0.0.0.0 --port $(BACKEND_PORT) --workers 2 > $(LOG_DIR)/backend.log 2>&1 & echo $$! > $(BACKEND_PID_FILE); \
		echo "[start-backend] PID: $$(cat $(BACKEND_PID_FILE))"; \
	fi

start-agent:
	@set -e; \
	mkdir -p $(RUN_DIR) $(LOG_DIR); \
	if [ -f $(AGENT_PID_FILE) ] && kill -0 $$(cat $(AGENT_PID_FILE)) 2>/dev/null; then \
		echo "[start-agent] Already running (PID: $$(cat $(AGENT_PID_FILE)))"; \
	else \
		echo "[start-agent] Starting agent on :$(AGENT_PORT) ..."; \
		nohup $(VENV_BIN)/uvicorn agent.main:app --host 0.0.0.0 --port $(AGENT_PORT) --workers 1 > $(LOG_DIR)/agent.log 2>&1 & echo $$! > $(AGENT_PID_FILE); \
		echo "[start-agent] PID: $$(cat $(AGENT_PID_FILE))"; \
	fi

start-frontend:
	@set -e; \
	mkdir -p $(RUN_DIR) $(LOG_DIR); \
	if [ -f $(FRONTEND_PID_FILE) ] && kill -0 $$(cat $(FRONTEND_PID_FILE)) 2>/dev/null; then \
		echo "[start-frontend] Already running (PID: $$(cat $(FRONTEND_PID_FILE)))"; \
	else \
		if [ -f $(FRONTEND_PID_FILE) ]; then rm -f $(FRONTEND_PID_FILE); fi; \
		echo "[start-frontend] Starting frontend preview on :$(FRONTEND_PORT) ..."; \
		cd frontend; nohup npx vite preview --host 0.0.0.0 --port $(FRONTEND_PORT) --strictPort > $(LOG_DIR)/frontend.log 2>&1 & echo $$! > $(FRONTEND_PID_FILE); \
		echo "[start-frontend] PID: $$(cat $(FRONTEND_PID_FILE))"; \
	fi

stop: stop-frontend stop-agent stop-backend
	@echo "[stop] All services stopped"

stop-backend:
	@set -e; \
	if [ -f $(BACKEND_PID_FILE) ] && kill -0 $$(cat $(BACKEND_PID_FILE)) 2>/dev/null; then \
		echo "[stop-backend] Stopping PID $$(cat $(BACKEND_PID_FILE))"; \
		kill $$(cat $(BACKEND_PID_FILE)); \
		rm -f $(BACKEND_PID_FILE); \
	else \
		echo "[stop-backend] Not running"; \
	fi

stop-agent:
	@set -e; \
	if [ -f $(AGENT_PID_FILE) ] && kill -0 $$(cat $(AGENT_PID_FILE)) 2>/dev/null; then \
		echo "[stop-agent] Stopping PID $$(cat $(AGENT_PID_FILE))"; \
		kill $$(cat $(AGENT_PID_FILE)); \
		rm -f $(AGENT_PID_FILE); \
	else \
		echo "[stop-agent] Not running"; \
	fi

stop-frontend:
	@set -e; \
	echo "[stop-frontend] Cleaning frontend processes ..."; \
	if [ -f $(FRONTEND_PID_FILE) ] && kill -0 $$(cat $(FRONTEND_PID_FILE)) 2>/dev/null; then \
		echo "[stop-frontend] Stopping PID $$(cat $(FRONTEND_PID_FILE))"; \
		kill $$(cat $(FRONTEND_PID_FILE)); \
		sleep 1; \
	else \
		echo "[stop-frontend] PID file missing or stale"; \
	fi
	@set -e; \
	for pid in $$(pgrep -f "vite preview --host 0.0.0.0" || true); do \
		if [ "$$pid" != "$$$$" ]; then kill $$pid >/dev/null 2>&1 || true; fi; \
	done; \
	for pid in $$(pgrep -f "npm run preview -- --host 0.0.0.0" || true); do \
		if [ "$$pid" != "$$$$" ]; then kill $$pid >/dev/null 2>&1 || true; fi; \
	done
	@rm -f $(FRONTEND_PID_FILE)

restart: stop start

status:
	@echo "[status] backend:"; \
	if [ -f $(BACKEND_PID_FILE) ] && kill -0 $$(cat $(BACKEND_PID_FILE)) 2>/dev/null; then echo "  running (PID $$(cat $(BACKEND_PID_FILE)))"; else echo "  stopped"; fi
	@echo "[status] agent:"; \
	if [ -f $(AGENT_PID_FILE) ] && kill -0 $$(cat $(AGENT_PID_FILE)) 2>/dev/null; then echo "  running (PID $$(cat $(AGENT_PID_FILE)))"; else echo "  stopped"; fi
	@echo "[status] frontend:"; \
	if [ -f $(FRONTEND_PID_FILE) ] && kill -0 $$(cat $(FRONTEND_PID_FILE)) 2>/dev/null; then echo "  running (PID $$(cat $(FRONTEND_PID_FILE)))"; else echo "  stopped"; fi

health:
	@echo "[health] backend  http://127.0.0.1:$(BACKEND_PORT)/api/v1/health"; curl -fsS http://127.0.0.1:$(BACKEND_PORT)/api/v1/health || true
	@echo "[health] agent    http://127.0.0.1:$(AGENT_PORT)/health"; curl -fsS http://127.0.0.1:$(AGENT_PORT)/health || true
	@echo "[health] frontend http://127.0.0.1:$(FRONTEND_PORT)"; curl -fsS -I http://127.0.0.1:$(FRONTEND_PORT) | head -n 1 || true

logs:
	@echo "Backend log : $(LOG_DIR)/backend.log"
	@echo "Agent log   : $(LOG_DIR)/agent.log"
	@echo "Frontend log: $(LOG_DIR)/frontend.log"
	@echo "Use: tail -f logs/backend.log"

clean:
	@echo "[clean] Removing runtime PID files"
	@rm -f $(BACKEND_PID_FILE) $(AGENT_PID_FILE) $(FRONTEND_PID_FILE)
