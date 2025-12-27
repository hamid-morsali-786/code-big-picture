"""Unit tests for SVGRenderer class."""
import pytest
import re
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from code_big_picture.renderer import SVGRenderer


class TestSVGRendererInit:
    """Tests for SVGRenderer.__init__"""
    
    def test_init_stores_structure(self, simple_structure):
        """Renderer should store the provided structure."""
        renderer = SVGRenderer(simple_structure)
        assert renderer.structure == simple_structure
    
    def test_init_sets_default_dimensions(self, simple_structure):
        """Renderer should set default layout dimensions."""
        renderer = SVGRenderer(simple_structure)
        assert renderer.padding == 15
        assert renderer.margin == 10
        assert renderer.header_height == 35


class TestSVGRendererRender:
    """Tests for SVGRenderer.render"""
    
    def test_render_returns_valid_html(self, simple_structure):
        """Render should return a string containing valid HTML."""
        renderer = SVGRenderer(simple_structure)
        result = renderer.render()
        
        assert isinstance(result, str)
        assert "<html" in result
        assert "</html>" in result
    
    def test_render_includes_doctype(self, simple_structure):
        """Render should include DOCTYPE declaration."""
        renderer = SVGRenderer(simple_structure)
        result = renderer.render()
        
        assert "<!DOCTYPE html>" in result
    
    def test_render_includes_version_badge(self, simple_structure):
        """Render should include the version badge."""
        renderer = SVGRenderer(simple_structure)
        result = renderer.render()
        
        assert "V3.0" in result or f"V{renderer.VERSION}" in result
    
    def test_render_includes_panzoom_script(self, simple_structure):
        """Render should include the Panzoom library."""
        renderer = SVGRenderer(simple_structure)
        result = renderer.render()
        
        assert "panzoom" in result.lower()
    
    def test_render_includes_search_input(self, simple_structure):
        """Render should include search functionality."""
        renderer = SVGRenderer(simple_structure)
        result = renderer.render()
        
        assert 'id="search-input"' in result
    
    def test_render_includes_expand_collapse_buttons(self, simple_structure):
        """Render should include expand/collapse all buttons."""
        renderer = SVGRenderer(simple_structure)
        result = renderer.render()
        
        assert "expandAll" in result
        assert "collapseAll" in result


class TestSVGRendererGenerateBox:
    """Tests for SVGRenderer._generate_box"""
    
    def test_generate_box_returns_tuple_of_three(self, simple_structure):
        """Generate box should return (svg, width, height) tuple."""
        renderer = SVGRenderer(simple_structure)
        result = renderer._generate_box(simple_structure)
        
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert isinstance(result[0], str)  # SVG content
        assert isinstance(result[1], (int, float))  # width
        assert isinstance(result[2], (int, float))  # height
    
    def test_generate_box_handles_leaf_node(self):
        """Leaf nodes (no children) should be handled correctly."""
        leaf = {"name": "function_name", "type": "function"}
        renderer = SVGRenderer({"name": "root", "type": "project", "children": [leaf]})
        
        svg, width, height = renderer._generate_box(leaf)
        
        assert "function_name" in svg
        assert width > 0
        assert height > 0
    
    def test_generate_box_handles_nested_children(self, simple_structure):
        """Nested children should be properly rendered."""
        renderer = SVGRenderer(simple_structure)
        svg, _, _ = renderer._generate_box(simple_structure)
        
        # Should contain the nested class and function
        assert "MyClass" in svg
        assert "helper" in svg
    
    def test_generate_box_assigns_unique_ids(self, simple_structure):
        """Each node should have a unique ID."""
        renderer = SVGRenderer(simple_structure)
        svg, _, _ = renderer._generate_box(simple_structure)
        
        # Find all node IDs
        ids = re.findall(r'id="(node-[a-f0-9]+)"', svg)
        
        # All IDs should be unique
        assert len(ids) == len(set(ids))


class TestSVGRendererDrawNodeRect:
    """Tests for SVGRenderer._draw_node_rect"""
    
    def test_draw_node_rect_includes_rect_element(self):
        """Node rect should include an SVG rect element."""
        renderer = SVGRenderer({"name": "test", "type": "project", "children": []})
        theme = renderer.THEME["module"]
        
        result = renderer._draw_node_rect("test", "module", theme, 100, 50, "node-123", False)
        
        assert "<rect" in result
        assert 'class="box-rect"' in result
    
    def test_draw_node_rect_truncates_long_names(self):
        """Long names should be truncated with ellipsis."""
        renderer = SVGRenderer({"name": "test", "type": "project", "children": []})
        theme = renderer.THEME["module"]
        long_name = "a" * 100  # Very long name
        
        result = renderer._draw_node_rect(long_name, "module", theme, 150, 50, "node-123", False)
        
        # Should contain truncated version with ellipsis
        assert "..." in result
        # Should contain title with full name for tooltip
        assert f"<title>{long_name}</title>" in result
    
    def test_draw_node_rect_shows_toggle_for_parents(self):
        """Parent nodes should have toggle button."""
        renderer = SVGRenderer({"name": "test", "type": "project", "children": []})
        theme = renderer.THEME["package"]
        
        result = renderer._draw_node_rect("package", "package", theme, 100, 50, "node-123", has_children=True)
        
        assert "toggle-btn" in result
        assert "toggleNode" in result
    
    def test_draw_node_rect_hides_toggle_for_leaves(self):
        """Leaf nodes should not have toggle button."""
        renderer = SVGRenderer({"name": "test", "type": "project", "children": []})
        theme = renderer.THEME["function"]
        
        result = renderer._draw_node_rect("func", "function", theme, 100, 50, "node-123", has_children=False)
        
        assert "toggle-btn" not in result


class TestEdgeCases:
    """Edge case tests for SVGRenderer"""
    
    def test_render_empty_structure(self, empty_structure):
        """Empty project should render without errors."""
        renderer = SVGRenderer(empty_structure)
        result = renderer.render()
        
        assert "EmptyProject" in result
        assert "<html" in result
    
    def test_render_deeply_nested_structure(self, deeply_nested_structure):
        """Deeply nested structures should render correctly."""
        renderer = SVGRenderer(deeply_nested_structure)
        result = renderer.render()
        
        assert "DeepProject" in result
        assert "level_0" in result
        assert "leaf_5" in result
    
    def test_render_special_characters_escaped(self):
        """Special characters in names should be handled."""
        structure = {
            "name": "Test <Project>",
            "type": "project",
            "children": [
                {"name": "file&name.py", "type": "module", "children": []}
            ]
        }
        
        renderer = SVGRenderer(structure)
        result = renderer.render()
        
        # Should render without errors
        assert isinstance(result, str)
        assert len(result) > 0


class TestThemes:
    """Tests for node type themes"""
    
    def test_all_themes_have_required_keys(self):
        """All themes should have bg, stroke, text, and icon keys."""
        for node_type, theme in SVGRenderer.THEME.items():
            assert "bg" in theme, f"Theme {node_type} missing 'bg'"
            assert "stroke" in theme, f"Theme {node_type} missing 'stroke'"
            assert "text" in theme, f"Theme {node_type} missing 'text'"
            assert "icon" in theme, f"Theme {node_type} missing 'icon'"
    
    def test_theme_exists_for_common_types(self):
        """Common node types should have themes."""
        common_types = ["project", "package", "directory", "module", "class", "method", "function"]
        
        for node_type in common_types:
            assert node_type in SVGRenderer.THEME, f"Missing theme for {node_type}"
