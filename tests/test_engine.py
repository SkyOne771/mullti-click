import threading
import time
import unittest

from multiclick.engine import ClickEngine


class ClickEngineTests(unittest.TestCase):
    def make_engine(self, sink=None):
        engine = ClickEngine(sink or (lambda: None))
        self.addCleanup(engine.close)
        return engine

    def wait_until(self, predicate):
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            if predicate():
                return
            threading.Event().wait(0.002)
        self.fail("Click worker did not finish in time")

    def test_five_total_clicks_include_the_original(self):
        clicks = []
        engine = self.make_engine(lambda: clicks.append(1))
        engine.configure(5, 10)
        engine.set_enabled(True)
        engine.physical_click()
        self.wait_until(lambda: engine.snapshot()[2] == 4)
        engine.set_enabled(False)
        self.assertEqual(len(clicks) + 1, 5)
        self.assertEqual(engine.snapshot()[1:3], (1, 4))

    def test_rapid_physical_clicks_each_create_a_full_burst(self):
        engine = self.make_engine()
        engine.configure(10, 10)
        engine.set_enabled(True)
        engine.physical_click()
        engine.physical_click()
        self.wait_until(lambda: engine.snapshot()[2] == 18)
        engine.set_enabled(False)
        self.assertEqual(engine.snapshot()[1:3], (2, 18))

    def test_disabled_clicks_are_ignored(self):
        engine = self.make_engine()
        engine.physical_click()
        self.assertEqual(engine.snapshot()[1:3], (0, 0))

    def test_stop_cancels_current_and_queued_bursts(self):
        clicked = threading.Event()
        engine = self.make_engine(clicked.set)
        engine.configure(100, 10)
        engine.set_enabled(True)
        engine.physical_click()
        engine.physical_click()
        self.assertTrue(clicked.wait(1))
        engine.set_enabled(False)
        stopped_count = engine.snapshot()[2]
        engine.configure(2, 30)
        engine.set_enabled(True)
        engine.physical_click()
        self.wait_until(lambda: engine.snapshot()[2] > stopped_count)
        engine.set_enabled(False)
        self.assertEqual(engine.snapshot()[2], stopped_count + 1)

    def test_invalid_settings(self):
        engine = self.make_engine()
        for multiplier, interval in [(1, 40), (101, 40), (5, 0), (5, 1001), (2.5, 40)]:
            with self.subTest(multiplier=multiplier, interval=interval):
                with self.assertRaises(ValueError):
                    engine.configure(multiplier, interval)

    def test_injection_failure_disables_and_clears_work(self):
        def fail():
            raise OSError("blocked")
        engine = self.make_engine(fail)
        engine.configure(10, 10)
        engine.set_enabled(True)
        engine.physical_click()
        self.wait_until(lambda: engine.snapshot()[3] is not None)
        self.assertEqual(engine.snapshot(), (False, 1, 0, "blocked"))

    def test_close_cancels_work_and_joins_thread(self):
        engine = self.make_engine()
        engine.set_enabled(True)
        engine.physical_click()
        engine.close()
        self.assertFalse(engine._worker.is_alive())
        self.assertFalse(engine.set_enabled(True))


if __name__ == "__main__":
    unittest.main()
