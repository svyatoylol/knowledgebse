---
title: "Обобщённые типы (Generics) в C#"
keywords: [C#, generics C#, обобщённые типы C#, generic методы C#, generic классы C#, type parameter C#, ограничения generics C#, where C#, List C#, Dictionary C#, основы C#, обучение C#]
---

# Обобщённые типы (Generics) в C#

Обобщения позволяют писать классы и методы, которые работают **с любым типом данных**, не теряя типобезопасности.

## Зачем нужны

Без generics пришлось бы писать отдельный метод для каждого типа:

```csharp
int Max(int a, int b) => a > b ? a : b;
double Max(double a, double b) => a > b ? a : b;
string Max(string a, string b) => ... // и так далее
```

С generics — один метод для всех:

```csharp
T Max<T>(T a, T b) where T : IComparable<T>
{
    return a.CompareTo(b) > 0 ? a : b;
}

Console.WriteLine(Max(3, 7));       // 7
Console.WriteLine(Max(3.14, 2.71)); // 3.14
Console.WriteLine(Max("apple", "banana")); // banana
```

## Generic-метод

```csharp
T[] Repeat<T>(T value, int count)
{
    T[] result = new T[count];
    for (int i = 0; i < count; i++)
        result[i] = value;
    return result;
}

int[] threes = Repeat(3, 5);       // { 3, 3, 3, 3, 3 }
string[] hellos = Repeat("hi", 3); // { "hi", "hi", "hi" }
```

## Generic-класс

```csharp
class Box<T>
{
    public T Value { get; set; }

    public Box(T value)
    {
        Value = value;
    }

    public void Print() => Console.WriteLine(Value);
}

Box<int> intBox = new Box<int>(42);
Box<string> strBox = new Box<string>("Привет");

intBox.Print(); // 42
strBox.Print(); // Привет
```

## Несколько параметров типа

```csharp
class Pair<TFirst, TSecond>
{
    public TFirst First { get; set; }
    public TSecond Second { get; set; }

    public Pair(TFirst first, TSecond second)
    {
        First = first;
        Second = second;
    }
}

var pair = new Pair<string, int>("Возраст", 25);
Console.WriteLine($"{pair.First}: {pair.Second}"); // Возраст: 25
```

## Ограничения (where)

Можно указать, какие типы допустимы:

```csharp
// только классы (ссылочные типы)
T Method<T>(T value) where T : class { }

// только структуры (значимые типы)
T Method<T>(T value) where T : struct { }

// только типы с конструктором без параметров
T Create<T>() where T : new() => new T();

// только наследники определённого класса
T Method<T>(T value) where T : Animal { }

// только реализующие интерфейс
T Max<T>(T a, T b) where T : IComparable<T> { }

// несколько ограничений сразу
T Method<T>(T value) where T : class, IDisposable, new() { }
```

## Встроенные generic-коллекции

```csharp
List<int> list = new List<int> { 1, 2, 3 };

Dictionary<string, int> dict = new Dictionary<string, int>
{
    { "один", 1 },
    { "два", 2 }
};

Queue<string> queue = new Queue<string>();
Stack<int> stack = new Stack<int>();

HashSet<int> set = new HashSet<int> { 1, 2, 3, 2 }; // { 1, 2, 3 }
```

## Generic-интерфейс

```csharp
interface IRepository<T>
{
    T GetById(int id);
    void Save(T entity);
    void Delete(int id);
}

class UserRepository : IRepository<User>
{
    public User GetById(int id) { ... }
    public void Save(User user) { ... }
    public void Delete(int id) { ... }
}
```

## Итого

| Что | Синтаксис |
|---|---|
| Generic-метод | `T Method<T>(T value)` |
| Generic-класс | `class Box<T>` |
| Несколько параметров | `class Pair<T1, T2>` |
| Только классы | `where T : class` |
| Только структуры | `where T : struct` |
| Реализует интерфейс | `where T : IComparable<T>` |
| Есть конструктор | `where T : new()` |