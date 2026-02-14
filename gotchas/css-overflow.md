# CSS Grid/Flex 오버플로우 삽질 방지

## 증상

Grid나 Flex 레이아웃에서 자식 요소가 부모를 뚫고 나감.
화면이 가로로 스크롤되거나 레이아웃이 깨짐.

## 원인

Grid/Flex 자식의 기본값이 `min-width: auto`라서 콘텐츠 크기 이하로 줄어들지 않음.

## 해결

```html
<!-- 모든 grid/flex 자식에 min-w-0 추가 -->
<div className="grid grid-cols-3">
  <div className="min-w-0">...</div>
  <div className="min-w-0">...</div>
  <div className="min-w-0">...</div>
</div>
```

중첩된 경우 **매 레벨마다** `min-w-0` 필요:

```html
<div className="flex">
  <div className="min-w-0 flex-1">        <!-- 1단계 -->
    <div className="grid grid-cols-2">
      <div className="min-w-0">           <!-- 2단계 -->
        <div className="truncate">긴 텍스트...</div>
      </div>
    </div>
  </div>
</div>
```

## 확실한 방법

격리가 필요하면 래퍼로 감싸기:

```html
<div className="min-w-0 min-h-0 overflow-hidden">
  {children}
</div>
```
