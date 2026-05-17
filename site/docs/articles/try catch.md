---
title: "Обработка исключений: try, catch, finally в C#"
keywords: [C#, try catch C#, finally C#, исключения C#, exception C#, обработка ошибок C#, throw C#, Exception C#, NullReferenceException C#, основы C#, обучение C#]
---

# Обработка исключений: try, catch, finally в C#

Исключение — это ошибка, которая возникает **во время выполнения** программы. `try/catch/finally` позволяет её поймать и обработать, не допустив краша.

## Базовый синтаксис

```csharp
try
{
    // код, который может выбросить исключение
    int result = 10 / 0;
}
catch (Exception ex)
{
    // что делать если исключение произошло
    Console.WriteLine($"Ошибка: {ex.Message}");
}
```

## finally

Блок `finally` выполняется **всегда** — и при ошибке, и без неё:

```csharp
try
{
    Console.WriteLine("Работаем...");
    int result = 10 / 0;
}
catch (Exception ex)
{
    Console.WriteLine($"Ошибка: {ex.Message}");
}
finally
{
    Console.WriteLine("Это выполнится в любом случае");
}
```

Типичное применение — закрыть файл, соединение с БД, освободить ресурс.

## Несколько блоков catch

Можно ловить разные типы исключений по-разному:

```csharp
try
{
    string text = null;
    Console.WriteLine(text.Length);
}
catch (NullReferenceException ex)
{
    Console.WriteLine("Обращение к null!");
}
catch (DivideByZeroException ex)
{
    Console.WriteLine("Деление на ноль!");
}
catch (Exception ex)
{
    // поймает всё остальное — ставить последним
    Console.WriteLine($"Неизвестная ошибка: {ex.Message}");
}
```

## Свойства Exception

```csharp
catch (Exception ex)
{
    Console.WriteLine(ex.Message);    // текст ошибки
    Console.WriteLine(ex.StackTrace); // где именно произошла
    Console.WriteLine(ex.GetType());  // тип исключения
}
```

## throw — выбросить исключение

```csharp
void SetAge(int age)
{
    if (age < 0)
        throw new ArgumentException("Возраст не может быть отрицательным");

    this.age = age;
}
```

### Перебросить пойманное исключение

```csharp
catch (Exception ex)
{
    Console.WriteLine("Логируем...");
    throw; // пробрасываем дальше, сохраняя stacktrace
}
```

## Свои исключения

```csharp
class InsufficientFundsException : Exception
{
    public decimal Amount { get; }

    public InsufficientFundsException(decimal amount)
        : base($"Недостаточно средств: {amount}")
    {
        Amount = amount;
    }
}

// использование
throw new InsufficientFundsException(500m);
```

## Фильтры исключений (when)

```csharp
catch (Exception ex) when (ex.Message.Contains("timeout"))
{
    Console.WriteLine("Превышено время ожидания");
}
```

## Распространённые исключения .NET

| Исключение | Причина |
|---|---|
| `NullReferenceException` | обращение к `null` |
| `IndexOutOfRangeException` | выход за границы массива |
| `DivideByZeroException` | деление на ноль |
| `InvalidCastException` | неверное приведение типов |
| `ArgumentException` | неверный аргумент метода |
| `IOException` | ошибка при работе с файлами |
| `OverflowException` | переполнение числового типа |

## Итого

| Блок | Когда выполняется |
|---|---|
| `try` | всегда, основной код |
| `catch` | только при исключении |
| `finally` | всегда, после try/catch |
| `throw` | выбросить исключение вручную |
| `when` | фильтр для catch |