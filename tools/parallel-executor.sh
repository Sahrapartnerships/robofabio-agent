#!/bin/bash
# parallel-executor.sh - Parallele Task-Ausführung mit sessions_spawn
# Usage: ./parallel-executor.sh task1 task2 task3...

WORKSPACE="/root/.openclaw/workspace"
TASK_DIR="$WORKSPACE/parallel-tasks"
LOG_DIR="$TASK_DIR/logs"
mkdir -p "$LOG_DIR"

# Task Definition
# Jeder Task ist eine Datei mit Befehlen

create_task() {
    local task_name="$1"
    local commands="$2"
    
    cat > "$TASK_DIR/${task_name}.sh" << EOF
#!/bin/bash
# Task: $task_name
# Created: $(date)

$commands

echo "Task $task_name completed at \$(date)"
EOF
    chmod +x "$TASK_DIR/${task_name}.sh"
    echo "Created: $TASK_DIR/${task_name}.sh"
}

# Beispiel Tasks für Elternratgeber
create_task "generate-images-batch-1" "
cd /root/life/elternratgeber-system
python3 -c '
import sys
sys.path.insert(0, \"tiktok_system\")
from carousel_generator import create_carousel
# Generate carousel 6-10
for i in range(6, 11):
    print(f\"Generating carousel {i}...\")
'
"

create_task "optimize-landing-page" "
cd /root/life/elternratgeber-system
# Run A/B tests on landing page
python3 -c '
import sys
sys.path.insert(0, \"tiktok_system\")
from ab_test_engine import run_landing_page_tests
run_landing_page_tests()
'
"

create_task "research-competitors" "
# Research 5 competitor products
echo 'Researching competitor pricing...'
# Results go to competitor_research.md
"

echo "Tasks created. Run with: parallel-executor.sh run"
