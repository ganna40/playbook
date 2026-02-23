# DND-KIT - 드래그 앤 드롭 툴킷 (React)

> React 전용 모던 DnD 라이브러리. 가볍고 확장성 좋음.
> 목록 정렬, 패널 간 이동, 캔버스 드롭 등에 사용.

## 필요 라이브러리

```bash
npm install @dnd-kit/core @dnd-kit/utilities
# 정렬 필요하면 추가
npm install @dnd-kit/sortable
```

## 핵심 코드

### 기본 드래그 → 드롭

```tsx
import { DndContext, type DragEndEvent, useSensor, useSensors, PointerSensor } from '@dnd-kit/core';
import { useDraggable } from '@dnd-kit/core';

function DraggableItem({ id, data, children }: { id: string; data: any; children: React.ReactNode }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id,
    data,
  });

  const style = transform
    ? { transform: `translate(${transform.x}px, ${transform.y}px)` }
    : undefined;

  return (
    <div
      ref={setNodeRef}
      {...listeners}
      {...attributes}
      style={style}
      className={`cursor-grab active:cursor-grabbing ${isDragging ? 'opacity-50' : ''}`}
    >
      {children}
    </div>
  );
}

function App() {
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 5 },
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active } = event;
    const item = active.data.current?.item;
    if (!item) return;

    const x = (event.activatorEvent as MouseEvent).clientX + (event.delta?.x ?? 0);
    const y = (event.activatorEvent as MouseEvent).clientY + (event.delta?.y ?? 0);

    addItemToCanvas(item, { x, y });
  };

  return (
    <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
      <Sidebar />
      <Canvas />
    </DndContext>
  );
}
```

### 드롭 영역 (useDroppable)

```tsx
import { useDroppable } from '@dnd-kit/core';

function DropZone({ id, children }: { id: string; children: React.ReactNode }) {
  const { isOver, setNodeRef } = useDroppable({ id });

  return (
    <div
      ref={setNodeRef}
      className={`p-4 border-2 border-dashed rounded-lg ${isOver ? 'border-accent bg-accent/10' : 'border-border'}`}
    >
      {children}
    </div>
  );
}
```

### 정렬 가능한 리스트 (Sortable)

```tsx
import { SortableContext, useSortable, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

function SortableItem({ id }: { id: string }) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id });
  const style = { transform: CSS.Transform.toString(transform), transition };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      {id}
    </div>
  );
}

function SortableList({ items }: { items: string[] }) {
  return (
    <SortableContext items={items} strategy={verticalListSortingStrategy}>
      {items.map(id => <SortableItem key={id} id={id} />)}
    </SortableContext>
  );
}
```

## 주의사항

- **activationConstraint 필수**: distance: 5 없으면 클릭도 드래그로 인식
- **DndContext는 최상위에**: React Flow와 함께 쓸 때 DndContext가 ReactFlow를 감싸야 함
- **transform 직접 적용**: useDraggable의 transform은 CSS transform으로 직접 적용
- **React 19 호환**: @dnd-kit/core v6.3+은 React 19 지원
- **data 전달**: useDraggable({ data: { item } }) → event.active.data.current?.item

## React Flow와 함께 쓰기

```tsx
<DndContext sensors={sensors} onDragEnd={handleDragEnd}>
  <div className="flex">
    <CatalogPanel />
    <ReactFlow onInit={setReactFlowInstance} ... />
  </div>
</DndContext>

const handleDragEnd = (event: DragEndEvent) => {
  const item = event.active.data.current?.item;
  if (!item || !reactFlowInstance) return;

  const position = reactFlowInstance.screenToFlowPosition({
    x: (event.activatorEvent as MouseEvent).clientX + (event.delta?.x ?? 0),
    y: (event.activatorEvent as MouseEvent).clientY + (event.delta?.y ?? 0),
  });

  addNodeToFlow(item, position);
};
```

## 사용 예시

```tsx
<DraggableItem id={item.id} data={{ item }}>
  <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg cursor-grab">
    <ServerIcon size={14} />
    <span>가상머신</span>
  </div>
</DraggableItem>
```
