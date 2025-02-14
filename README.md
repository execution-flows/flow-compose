# ___Flow Compose___ - configurable function composition.

___Flow Compose___ allows one function to access and call other functions through an alias name instead of referencing them directly.  

## Key Features

* __Easy:__ Designed to be intuitive and easy to follow the code.
* __Fast execution:__ Most of the execution is performed during Python module load time, not runtime.
* __Quick to learn:__ Start by writing a normal Python function and follow the example below to expand it into a flow with flow functions.
* __Fast to code:__ You write Python the same way as you would. But with a high level of code reusability.
* __Python friendly:__ Uses Python's best practices and rules.

## Installation

```shell
pip install flow-compose
```

## Usage

For examples of __flow-compose__ code, check the [test suite](./tests).

### Simple flow

Pick any function in your code and add a `@flow()` decorator.

```python
from flow_compose import flow

@flow()
def hello_world() -> None:
    print("Hello, World!")

hello_world()
```

### Function composition

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

1. `greeting` is an alias name for the `greeting_hello_world` flow function.
2. `greet` is an alias name for the `greet_using_greeting` flow function.
3. The purpose of alias function names is to separate concrete function implementation from the invocation of a composed function.
4. `flow-compose` changes the external signature of functions decorated with `@flow` or `@flow_function` decorators so they can be called without arguments that will be passed by `flow-compose`.
5. In this example, although `hello_world` has one argument, because the argument is annotated with `FlowFunction`, `flow-compose` removes it from the exposed function signature, so you can invoke without arguments like `hello_world()`.
6. `flow-compose` will pass `greet: FlowFunction` from the flow configuration to the body of the flow.

This approach might look like an overkill, but we do this to give the `greet_using_greeting` function the ability to greet different `greetings` without changing the `greet_using_greeting` function or changing the way we invoke the `hello_world` function.    

The `greet_using_greeting` flow function does not specify which `greeting` it will use. `flow-compose` sends the `greeting` function to the `greet_using_greeting` based on the top-level flow configuration - `greeting_hello_world`.

Different flows can define different `greeting` functions without changing the `greet_using_greeting` function.

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

### Flow arguments

Passing arguments to a flow function is the same as with any function.

```python
@flow()
def greet(greeting: str) -> None:
    print(greeting)

greet("Hello, World!")
```

> Example test: 
> * [test_flow_with_non_flow_function_argument.py](tests/test_flow_with_non_flow_function_argument.py)

But to make the flow propagate arguments to other functions in the flow, we have to define the argument in the flow configuration as a `FlowArgument` object.  

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

The `greet_in_user_language__by_user_email` flow has much more functionality, but we did not need to change the `greet_using_greeting` function to accommodate new functionality.

1. `user_email` is defined as a `FlowArgument`. `FlowArgument` is a subclass of a `FlowFunction`. Now, to invoke the flow you must pass `user_email` as a keyword argument. 
2. `user_email` is part of the flow configuration, and any flow function can access it.
3. `user`, `user_language`, `greeting`, and `greet` are flow function aliases configured in the `flow` configuration.
4. `user__using_user_email`, `user_language__using_user`, and `greeting__from_international_greeting_database__using_user_language` flow functions are unaware of one another.
5. Any flow function can access any other flow function defined in the flow configuration by adding an argument annotated with `FlowFunction` and named the same as the flow function alias name.
6. Flow functions do not know which concrete implementation the alias name points to in the flow configuration.
7. The `cached` argument ensures that a `flow_function` gets called only once during single flow execution. The result of the first execution is cached and returned in subsequent executions.  

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

We changed the `FlowArgument` from `user_email` to `user_id` and added the `user__using_user_id` function to deliver this variation. For example, the next variation could get `user_language` from the HTTP request header. Or we can get a user object from the HTTP session. All other functions will always stay the same.

To deliver the next flow variation, we only need to duplicate a configuration and pass it in the flow decorator—you will never have to copy/paste functions you already have. You only add new functions.

### Reusing flow configurations

A configuration is an `**kwargs` argument passed to a Python function. So it can be declared as a dictionary.

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
    flow_argument_alias=FlowArgument(T, value=argument_value),
    flow_function_alias=concrete_flow_function_name,
)
def flow_name(
    standard_python_argument: T,
    flow_argument: FlowArgument[T],
    flow_function: FlowFunction[T] = optional_flow_function_configuration_override,
) -> T:
    ...
```

__Note:__ Type `T` represents any kind of Python type.

#### Flow configuration

1.`flow_argument_alias` - is an alias name for an input flow argument that you must send as an argument during the flow invocation. 
  * The `T` type is the type of the argument.
  * The first argument in the `FlowArgument` construction is the flow argument type.
  * `value` argument is optional and defines its value when it is missing in the invocation arguments.
  * It is available to all flow functions in the flow.
  * It is a `callable`. You must invoke it to get its value: `flow_argument_alias()`.

2.`flow_function_alias` - An alias name for a flow function that is available to all `flow_functions` in the `flow`.
  * The value, marked as `concrete_flow_function_name`, has to be a flow function - a function that is decorated with `@flow_function` decorator.

#### The arguments of the flow body

1. `standard_python_argument` - a standard Python function argument of any valid Python type passed during flow function invocation.
   * Available only in the body of the flow.
   * It is not part of the flow configuration. 
   * Therefore, it is not available to other flow functions in the flow.

2. `flow_argument` - An alias name for a flow argument that defined in the flow configuration.
   * The `T` type is the type of the argument.

3. `flow_function` - a flow function defined in the flow configuration made available to the code in the flow function body.
   * When the `flow_function` has a default value marked as `optional_flow_function_configuration_override` in the reference code, you can use it in the flow body. The rest of the flow functions have access to the definition from the flow configuration.
   * The `T` type is the return type of the function.

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

1. `cached` - an optional argument with default value `False`.
    * When set to `True`, the function will be called only once during a single flow execution, and the flow context will cache its return value for the duration of the flow execution.
    * We set the `cached` flag to `True` when:
      1. The function execution is expensive - like reading from a database or sending a request to an external API, and the result will not change during the flow execution.
      2. We want to make the function idempotent - like when creating or updating a database record. We want to ensure we create only one record or update the same record only once.

2. `standard_python_argument` - a standard Python function argument of any valid Python type passed during flow function invocation.
   * Available only in the body of the flow function.
   * It is not available to other flow functions in the flow.

3. `flow_function` - a flow function defined in the flow configuration made available to the code in the flow function body.
   * When the `flow_function` has a default value marked as `optional_flow_function_configuration_override` in the reference code, you can use it in the flow body. The rest of the flow functions have access to the definition from the flow configuration.
   * The `T` type is the return type of the function.

## What's next?

* To support this project, please give us a star on [Github](https://github.com/execution-flows/flow-compose).
* If you want to start using _flow-compose_, let us know how we can help by emailing [Vinko Buble](emailto:vinkobuble@gmail.com).
* If you are already using _flow-compose_, please share your feedback with [Vinko Buble](emailto:vinkobuble@gmail.com).
