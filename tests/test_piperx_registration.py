import sys
import types

from lerobot.robots.piper_follower import PiperXFollowerConfig
from lerobot.teleoperators.piper_leader import PiperXLeaderConfig


class _FakePiperInterface:
    def __init__(self, *args, **kwargs):
        pass


class _FakeLogLevel:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    SILENT = "SILENT"


fake_piper_sdk = types.SimpleNamespace(C_PiperInterface_V2=_FakePiperInterface, LogLevel=_FakeLogLevel)
sys.modules.setdefault("piper_sdk", fake_piper_sdk)


def test_piperx_single_arm_config_registration():
    from lerobot.robots import make_robot_from_config
    from lerobot.teleoperators import make_teleoperator_from_config

    follower = PiperXFollowerConfig(port="can_follower", id="follower", require_calibration=False)
    leader = PiperXLeaderConfig(
        port="can_leader",
        id="leader",
        require_calibration=False,
        allow_missing_ctrl_mode_on_connect=True,
    )

    assert follower.type == "piperx_follower"
    assert leader.type == "piperx_leader"
    assert make_robot_from_config(follower).__class__.__name__ == "PiperXFollower"
    assert make_teleoperator_from_config(leader).__class__.__name__ == "PiperXLeader"


def test_piperx_bimanual_config_registration():
    from lerobot.robots import make_robot_from_config
    from lerobot.robots.bi_piper_follower import BiPiperXFollowerConfig
    from lerobot.teleoperators import make_teleoperator_from_config
    from lerobot.teleoperators.bi_piper_leader import BiPiperXLeaderConfig

    follower = BiPiperXFollowerConfig(
        id="bi_follower",
        left_arm_config=PiperXFollowerConfig(port="can_left_follower", require_calibration=False),
        right_arm_config=PiperXFollowerConfig(port="can_right_follower", require_calibration=False),
    )
    leader = BiPiperXLeaderConfig(
        id="bi_leader",
        left_arm_config=PiperXLeaderConfig(port="can_left_leader", require_calibration=False),
        right_arm_config=PiperXLeaderConfig(port="can_right_leader", require_calibration=False),
    )

    assert follower.type == "bi_piperx_follower"
    assert leader.type == "bi_piperx_leader"
    assert make_robot_from_config(follower).__class__.__name__ == "BiPiperXFollower"
    assert make_teleoperator_from_config(leader).__class__.__name__ == "BiPiperXLeader"


def test_duplicate_third_party_piper_plugin_registration_is_skipped(monkeypatch, caplog):
    from lerobot.utils import import_utils

    class _FakeDistribution:
        metadata = {"Name": "lerobot_robot_piper"}

    def _raise_duplicate_registration(module_name):
        raise ValueError(
            "Cannot register <class 'PluginPiperLeaderConfig'> as piper_leader "
            "because <class 'PiperLeaderConfig'> is already registered as piper_leader"
        )

    monkeypatch.setattr(import_utils.importlib.metadata, "distributions", lambda: [_FakeDistribution()])
    monkeypatch.setattr(import_utils.importlib, "import_module", _raise_duplicate_registration)

    import_utils.register_third_party_plugins()

    assert "Could not import third-party plugin" not in caplog.text


def test_legacy_third_party_piper_plugin_is_not_imported(monkeypatch):
    from lerobot.utils import import_utils

    class _FakeDistribution:
        metadata = {"Name": "lerobot_robot_piper"}

    imported = []

    def _record_import(module_name):
        imported.append(module_name)

    monkeypatch.setattr(import_utils.importlib.metadata, "distributions", lambda: [_FakeDistribution()])
    monkeypatch.setattr(import_utils.importlib, "import_module", _record_import)

    import_utils.register_third_party_plugins()

    assert imported == []
