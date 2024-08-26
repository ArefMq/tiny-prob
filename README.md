# Tiny-Prob
A tool for adding Variable-level Visualization and Code Execution to Python code.

## How to Start
You can get the project by installing it via pip:
```shell
pip install tinyprob
```

or by installing from source by running:
```shell
make install
```

Once you have installed the library, you can use it like this:
```python
from  tiny_prob  import capture_all, TinyProb

@capture_all
class  MyClass:
	a: int = 10

	def do_something(self):
		...

with TinyProb():
	# The webserver is open in this context
	my_obj = MyClass()
	my_obj.do_something()

# The program does not exit by default, as the
# webserver is still running and serving the last 
# state of the program
```
After running this code, a browser page will pop-up on your default browser, and enables you to interact with the code.
You can then access the webserver at [local host](http://127.0.0.1:8080) or by `curl http://127.0.0.1:8080/all_pins`


TODO: image of the page

## How does it work


## Examples

In this section we discuss the different way you can benefit from tiny-prob. The most primitive way to use TP, is to instantiate a `TinyProb()` context and use it like this:
```python
from  tiny_prob  import SetConfig, TinyProb

# This function should be called before any TinyProb functionality used.
SetConfig(
	open_browser=True,
	ask_before_exit=True
	# Any other configs neccessary
)

with TinyProb():
	# The webserver is accessible as long as this context is open.
```


You can add pins manually to view them in the UI. You have to note that, this will be shown in the UI with capability to edit, however, editing this would have no effect as the setter function is not connected. See the enxt example:
```python
with TinyProb() as tp:
    tp.add_pin("a", 1)
```

you can have the `getter` function to view the variable value:
```python
with TinyProb() as tp:
    getter, _ = tp.add_pin("var", 2)

    for i in range(10):
	    # Edit the value in the UI and see its change here:
        print("var:", getter())
        sleep(1)
```

and similarly have the setter function to set it
```python
with TinyProb() as tp:
    _, setter = tp.add_pin("var", 2)

    for i in range(10):
	    # This will update the value on UI
        setter(value=i ** 2)
        sleep(1)
```


You can also easily append logs:

```python
with TinyProb() as tp:
    import logging
    logger = logging.getLogger("tiny_prob")

    logger.addHandler(tp.get_log_handler())

    logger.error("Starting TinyProb -> This is a Error")
    logger.warning("Starting TinyProb -> This is a Warning")
    logger.info("Starting TinyProb -> This is a INFO")
```


```python
with TinyProb() as tp:
    ev = tp.add_event_pin("event1")
    ev += lambda: print("Event 1 triggered")
    ev += lambda x: print(f"Event 1 triggered with value {x}")
```

```python
with TinyProb() as tp:
    prob = tp.add_debug_prob("event1")
    prob.wait()
    print("Continuing after event 1")
```

```python
from tiny_prob import capture_all

 @capture_all
 class MyClass:
     a: int = 10
     b: str = "Foo"
     something = Something() # This will not be captured

 with TinyProb() as tp:
     my_class = MyClass()
     my_class.a = 12
```

```python
from tiny_prob import capture

 @capture("a")
 class MyClass:
     a: int = 10
     b: str = "Bar"
```


## Contribute
