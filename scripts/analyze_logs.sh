#!/usr/bin/env bash
# Log analysis using core Linux commands: grep, awk, cut, sort, uniq, wc, head, tail
LOG="${1:-sample_logs/pipeline_sample.log}"
[ -f "$LOG" ] || { echo "Log file not found: $LOG"; exit 1; }

echo "=== 1. Total lines (wc) ===";                 wc -l < "$LOG"
echo; echo "=== 2. Count by log level (cut|sort|uniq) ==="
cut -d'|' -f2 "$LOG" | tr -d ' ' | sort | uniq -c | sort -rn
echo; echo "=== 3. Last 5 ERROR lines (grep|tail) ==="
grep "| ERROR |" "$LOG" | tail -5
echo; echo "=== 4. Failures per city (grep|sort|uniq) ==="
grep -E "WARNING|ERROR" "$LOG" | grep -o "city=[A-Za-z]*" | sort | uniq -c | sort -rn
echo; echo "=== 5. HTTP status code distribution (grep -o) ==="
grep -o "status=[0-9]*" "$LOG" | sort | uniq -c | sort -rn
echo; echo "=== 6. Average API latency in ms (awk) ==="
grep -o "latency_ms=[0-9]*" "$LOG" | cut -d= -f2 | awk '{s+=$1; n++} END {printf "avg=%.1f ms over %d calls\n", s/n, n}'
echo; echo "=== 7. Top 5 slowest calls (sort) ==="
grep "latency_ms=" "$LOG" | awk -F'latency_ms=' '{split($2,a," "); print a[1] "\t" $0}' | sort -rn | head -5 | cut -f2-
echo; echo "=== 8. Errors per hour of day (awk) ==="
grep "| ERROR |" "$LOG" | awk '{split($2,t,":"); print t[1]}' | sort | uniq -c
echo; echo "=== 9. Rate-limit (429) events (grep -c) ==="
grep -c "status=429" "$LOG"
echo; echo "=== 10. Save error report (redirection) ==="
mkdir -p logs
grep -E "ERROR|WARNING" "$LOG" > logs/error_report.txt && echo "Saved $(wc -l < logs/error_report.txt) lines -> logs/error_report.txt"
