---
title: "Кортежи в C#"
keywords: [C#, кортежи C#, tuple C#, ValueTuple C#, деконструкция C#, именованные кортежи C#, возврат нескольких значений C#, основы C#, обучение C#]
---

# Кортежи в C#

Кортеж — это лёгкий способ **сгруппировать несколько значений** без создания отдельного класса.

## Создание

```csharp
// Безымянный кортеж
var person = (25, "Алиса");
Console.WriteLine(person.Item1); // 25
Console.WriteLine(person.Item2); // Алиса

// Именованный кортеж (рекомендуется)
var person = (Age: 25, Name: "Алиса");
Console.WriteLine(person.Age);  // 25
Console.WriteLine(person.Name); // Алиса
```

## Явное указание типа

```csharp
(int Age, string Name) person = (25, "Алиса");
Console.WriteLine(person.Age);  // 25
Console.WriteLine(person.Name); // Алиса
```

## Возврат нескольких значений из метода

Главное применение кортежей:

```csharp
(int Min, int Max) GetMinMax(int[] numbers)
{
    return (numbers.Min(), numbers.Max());
}

var result = GetMinMax(new[] { 3, 1, 8, 2, 9 });
Console.WriteLine(result.Min); // 1
Console.WriteLine(result.Max); // 9
```

## Деконструкция

Разобрать кортеж на отдельные переменные:

```csharp
var person = (Age: 25, Name: "Алиса");

var (age, name) = person;
Console.WriteLine(age);  // 25
Console.WriteLine(name); // Алиса

// Прямо в объявлении
(int age, string name) = GetMinMax(numbers);

// Пропустить ненужное поле
var (_, name) = person;
```

## Кортежи в коллекциях

```csharp
List<(string Name, int Score)> leaderboard = new()
{
    ("Алиса", 100),
    ("Боб", 85),
    ("Карл", 92)
};

foreach (var (name, score) in leaderboard)
{
    Console.WriteLine($"{name}: {score}");
}
```

## Сравнение кортежей

```csharp
var a = (1, "Алиса");
var b = (1, "Алиса");

Console.WriteLine(a == b); // true — сравниваются поэлементно
```

## Когда использовать, а когда нет

| Ситуация | Что использовать |
|---|---|
| Вернуть 2–3 значения из метода | кортеж |
| Временная группировка данных | кортеж |
| Сложная логика, много полей | класс или struct |
| Публичное API библиотеки | класс или struct |

## Итого

| Что | Синтаксис |
|---|---|
| Создать | `(Age: 25, Name: "Алиса")` |
| Получить поле | `person.Age` |
| Деконструировать | `var (age, name) = person;` |
| Пропустить поле | `var (_, name) = person;` |
| Вернуть из метода | `(int, string) Method()` |