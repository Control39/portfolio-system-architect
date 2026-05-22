"""
Tests for task_manager module.
Covers: ConnectionTaskManager scheduling, cancellation, counting.
"""

import asyncio

import pytest

from apps.chat_backend.task_manager import ConnectionTaskManager


@pytest.fixture
def event_loop():
    """Create an event loop for testing"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def task_manager(event_loop):
    """Create a ConnectionTaskManager instance"""
    return ConnectionTaskManager(event_loop)


class TestConnectionTaskManagerInit:
    """Tests for ConnectionTaskManager initialization"""

    def test_init_creates_empty_tasks_dict(self, task_manager):
        assert task_manager._tasks == {}
        assert task_manager.total_active() == 0

    def test_init_with_loop(self, event_loop):
        tm = ConnectionTaskManager(event_loop)
        assert tm._loop is event_loop


class TestSchedule:
    """Tests for schedule method"""

    @pytest.mark.asyncio
    async def test_schedule_creates_future(self, task_manager, event_loop):
        """Test that schedule creates a Future for the coroutine"""

        async def dummy_coro():
            return "done"

        fut = task_manager.schedule("conn-1", dummy_coro())

        assert fut is not None
        assert task_manager.active_count("conn-1") == 1
        assert task_manager.total_active() == 1

        # Wait for completion
        await asyncio.sleep(0.01)
        assert fut.done()

    @pytest.mark.asyncio
    async def test_schedule_adds_to_bucket(self, task_manager, event_loop):
        """Test that scheduled tasks are stored in the correct bucket"""

        async def dummy_coro():
            await asyncio.sleep(0.01)
            return "done"

        fut1 = task_manager.schedule("conn-1", dummy_coro())
        fut2 = task_manager.schedule("conn-1", dummy_coro())

        assert task_manager.active_count("conn-1") == 2
        assert task_manager.total_active() == 2

        # Verify they're in the same bucket
        bucket = task_manager._tasks.get("conn-1")
        assert fut1 in bucket
        assert fut2 in bucket

    @pytest.mark.asyncio
    async def test_schedule_separate_connections(self, task_manager, event_loop):
        """Test that different connections have separate buckets"""

        async def dummy_coro():
            await asyncio.sleep(0.01)

        task_manager.schedule("conn-1", dummy_coro())
        task_manager.schedule("conn-2", dummy_coro())

        assert task_manager.active_count("conn-1") == 1
        assert task_manager.active_count("conn-2") == 1
        assert task_manager.total_active() == 2

    @pytest.mark.asyncio
    async def test_schedule_removes_completed_future(self, task_manager, event_loop):
        """Test that completed futures are removed from the bucket"""

        async def quick_coro():
            return "done"

        fut = task_manager.schedule("conn-1", quick_coro())

        # Wait for completion
        while not fut.done():
            await asyncio.sleep(0.001)

        # Future should be removed from bucket via done callback
        bucket = task_manager._tasks.get("conn-1")
        assert fut not in bucket if bucket else True
        assert task_manager.active_count("conn-1") == 0


class TestCancelAll:
    """Tests for cancel_all method"""

    @pytest.mark.asyncio
    async def test_cancel_all_cancels_all_tasks(self, task_manager, event_loop):
        """Test that cancel_all cancels all tasks for a connection"""

        async def slow_coro():
            await asyncio.sleep(10)
            return "done"

        fut1 = task_manager.schedule("conn-1", slow_coro())
        fut2 = task_manager.schedule("conn-1", slow_coro())

        task_manager.cancel_all("conn-1")

        assert fut1.cancelled() or fut1.done()
        assert fut2.cancelled() or fut2.done()
        assert task_manager.active_count("conn-1") == 0

    @pytest.mark.asyncio
    async def test_cancel_all_nonexistent_connection(self, task_manager, event_loop):
        """Test that cancel_all handles nonexistent connections gracefully"""
        task_manager.cancel_all("nonexistent")
        # Should not raise

    @pytest.mark.asyncio
    async def test_cancel_all_only_affects_target(self, task_manager, event_loop):
        """Test that cancel_all only affects the target connection"""

        async def slow_coro():
            await asyncio.sleep(10)

        task_manager.schedule("conn-1", slow_coro())
        task_manager.schedule("conn-2", slow_coro())

        task_manager.cancel_all("conn-1")

        assert task_manager.active_count("conn-1") == 0
        # conn-2 should still have its task
        assert task_manager.active_count("conn-2") == 1


class TestActiveCount:
    """Tests for active_count method"""

    def test_active_count_empty(self, task_manager):
        assert task_manager.active_count("conn-1") == 0

    @pytest.mark.asyncio
    async def test_active_count_single(self, task_manager, event_loop):
        async def dummy():
            await asyncio.sleep(10)

        task_manager.schedule("conn-1", dummy())
        assert task_manager.active_count("conn-1") == 1

    @pytest.mark.asyncio
    async def test_active_count_multiple(self, task_manager, event_loop):
        async def dummy():
            await asyncio.sleep(10)

        for _ in range(5):
            task_manager.schedule("conn-1", dummy())

        assert task_manager.active_count("conn-1") == 5


class TestTotalActive:
    """Tests for total_active method"""

    def test_total_active_empty(self, task_manager):
        assert task_manager.total_active() == 0

    @pytest.mark.asyncio
    async def test_total_active_single_connection(self, task_manager, event_loop):
        async def dummy():
            await asyncio.sleep(10)

        task_manager.schedule("conn-1", dummy())
        assert task_manager.total_active() == 1

    @pytest.mark.asyncio
    async def test_total_active_multiple_connections(self, task_manager, event_loop):
        async def dummy():
            await asyncio.sleep(10)

        for _ in range(3):
            task_manager.schedule("conn-1", dummy())
        for _ in range(2):
            task_manager.schedule("conn-2", dummy())

        assert task_manager.total_active() == 5


class TestTaskManagerIntegration:
    """Integration tests for full lifecycle"""

    @pytest.mark.asyncio
    async def test_full_lifecycle_schedule_cancel(self, task_manager, event_loop):
        """Test complete lifecycle: schedule -> cancel -> verify"""
        cancelled = []

        async def cancellable_coro():
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                cancelled.append(True)
                raise

        fut = task_manager.schedule("conn-1", cancellable_coro())

        assert task_manager.active_count("conn-1") == 1

        task_manager.cancel_all("conn-1")

        # Give cancellation time to propagate
        await asyncio.sleep(0.01)

        assert task_manager.active_count("conn-1") == 0
        assert len(cancelled) == 1 or fut.done()

    @pytest.mark.asyncio
    async def test_rapid_schedule_cancel_cycle(self, task_manager, event_loop):
        """Test rapid scheduling and cancellation cycles"""

        async def quick_coro():
            await asyncio.sleep(0.001)
            return "done"

        for i in range(10):
            task_manager.schedule(f"conn-{i}", quick_coro())

        assert task_manager.total_active() == 10

        for i in range(10):
            task_manager.cancel_all(f"conn-{i}")

        await asyncio.sleep(0.01)
        assert task_manager.total_active() == 0

    @pytest.mark.asyncio
    async def test_mixed_completed_and_pending_tasks(self, task_manager, event_loop):
        """Test mix of completed and pending tasks"""

        async def quick():
            return "done"

        async def slow():
            await asyncio.sleep(10)

        # Schedule quick tasks
        for _ in range(3):
            task_manager.schedule("conn-1", quick())

        # Wait for quick tasks to complete
        await asyncio.sleep(0.05)

        # Schedule slow tasks
        for _ in range(2):
            task_manager.schedule("conn-1", slow())

        # Should have 2 active tasks (quick ones completed and removed)
        assert task_manager.active_count("conn-1") == 2

        task_manager.cancel_all("conn-1")
        await asyncio.sleep(0.01)
        assert task_manager.active_count("conn-1") == 0
