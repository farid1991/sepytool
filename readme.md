# SEpyTool (SETool clone)
Service tool for Sony Ericsson phones

## Supported phones
* DB2000
* DB2010
* DB2012
* DB2020

## Supported interface
* Serial only

## Prerequisites
* Python 3.4 or later installed on your machine.
* To install these requirements, run the following commands:

    ```bash
    # Upgrade pip to the latest version
    python -m pip install -U pip

    # Install the required packages
    pip install -r requirements.txt
    ```
## Features
* Identify Phones Info
* Unlock user code

## TODO
```
* Flash firmware
* Patch firmware
* Read Write GDFS
* Unlock sim
* Ericsson phones support
```

## Examples
* Identify phone in Service Mode
    ```
    python setool.py -p COM1 -b 115200 -e Identify
    ```

## License

[MIT](https://choosealicense.com/licenses/mit/)