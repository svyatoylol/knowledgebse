---
title: "списки (List) в C#"
keywords: [C#, List C#, списки C#, коллекции C#, добавление элементов C#, Remove C#, Count C#, IndexOf C#, основы C#, обучение C#]
---

# Массивы в C#


---

# Списки (List)

## Что такое List

`List` — это динамический список, который может:

* увеличиваться;
* уменьшаться;
* изменяться во время работы программы.

---

## Подключение

```csharp 
using System.Collections.Generic;
```

---

## Создание списка

```csharp 
List<int> numbers = new List<int>();
```

---

## Добавление элементов

```csharp 
numbers.Add(10);
numbers.Add(20);
numbers.Add(30);
```

---

## Вывод списка

```csharp 
foreach (int number in numbers)
{
    Console.WriteLine(number);
}
```

---

## Доступ по индексу

```csharp 
Console.WriteLine(numbers[0]);
```

---

## Количество элементов

```csharp 
Console.WriteLine(numbers.Count);
```

---

## Удаление элемента

```csharp 
numbers.Remove(20);
```

Удаляет первое совпадение.

---

## Удаление по индексу

```csharp 
numbers.RemoveAt(0);
```

---

## Проверка наличия элемента

```csharp 
bool exists = numbers.Contains(10);
```

---

## Поиск индекса

```csharp 
int index = numbers.IndexOf(20);
```

Если элемент не найден → `-1`.

---

## Очистка списка

```csharp 
numbers.Clear();
```

---

# Разница массива и списка

| Массив               | List                    |
| -------------------- | ----------------------- |
| Фиксированный размер | Динамический размер     |
| Быстрее              | Гибче                   |
| Не изменяется размер | Можно добавлять/удалять |
| `Length`             | `Count`                 |

---

# Пример программы со списком

```csharp 
List<int> numbers = new List<int>();

numbers.Add(5);
numbers.Add(10);
numbers.Add(15);

int sum = 0;

foreach (int n in numbers)
{
    sum += n;
}

Console.WriteLine(sum);
```

---

# Вложенные списки (List of List)

```csharp 
List<List<int>> matrix = new List<List<int>>();
```

Пример добавления:

```csharp id="w8t3mn"
matrix.Add(new List<int> { 1, 2 });
matrix.Add(new List<int> { 3, 4 });
```

---

# Частые ошибки

## Нет using

```csharp
List<int> numbers = new List<int>();
```

Ошибка, если не подключить:

```csharp
using System.Collections.Generic;
```

---

## Выход за границы массива

```csharp 
int[] arr = { 1, 2, 3 };

Console.WriteLine(arr[5]);
```

Это ошибка.

---

## Удаление несуществующего элемента

```csharp 
numbers.Remove(100);
```

Ошибки нет, но ничего не произойдёт.

---

# Когда использовать List

Используй `List`, если:

* количество элементов неизвестно;
* данные будут добавляться или удаляться;
* нужна гибкость.

---

# Когда использовать массив

Используй массив, если:

* размер заранее известен;
* важна производительность;
* структура не меняется.

---
