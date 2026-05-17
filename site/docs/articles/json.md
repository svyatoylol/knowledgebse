---
title: "Работа с JSON в C#"
keywords: [C#, JSON C#, System.Text.Json C#, JsonSerializer C#, сериализация C#, десериализация C#, JsonProperty C#, Newtonsoft C#, API C#, основы C#, обучение C#]
---

# Работа с JSON в C#

JSON — популярный формат обмена данными. В C# для работы с ним используют встроенную библиотеку `System.Text.Json` или популярную стороннюю `Newtonsoft.Json`.

## System.Text.Json (встроенная, рекомендуется)

```csharp
using System.Text.Json;
```

## Сериализация — объект в JSON

```csharp
class User
{
    public string Name { get; set; }
    public int Age { get; set; }
    public string Email { get; set; }
}

User user = new User { Name = "Алиса", Age = 25, Email = "alice@mail.com" };

string json = JsonSerializer.Serialize(user);
Console.WriteLine(json);
// {"Name":"Алиса","Age":25,"Email":"alice@mail.com"}
```

### Красивый вывод

```csharp
var options = new JsonSerializerOptions { WriteIndented = true };
string json = JsonSerializer.Serialize(user, options);
// {
//   "Name": "Алиса",
//   "Age": 25,
//   "Email": "alice@mail.com"
// }
```

## Десериализация — JSON в объект

```csharp
string json = """{"Name":"Алиса","Age":25,"Email":"alice@mail.com"}""";

User user = JsonSerializer.Deserialize<User>(json);
Console.WriteLine(user.Name); // Алиса
```

## Коллекции

```csharp
// Сериализация списка
List<User> users = new List<User> { ... };
string json = JsonSerializer.Serialize(users);

// Десериализация списка
List<User> users = JsonSerializer.Deserialize<List<User>>(json);

// Словарь
Dictionary<string, int> scores = new() { {"Алиса", 100}, {"Боб", 85} };
string json = JsonSerializer.Serialize(scores);
```

## Атрибуты

### `[JsonPropertyName]` — имя поля в JSON

```csharp
class User
{
    [JsonPropertyName("full_name")]
    public string Name { get; set; }

    [JsonPropertyName("user_age")]
    public int Age { get; set; }
}

// {"full_name":"Алиса","user_age":25}
```

### `[JsonIgnore]` — пропустить поле

```csharp
class User
{
    public string Name { get; set; }

    [JsonIgnore]
    public string Password { get; set; } // не попадёт в JSON
}
```

## Настройки сериализации

```csharp
var options = new JsonSerializerOptions
{
    WriteIndented = true,                                    // красивый вывод
    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,       // camelCase имена
    PropertyNameCaseInsensitive = true,                      // регистр не важен при чтении
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull // пропускать null
};
```

## Работа с файлами

```csharp
// Записать JSON в файл
await File.WriteAllTextAsync("data.json", JsonSerializer.Serialize(user));

// Прочитать JSON из файла
string json = await File.ReadAllTextAsync("data.json");
User user = JsonSerializer.Deserialize<User>(json);

// Или через поток (эффективнее для больших файлов)
using FileStream fs = File.OpenRead("data.json");
User user = await JsonSerializer.DeserializeAsync<User>(fs);
```

## JsonDocument — читать без класса

Когда структура JSON неизвестна заранее:

```csharp
string json = """{"name":"Алиса","age":25}""";

using JsonDocument doc = JsonDocument.Parse(json);
JsonElement root = doc.RootElement;

string name = root.GetProperty("name").GetString(); // Алиса
int age = root.GetProperty("age").GetInt32();       // 25
```

## Newtonsoft.Json

Популярная альтернатива с более широкими возможностями:

```bash
dotnet add package Newtonsoft.Json
```

```csharp
using Newtonsoft.Json;

// Сериализация
string json = JsonConvert.SerializeObject(user, Formatting.Indented);

// Десериализация
User user = JsonConvert.DeserializeObject<User>(json);
```

## System.Text.Json vs Newtonsoft.Json

| | System.Text.Json | Newtonsoft.Json |
|---|---|---|
| Встроенная | + | - нужен пакет |
| Скорость | быстрее | медленнее |
| Гибкость | меньше | больше |
| Поддержка старых проектов | хуже | лучше |

## Итого

| Что | Как |
|---|---|
| Объект → JSON | `JsonSerializer.Serialize(obj)` |
| JSON → объект | `JsonSerializer.Deserialize<T>(json)` |
| Переименовать поле | `[JsonPropertyName("name")]` |
| Пропустить поле | `[JsonIgnore]` |
| Без класса | `JsonDocument.Parse(json)` |
| Красивый вывод | `WriteIndented = true` |