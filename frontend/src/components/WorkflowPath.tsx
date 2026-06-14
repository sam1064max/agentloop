import { useState, useCallback } from 'react';
import type { PathAnalysis, PathNode, PathEdge } from '../types';
import clsx from 'clsx';

interface WorkflowPathProps {
  analysis: PathAnalysis;
  onNodeClick?: (node: PathNode) => void;
  onEdgeClick?: (edge: PathEdge) => void;
}

interface NodePosition {
  x: number;
  y: number;
}

const NODE_HEIGHT = 60;
const NODE_WIDTH = 160;
const NODE_MARGIN_X = 80;
const NODE_MARGIN_Y = 40;
const COLUMNS = 5;

export default function WorkflowPath({ analysis, onNodeClick, onEdgeClick }: WorkflowPathProps) {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [hoveredEdge, setHoveredEdge] = useState<string | null>(null);

  const getNodePosition = useCallback((nodeId: string, index: number): NodePosition => {
    const column = index % COLUMNS;
    const row = Math.floor(index / COLUMNS);
    return {
      x: 50 + column * (NODE_WIDTH + NODE_MARGIN_X),
      y: 50 + row * (NODE_HEIGHT + NODE_MARGIN_Y),
    };
  }, []);

  const getEdgePath = useCallback((source: PathNode, targetIndex: number, target: PathNode) => {
    const sourcePos = getNodePosition(source, analysis.nodes.indexOf(source));
    const targetPos = getNodePosition(target, targetIndex);
    
    const midX = (sourcePos.x + NODE_WIDTH / 2 + targetPos.x + NODE_WIDTH / 2) / 2;
    
    return `M ${sourcePos.x + NODE_WIDTH} ${sourcePos.y + NODE_HEIGHT / 2}
            C ${midX} ${sourcePos.y + NODE_HEIGHT / 2},
              ${midX} ${targetPos.y + NODE_HEIGHT / 2},
              ${targetPos.x} ${targetPos.y + NODE_HEIGHT / 2}`;
  }, [analysis.nodes, getNodePosition]);

  const maxCount = Math.max(...analysis.nodes.map(n => n.count));

  const svgWidth = 3 * (NODE_WIDTH + NODE_MARGIN_X) + 100;
  const svgHeight = Math.ceil(analysis.nodes.length / COLUMNS) * (NODE_HEIGHT + NODE_MARGIN_Y) + 100;

  return (
    <div className="card overflow-x-auto">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">Workflow Path Analysis</h3>
          <p className="text-sm text-slate-500">
            {analysis.totalSessions.toLocaleString()} total sessions • Avg path length: {analysis.avgPathLength} steps
          </p>
        </div>
        <div className="text-sm text-slate-500">
          Most common: {analysis.mostCommonPath.join(' → ')}
        </div>
      </div>

      <div className="relative" style={{ minWidth: svgWidth }}>
        <svg width={svgWidth} height={svgHeight} className="overflow-visible">
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon points="0 0, 10 3.5, 0 7" fill="#94a3b8" />
            </marker>
          </defs>

          {analysis.edges.map((edge, index) => {
            const sourceIndex = analysis.nodes.findIndex(n => n.id === edge.source);
            const targetIndex = analysis.nodes.findIndex(n => n.id === edge.target);
            const source = analysis.nodes[sourceIndex];
            const target = analysis.nodes[targetIndex];
            
            if (sourceIndex === -1 || targetIndex === -1) return null;

            const sourcePos = getNodePosition(source, sourceIndex);
            const targetPos = getNodePosition(target, targetIndex);
            const edgeId = `${edge.source}-${edge.target}`;
            const isHovered = hoveredEdge === edgeId;

            return (
              <g key={index}>
                <path
                  d={`M ${sourcePos.x + NODE_WIDTH} ${sourcePos.y + NODE_HEIGHT / 2}
                      L ${targetPos.x} ${targetPos.y + NODE_HEIGHT / 2}`}
                  fill="none"
                  stroke={isHovered ? '#0d8bf5' : '#cbd5e1'}
                  strokeWidth={isHovered ? 3 : 2}
                  markerEnd="url(#arrowhead)"
                  className="transition-all duration-200 cursor-pointer"
                  onMouseEnter={() => setHoveredEdge(edgeId)}
                  onMouseLeave={() => setHoveredEdge(null)}
                  onClick={() => onEdgeClick?.(edge)}
                />
                <text
                  x={(sourcePos.x + NODE_WIDTH + targetPos.x) / 2}
                  y={(sourcePos.y + targetPos.y) / 2 + NODE_HEIGHT / 2 - 8}
                  textAnchor="middle"
                  className="text-xs fill-slate-500"
                >
                  {edge.count.toLocaleString()}
                </text>
                <text
                  x={(sourcePos.x + NODE_WIDTH + targetPos.x) / 2}
                  y={(sourcePos.y + targetPos.y) / 2 + NODE_HEIGHT / 2 + 8}
                  textAnchor="middle"
                  className={clsx(
                    'text-xs font-medium',
                    edge.successRate >= 90 ? 'fill-success-600' :
                    edge.successRate >= 70 ? 'fill-warning-600' :
                    'fill-danger-600'
                  )}
                >
                  {edge.successRate.toFixed(1)}%
                </text>
              </g>
            );
          })}

          {analysis.nodes.map((node, index) => {
            const pos = getNodePosition(node, index);
            const isHovered = hoveredNode === node.id;
            const successRateColor = node.successRate >= 95 ? 'bg-success-500' :
                                      node.successRate >= 85 ? 'bg-warning-500' :
                                      'bg-danger-500';

            return (
              <g
                key={node.id}
                className="cursor-pointer"
                onMouseEnter={() => setHoveredNode(node.id)}
                onMouseLeave={() => setHoveredNode(null)}
                onClick={() => onNodeClick?.(node)}
              >
                <rect
                  x={pos.x}
                  y={pos.y}
                  width={NODE_WIDTH}
                  height={NODE_HEIGHT}
                  rx={8}
                  fill={isHovered ? '#f0f7ff' : '#ffffff'}
                  stroke={isHovered ? '#0d8bf5' : '#e2e8f0'}
                  strokeWidth={isHovered ? 2 : 1}
                  className="transition-all duration-200"
                />
                
                <div
                  className={clsx(
                    'absolute w-3 h-3 rounded-full',
                    successRateColor
                  )}
                  style={{
                    left: pos.x + NODE_WIDTH - 16,
                    top: pos.y + 12,
                  }}
                />

                <text x={pos.x + 12} y={pos.y + 24} className="text-sm font-medium fill-slate-900">
                  {node.name}
                </text>
                <text x={pos.x + 12} y={pos.y + 42} className="text-xs fill-slate-500">
                  {node.count.toLocaleString()} sessions
                </text>
                <text x={pos.x + 12} y={posY => pos.y + 56} className="text-xs fill-slate-400">
                  {node.avgDuration}ms avg
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      <div className="mt-4 flex items-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-success-500" />
          <span className="text-slate-600">High success (≥95%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-warning-500" />
          <span className="text-slate-600">Medium (85-95%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-danger-500" />
          <span className="text-slate-600">Low (<85%)</span>
        </div>
      </div>
    </div>
  );
}