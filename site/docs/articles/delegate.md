---
title: "Делегаты в C#"
keywords: [C#, делегаты C#, delegate C#,Func C#, Action C#, Predicate C#, анонимные методы C#, лямбда C#, обратный вызов C#, callback C#, основы C#, обучение C#]
---

# Делегаты в C#

Делегат — это тип, который хранит **ссылку на метод**. Проще говоря, переменная, в которую можно положить метод и вызвать его позже.

## Объявление и использование

```csharp
// 1. Объявить тип делегата
delegate int Operation(int a, int b);

// 2. Создать метод подходящей сигнатуры
int Add(int a, int b) => a + b;
int Multiply(int a, int b) => a * b;

// 3. Присвоить и вызвать
Operation op = Add;
Console.WriteLine(op(3, 4)); // 7

op = Multiply;
Console.WriteLine(op(3, 4)); // 12
```

Сигнатура метода должна **точно совпадать** с сигнатурой делегата.

## Встроенные делегаты

Создавать собственные делегаты нужно редко — в .NET есть готовые:

### `Action` — метод, который ничего не возвращает

```csharp
Action greet = () => Console.WriteLine("Привет!");
greet(); // Привет!

Action<string> greetName = name => Console.WriteLine($"Привет, {name}!");
greetName("Алиса"); // Привет, Алиса!

Action<int, int> printSum = (a, b) => Console.WriteLine(a + b);
```

### `Func` — метод, который возвращает значение

Последний тип-параметр — возвращаемый тип:

```csharp
Func<int> getNumber = () => 42;
Console.WriteLine(getNumber()); // 42

Func<int, int, int> add = (a, b) => a + b;
Console.WriteLine(add(3, 4)); // 7

Func<string, int> getLength = s => s.Length;
```

### `Predicate` — метод, возвращающий `bool`

```csharp
Predicate<int> isEven = n => n % 2 == 0;
Console.WriteLine(isEven(4)); // true
Console.WriteLine(isEven(7)); // false
```

## Делегат как параметр метода

Главная сила делегатов — передавать поведение в метод:

```csharp
void PrintResult(int a, int b, Func<int, int, int> operation)
{
    Console.WriteLine(operation(a, b));
}

PrintResult(10, 5, (a, b) => a + b); // 15
PrintResult(10, 5, (a, b) => a * b); // 50
```

## Multicast-делегаты

Делегат может хранить **несколько методов** сразу — все вызовутся по порядку:

```csharp
Action log = () => Console.WriteLine("Лог в консоль");
log += () => Console.WriteLine("Лог в файл");
log += () => Console.WriteLine("Лог на сервер");

log(); 
// Лог в консоль
// Лог в файл
// Лог на сервер

log -= () => Console.WriteLine("Лог в файл"); // убрать метод
```

## Анонимные методы

```csharp
Func<int, int> square = delegate(int x)
{
    return x * x;
};

Console.WriteLine(square(5)); // 25
```

Сейчас вместо этого используют лямбды — они короче.

## Итого

| Что | Синтаксис |
|---|---|
| Свой делегат | `delegate int Op(int a, int b);` |
| Без возврата | `Action<string>` |
| С возвратом | `Func<int, int, int>` |
| Возвращает bool | `Predicate<int>` |
| Добавить метод | `del += Method;` |
| Убрать метод | `del -= Method;` |