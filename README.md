# Alcatel SR OS Port Check

This Python script uses **Netmiko** to connect to an **Alcatel/Nokia SR OS** device and check ports matching specific configuration expressions.

## What it does

- Connects to the equipment using SSH.
- Searches the configuration for ports matching two defined expressions.
- Removes duplicate ports.
- Checks each port's **Admin** and **Oper** status.
- Retrieves the **wavelength** when available.
- Saves the results to `check_host.csv`.

## Requirements

```bash
pip install netmiko
```

The script requires valid credentials and authorized access to the target equipment.

## Output

The results are saved as:

```text
check_host.csv
```

With the following format:

```text
Hardware_Name;port;status;WaveLength
```

The `<your expression>` placeholders in the script must be replaced with the configuration filters you want to check.
