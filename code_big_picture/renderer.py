import json
from typing import Dict, Any, List, Tuple

class SVGRenderer:
    """Generates a high-end nested box visualization with Tiling Layout and Pan/Zoom."""
    
    # Modern Professional Palette
    THEME = {
        "project": {"bg": "#ffffff", "stroke": "#1a1a1b", "text": "#1a1a1b", "icon": "cube"},
        "package": {"bg": "#f8f9fa", "stroke": "#495057", "text": "#212529", "icon": "package"},
        "directory": {"bg": "#ffffff", "stroke": "#adb5bd", "text": "#495057", "icon": "folder"},
        "module": {"bg": "#e7f5ff", "stroke": "#1971c2", "text": "#1864ab", "icon": "file-code"},
        "class": {"bg": "#f3f0ff", "stroke": "#6741d9", "text": "#5f3dc4", "icon": "box"},
        "method": {"bg": "#fff0f6", "stroke": "#c2255c", "text": "#a61e4d", "icon": "terminal"},
        "function": {"bg": "#fff9db", "stroke": "#f08c00", "text": "#e67700", "icon": "terminal"},
        "file": {"bg": "#f1f3f5", "stroke": "#868e96", "text": "#495057", "icon": "file-text"},
        "error": {"bg": "#fff5f5", "stroke": "#fa5252", "text": "#c92a2a", "icon": "alert-circle"}
    }

    def __init__(self, structure: Dict[str, Any]):
        self.structure = structure
        self.padding = 15
        self.margin = 10
        self.header_height = 35
        self.min_leaf_width = 120
        self.max_leaf_width = 350
        self.min_leaf_height = 42

    def render(self) -> str:
        """Returns complex HTML with Icons, Pan/Zoom and High Density."""
        svg_content, width, height = self._generate_box(self.structure)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Big Picture V2.2</title>
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
            overflow: hidden;
            height: 100vh;
            width: 100vw;
        }}

        header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 70px;
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(0,0,0,0.05);
            box-shadow: 0 2px 20px rgba(0,0,0,0.03);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 40px;
            z-index: 1000;
            gap: 20px;
        }}
        
        .brand {{
            display: flex;
            align-items: center;
            gap: 14px;
            flex-shrink: 0;
        }}

        .header-controls {{
            display: flex;
            gap: 8px;
            align-items: center;
            flex-shrink: 0;
        }}

        .header-btn {{
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 8px 14px;
            background: white;
            border: 1px solid rgba(0,0,0,0.1);
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            color: #1e293b;
            transition: all 0.2s ease;
            font-family: inherit;
        }}

        .header-btn:hover {{
            background: #f8fafc;
            border-color: rgba(59, 130, 246, 0.3);
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}

        .header-btn svg {{
            opacity: 0.7;
        }}

        h1 {{ margin: 0; font-size: 1.1rem; font-weight: 800; color: var(--text-primary); }}
        .badge {{ font-size: 0.65rem; background: var(--accent); color: white; padding: 3px 8px; border-radius: 12px; font-weight: 600; }}

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
            outline: none;
        }}
        
        .search-icon {{
            position: absolute;
            left: 12px;
            opacity: 0.4;
        }}

        #viewport {{ 
            position: fixed;
            top: 70px;
            left: 0;
            right: 0;
            bottom: 0;
            width: 100vw; 
            height: calc(100vh - 70px); 
            cursor: grab; 
            overflow: hidden;
        }}
        .box-rect {{ transition: all 0.3s ease; }}
        
        .node {{ transition: opacity 0.3s ease; }}
        .node.dimmed {{ opacity: 0.15; filter: grayscale(100%); }}
        .node.highlighted > .box-rect {{
            stroke: var(--accent) !important;
            stroke-width: 3;
            filter: drop-shadow(0 0 15px rgba(59, 130, 246, 0.4));
        }}

        .box-rect {{
            transition: height 0.3s ease, stroke-width 0.3s ease;
        }}

        .node-content {{
            transition: opacity 0.3s ease;
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
        }}

        /* Legend Style */
        .legend {{
            position: fixed;
            bottom: 30px;
            left: 30px;
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
            padding: 12px 18px;
            border-radius: 16px;
            border: 1px solid rgba(0,0,0,0.05);
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            display: flex;
            flex-direction: column;
            gap: 8px;
            z-index: 100;
        }}
        
        .legend-title {{
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #64748b;
            margin-bottom: 4px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 11px;
            font-weight: 600;
            color: #475569;
        }}
        
        .legend-icon {{
            width: 14px;
            height: 14px;
            opacity: 0.7;
        }}
    </style>
</head>
<body>
    <svg style="display:none">
        <!-- Project: Full isometric cube -->
        <symbol id="cube" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
            <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
            <line x1="12" y1="22.08" x2="12" y2="12"></line>
        </symbol>
        <!-- Package: Stacked layers (Hierarchy) -->
        <symbol id="package" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
            <polyline points="2 17 12 22 22 17"></polyline>
            <polyline points="2 12 12 17 22 12"></polyline>
        </symbol>
        <!-- Folder: Directory container -->
        <symbol id="folder" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
        </symbol>
        <!-- Python Module: File with code tags -->
        <symbol id="file-code" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <path d="m10 13-2 2 2 2"></path><path d="m14 17 2-2-2-2"></path>
        </symbol>
        <!-- Class: Structured box (Blueprint) -->
        <symbol id="box" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
            <circle cx="12" cy="12" r="3" fill="currentColor" opacity="0.4"></circle>
        </symbol>
        <!-- Logic icons unchanged -->
        <symbol id="terminal" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></symbol>
        <symbol id="file-text" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><line x1="10" y1="9" x2="8" y2="9"></line></symbol>
        <symbol id="alert-circle" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></symbol>
    </svg>

    <header>
        <div class="brand">
            <h1>Code Big Picture</h1>
            <div class="badge">V3.0</div>
        </div>
        
        <div class="header-controls">
            <button class="header-btn" onclick="collapseAll()" title="بستن همه نودها">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <line x1="9" y1="12" x2="15" y2="12"></line>
                </svg>
                بستن همه
            </button>
            <button class="header-btn" onclick="expandAll()" title="باز کردن همه نودها">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <line x1="12" y1="8" x2="12" y2="16"></line>
                    <line x1="8" y1="12" x2="16" y2="12"></line>
                </svg>
                باز کردن همه
            </button>
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

    <div class="legend" id="map-legend">
        <div class="legend-title">Map Guide / راهنما</div>
        <div class="legend-item"><svg class="legend-icon"><use href="#cube" /></svg> Project</div>
        <div class="legend-item"><svg class="legend-icon"><use href="#package" /></svg> Package</div>
        <div class="legend-item"><svg class="legend-icon"><use href="#folder" /></svg> Directory</div>
        <div class="legend-item"><svg class="legend-icon"><use href="#file-code" /></svg> Python Module</div>
        <div class="legend-item"><svg class="legend-icon"><use href="#box" /></svg> Class</div>
        <div class="legend-item"><svg class="legend-icon"><use href="#terminal" /></svg> Function / Method</div>
        <div class="legend-item"><svg class="legend-icon"><use href="#file-text" /></svg> Other File</div>
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
            
            panzoom.pan(x, y, {{ animate: true }});
            panzoom.zoom(scale, {{ animate: true }});
        }}

        // Expand All Nodes - Toggle all collapsed nodes
        window.expandAll = function() {{
            const allNodes = document.querySelectorAll('.node');
            // Expand from top to bottom (parent first)
            allNodes.forEach(node => {{
                const content = document.getElementById('content-' + node.id);
                if (content && content.style.display === 'none') {{
                    // This node is collapsed, expand it
                    window.toggleNode(node.id);
                }}
            }});
            
            // Auto-fit after expansion
            setTimeout(() => {{
                fitToScreen();
            }}, 400);
        }}

        // Collapse All Nodes
        window.collapseAll = function() {{
            const allNodes = document.querySelectorAll('.node');
            // Reverse order to collapse children first (bottom-up)
            const nodesArray = Array.from(allNodes).reverse();
            
            nodesArray.forEach(node => {{
                const content = document.getElementById('content-' + node.id);
                if (content && content.style.display !== 'none') {{
                    // This node is expanded, collapse it
                    window.toggleNode(node.id);
                }}
            }});
            
            // Auto-fit after collapse for better view
            setTimeout(() => {{
                fitToScreen();
            }}, 400);
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

        function getTranslateY(el) {{
            const transform = el.getAttribute('transform') || '';
            const match = /translate\\([^,]+,\\s*([^)]+)\\)/.exec(transform);
            return match ? parseFloat(match[1]) : 0;
        }}

        function setTranslateY(el, y) {{
            const transform = el.getAttribute('transform') || '';
            // Handle translate(x, y)
            const newTransform = transform.replace(/(translate\\([^,]+,)\\s*[^)]+\\)/, `$1 ${{y}})`);
            el.setAttribute('transform', newTransform);
            el.setAttribute('data-y', y);
        }}

        function getRowHeight(rowEl) {{
            let maxH = 0;
            const items = rowEl.children; // <g transform>
            for (let itm of items) {{
                const rect = itm.querySelector('.box-rect');
                if (rect) {{
                    maxH = Math.max(maxH, parseFloat(rect.getAttribute('height')));
                }}
            }}
            return maxH;
        }}

        // ========================================
        // V3.0 DYNAMIC HEIGHT CALCULATION ENGINE
        // ========================================
        // Instead of using stored data-full-h, we calculate actual height
        // based on current visible children state.

        function calculateActualNodeHeight(nodeG) {{
            const content = document.getElementById('content-' + nodeG.id);
            const rect = nodeG.querySelector('.box-rect');
            
            if (!content || content.style.display === 'none') {{
                return 35; // Header only (collapsed)
            }}
            
            // Content is visible, calculate actual height from rows
            const headerH = 35;
            const margin = 8;
            let contentHeight = 0;
            
            const rows = content.querySelectorAll(':scope > .row');
            for (let row of rows) {{
                const rowH = getRowHeight(row);
                contentHeight += rowH + margin;
            }}
            
            return headerH + contentHeight;
        }}

        function repositionRows(container) {{
            const headerH = 35;
            const margin = 8;
            let y = headerH;
            
            const rows = container.querySelectorAll(':scope > .row');
            for (let row of rows) {{
                const rowH = getRowHeight(row);
                row.setAttribute('data-row-h', rowH);
                row.setAttribute('data-y', y);
                
                // Update transform to new Y position
                const currentTransform = row.getAttribute('transform') || '';
                // Replace the translate Y value
                const xMatch = /translate\(([^,]+),/.exec(currentTransform);
                const xVal = xMatch ? xMatch[1] : '0';
                row.setAttribute('transform', `translate(${{xVal}}, ${{y}})`);
                
                y += rowH + margin;
            }}
        }}

        function recalculateFromNode(nodeG) {{
            const content = document.getElementById('content-' + nodeG.id);
            const rect = nodeG.querySelector('.box-rect');
            
            if (!rect) return;
            
            // Calculate actual height based on current state
            const newH = calculateActualNodeHeight(nodeG);
            rect.setAttribute('height', newH);
            
            // Reposition rows within this node if content is visible
            if (content && content.style.display !== 'none') {{
                repositionRows(content);
            }}
            
            // Propagate to parent node
            const wrapper = nodeG.parentElement;
            const row = wrapper ? wrapper.parentElement : null;
            
            if (row && row.classList.contains('row')) {{
                // Update this row's height
                const newRowH = getRowHeight(row);
                row.setAttribute('data-row-h', newRowH);
                
                // Reposition all sibling rows in parent container
                const container = row.parentElement;
                if (container && container.classList.contains('node-content')) {{
                    repositionRows(container);
                    
                    // Recurse to parent node
                    const parentNodeG = container.parentElement;
                    if (parentNodeG && parentNodeG.classList.contains('node')) {{
                        recalculateFromNode(parentNodeG);
                    }}
                }}
            }}
        }}

        // Toggle Logic with Dynamic Height Calculation (V3.0)
        window.toggleNode = function(nodeId) {{
            const nodeG = document.getElementById(nodeId);
            const content = document.getElementById('content-' + nodeId);
            const btnText = nodeG.querySelector('.toggle-btn text');
            
            if (!content) return; // Leaf node, can't toggle
            
            const isExpanding = (content.style.display === 'none');
            
            // Toggle visibility
            if (isExpanding) {{
                content.style.display = 'block';
                btnText.textContent = '-';
                nodeG.classList.remove('collapsed');
            }} else {{
                content.style.display = 'none';
                btnText.textContent = '+';
                nodeG.classList.add('collapsed');
            }}
            
            // Recalculate this node and propagate up the tree
            recalculateFromNode(nodeG);
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
        """Generates SVG with a smart layout and dynamic sizing."""
        import uuid
        node_id = f"node-{uuid.uuid4().hex[:8]}"
        
        node_type = node.get("type", "unknown")
        name = node.get("name", "Unknown")
        children = node.get("children", [])
        
        theme = self.THEME.get(node_type, self.THEME["method"])
        
        if not children:
            # Dynamic Width Calculation for leaf nodes
            # Roughly 8px per character + icon space + padding
            estimated_w = (len(name) * 8.5) + 40
            w = max(self.min_leaf_width, min(self.max_leaf_width, estimated_w))
            h = self.min_leaf_height
            svg = self._draw_node_rect(name, node_type, theme, w, h, node_id, has_children=False)
            return svg, w, h

        # Layout children...
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

        row_heights = [max(c[2] for c in row) for row in rows]
        row_widths = [sum(c[1] for c in row) + (len(row)-1)*self.margin for row in rows]
        
        total_width = max(row_widths) + (2 * self.padding)
        total_height = sum(row_heights) + (len(rows)-1)*self.margin + self.header_height + self.padding
        
        content_svg = []
        y_offset = self.header_height
        for i, row in enumerate(rows):
            x_offset = self.padding
            row_items = []
            for c_svg, c_w, c_h in row:
                row_items.append(f'<g transform="translate({x_offset}, 0)">{c_svg}</g>')
                x_offset += c_w + self.margin
            
            content_svg.append(f'<g class="row" transform="translate(0, {y_offset})" data-y="{y_offset}" data-row-h="{row_heights[i]}">{"".join(row_items)}</g>')
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
        """Helper to draw the rectangle with ICON and Truncated text."""
        # Truncation logic
        display_name = name
        max_chars = int((w - 45) / 8) # Estimated capacity
        if len(name) > max_chars and max_chars > 3:
            display_name = name[:max_chars-3] + "..."

        toggle_btn = ""
        if has_children:
            toggle_btn = f"""
            <g class="toggle-btn" onclick="toggleNode('{node_id}')" style="cursor: pointer; opacity: 0.6;">
                <circle cx="{w - 15}" cy="15" r="7" fill="white" stroke="{theme['stroke']}" stroke-width="1"/>
                <text x="{w - 15}" y="19" text-anchor="middle" font-size="10" font-weight="bold" fill="{theme['stroke']}" style="pointer-events: none;">-</text>
            </g>
            """
            
        icon = f'<use href="#{theme["icon"]}" x="8" y="8" width="16" height="16" stroke="{theme["stroke"]}" />'
        
        return f"""
        <rect class="box-rect" width="{w}" height="{h}" stroke="{theme['stroke']}" fill="{theme['bg']}" rx="6" ry="6" data-full-h="{h}" />
        {icon}
        <text x="30" y="20" fill="{theme['text']}" style="font-weight: 700; font-size: 13px;">
            {display_name}
            <title>{name}</title>
        </text>
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
