---
title: "LINQ в C#"
keywords: [C#, LINQ C#, linq запросы C#, where C#, select C#, orderby C#, groupby C#, aggregate C#, коллекции C#, фильтрация C#, основы C#, обучение C#]
---

# LINQ в C#

LINQ (Language Integrated Query) — это способ **делать запросы к коллекциям** прямо в коде на C#, как SQL к базе данных.

## Подключение

```csharp
using System.Linq;
```

## Два синтаксиса

LINQ можно писать двумя способами — результат одинаковый:

```csharp
int[] numbers = { 5, 3, 8, 1, 9, 2, 7 };

// Метод-синтаксис (используется чаще)
var result = numbers.Where(n => n > 4).OrderBy(n => n);

// Запрос-синтаксис (похож на SQL)
var result = from n in numbers
             where n > 4
             orderby n
             select n;
```

## Основные методы

### `Where` — фильтрация

```csharp
var evens = numbers.Where(n => n % 2 == 0);
```

### `Select` — преобразование

```csharp
var squared = numbers.Select(n => n * n);

// Преобразование объектов
var names = users.Select(u => u.Name);
```

### `OrderBy` / `OrderByDescending` — сортировка

```csharp
var asc  = numbers.OrderBy(n => n);
var desc = numbers.OrderByDescending(n => n);

// Сортировка по нескольким полям
var sorted = users.OrderBy(u => u.LastName).ThenBy(u => u.FirstName);
```

### `First` / `Last` / `Single`

```csharp
int first = numbers.First();                  // первый (исключение если пусто)
int firstEven = numbers.First(n => n % 2 == 0);

int? safe = numbers.FirstOrDefault(n => n > 100); // null если не найден

int only = numbers.Single(n => n == 5);       // ровно один, иначе исключение
```

### `Any` / `All` / `Count`

```csharp
bool hasEven = numbers.Any(n => n % 2 == 0);   // true
bool allPositive = numbers.All(n => n > 0);     // true
int count = numbers.Count(n => n > 4);          // 4
```

### `Sum` / `Min` / `Max` / `Average`

```csharp
int sum     = numbers.Sum();
int min     = numbers.Min();
int max     = numbers.Max();
double avg  = numbers.Average();

// С условием
int sumBig = numbers.Where(n => n > 4).Sum();
```

### `GroupBy` — группировка

```csharp
var groups = users.GroupBy(u => u.City);

foreach (var group in groups)
{
    Console.WriteLine($"Город: {group.Key}");
    foreach (var user in group)
        Console.WriteLine($"  {user.Name}");
}
```

### `SelectMany` — разворачивание вложенных коллекций

```csharp
var allTags = posts.SelectMany(p => p.Tags);
```

### `Distinct` / `Skip` / `Take`

```csharp
var unique = numbers.Distinct();
var page   = numbers.Skip(10).Take(5); // пагинация: пропустить 10, взять 5
```

## Отложенное выполнение

LINQ не выполняется сразу — только когда данные реально нужны:

```csharp
var query = numbers.Where(n => n > 4); // запрос ещё не выполнен

foreach (var n in query) { } // вот здесь выполняется
```

Чтобы выполнить сразу и сохранить результат:

```csharp
List<int> result = numbers.Where(n => n > 4).ToList();
int[] arr = numbers.Where(n => n > 4).ToArray();
```

## Цепочки методов

Методы LINQ легко объединяются:

```csharp
var result = users
    .Where(u => u.Age >= 18)
    .OrderBy(u => u.Name)
    .Select(u => u.Name)
    .ToList();
```

## Итого

| Метод | Что делает |
|---|---|
| `Where` | фильтрует |
| `Select` | преобразует |
| `OrderBy` | сортирует |
| `GroupBy` | группирует |
| `First/Last` | первый/последний элемент |
| `Any/All` | проверка условия |
| `Count/Sum/Min/Max/Average` | агрегация |
| `Skip/Take` | срез коллекции |
| `ToList/ToArray` | выполнить и сохранить |