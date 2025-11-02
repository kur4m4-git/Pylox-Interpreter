# PyLox

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **complete Python implementation** of the **Lox** programming language from the book  
[*Crafting Interpreters*](https://craftinginterpreters.com) by Robert Nystrom.

---


## Installation
To install PyLox, ensure you have Python 3.8 or higher. 
  ```sh
  $ git clone https://github.com/kur4m4-git/Pylox.git
  $ pip install pylox/
  ```

## Usage

### REPL Mode
For PyLox REPL, use pylox command without any arguments
  ```
  $ pylox
  Welcome to python-lox 1.3.0!
  > print(1 + 2)
  3
  > var name = "Alice"
  > print("Hello, " + name + "!")
  Hello, Alice!
  >
  ```
### File Mode
Run a Lox script from a file:
```bash
pylox test.lox
```
Example `test.lox`:
```lox
print(1 + 2);
print(nil);
var x = 10;
print(x / 2);
```
Output:
```
3
None
5
```
## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

