---
title: "Конструкция switch в C#"
keywords: [C#, switch C#, case C#, default C#, условные конструкции C#, выбор варианта C#, основы C#, обучение C#, ветвление C#, switch expression]
---

# Конструкция switch в C#

## Что такое switch

`switch` — это условная конструкция, которая позволяет выбирать один вариант из нескольких.

Она используется, когда нужно сравнить одно значение с несколькими вариантами.

Например:
- номер дня недели;
- команда пользователя;
- пункт меню;
- оценка;
- состояние программы.

---

# Зачем нужен switch

Без `switch` пришлось бы писать много `if else`.

Например:

```csharp 
if (day == 1)
{
    Console.WriteLine("Понедельник");
}
else if (day == 2)
{
    Console.WriteLine("Вторник");
}
else if (day == 3)
{
    Console.WriteLine("Среда");
}
````

С `switch` код становится проще и понятнее.

---

# Синтаксис switch

```csharp 
switch (значение)
{
    case вариант:
        код;
        break;

    case вариант:
        код;
        break;

    default:
        код;
        break;
}
```

---

# Простейший пример

```csharp 
int day = 2;

switch (day)
{
    case 1:
        Console.WriteLine("Понедельник");
        break;

    case 2:
        Console.WriteLine("Вторник");
        break;

    case 3:
        Console.WriteLine("Среда");
        break;
}
```

---

# Как работает switch

1. Проверяется значение в `switch`.
2. Выполняется подходящий `case`.
3. После `break` конструкция завершается.

---

# Что такое case

`case` — это отдельный вариант проверки.

```csharp 
case 1:
```

означает:

> если значение равно `1`

---

# Что такое break

`break` завершает выполнение `switch`.

```csharp 
break;
```

Если забыть `break`, программа перейдёт к следующему `case`.

В современных версиях C# это обычно вызывает ошибку компиляции.

---

# Конструкция default

`default` выполняется, если ни один `case` не подошёл.

```csharp 
default:
    Console.WriteLine("Неизвестное значение");
    break;
```

---

# Пример с default

```csharp 
int number = 10;

switch (number)
{
    case 1:
        Console.WriteLine("Один");
        break;

    case 2:
        Console.WriteLine("Два");
        break;

    default:
        Console.WriteLine("Другое число");
        break;
}
```

---

# switch со строками

`switch` может работать со строками.

```csharp 
string command = "start";

switch (command)
{
    case "start":
        Console.WriteLine("Запуск");
        break;

    case "stop":
        Console.WriteLine("Остановка");
        break;

    default:
        Console.WriteLine("Неизвестная команда");
        break;
}
```

---

# Несколько case подряд

Можно объединять варианты.

```csharp 
int month = 1;

switch (month)
{
    case 12:
    case 1:
    case 2:
        Console.WriteLine("Зима");
        break;
}
```

---

# Локальные переменные в case

Внутри `case` можно писать обычный код.

```csharp 
switch (number)
{
    case 1:
        int x = 10;

        Console.WriteLine(x);
        break;
}
```

---

# switch expression

В новых версиях C# есть сокращённая форма — `switch expression`.

## Пример

```csharp 
int day = 1;

string name = day switch
{
    1 => "Понедельник",
    2 => "Вторник",
    3 => "Среда",
    _ => "Неизвестный день"
};
```

---

# Символ _

В `switch expression` символ `_` заменяет `default`.

```csharp 
_ => "Неизвестное значение"
```

---

# Когда использовать switch

`switch` удобен, когда:

* проверяется одно значение;
* вариантов много;
* нужна более читаемая структура.

---

# Когда лучше использовать if

`if` удобнее, если:

* условия сложные;
* используются диапазоны;
* нужно несколько разных сравнений.

Например:

```csharp 
if (age >= 18 && hasTicket)
{
    Console.WriteLine("Вход разрешён");
}
```

---

# Частые ошибки

## Забыли break

```csharp 
case 1:
    Console.WriteLine("One");
```

Нужно:

```csharp 
case 1:
    Console.WriteLine("One");
    break;
```

---

# Повторяющиеся case

Нельзя писать одинаковые варианты.

Неправильно:

```csharp 
case 1:
case 1:
```

---

# Пример программы

```csharp 
Console.Write("Введите номер дня: ");

int day = Convert.ToInt32(Console.ReadLine());

switch (day)
{
    case 1:
        Console.WriteLine("Понедельник");
        break;

    case 2:
        Console.WriteLine("Вторник");
        break;

    case 3:
        Console.WriteLine("Среда");
        break;

    default:
        Console.WriteLine("Неизвестный день");
        break;
}
```

