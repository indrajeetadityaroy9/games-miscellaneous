"""Thread-safe executor for RL agent actions."""

from concurrent.futures import ThreadPoolExecutor, Future
from typing import TypeVar, Generic, Callable, Optional
import threading

from .base import RLAgent, AgentResponse

StateT = TypeVar("StateT")
ActionT = TypeVar("ActionT")


class RLExecutor(Generic[StateT, ActionT]):
    """
    Thread-safe executor for RL agent actions.
    Manages inference calls from synchronous Textual context.
    """

    def __init__(
        self, agent: RLAgent[StateT, ActionT], max_workers: int = 1
    ) -> None:
        self.agent = agent
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = threading.Lock()
        self._pending_future: Optional[Future] = None

    def request_action(
        self,
        state: StateT,
        callback: Callable[[AgentResponse[ActionT]], None],
        error_callback: Optional[Callable[[Exception], None]] = None,
    ) -> None:
        """
        Request an agent action asynchronously.
        Calls callback with result when complete.
        """

        def run_inference() -> None:
            try:
                result = self.agent.get_action(state)
                callback(result)
            except Exception as e:
                if error_callback:
                    error_callback(e)
                else:
                    # Try fallback action
                    fallback = self.agent.get_fallback_action(state)
                    if fallback is not None:
                        callback(AgentResponse(action=fallback, fallback_used=True))
                    else:
                        raise

        with self._lock:
            self._pending_future = self._executor.submit(run_inference)

    def is_busy(self) -> bool:
        """Check if an action request is currently pending."""
        with self._lock:
            if self._pending_future is None:
                return False
            return not self._pending_future.done()

    def cancel_pending(self) -> None:
        """Cancel any pending requests."""
        with self._lock:
            if self._pending_future is not None:
                self._pending_future.cancel()
                self._pending_future = None

    def shutdown(self) -> None:
        """Shutdown the executor."""
        self.cancel_pending()
        self._executor.shutdown(wait=False)
