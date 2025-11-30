# SKILL Programming Basics

## Introduction

SKILL is Cadence's scripting language for Virtuoso. This document covers only the essential basics needed for simple operations.

---

## Basic Syntax

### Variables

```skill
; Define a variable
myVar = 5
myString = "hello"
myList = list(1 2 3)
```

### Comments

```skill
; Single line comment

/* 
Multi-line
comment
*/
```

---

## Basic Data Types

### Numbers

```skill
intValue = 42
floatValue = 3.14
```

### Strings

```skill
str = "Hello World"
formatted = sprintf(nil "Value: %d" 42)
```

### Lists

```skill
myList = list(1 2 3 4 5)
emptyList = list()
```

---

## Output

### Print to CIW

```skill
; Simple print
printf("Hello World\n")

; Formatted print
printf("Value: %d\n" 42)
printf("Float: %f\n" 3.14)
printf("String: %s\n" "text")
```

---

## Control Flow

### Conditionals

```skill
if( condition then
  ; do something
else
  ; do something else
)
```

### When (if without else)

```skill
when( condition
  ; do something
)
```

### Unless (inverse if)

```skill
unless( condition
  ; do this if condition is false
)
```

---

## Loops

### For Loop

```skill
for( i 1 10
  printf("Count: %d\n" i)
)
```

### Foreach Loop

```skill
foreach( item myList
  printf("Item: %L\n" item)
)
```

---

## Functions

### Define Function

```skill
procedure( myFunction(arg1 arg2)
  ; function body
  arg1 + arg2
)
```

### Call Function

```skill
result = myFunction(5 3)
```

---

## Basic Virtuoso Operations

### Get Current Cellview

```skill
cv = geGetWindowCellView()
if( cv then
  printf("Library: %s\n" cv~>libName)
  printf("Cell: %s\n" cv~>cellName)
  printf("View: %s\n" cv~>viewName)
)
```

### Create Simple Rectangle

```skill
; Get current cellview
cv = geGetEditCellView()

; Create rectangle
dbCreateRect(
  cv                    ; cellview
  list("metal1" "drawing")  ; layer
  list(0:0 10:10)      ; bounding box
)
```

---

## Coordinate System

### Points

```skill
; Define a point (x:y)
pt1 = 0:0
pt2 = 10:20

; Access coordinates
xCoord = xCoord(pt1)
yCoord = yCoord(pt1)
```

### Bounding Box

```skill
; Define bounding box
bbox = list(0:0 100:100)  ; lower-left : upper-right
```

---

## Common Patterns

### Check if Variable Exists

```skill
if( boundp('myVar) then
  printf("Variable exists\n")
)
```

### Safe Execution

```skill
when( cv = geGetEditCellView()
  ; Only execute if cv is valid
  printf("Cell: %s\n" cv~>cellName)
)
```

### Error Handling

```skill
if( cv then
  ; cv is valid
  ; do operations
else
  ; cv is nil
  printf("Error: No cellview open\n")
)
```

---

## Loading Files

### Load SKILL File

```skill
load("path/to/file.il")
```

### From CIW

```
CIW> load("my_script.il")
```

---

## Quick Reference

### Common Functions

```skill
; Print
printf("text")

; Get cellview
geGetEditCellView()
geGetWindowCellView()

; Create objects
dbCreateRect(cv layer bbox)
dbCreatePath(cv layer points width)

; List operations
list(1 2 3)
length(myList)
car(myList)   ; first element
cdr(myList)   ; rest of list

; String operations
sprintf(nil "format" args)
strlen(str)
```

---

## Next Steps

This covers only the absolute basics. For specialized tasks:

1. Use `search_knowledge()` to find relevant knowledge
2. Load specific domain knowledge when needed
3. Refer to specialized documentation for complex operations

Remember: This is intentionally minimal. Real-world SKILL programming requires loading specialized knowledge on-demand.
