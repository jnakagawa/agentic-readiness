#!/bin/zsh
export PATH="$HOME/.zero/runtime/bin:$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
REPO="$HOME/github/agentic-readiness"; LOG_DIR="$HOME/Library/Logs"
cd "$REPO" || exit 1
"$REPO/.venv/bin/python" "$HOME/.local/bin/asrs_local_verify.py" >> "$LOG_DIR/asrs-local-verify.log" 2>&1
CLAUDE_BIN="$(command -v claude || echo "$HOME/.claude/local/claude")"
# WATCHDOG (Cycle 261, 2026-08-05): bound the agent's AWAKE runtime so a hung — or
# overnight-SUSPENDED — agent instance can never keep this launcher process alive for
# hours. launchd (StartCalendarInterval) is NON-REENTRANT: while a previous instance
# is still alive it SKIPS every subsequent :41 firing, so one long-lived agent wedges
# the whole local loop (root cause of the ~15h 2026-08-05 stall: the 02:41Z agent
# stayed alive, suspended through an overnight system sleep, blocking 14 :41 slots and
# every new verify artifact). The verify FLOOR already ran above (line 5) before the
# agent, so bounding the agent here loses no floor coverage. The watchdog's `sleep` is
# itself suspended during system sleep, so it bounds AWAKE runtime (not wall-clock): an
# agent merely paused overnight is NOT killed; one that runs >45min awake is. macOS
# ships no timeout(1)/gtimeout, so this background-kill pattern is the portable form.
AGENT_TIMEOUT="${ASRS_AGENT_TIMEOUT:-2700}"   # seconds of AWAKE agent runtime (45 min)
"$CLAUDE_BIN" -p "You are running ONE LOCAL cycle of the ASRS Improvement Loop in this checkout (jnakagawa/agentic-readiness). Read loop/PLAYBOOK.md fully — especially the Local cycle section, which is your law — then loop/STATE.md and loop/BACKLOG.md. This hour's verification artifact already exists (newest runs/local/verify_*.json); read it, don't redo it. First review+merge any open peer-gated PR (run its live re-scores). Then execute exactly ONE [LOCAL] backlog item. Spend NOTHING (zero CLI \$0 operations only, never a nonzero --max-pay). Stay inside this repo. LOG the cycle, update STATE/BACKLOG, commit and push to main per the playbook's ship rules. Never run more than one cycle per fire." --model claude-opus-4-8 --dangerously-skip-permissions --max-turns 120 >> "$LOG_DIR/asrs-local-cycle.log" 2>&1 &
AGENT_PID=$!
( sleep "$AGENT_TIMEOUT"; kill -TERM "$AGENT_PID" 2>/dev/null; sleep 30; kill -KILL "$AGENT_PID" 2>/dev/null ) &
WATCHDOG_PID=$!
wait "$AGENT_PID" 2>/dev/null
kill -TERM "$WATCHDOG_PID" 2>/dev/null; wait "$WATCHDOG_PID" 2>/dev/null
