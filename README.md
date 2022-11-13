# FAT16_Reader

Simple implementation Reader of img formatted with FAT_16.

## Using

Instantiate the class.
```python
from fat16_reader import Reader

f16r = Reader('PATH/TO/FAT16/IMG')
```

Now you can navigate to you img like in a normal shell

## Commands

- **dir**: &emsp;&emsp;&emsp;&emsp;&emsp;&nbsp;List all contents of current directory
- **ls**: &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;See ***dir***
- **cd** *[directory]*: &emsp;Move to *directory*
- **more** *[file]*: &emsp;&emsp;Read contents of *file*

*NOTE*: All command/arguments are CASE SENSITIVE 