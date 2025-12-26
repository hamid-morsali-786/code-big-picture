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
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(12px);
            padding: 8px 16px;
            border-radius: 50px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
            display: flex;
            align-items: center;
            gap: 20px;
            transition: all 0.3s ease;
        }}
        
        header:hover {{
             box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        h1 {{ margin: 0; font-size: 1.1rem; font-weight: 800; color: var(--text-primary); }}
        .badge {{ font-size: 0.65rem; background: var(--accent); color: white; padding: 3px 8px; border-radius: 12px; font-weight: 600; }}

        /* Search Bar */
        .search-container {{
            position: relative;
            display: flex;
            align-items: center;
        }}
        
        #search-input {{
            background: rgba(0,0,0,0.04);
            border: none;
            border-radius: 20px;
            padding: 8px 16px;
            padding-left: 36px;
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
            width: 200px;
            transition: all 0.2s ease;
            outline: none;
            color: var(--text-primary);
        }}
        
        #search-input:focus {{
            background: white;
            box-shadow: 0 0 0 2px var(--accent);
            width: 280px;
        }}
        
        .search-icon {{
            position: absolute;
            left: 12px;
            opacity: 0.4;
            pointer-events: none;
        }}

        #viewport {{
            width: 100vw;
            height: 100vh;
            cursor: grab;
        }}
        #viewport:active {{ cursor: grabbing; }}

        .box-rect {{
            transition: all 0.3s ease;
            stroke-dasharray: 0;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.02));
        }}
        
        /* Highlighting Logic */
        .node {{
            transition: opacity 0.3s ease;
        }}
        
        .node.dimmed {{
            opacity: 0.15;
            filter: grayscale(100%);
        }}
        
        .node.highlighted > .box-rect {{
            stroke: var(--accent) !important;
            stroke-width: 3;
            filter: drop-shadow(0 0 15px rgba(59, 130, 246, 0.4));
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
            color: var(--text-primary);
        }}
        .btn:hover {{ transform: scale(1.1); background: #f8fafc; }}
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <h1>Code Big Picture</h1>
            <div class="badge">V2.1</div>
        </div>
        
        <div class="search-container">
            <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <input type="text" id="search-input" placeholder="Search modules, classes..." autocomplete="off">
        </div>
    </header>

    <div id="viewport">
        <svg id="main-svg" width="100%" height="100%">
            <g id="scene">
                {svg_content}
            </g>
        </svg>
    </div>

    <div class="controls">
        <button class="btn" onclick="zoom(1.2)" title="Zoom In">+</button>
        <button class="btn" onclick="zoom(0.8)" title="Zoom Out">-</button>
        <button class="btn" onclick="resetView()" title="Fit to Screen">⟲</button>
    </div>

    <script src="https://unpkg.com/@panzoom/panzoom@4.5.1/dist/panzoom.min.js"></script>
    <script>
        const elem = document.getElementById('scene');
        const svg = document.getElementById('main-svg');
        const searchInput = document.getElementById('search-input');
        
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
            searchInput.value = '';
            performSearch('');
        }}
        
        function fitToScreen() {{
            const bbox = elem.getBBox();
            const parentWidth = parent.clientWidth;
            const parentHeight = parent.clientHeight;
            
            const scaleX = (parentWidth - 100) / bbox.width;
            const scaleY = (parentHeight - 100) / bbox.height;
            const scale = Math.min(scaleX, scaleY);
            
            const x = (parentWidth - bbox.width * scale) / 2 - bbox.x * scale;
            const y = (parentHeight - bbox.height * scale) / 2 - bbox.y * scale;
            
            panzoom.zoom(scale);
            panzoom.pan(x / scale, y / scale);
            
            setTimeout(() => {{
                 panzoom.zoom(scale);
                 panzoom.pan(x / scale, y / scale);
            }}, 10);
        }}

        // Search Logic
        function performSearch(query) {{
            const term = query.toLowerCase().trim();
            const nodes = document.querySelectorAll('.node');
            
            if (!term) {{
                nodes.forEach(node => {{
                    node.classList.remove('dimmed', 'highlighted');
                }});
                return;
            }}

            // 1. Reset all
            nodes.forEach(node => node.classList.add('dimmed'));
            nodes.forEach(node => node.classList.remove('highlighted'));

            // 2. Find matches
            const matchedNodes = [];
            nodes.forEach(node => {{
                // We store the name in a data attribute for easier access, 
                // but let's grab the text element content for now
                const textEl = node.querySelector('text');
                if (textEl && textEl.textContent.toLowerCase().includes(term)) {{
                    matchedNodes.push(node);
                    node.classList.remove('dimmed');
                    node.classList.add('highlighted');
                }}
            }});
            
            // 3. Reveal parents of matches
            matchedNodes.forEach(node => {{
                let parent = node.parentElement; 
                while (parent) {{
                     if (parent.classList && parent.classList.contains('node')) {{
                         parent.classList.remove('dimmed');
                         // Auto expand parents if collapsed? (future enhancement)
                     }}
                     parent = parent.parentElement;
                     if (parent.id === 'scene') break;
                }}
            }});
        }}

        // Collapse/Expand Logic
        window.toggleNode = function(nodeId) {{
            const content = document.getElementById('content-' + nodeId);
            const node = document.getElementById(nodeId);
            const btnText = node.querySelector('.toggle-btn text');
            
            if (content.style.display === 'none') {{
                // Expand
                content.style.display = 'block';
                btnText.textContent = '-';
                node.classList.remove('collapsed');
            }} else {{
                // Collapse
                content.style.display = 'none';
                btnText.textContent = '+';
                node.classList.add('collapsed');
            }}
            
            // Note: Since SVG elements don't auto-reflow, the parent box will remain large.
            // This is "Ghost Mode" collapsing, which clears visual noise but preserves layout.
        }};

        searchInput.addEventListener('input', (e) => {{
            performSearch(e.target.value);
        }});
        
        // Disable PanZoom when typing in search
        searchInput.addEventListener('focus', () => {{
             // panzoom.pause() // Not widely supported in v4 default?
             // Actually it's fine, wheel event is on parent div.
        }});

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
        import uuid
        node_id = f"node-{uuid.uuid4().hex[:8]}"
        
        node_type = node.get("type", "unknown")
        name = node.get("name", "Unknown")
        children = node.get("children", [])
        
        theme = self.THEME.get(node_type, self.THEME["method"])
        
        if not children:
            # Leaf node
            w, h = self.min_leaf_width, self.min_leaf_height
            # No toggle for leaves
            svg = self._draw_node_rect(name, node_type, theme, w, h, node_id, has_children=False)
            return svg, w, h

        # Layout children
        MAX_ROW_WIDTH = 1200 if depth == 0 else 800
        
        rows: List[List[Tuple[str, float, float]]] = [[]]
        current_row_w = 0
        
        for child in children:
            c_svg, c_w, c_h = self._generate_box(child, depth + 1)
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
        <g class="node" id="{node_id}">
            {self._draw_node_rect(name, node_type, theme, total_width, total_height, node_id, has_children=True)}
            <g id="content-{node_id}" class="node-content" transform="translate(0, 5)">
                {''.join(content_svg)}
            </g>
        </g>
        """
        
        return svg, total_width, total_height

    def _draw_node_rect(self, name: str, node_type: str, theme: dict, w: float, h: float, node_id: str, has_children: bool) -> str:
        """Helper to draw the actual rectangle, labels, and toggle button."""
        toggle_btn = ""
        if has_children:
            toggle_btn = f"""
            <g class="toggle-btn" onclick="toggleNode('{node_id}')" style="cursor: pointer; opacity: 0.7;">
                <circle cx="{w - 20}" cy="25" r="10" fill="white" stroke="{theme['stroke']}" stroke-width="1"/>
                <text x="{w - 20}" y="29" text-anchor="middle" font-size="14" font-weight="bold" fill="{theme['stroke']}" style="pointer-events: none;">-</text>
            </g>
            """
            
        return f"""
        <rect class="box-rect" width="{w}" height="{h}" stroke="{theme['stroke']}" fill="{theme['bg']}" rx="8" ry="8" />
        <text x="15" y="25" fill="{theme['text']}" style="font-weight: 800; font-size: 14px;">{name}</text>
        <text x="15" y="40" class="type-label" fill="{theme['text']}">{node_type}</text>
        {toggle_btn}
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
