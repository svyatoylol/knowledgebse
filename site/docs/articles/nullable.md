---
title: "null и nullable-типы в C#"
keywords: [C#, null C#, nullable C#, nullable types C#, NullReferenceException C#, оператор C#, null-условный оператор C#, null coalescing C#, ссылочные типы C#, основы C#, обучение C#]
---

# null и nullable-типы в C#

`null` означает **отсутствие значения**. Это не ноль и не пустая строка — это «ничего».

## Ссылочные типы и null

Ссылочные типы (`string`, классы, массивы) могут быть `null` по умолчанию:

```csharp
string name = null;
Console.WriteLine(name); // выведет пустую строку, но...

Console.WriteLine(name.Length); //  NullReferenceException!
```

## Значимые типы и null

`int`, `bool`, `double` и другие значимые типы **не могут** быть `null`:

```csharp
int number = null; //  ошибка компиляции
```

Чтобы разрешить `null` для значимого типа, используют **nullable-синтаксис** `?`:

```csharp
int? number = null;  // 
bool? isReady = null; // 

Console.WriteLine(number.HasValue); // false
Console.WriteLine(number == null);  // true
```

### Получить значение из nullable

```csharp
int? number = 42;

Console.WriteLine(number.Value);        // 42 (исключение если null!)
Console.WriteLine(number.GetValueOrDefault());    // 42
Console.WriteLine(number.GetValueOrDefault(0));   // 42, или 0 если null
```

## Операторы для работы с null

### `??` — оператор объединения с null

Возвращает левую часть, если она не `null`, иначе — правую:

```csharp
string name = null;
string result = name ?? "Гость";
Console.WriteLine(result); // Гость

int? age = null;
int value = age ?? 0;
Console.WriteLine(value); // 0
```

### `??=` — присвоить если null

```csharp
string name = null;
name ??= "Гость";
Console.WriteLine(name); // Гость
```

### `?.` — null-условный оператор

Вызывает метод или свойство только если объект не `null`:

```csharp
string name = null;
int? length = name?.Length; // не упадёт, вернёт null

string upper = name?.ToUpper(); // null, без исключения
```

Удобно при обращении к цепочке свойств:

```csharp
int? length = user?.Address?.Street?.Length;
```

### `!` — оператор подавления null (null-forgiving)

Говорит компилятору «я уверен, что это не null»:

```csharp
string name = GetName()!; // отключает предупреждение
```

Используй осторожно — если ошибёшься, получишь исключение в рантайме.

## Nullable reference types (C# 8+)

В современных проектах включён режим, при котором компилятор **предупреждает** об опасных операциях с `null` для ссылочных типов:

```csharp
string name = null;   //  предупреждение компилятора
string? name = null;  //  явно сказали, что null допустим
```

Это настраивается в файле проекта:

```xml
<Nullable>enable</Nullable>
```

## Проверка на null

```csharp
string name = GetName();

// классический способ
if (name != null)
{
    Console.WriteLine(name.Length);
}

// современный способ (pattern matching)
if (name is not null)
{
    Console.WriteLine(name.Length);
}

// или
if (name is null) { ... }
```

## Итого

| Что | Синтаксис |
|---|---|
| Nullable значимый тип | `int? x = null;` |
| Значение по умолчанию | `x ?? 0` |
| Присвоить если null | `x ??= 0` |
| Безопасный вызов | `obj?.Method()` |
| Проверка | `if (x is null)` |
| Подавление предупреждения | `x!` |