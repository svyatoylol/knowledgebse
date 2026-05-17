```markdown
---
title: "Массивы в C#"
keywords: [C#, массивы C#, array C#, одномерный массив C#, многомерный массив C#, индекс массива C#, длина массива C#, foreach C#, основы C#, обучение C#, коллекции C#]
---

# Массивы в C#

Массив — это структура данных, которая хранит **фиксированное количество элементов одного типа**.

## Объявление и создание

```csharp
// Объявление и инициализация
int[] numbers = new int[5]; // массив из 5 нулей

// С начальными значениями
int[] numbers = new int[] { 1, 2, 3, 4, 5 };

// Короткий синтаксис
int[] numbers = { 1, 2, 3, 4, 5 };

string[] names = { "Алиса", "Боб", "Карл" };
```

## Доступ к элементам

Индексация начинается с **0**.

```csharp
int[] numbers = { 10, 20, 30, 40, 50 };

Console.WriteLine(numbers[0]); // 10
Console.WriteLine(numbers[2]); // 30

numbers[1] = 99; // изменить элемент
```

## Длина массива

```csharp
int[] numbers = { 1, 2, 3, 4, 5 };
Console.WriteLine(numbers.Length); // 5
```

## Перебор элементов

**Через `for`:**
```csharp
for (int i = 0; i < numbers.Length; i++)
{
    Console.WriteLine(numbers[i]);
}
```

**Через `foreach`** (когда индекс не нужен):
```csharp
foreach (int n in numbers)
{
    Console.WriteLine(n);
}
```

## Многомерные массивы

```csharp
// Двумерный массив (таблица 3x2)
int[,] matrix = {
    { 1, 2 },
    { 3, 4 },
    { 5, 6 }
};

Console.WriteLine(matrix[0, 1]); // 2
Console.WriteLine(matrix[2, 0]); // 5
```

## Массив массивов (зубчатый)

```csharp
int[][] jagged = new int[3][];
jagged[0] = new int[] { 1, 2 };
jagged[1] = new int[] { 3, 4, 5 };
jagged[2] = new int[] { 6 };

Console.WriteLine(jagged[1][2]); // 5
```

## Полезные методы

```csharp
int[] nums = { 5, 2, 8, 1, 9 };

Array.Sort(nums);                        // { 1, 2, 5, 8, 9 }
Array.Reverse(nums);                     // { 9, 8, 5, 2, 1 }
int idx = Array.IndexOf(nums, 5);        // найти индекс элемента
int[] copy = new int[nums.Length];
Array.Copy(nums, copy, nums.Length);     // копировать массив
```

## Типичные ошибки

**Выход за границы массива:**
```csharp
int[] arr = { 1, 2, 3 };
Console.WriteLine(arr[5]); // IndexOutOfRangeException!
```

Всегда проверяйте, что индекс находится в диапазоне `0 .. Length - 1`.

## Итого

| Что | Как |
|-----|-----|
| Создать | `int[] arr = new int[5];` |
| Получить элемент | `arr[i]` |
| Длина | `arr.Length` |
| Перебрать | `for` или `foreach` |
| Двумерный | `int[,] matrix` |
| Зубчатый | `int[][] jagged` |
```