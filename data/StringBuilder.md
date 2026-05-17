---
title: "StringBuilder в C#"
keywords: [C#, StringBuilder C#, строки C#, конкатенация строк C#, System.Text C#, Append C#, Insert C#, Replace C#, производительность строк C#, основы C#, обучение C#]
---

# StringBuilder в C#

`StringBuilder` — это класс для **эффективного построения строк** когда нужно много изменений. Обычная строка (`string`) в C# неизменяема — каждая конкатенация создаёт новый объект в памяти.

## Проблема обычных строк

```csharp
string result = "";
for (int i = 0; i < 10000; i++)
{
    result += i; // каждый раз создаётся новая строка — медленно!
}
```

`StringBuilder` изменяет строку **на месте**, без создания новых объектов.

## Подключение

```csharp
using System.Text;
```

## Создание

```csharp
StringBuilder sb = new StringBuilder();
StringBuilder sb = new StringBuilder("Начальный текст");
StringBuilder sb = new StringBuilder(256); // начальная ёмкость буфера
```

## Основные методы

### `Append` — добавить в конец

```csharp
StringBuilder sb = new StringBuilder();
sb.Append("Привет");
sb.Append(", ");
sb.Append("мир");
sb.Append('!');
sb.Append(42);

Console.WriteLine(sb); // Привет, мир!42
```

### `AppendLine` — добавить с переносом строки

```csharp
sb.AppendLine("Первая строка");
sb.AppendLine("Вторая строка");
```

### `AppendFormat` — добавить с форматированием

```csharp
sb.AppendFormat("Имя: {0}, Возраст: {1}", "Алиса", 25);
```

### `Insert` — вставить в позицию

```csharp
StringBuilder sb = new StringBuilder("Привет мир!");
sb.Insert(7, "прекрасный ");
Console.WriteLine(sb); // Привет прекрасный мир!
```

### `Remove` — удалить символы

```csharp
StringBuilder sb = new StringBuilder("Привет, мир!");
sb.Remove(7, 5); // начиная с индекса 7, удалить 5 символов
Console.WriteLine(sb); // Привет, !
```

### `Replace` — заменить

```csharp
StringBuilder sb = new StringBuilder("кот сидит на коте");
sb.Replace("кот", "пёс");
Console.WriteLine(sb); // пёс сидит на псе... 
// Replace заменяет все вхождения!
```

### `Clear` — очистить

```csharp
sb.Clear();
Console.WriteLine(sb.Length); // 0
```

## Цепочка вызовов

Все методы возвращают сам `StringBuilder`, поэтому можно писать цепочкой:

```csharp
string result = new StringBuilder()
    .Append("Имя: ")
    .Append("Алиса")
    .AppendLine()
    .Append("Возраст: ")
    .Append(25)
    .ToString();
```

## Получить строку

```csharp
StringBuilder sb = new StringBuilder("Привет, мир!");
string result = sb.ToString();

// Часть строки
string part = sb.ToString(0, 6); // Привет
```

## Полезные свойства

```csharp
StringBuilder sb = new StringBuilder("Привет");

Console.WriteLine(sb.Length);    // 6 — текущая длина
Console.WriteLine(sb.Capacity);  // размер внутреннего буфера
Console.WriteLine(sb[0]);        // П — доступ по индексу
sb[0] = 'п';                     // изменить символ по индексу
```

## Когда использовать

| Ситуация | Что использовать |
|---|---|
| Строка не меняется | `string` |
| Редкая конкатенация (2–5 раз) | `string` + `$""` |
| Цикл или много изменений | `StringBuilder` |
| Построение длинного текста | `StringBuilder` |

## Итого

| Метод | Что делает |
|---|---|
| `Append(value)` | добавить в конец |
| `AppendLine(value)` | добавить с `\n` |
| `AppendFormat(...)` | добавить с форматом |
| `Insert(index, value)` | вставить в позицию |
| `Remove(index, count)` | удалить символы |
| `Replace(old, new)` | заменить все вхождения |
| `Clear()` | очистить |
| `ToString()` | получить строку |