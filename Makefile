SHELL := /bin/bash

VENV    := .venv/bin
PY      := $(VENV)/python
RUN     := run
LOG     := logs

PORT_BACKEND  ?= 8000
PORT_AGENT    ?= 8001
PORT_FRONTEND ?= 4173

BACKEND_CMD  := $(PY) -m uvicorn backend.main:app --host 0.0.0.0 --port $(PORT_BACKEND) --workers 2
AGENT_CMD    := $(PY) -m uvicorn agent.main:app --host 0.0.0.0 --port $(PORT_AGENT) --workers 1
FRONTEND_CMD := bash -c 'cd frontend && exec npx vite preview --host 0.0.0.0 --port $(PORT_FRONTEND)'

.PHONY: help setup install init-db build lint dev start stop restart status health logs clean

# ============================================================================
# 通用后台服务启停宏
# 用法: $(call start_service,名称,pid文件,启动命令,日志文件)
#       $(call stop_service,名称,pid文件)
# ============================================================================
define start_service
	@mkdir -p $(RUN) $(LOG); \
	if [ -f $2 ] && kill -0 $$(cat $2) 2>/dev/null; then \
		echo "[$1] 已在运行 (PID $$(cat $2))"; \
	else \
		echo "[$1] 启动中..."; \
		nohup $3 > $4 2>&1 & echo $$! > $2; \
		sleep 1; \
		echo "[$1] 已启动 (PID $$(cat $2))"; \
	fi
endef

define stop_service
	@if [ -f $2 ] && kill -0 $$(cat $2) 2>/dev/null; then \
		echo "[$1] 停止 (PID $$(cat $2))"; \
		kill $$(cat $2) 2>/dev/null || true; \
	fi; \
	rm -f $2; \
	echo "[$1] 已停止"
endef

start-backend:  ; $(call start_service,backend,$(RUN)/backend.pid,$(BACKEND_CMD),$(LOG)/backend.log)
start-agent:    ; $(call start_service,agent,$(RUN)/agent.pid,$(AGENT_CMD),$(LOG)/agent.log)
start-frontend: ; $(call start_service,frontend,$(RUN)/frontend.pid,$(FRONTEND_CMD),$(LOG)/frontend.log)
stop-backend:   ; $(call stop_service,backend,$(RUN)/backend.pid)
stop-agent:     ; $(call stop_service,agent,$(RUN)/agent.pid)
stop-frontend:  ; $(call stop_service,frontend,$(RUN)/frontend.pid)

# ============================================================================
# 目标
# ============================================================================

help:
	@echo "用法: make <target>"
	@echo ""
	@echo "环境:"
	@echo "  setup       创建运行目录并生成 .env"
	@echo "  install     安装 Python 依赖与前端依赖"
	@echo "  init-db     初始化数据库（建表/模板/演示账号）"
	@echo ""
	@echo "服务:"
	@echo "  start       构建前端并后台启动全部服务 (backend:$(PORT_BACKEND) agent:$(PORT_AGENT) frontend:$(PORT_FRONTEND))"
	@echo "  stop        停止全部服务"
	@echo "  restart     重启全部服务"
	@echo "  start-{backend,agent,frontend} / stop-{backend,agent,frontend}"
	@echo "  status      查看服务状态"
	@echo "  health      健康检查"
	@echo "  logs        查看日志位置"
	@echo ""
	@echo "开发:"
	@echo "  dev         前台启动前端开发服务器 (热更新)"
	@echo "  build       前端构建 (vue-tsc + vite)"
	@echo "  lint        前端 ESLint"

setup:
	@mkdir -p $(RUN) $(LOG) generated_docs storage/db; \
	[ -f .env ] || cp .env.example .env; \
	echo "[setup] 目录已就绪，请检查 .env 配置"

install:
	@python3 -m venv .venv; \
	$(PY) -m pip install -r requirements-backend.txt -r agent/requirements.txt; \
	cd frontend && npm install; \
	echo "[install] 依赖安装完成"

init-db:
	$(PY) scripts/init_db.py

build:
	cd frontend && npm run build

lint:
	cd frontend && npm run lint

dev:
	cd frontend && npm run dev

start: setup build start-backend start-agent start-frontend
	@$(MAKE) status

stop: stop-frontend stop-agent stop-backend
	@echo "[stop] 全部服务已停止"

restart: stop start

status:
	@for spec in "backend:$(RUN)/backend.pid" "agent:$(RUN)/agent.pid" "frontend:$(RUN)/frontend.pid"; do \
		name=$${spec%%:*}; pid_file=$${spec#*:}; \
		if [ -f $$pid_file ] && kill -0 $$(cat $$pid_file) 2>/dev/null; then \
			echo "[$$name] 运行中 (PID $$(cat $$pid_file))"; \
		else \
			echo "[$$name] 已停止"; \
		fi; \
	done

health:
	@curl -fsS http://127.0.0.1:$(PORT_BACKEND)/api/v1/health && echo " <- backend"; \
	curl -fsS http://127.0.0.1:$(PORT_AGENT)/health && echo " <- agent"; \
	curl -fsSI http://127.0.0.1:$(PORT_FRONTEND) -o /dev/null && echo "frontend ok"

logs:
	@echo "backend : $(LOG)/backend.log"
	@echo "agent   : $(LOG)/agent.log"
	@echo "frontend: $(LOG)/frontend.log"

clean:
	@rm -f $(RUN)/*.pid; \
	echo "[clean] 已清理 PID 文件"
