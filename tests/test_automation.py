import numpy as np
import pytest

from siglent.automation import DataCollector, TriggerWaitCollector
from siglent.waveform import WaveformData


class FakeChannel:
    def __init__(self, channel_number: int, enabled: bool = True):
        self.channel_number = channel_number
        self.enabled = enabled
        self.scale_updates = []

    def set_scale(self, scale):
        self.scale_updates.append(scale)


class FakeWaveform:
    def __init__(self):
        self.calls = []

    def acquire(self, channel: int):
        self.calls.append(channel)
        return WaveformData(
            time=np.array([0.0, 1.0]),
            voltage=np.array([0.0, 1.0]),
            channel=channel,
            sample_rate=2.0,
            record_length=2,
            timebase=1.0,
            voltage_scale=1.0,
            voltage_offset=0.0,
        )

    def save_waveform(self, waveform, filename, format="npz"):
        # Minimal placeholder to satisfy DataCollector.save_data
        return (waveform, filename, format)


class FakeTrigger:
    def __init__(self):
        self.mode = "STOP"


class FakeScope:
    def __init__(self, trigger_status=None):
        self.waveform = FakeWaveform()
        self.trigger = FakeTrigger()
        self.channel1 = FakeChannel(1, enabled=True)
        self.channel2 = FakeChannel(2, enabled=False)
        self._connected = True
        self.trigger_single_count = 0
        self.timebase_set_calls = []
        self._trigger_status = trigger_status or ["Stop"]
        self._query_count = 0

    def connect(self):
        self._connected = True

    def disconnect(self):
        self._connected = False

    def trigger_single(self):
        self.trigger_single_count += 1

    def auto_setup(self):
        return None

    def query(self, command: str):
        self._query_count += 1
        if command == ":TRIG:STAT?" and self._trigger_status:
            return self._trigger_status.pop(0)
        return ""

    def write(self, command: str):
        # TDIV commands are captured for assertions
        if command.startswith("TDIV"):
            self.timebase_set_calls.append(command.split(" ", 1)[1])

    @property
    def timebase(self):
        return 0.001

    @timebase.setter
    def timebase(self, value):
        self.timebase_set_calls.append(value)

    def set_timebase(self, value):
        self.timebase = value


class FakeTime:
    def __init__(self, step: float = 0.02):
        self.t = 0.0
        self.step = step

    def time(self):
        self.t += self.step
        return self.t

    def sleep(self, seconds: float):
        self.t += seconds


@pytest.fixture
def collector():
    dc = DataCollector("dummy")
    dc.scope = FakeScope()
    dc._connected = True
    return dc


def test_capture_single_uses_channel_enabled_and_waveform_acquire(monkeypatch, collector):
    fake_time = FakeTime()
    monkeypatch.setattr("siglent.automation.time", fake_time)

    waveforms = collector.capture_single([1, 2])

    assert list(waveforms.keys()) == [1]
    assert collector.scope.waveform.calls == [1]
    assert collector.scope.trigger_single_count == 1


def test_batch_capture_applies_timebase_and_scale(monkeypatch, collector):
    fake_time = FakeTime()
    monkeypatch.setattr("siglent.automation.time", fake_time)

    progress_updates = []

    results = collector.batch_capture(
        channels=[1],
        timebase_scales=["1e-3", "2e-3"],
        voltage_scales={1: [0.5, 1.0]},
        triggers_per_config=2,
        progress_callback=lambda current, total, status: progress_updates.append((current, total, status)),
    )

    assert len(results) == 8  # 4 configs * 2 triggers
    assert collector.scope.timebase_set_calls == ["1e-3", "1e-3", "2e-3", "2e-3"]
    assert collector.scope.channel1.scale_updates == [0.5, 1.0, 0.5, 1.0]
    assert collector.scope.waveform.calls == [1] * 8
    assert len(progress_updates) == 8


def test_start_continuous_capture_uses_trigger_mode(monkeypatch, collector):
    fake_time = FakeTime(step=0.01)
    monkeypatch.setattr("siglent.automation.time", fake_time)

    captures = collector.start_continuous_capture(
        channels=[1],
        duration=0.1,
        interval=0.02,
        output_dir=None,
        progress_callback=lambda *_: None,
    )

    assert collector.scope.trigger.mode == "AUTO"
    assert len(captures) > 1
    assert collector.scope.waveform.calls == [1] * len(captures)


def test_trigger_wait_collector_waits_for_stop(monkeypatch):
    fake_scope = FakeScope(trigger_status=["Run", "Run", "Stop"])
    collector = TriggerWaitCollector("dummy")
    collector.collector.scope = fake_scope
    collector.collector._connected = True

    fake_time = FakeTime()
    monkeypatch.setattr("siglent.automation.time", fake_time)

    waveforms = collector.wait_for_trigger([1], max_wait=0.5, save_on_trigger=False)

    assert waveforms is not None
    assert fake_scope.waveform.calls == [1]
    assert fake_scope.trigger_single_count == 1
    assert fake_scope._query_count >= 1
