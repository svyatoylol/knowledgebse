---
title: "Цикл foreach в C#"
keywords: [C#, foreach C#, циклы C#, перебор коллекций C#, массивы C#, List C#, коллекции C#, основы C#, обучение C#, IEnumerable C#]
---

# Цикл foreach в C#

## Что такое foreach

`foreach` — это цикл, который используется для перебора элементов коллекции.

Он позволяет проходить по:
- массивам (`array`);
- спискам (`List`);
- строкам;
- другим коллекциям.

Главная идея:  
не думать об индексах, а работать сразу с элементами.

---

# Синтаксис foreach

```csharp
foreach (тип переменная in коллекция)
{
    код;
}
````

---

# Простейший пример с массивом

```csharp id="f1k9qa"
int[] numbers = { 1, 2, 3, 4, 5 };

foreach (int number in numbers)
{
    Console.WriteLine(number);
}
```

---

# Как это работает

* `numbers` — коллекция
* `number` — текущий элемент

На каждой итерации `number` принимает следующее значение массива.

---

# Пример со списком List

```csharp id="l3m7xz"
List<string> names = new List<string>
{
    "Анна",
    "Иван",
    "Пётр"
};

foreach (string name in names)
{
    Console.WriteLine(name);
}
```

---

# Перебор строки

Строка — это набор символов.

```csharp id="s8p2we"
string text = "Hello";

foreach (char c in text)
{
    Console.WriteLine(c);
}
```

---

# В чём отличие foreach от for

## foreach

```csharp id="f9k2mn"
foreach (int x in numbers)
{
    Console.WriteLine(x);
}
```

Плюсы:

* проще;
* нет индексов;
* меньше ошибок.

Минусы:

* нельзя изменить индекс;
* нельзя пропускать элементы.

---

## for

```csharp id="f3t8qa"
for (int i = 0; i < numbers.Length; i++)
{
    Console.WriteLine(numbers[i]);
}
```

Плюсы:

* полный контроль;
* можно менять шаг;
* можно работать с индексами.

---

# Когда использовать foreach

Используй `foreach`, если:

* нужно просто перебрать элементы;
* не нужно менять коллекцию;
* не важны индексы.

---

# Когда foreach не подходит

Нельзя:

* изменять элементы коллекции напрямую;
* удалять элементы во время перебора.

Пример ошибки:

```csharp id="e5k1xz"
List<int> numbers = new List<int> { 1, 2, 3 };

foreach (int n in numbers)
{
    if (n == 2)
    {
        numbers.Remove(n); // ошибка
    }
}
```

---

# Правильное удаление элементов

Используют `for`:

```csharp id="r4m9qa"
for (int i = 0; i < numbers.Count; i++)
{
    if (numbers[i] == 2)
    {
        numbers.RemoveAt(i);
        i--;
    }
}
```

---

# Использование foreach с условиями

```csharp id="k7t3mn"
int[] numbers = { 1, 2, 3, 4, 5 };

foreach (int n in numbers)
{
    if (n % 2 == 0)
    {
        Console.WriteLine(n + " — чётное");
    }
}
```

---

# Что такое readonly перебор

`foreach` не позволяет изменять сам элемент:

```csharp
foreach (int n in numbers)
{
    n = 10; // ошибка
}
```

---

# Вложенный foreach

```csharp id="v2m8qa"
List<List<int>> matrix = new List<List<int>>
{
    new List<int> { 1, 2 },
    new List<int> { 3, 4 }
};

foreach (var row in matrix)
{
    foreach (var item in row)
    {
        Console.WriteLine(item);
    }
}
```

---

# Частые ошибки

## Попытка изменить коллекцию

```csharp id="x8m1qa"
foreach (var item in list)
{
    list.Add(item); // ошибка
}
```

---

## Использование без коллекции

```csharp id="y3k9mn"
foreach (int x in 10) // ошибка
```

---

# Пример программы

Подсчёт суммы элементов:

```csharp id="z7p2qa"
List<int> numbers = new List<int> { 5, 10, 15 };

int sum = 0;

foreach (int n in numbers)
{
    sum += n;
}

Console.WriteLine(sum);
```

---

# Итоги

`foreach` — удобный способ перебора данных.

Важно понимать:

* он работает с коллекциями;
* не использует индексы;
* не позволяет изменять коллекцию напрямую;
* идеально подходит для чтения данных.

```
