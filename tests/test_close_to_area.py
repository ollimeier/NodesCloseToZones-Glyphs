import os
import sys
import types
import unittest

try:
    import importlib.util as importlib_util
except ImportError:
    importlib_util = None


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

    plugin_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            "NodesCloseToZones.glyphsReporter",
            "Contents",
            "Resources",
            "plugin.py",
        )
    )

    if importlib_util is not None:
        spec = importlib_util.spec_from_file_location("nodes_close_to_zones_plugin", plugin_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("Could not load plugin module spec")
        module = importlib_util.module_from_spec(spec)
        sys.modules["nodes_close_to_zones_plugin"] = module
        spec.loader.exec_module(module)
        return module

    try:
        import imp
    except ImportError:
        raise RuntimeError("No compatible module loader available")

    return imp.load_source("nodes_close_to_zones_plugin", plugin_path)


class TestCloseToArea(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plugin = _load_plugin_module()

    def test_returns_true_for_point_just_below_positive_zone(self):
        self.assertTrue(self.plugin.closeToArea(4, 100, 20, 99))

    def test_returns_false_for_point_inside_zone(self):
        self.assertFalse(self.plugin.closeToArea(4, 100, 20, 110))

    def test_returns_false_for_point_on_positive_zone_start_boundary(self):
        self.assertFalse(self.plugin.closeToArea(4, 100, 20, 100))

    def test_returns_false_for_point_on_positive_zone_end_boundary(self):
        self.assertFalse(self.plugin.closeToArea(4, 100, 20, 120))

    def test_returns_true_for_point_just_above_positive_zone(self):
        self.assertTrue(self.plugin.closeToArea(4, 100, 20, 121))

    def test_returns_true_for_point_below_lower_boundary_of_negative_size_zone(self):
        self.assertTrue(self.plugin.closeToArea(4, 200, -20, 179))

    def test_returns_false_for_point_far_from_negative_size_zone(self):
        self.assertFalse(self.plugin.closeToArea(4, 200, -20, 150))

    def test_returns_false_for_point_inside_negative_size_zone(self):
        self.assertFalse(self.plugin.closeToArea(4, 200, -20, 190))

    def test_returns_false_for_point_on_lower_boundary_of_negative_size_zone(self):
        self.assertFalse(self.plugin.closeToArea(4, 200, -20, 180))

    def test_returns_true_for_point_just_above_upper_boundary_of_negative_size_zone(self):
        self.assertTrue(self.plugin.closeToArea(4, 200, -20, 201))


if __name__ == "__main__":
    unittest.main()
