# REACT-FLOW - 노드 기반 다이어그램 캔버스

> 노드를 배치하고, 엣지로 연결하고, 줌/팬/미니맵까지 지원하는 인터랙티브 다이어그램 캔버스.
> 아키텍처 다이어그램, 워크플로우, 마인드맵 등에 사용.

## 필요 라이브러리

```bash
npm install @xyflow/react
```

```tsx
import '@xyflow/react/dist/style.css';
```

## 핵심 코드

### 기본 캔버스

```tsx
import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
  type Connection,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

function FlowCanvas() {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  const onConnect = (conn: Connection) => {
    const edge = { id: `e-${Date.now()}`, source: conn.source!, target: conn.target! };
    setEdges(prev => [...prev, edge]);
  };

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      fitView
    >
      <Background color="#30363D" gap={20} />
      <Controls />
      <MiniMap nodeColor="#58A6FF" />
    </ReactFlow>
  );
}

// 반드시 ReactFlowProvider로 감싸야 함
export default function App() {
  return (
    <ReactFlowProvider>
      <div style={{ width: '100%', height: '100vh' }}>
        <FlowCanvas />
      </div>
    </ReactFlowProvider>
  );
}
```

### 커스텀 노드

```tsx
import { Handle, Position, type NodeProps } from '@xyflow/react';

function CustomNode({ data }: NodeProps) {
  return (
    <div className="bg-bg-card border border-border rounded-lg px-4 py-2">
      <Handle type="target" position={Position.Left} />
      <div className="text-sm font-semibold">{data.label}</div>
      <div className="text-xs text-gray-400">{data.description}</div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

// nodeTypes 등록 (컴포넌트 밖에서!)
const nodeTypes = { custom: CustomNode };

// ReactFlow에 전달
<ReactFlow nodeTypes={nodeTypes} ... />
```

### 노드 추가

```tsx
const addNode = (label: string, position: { x: number; y: number }) => {
  const newNode: Node = {
    id: `n-${Date.now()}`,
    type: 'custom',
    position,
    data: { label },
  };
  setNodes(prev => [...prev, newNode]);
};
```

### screenToFlowPosition (외부에서 캔버스 좌표 변환)

```tsx
const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);

<ReactFlow onInit={setReactFlowInstance} ... />

// 화면 좌표 → 캔버스 좌표 변환 (DnD 등에서 사용)
const flowPos = reactFlowInstance.screenToFlowPosition({ x: clientX, y: clientY });
```

## CSS

```css
/* 다크 테마 오버라이드 */
.react-flow__node { color: #E6EDF3; }
.react-flow__edge-path { stroke: #58A6FF; }
.react-flow__handle { background: #58A6FF; width: 8px; height: 8px; }
.react-flow__attribution { display: none; }

/* 반드시 컨테이너에 고정 높이 필요 */
.react-flow-container { width: 100%; height: 100%; }
```

## 주의사항

- **ReactFlowProvider 필수**: useNodesState, useEdgesState 등 훅은 Provider 안에서만 동작
- **컨테이너 높이 필수**: 부모에 height: 100% 또는 고정 높이 없으면 캔버스가 안 보임
- **nodeTypes는 컴포넌트 밖에 선언**: 렌더 안에 넣으면 매번 재생성되어 성능 저하
- **useNodesState 제네릭**: TypeScript에서 useNodesState<Node>([]) 형태로 타입 명시해야 never[] 추론 방지
- **React 19 호환**: @xyflow/react v12는 React 19 지원

## 사용 예시

```tsx
// infra-quote에서의 실제 사용 패턴
const onNodeDragStop = (_: any, node: Node) => {
  updateNodePosition(node.id, node.position);
};

<ReactFlow
  nodes={nodes}
  edges={edges}
  onNodesChange={onNodesChange}
  onEdgesChange={onEdgesChange}
  onConnect={onConnect}
  onNodeClick={(_, node) => selectNode(node.id)}
  onPaneClick={() => deselectAll()}
  onNodeDragStop={onNodeDragStop}
  onInit={setReactFlowInstance}
  nodeTypes={nodeTypes}
  fitView
/>
```
