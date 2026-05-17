---
title: "Пространства имён в C#"
keywords: [C#, namespace C#, пространство имён C#, using C#, директива using C#, вложенные namespace C#, организация кода C#, основы C#, обучение C#]
---

# Пространства имён в C#

Пространство имён (`namespace`) — это способ **организовать и сгруппировать** связанный код, а также избежать конфликтов имён между классами.

## Зачем это нужно

Представь, что в двух библиотеках есть класс `Logger`. Без пространств имён возник бы конфликт. С ними — нет:

```csharp
MyApp.Logging.Logger
ThirdParty.Logging.Logger
```

## Объявление

```csharp
namespace MyApp.Logging
{
    class Logger
    {
        public void Log(string message) { ... }
    }
}
```

С C# 10 можно использовать **файловый namespace** без фигурных скобок — весь файл принадлежит этому пространству:

```csharp
namespace MyApp.Logging;

class Logger
{
    public void Log(string message) { ... }
}
```

## Директива using

Чтобы не писать полное имя каждый раз, используют `using`:

```csharp
using MyApp.Logging;

Logger logger = new Logger(); // без using пришлось бы: MyApp.Logging.Logger
```

## Стандартные пространства имён .NET

| Namespace | Что содержит |
|---|---|
| `System` | базовые типы, `Console`, `Math` |
| `System.Collections.Generic` | `List<T>`, `Dictionary<T>` |
| `System.IO` | работа с файлами |
| `System.Linq` | LINQ-запросы |
| `System.Text` | `StringBuilder`, кодировки |

## Псевдоним для namespace

Если два пространства имён содержат класс с одинаковым именем:

```csharp
using MyLogging = MyApp.Logging;
using TheirLogging = ThirdParty.Logging;

MyLogging.Logger myLogger = new MyLogging.Logger();
TheirLogging.Logger theirLogger = new TheirLogging.Logger();
```

## Вложенные пространства имён

```csharp
namespace MyApp
{
    namespace Logging
    {
        class Logger { }
    }
}

// То же самое, короче:
namespace MyApp.Logging
{
    class Logger { }
}
```

## Global using (C# 10+)

Если `using` нужен во всём проекте, его можно объявить один раз:

```csharp
// GlobalUsings.cs
global using System.Collections.Generic;
global using MyApp.Logging;
```

После этого директива действует во **всех файлах проекта**.

## Итого

| Что | Синтаксис |
|---|---|
| Объявить | `namespace MyApp.Logging { }` |
| Файловый (C# 10+) | `namespace MyApp.Logging;` |
| Подключить | `using MyApp.Logging;` |
| Псевдоним | `using Alias = Some.Long.Namespace;` |
| Глобальный | `global using ...;` |