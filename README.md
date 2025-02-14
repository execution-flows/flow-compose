# ___Flow Compose___ - Configurable Function Composition.

___Flow Compose___ enables functions to call other functions using alias names instead of direct references.  

## Key Features

* __Easy:__ Intuitive design makes the code simple to follow.
* __Fast Execution:__ Most operations are performed during module load time, minimizing runtime overhead.
* __Quick to Learn:__ Start with a standard Python function and seamlessly extend it into a flow with flow functions.
* __Fast to Code:__ Write Python as usual while benefiting from high code reusability.
* __Python Friendly:__ Embraces Python's best practices and conventions.

## Installation

```shell
pip install flow-compose
```

## Usage

For examples of __flow-compose__ code, check the [test suite](./tests).

### Simple Flow

Pick any function in your code and add a `@flow()` decorator.

```python
from flow_compose import flow

@flow()
def hello_world() -> None:
    print("Hello, World!")

hello_world()
```

### Function Composition

When you need to expand your code with another function, instead of calling it directly, decorate it with a flow function decorator and call it indirectly using its alias name defined in the flow configuration.

```python
from flow_compose import flow, flow_function, FlowFunction


@flow_function()
def greeting_hello_world() -> str:
    return "Hello World!"


@flow_function()
def greet_using_greeting(greeting: FlowFunction[str]) -> None:
    print(greeting())


@flow(
    greeting=greeting_hello_world,
)
def hello_world(greet: FlowFunction[None] = greet_using_greeting) -> None:
    greet()

hello_world()
``` 
> Example tests: 
> * [test_flow_with_nullary_function.py](tests/test_flow_with_nullary_function.py)
> * [test_flow_with_function_composing_another_function.py](tests/test_flow_with_function_composing_another_function.py)
> * [test_flow_with_function_composing_another_function_with_arguments.py](tests/test_flow_with_function_composing_another_function_with_arguments.py) 


### A Quick Overview

#### 1. Alias Naming:

   * `greeting` is an alias name for the `greeting_hello_world` flow function.
   * `greet` is an alias name for the `greet_using_greeting` flow function.

   Using alias names decouples concrete function implementations from how they are invoked in a composed flow.

#### 2. Modified Functions' External Signatures: 

   The `flow-compose` tool alters the external signature of functions decorated with `@flow` or `@flow_function`. This allows these functions to be called without explicit arguments; instead, `flow-compose` automatically supplies the necessary parameters based on the flow configuration.  
   For example, consider the `hello_world` function, which has one argument. Because this argument is annotated with `FlowFunction`, `flow-compose` removes it from the exposed signature, allowing you to invoke `hello_world()` without any arguments. Under the hood, `flow-compose` passes the required `greet: FlowFunction[None]` from the flow configuration to the function.

#### 3. Flexible Function Composition:

Although this approach might seem elaborate, it enables the `greet_using_greeting` function to work with different `greeting` functions without changing its implementation or the way `hello_world` is invoked. The `greet_using_greeting` function doesn't specify which `greeting` to use; instead, `flow-compose` injects the appropriate function based on the top-level flow configuration (e.g., `greeting_hello_world`).
   
This design allows different flows to define distinct `greeting` functions while reusing the same `greet_using_greeting` logic, enhancing flexibility and promoting code reuse.


```python
@flow_function()
def greeting_in_spanish() -> str:
    return "Hola, Mundo!"


@flow(
    greeting=greeting_in_spanish,
    greet=greet_using_greeting,
)
def hello_world_in_spanish(greet: FlowFunction[None]) -> None:
    greet()


hello_world_in_spanish()
``` 

> Example tests: 
> * [test_flow_with_three_reverse_composing_functions.py](tests/test_flow_with_three_reverse_composing_functions.py), [test_flow_with_function_composing_another_function_with_arguments_with_default_values.py](tests/test_flow_with_function_composing_another_function_with_arguments_with_default_values.py)

### Flow Arguments

Passing arguments to a flow function works just like with any regular function.

```python
@flow()
def greet(greeting: str) -> None:
    print(greeting)

greet("Hello, World!")
```

> Example test: 
> * [test_flow_with_non_flow_function_argument.py](tests/test_flow_with_non_flow_function_argument.py)

However, to propagate these arguments to other functions within the flow, you must define the argument in the flow configuration as a `FlowArgument` object.  

```python
@flow_function(cached=True)
def greeting__from_international_greeting_database__using_user_language(user_language: FlowFunction[str]) -> str:
    return db(InternationalGreeting).get(language=user_language())


@flow_function(cached=True)
def user_language__using_user(user: FlowFunction[str]) -> str:
    return user().language


@flow_function(cached=True)
def user__using_user_email(user_email: FlowFunction[str]) -> User:
    return db(User).get(email=user_email())


@flow(
    user_email=FlowArgument(str),
    user=user__using_user_email,
    user_language=user_language__using_user,
    greeting=greeting__from_international_greeting_database__using_user_language,
    greet=greet_using_greeting,
)
def greet_in_user_language__by_user_email(greet: FlowFunction[None]) -> None:
    greet()

greet_in_user_language__by_user_email(
    user_email="vinkobuble@gmail.com"
)
``` 

> Example tests: 
> * [test_flow_with_all_functions_in_configuration.py](tests/test_flow_with_all_functions_in_configuration.py)
> * [test_flow_with_argument_used_in_the_flow.py](tests/test_flow_with_argument_used_in_the_flow.py)
> * [test_flow_with_cached_flow_function.py](tests/test_flow_with_cached_flow_function.py)
> * [test_flow_with_argument_default_value_overridden_by_invocation.py](tests/test_flow_with_argument_default_value_overridden_by_invocation.py)
> * [test_flow_with_cached_flow_function_with_argument.py](tests/test_flow_with_cached_flow_function_with_argument.py)

### A Quick Overview

The `greet_in_user_language__by_user_email` flow now provides much more functionality without requiring any changes to the `greet_using_greeting` function. Here's how it works:

#### 1. Flow Argument:  
   - `user_email` is defined as a `FlowArgument`, which is a subclass of `FlowFunction`.  
   - To invoke the flow, you must pass `user_email` as a keyword argument.

#### 2. Flow Configuration Access:  
   - `user_email` is part of the flow configuration, meaning any flow function can access it.

#### 3. Flow Function Aliases:  
   - `user`, `user_language`, `greeting`, and `greet` are flow function aliases defined in the flow configuration.

#### 4. Independent Flow Functions:  
   - The flow functions `user__using_user_email`, `user_language__using_user`, and `greeting__from_international_greeting_database__using_user_language` operate independently and are unaware of each other.

#### 5. Accessing Functions Using Aliases:  
   - Any flow function can access another flow function defined in the flow configuration by including an argument annotated with `FlowFunction` that has the same name as the corresponding alias.

#### 6. Decoupled Implementation:  
   - Flow functions do not need to know the concrete implementation behind the alias names specified in the flow configuration.

#### 7. Caching:  
   - The `cached` argument ensures that a flow function is executed only once during a single flow execution. The result from the first execution is cached and reused in subsequent calls.

### A variation to the flow

```python
@flow_function()
def user__using_user_id(user_id: FlowFunction[str]) -> User:
    return db(User).get(id=user_id())


@flow(
    user_id=FlowArgument(int),
    user=user__using_user_id,
    user_language=user_language__using_user,
    greeting=greeting__from_international_greeting_database__using_user_language,
    greet=greet_using_greeting,
)
def greet_in_user_language__by_user_id(greet: FlowFunction[None]) -> None:
    greet()

greet_in_user_language__by_user_id(
    user_id=1
)
```

We changed the `FlowArgument` from `user_email` to `user_id` and added the `user__using_user_id` function to implement this variation. For example, the next variation could extract `user_language` from the HTTP request header, or retrieve a user object from the HTTP session. All other functions remain unchanged.

To implement a new flow variation, simply duplicate the configuration and pass it into the flow decorator. You never need to copy or paste existing functions; you only add new ones.

### Reusing Flow Configurations

A configuration is passed to a Python function as a `**kwargs` argument, meaning it can be defined as a dictionary.

```python
flow_configuration = {
    "greet": greet_hello_world,
}

@flow(**flow_configuration)
def hello_world(greet: FlowFunction[None]) -> None:
    greet()
```

> Example tests:
> * [test_flow_with_configuration_as_dictionary.py](tests/test_flow_with_configuration_as_dictionary.py)

Handling a configuration as a dictionary opens all kinds of possibilities. Remember: the Python interpreter loads flow configuration during module loading time, not run time.

## Reference

### flow

```python
from flow_compose import flow, FlowArgument, FlowFunction

@flow(
    flow_argument_alias=FlowArgument(T, default=argument_value),
    flow_function_alias=concrete_flow_function_name,
)
def flow_name(
    standard_python_argument: T,
    flow_argument: FlowArgument[T],
    flow_function: FlowFunction[T] = optional_flow_function_configuration_override,
) -> T:
    ...
```

__Note:__ The type parameter `T` can represent any kind of Python type.

#### Flow Configuration

1. **`flow_argument_alias`**
  * An alias for an input flow argument that you must provide during flow invocation. 
  * The type parameter `T` represents the type of the argument.
  * The first argument in the `FlowArgument` constructor is the flow argument type.
  * The optional `default` argument defines a default value if the argument is missing during invocation.
  * It is accessible to all flow functions within the flow.
  * Being a `callable`, you must invoke it to obtain its value (e.g., `flow_argument_alias()`).

2. **`flow_function_alias`**
  * An alias for a flow function that is accessible to all `flow_functions` in the flow.
  * The value, referred to as `concrete_flow_function_name`, must be a flow function — that is, a function decorated with the `@flow_function` decorator.

#### The Arguments of the Flow Body

1. **`standard_python_argument`**  
  * A standard Python function argument of any valid Python type passed during flow function invocation.
  * Available only within the body of the flow.
  * It is not part of the flow configuration and, therefore, is not accessible to other flow functions.

2. **`flow_argument`**  
  * An alias for a flow argument defined in the flow configuration.
  * The type parameter `T` represents the type of the argument.

3. **`flow_function`**  
  * A flow function defined in the flow configuration that is made available within the flow function body.
  * When the `flow_function` has a default value, referred in the reference code as `optional_flow_function_configuration_override`, you can use it only in the flow body. The rest of the flow functions have access to the definition from the flow configuration.
  * The type parameter `T` represents the return type of the function.

### flow function

```python
from flow_compose import flow_function, FlowFunction

@flow_function(
    cached: bool = False
)
def flow_function_name(
    standard_python_argument: T,
    flow_function: FlowFunction[T] = optional_flow_function_configuration_override,
) -> T:
    ...
```

  * **`cached`**
    * An optional argument with the default value `False`.  
    * When set to `True`, the function is executed only once during a single flow execution, and its return value is cached in the flow context for the duration of that execution.
    * Use the `cached` flag when:
      1. The function execution is expensive — such as reading from a database or sending a request to an external API—and the result remains unchanged during the flow execution.
      2. You want the function to be idempotent — ensuring that, for example, a database record is created only once or updated only once.

  * **`standard_python_argument`**
    * A standard Python function argument of any valid type passed during flow function invocation.  
    * Available only within the body of the flow function.
    * Not accessible to other flow functions in the flow.

  * **`flow_function`** - a flow function defined in the flow configuration that is made available within the flow function body.  
    * If a `flow_function` has a default value, referred in the reference code as `optional_flow_function_configuration_override`, you can use that override only in the function body. The rest of the flow functions have access to the definition from the flow configuration.
    * The type parameter `T` represents the return type of the function.

## What's next?

* To support this project, please give us a star on [Github](https://github.com/execution-flows/flow-compose).
* If you want to start using _flow-compose_, let us know how we can help by emailing [Vinko Buble](emailto:vinkobuble@gmail.com).
* If you are already using _flow-compose_, please share your feedback with [Vinko Buble](emailto:vinkobuble@gmail.com).
