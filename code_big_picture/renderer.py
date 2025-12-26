import json
from typing import Dict, Any, List, Tuple

class SVGRenderer:
    """Generates a high-end nested box visualization with Tiling Layout and Pan/Zoom."""
    
    # Modern Professional Palette
    THEME = {
        "project": {"stroke": "#1a1a1a", "bg": "rgba(26, 26, 26, 0.02)", "text": "#1a1a1a"},
        "package": {"stroke": "#8B4513", "bg": "rgba(139, 69, 19, 0.05)", "text": "#8B4513"},
        "directory": {"stroke": "#8B4513", "bg": "rgba(139, 69, 19, 0.05)", "text": "#8B4513"},
        "module": {"stroke": "#228B22", "bg": "rgba(34, 139, 34, 0.05)", "text": "#228B22"},
        "class": {"stroke": "#DC143C", "bg": "rgba(220, 20, 60, 0.05)", "text": "#DC143C"},
        "method": {"stroke": "#800080", "bg": "rgba(128, 0, 128, 0.05)", "text": "#800080"},
        "function": {"stroke": "#800080", "bg": "rgba(128, 0, 128, 0.05)", "text": "#800080"}
    }

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.padding = 30
        self.margin = 20
        self.header_height = 40
        self.min_leaf_width = 180
        self.min_leaf_height = 80

    def render(self) -> str:
        """Returns complex HTML with Pan/Zoom and Modern Styling."""
        svg_content, width, height = self._generate_box(self.data)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Big Picture 2.0 - {{self.data.get('name', 'Project')}}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #fcfcfc;
            --card-bg: #ffffff;
            --text-primary: #1e293b;
            --accent: #3b82f6;
        }}
        
        body {{
            margin: 0;
            padding: 0;
            background-color: var(--bg-color);
            font-family: 'Inter', sans-serif;
            color: var(--text-primary);
            overflow: hidden; /* Hide body scroll for panzoom */
            height: 100vh;
            width: 100vw;
        }}

        header {{
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 100;
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
            padding: 12px 24px;
            border-radius: 50px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        h1 {{ margin: 0; font-size: 1.2rem; font-weight: 800; }}
        .badge {{ font-size: 0.7rem; background: var(--accent); color: white; padding: 2px 8px; border-radius: 10px; }}

        #viewport {{
            width: 100vw;
            height: 100vh;
            cursor: grab;
        }}
        #viewport:active {{ cursor: grabbing; }}

        .box-rect {{
            transition: all 0.2s ease;
            stroke-dasharray: 0;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.02));
        }}
        
        .node:hover > .box-rect {{
            stroke-width: 3;
            filter: drop-shadow(0 4px 12px rgba(0,0,0,0.1));
            stroke-dasharray: 5;
            animation: dash 10s linear infinite;
        }}

        @keyframes dash {{
            to {{ stroke-dashoffset: -100; }}
        }}

        text {{
            font-family: 'Inter', sans-serif;
            pointer-events: none;
        }}
        
        .type-label {{
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            opacity: 0.5;
            font-weight: 600;
        }}

        .controls {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        
        .btn {{
            width: 45px;
            height: 45px;
            border-radius: 50%;
            background: white;
            border: 1px solid rgba(0,0,0,0.1);
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            transition: transform 0.2s;
        }}
        .btn:hover {{ transform: scale(1.1); background: #f8fafc; }}
    </style>
</head>
<body>
    <header>
        <h1>Code Big Picture</h1>
        <div class="badge">V2.0 PREMIUM</div>
        <span style="opacity: 0.5; font-size: 0.9rem;">{self.data.get('name')}</span>
    </header>

    <div id="viewport">
        <svg id="main-svg" width="100%" height="100%">
            <g id="scene">
                {svg_content}
            </g>
        </svg>
    </div>

    <div class="controls">
        <button class="btn" onclick="zoom(1.2)">+</button>
        <button class="btn" onclick="zoom(0.8)">-</button>
        <button class="btn" onclick="resetView()">⟲</button>
    </div>

    <script src="https://unpkg.com/@panzoom/panzoom@4.5.1/dist/panzoom.min.js"></script>
    <script>
        const elem = document.getElementById('scene');
        const svg = document.getElementById('main-svg');
        
        const panzoom = Panzoom(elem, {{
            maxScale: 20,
            minScale: 0.01,
            contain: false
        }});
        
        const parent = elem.parentElement;
        parent.addEventListener('wheel', panzoom.zoomWithWheel);

        function zoom(scale) {{
            panzoom.zoom(panzoom.getScale() * scale, {{ animate: true }});
        }}

        function resetView() {{
            fitToScreen();
        }}
        
        function fitToScreen() {{
            const bbox = elem.getBBox();
            const parentWidth = parent.clientWidth;
            const parentHeight = parent.clientHeight;
            
            // Calculate scale to fit
            const scaleX = (parentWidth - 100) / bbox.width;
            const scaleY = (parentHeight - 100) / bbox.height;
            const scale = Math.min(scaleX, scaleY);
            
            // Center it
            const x = (parentWidth - bbox.width * scale) / 2 - bbox.x * scale;
            const y = (parentHeight - bbox.height * scale) / 2 - bbox.y * scale;
            
            panzoom.zoom(scale);
            panzoom.pan(x / scale, y / scale);
            
            // Adjust to ensure perfect centering
            setTimeout(() => {{
                 panzoom.zoom(scale);
                 panzoom.pan(x / scale, y / scale);
            }}, 10);
        }}

        // Auto-fit on load
        window.addEventListener('load', () => {{
             setTimeout(() => {{
                fitToScreen();
             }}, 100);
        }});
    </script>
</body>
</html>
"""

    def _generate_box(self, node: Dict[str, Any], depth: int = 0) -> Tuple[str, float, float]:
        """Generates SVG with a smart stacking/tiling layout."""
        node_type = node.get("type", "unknown")
        name = node.get("name", "Unknown")
        children = node.get("children", [])
        
        theme = self.THEME.get(node_type, self.THEME["method"])
        
        if not children:
            # Leaf node
            w, h = self.min_leaf_width, self.min_leaf_height
            svg = self._draw_node_rect(name, node_type, theme, w, h)
            return svg, w, h

        # Layout children
        # We'll use a simple wrap-around logic:
        # Max width for a package row depends on the depth or a fixed size
        MAX_ROW_WIDTH = 1200 if depth == 0 else 800
        
        rows: List[List[Tuple[str, float, float]]] = [[]]
        current_row_w = 0
        
        for child in children:
            c_svg, c_w, c_h = self._generate_box(child, depth + 1)
            # If adding this child exceeds MAX_ROW_WIDTH, start new row
            if current_row_w + c_w + self.margin > MAX_ROW_WIDTH and rows[-1]:
                rows.append([(c_svg, c_w, c_h)])
                current_row_w = c_w
            else:
                rows[-1].append((c_svg, c_w, c_h))
                current_row_w += c_w + self.margin

        # Calculate final dimensions
        row_heights = [max(c[2] for c in row) for row in rows]
        row_widths = [sum(c[1] for c in row) + (len(row)-1)*self.margin for row in rows]
        
        total_width = max(row_widths) + (2 * self.padding)
        total_height = sum(row_heights) + (len(rows)-1)*self.margin + self.header_height + self.padding
        
        # Draw the node
        content_svg = []
        y_offset = self.header_height
        
        for i, row in enumerate(rows):
            x_offset = self.padding
            for c_svg, c_w, c_h in row:
                content_svg.append(f'<g transform="translate({x_offset}, {y_offset})">{c_svg}</g>')
                x_offset += c_w + self.margin
            y_offset += row_heights[i] + self.margin

        svg = f"""
        <g class="node">
            {self._draw_node_rect(name, node_type, theme, total_width, total_height)}
            <g transform="translate(0, 5)">
                {''.join(content_svg)}
            </g>
        </g>
        """
        
        return svg, total_width, total_height

    def _draw_node_rect(self, name: str, node_type: str, theme: dict, w: float, h: float) -> str:
        """Helper to draw the actual rectangle and labels."""
        return f"""
        <rect class="box-rect" width="{w}" height="{h}" stroke="{theme['stroke']}" fill="{theme['bg']}" rx="8" ry="8" />
        <text x="15" y="25" fill="{theme['text']}" style="font-weight: 800; font-size: 14px;">{name}</text>
        <text x="15" y="40" class="type-label" fill="{theme['text']}">{node_type}</text>
        """

if __name__ == "__main__":
    # Test on a slightly more complex dummy data
    test_data = {
        "name": "SuperApp",
        "type": "project",
        "children": [
            {
                "name": "Auth", "type": "package",
                "children": [
                    {"name": "Login", "type": "class", "children": [{"name": "auth", "type": "method"}]},
                    {"name": "Logout", "type": "class", "children": [{"name": "clear", "type": "method"}]},
                    {"name": "Session", "type": "class", "children": [{"name": "check", "type": "method"}]}
                ]
            },
            {
                "name": "Data", "type": "package",
                "children": [
                    {"name": "API", "type": "module", "children": [{"name": "fetch", "type": "function"}]},
                    {"name": "DB", "type": "module", "children": [{"name": "save", "type": "function"}]}
                ]
            }
        ]
    }
    renderer = SVGRenderer(test_data)
    print(renderer.render())
