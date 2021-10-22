# Examples

Here you can find some examples / tutorials which might be helpful. Also make sure to read over the below list of implementation-focused features for building visual node editors with this library. Furthermore, for node implementations there is a directory with examples in the Ryven repo.

## Features

#### load & save  
All serialization and loading of projects. Data is stored using `json`, and for some parts `pickle`.

```python
project: dict = my_session.data()
with open(filepath, 'w') as f:
    f.write(json.dumps(project))
```

#### simple nodes system  
All information of a node is part of its class. A minimal node definition can be as simple as this

```python
import ryvencore_qt as rc

class PrintNode(rc.Node):
    """Prints your data."""

    title = 'Print'
    init_inputs = [
        rc.NodeInputBP()
    ]
    color = '#A9D5EF'

    def update_event(self, inp=-1):
        print(self.input(0))
```

#### dynamic nodes registration mechanism  
You can register and unregister nodes at any time. Registered nodes can be placed in a flow.
```python
my_session.register_nodes( [ <your_nodes> ] )
```

#### right-click operations system for nodes  
which can be edited through the API at any time
```python
self.actions[f'remove input {i}'] = {
    'method': self.rem_input,
    'data': i,
}

# with some method...
def rem_input(self, index):
    self.delete_input(index)
    del self.actions[f'remove input {len(self.inputs)}']
```

#### Qt widgets  
You can add custom QWidgets for the frontend of your nodes.

```python
class MyNode(rc.Node):
    #...
    main_widget_class: QWidget = MyNodeMainWidget
    main_widget_pos = 'below ports'  # alternatively 'between ports'
    # ...
```

#### many different modifiable themes  
See [Features Page](https://leon-thomm.github.io/ryvencore-qt/features/).

#### exec flow support  
While data flows should be the most common use case, exec flows (like [UnrealEngine BluePrints](https://docs.unrealengine.com/4.26/en-US/ProgrammingAndScripting/Blueprints/)) are also supported.

#### logging support  
```python
import logging

class MyNode(rc.Node):
    def __init__(self, params):
        super().__init__(params)

        self.my_logger = self.new_logger(title='nice log')
    
    def update_event(self, inp=-1):
        self.my_logger.info('updated!')
```

#### variables system  
with an update mechanism to build nodes that automatically adapt to change of variables

```python
import logging

class MyNode(rc.Node):
    # ...
    
    def somewhere(self):
        self.register_var_receiver(name='some_var_name', method=process_new_var_val)
    
    # with a method
    def process_new_var_val(self, val):
        print(f'received a new val!\n{val}\n')
```

#### stylus support for adding handwritten notes  
![](./docs/img/stylus_light.png)

#### rendering flow images  
...