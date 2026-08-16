import importlib.util
import sys
import types
import unittest
from pathlib import Path


def _load_plugin_module():
    objc = types.ModuleType("objc")
    objc.python_method = lambda func: func
    sys.modules.setdefault("objc", objc)

    appkit = types.ModuleType("AppKit")
    appkit.NSRange = object()
    sys.modules.setdefault("AppKit", appkit)

    glyphs_app = types.ModuleType("GlyphsApp")
    sys.modules.setdefault("GlyphsApp", glyphs_app)

    glyphs_plugins = types.ModuleType("GlyphsApp.plugins")
    glyphs_plugins.ReporterPlugin = type("ReporterPlugin", (), {})
    sys.modules.setdefault("GlyphsApp.plugins", glyphs_plugins)

    plugin_path = (
        Path(__file__).resolve().parents[1]
        / "NodesCloseToZones.glyphsReporter"
        / "Contents"
        / "Resources"
        / "plugin.py"
    )
    spec = importlib.util.spec_from_file_location("nodes_close_to_zones_plugin", plugin_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestCloseToArea(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plugin = _load_plugin_module()

    def test_returns_true_for_point_just_below_positive_zone(self):
        self.assertTrue(self.plugin.closeToArea(4, 100, 20, 99))


if __name__ == "__main__":
    unittest.main()
