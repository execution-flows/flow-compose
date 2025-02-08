# ___Execution Flows___ Framework using Function Composition

___Execution Flows___ is a programming paradigm that strictly distinguishes 

   1) top-level functions that are called to deliver functionality of a specific use case - like 
"create and invite a user with owner privileges".
   2) from mixin functions that are part of execution flow composition and deliver partial functionality, like "fetch user by email" or "send an owner invitation email". 

The idea behind ___Execution Flows___ is that an application is nothing but a congregation of top-level functions that deliver application features. Everything else is a building block (or a composing function) for execution flows.
