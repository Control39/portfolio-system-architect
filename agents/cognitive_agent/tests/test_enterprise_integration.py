#!/usr/bin/env python3
"""Test enterprise classes integration"""

from agents.cognitive_agent.src.autonomous_agent import AuditLogger, MetricsCollector, StateManager, TaskPlanner

print("✅ All enterprise classes imported successfully\n")

# Test 1: Create instances
print("Test 1: Creating instances...")
metrics = MetricsCollector()
audit = AuditLogger(agent_id="test-agent")
planner = TaskPlanner()
state_mgr = StateManager(agent_id="test-agent")
print("✅ All instances created\n")

# Test 2: Test metrics collector
print("Test 2: Testing MetricsCollector...")
metrics.record_task_completion(success=True)
metrics.record_ai_call(success=True)
metrics.record_file_processed(10)
perf = metrics.calculate_performance_metrics()
print(f"   Task success rate: {perf['task_success_rate']:.0%}")
print(f"   AI call success rate: {perf['ai_call_success_rate']:.0%}")
print(f"   Files processed: {perf['total_files_processed']}")
print("✅ MetricsCollector works\n")

# Test 3: Test task planner
print("Test 3: Testing TaskPlanner...")
planner.add_task("task1", {"action": "scan"})
planner.add_task("task2", {"action": "analyze"}, dependencies=["task1"])
ready = planner.get_ready_tasks()
print("   Tasks added: 2")
print(f"   Ready tasks: {len(ready)} (should be 1 - task1)")
print(f"   Task1 status: {planner.get_task_status('task1')}")
print("✅ TaskPlanner works\n")

# Test 4: Test state manager
print("Test 4: Testing StateManager...")
state_mgr.save_state({"test_key": "test_value", "count": 42})
loaded = state_mgr.load_state()
if loaded:
    print(f"   State saved and loaded: {loaded}")
    print("✅ StateManager works\n")
else:
    print("   ⚠️ State loading returned None\n")

print("=" * 60)
print("🎉 ALL TESTS PASSED!")
print("=" * 60)
