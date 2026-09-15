#!/usr/bin/python3

# Author: Abderrezzak YAHI

from netmiko import (
    ConnectHandler,
    NetMikoTimeoutException,
    NetMikoAuthenticationException,
)
import getpass


print("""
        ***********************       WARNING      **************************

          You must have prior authorization to run this script.
          All connections may be logged and monitored.

          By running this script, you confirm that you are authorized
          to access the target equipment.

        *********************************************************************
""")


def get_ports(output):
    """Extract port identifiers from SR OS configuration output."""
    ports = []

    for line in output.splitlines():
        line = line.strip()

        if not line:
            continue

        parts = line.split()

        try:
            port = parts[-2].split(":")[0]
            ports.append(port)
        except (IndexError, AttributeError):
            continue

    return ports


def main():

    # ----------------------------------------------------------------------
    # User credentials
    # ----------------------------------------------------------------------

    host = input("Please enter the hostname of your equipment: ").strip()
    username = input("Please enter your username: ").strip()
    password = getpass.getpass("Please enter your password: ")

    print(f"\nYou are going to connect to: {host}")
    print(f"You are going to log in as: {username}\n")

    device = {
        "device_type": "alcatel_sros",
        "host": host,
        "username": username,
        "password": password,
    }

    # ----------------------------------------------------------------------
    # Connect to equipment
    # ----------------------------------------------------------------------

    try:
        device_connect = ConnectHandler(**device)

        print(f"Successfully connected to {host}\n")

    except NetMikoAuthenticationException:
        print("ERROR: Authentication failed.")
        return

    except NetMikoTimeoutException:
        print("ERROR: Connection timed out.")
        return

    except Exception as error:
        print(f"ERROR: Unable to connect to {host}")
        print(error)
        return

    # ----------------------------------------------------------------------
    # Search configuration
    # ----------------------------------------------------------------------

    try:

        command_1 = (
            "admin display-config | match "
            "'<your expression>' context all | match sap"
        )

        command_2 = (
            "admin display-config | match "
            "'<your expression>' context all | match sap"
        )

        output_1 = device_connect.send_command(command_1)
        output_2 = device_connect.send_command(command_2)

        port_list_1 = get_ports(output_1)
        port_list_2 = get_ports(output_2)

        # Merge both lists and remove duplicates
        port_list = sorted(set(port_list_1).union(port_list_2))

        print(f"Found {len(port_list)} ports.")

        # ------------------------------------------------------------------
        # Check ports
        # ------------------------------------------------------------------

        with open("check_host.csv", "w", encoding="utf-8") as csv_file:

            csv_file.write(
                "Hardware_Name;port;status;WaveLength\n"
            )

            for port in port_list:

                command = (
                    f'show port {port} | '
                    'match expression "Description|Oper|Admin|Wavel"'
                )

                output = device_connect.send_command(command)

                lines = [
                    line.strip()
                    for line in output.splitlines()
                    if line.strip()
                ]

                # ----------------------------------------------------------
                # Extract wavelength
                # ----------------------------------------------------------

                wavelength = "lambda does not exist"

                if len(lines) >= 5:

                    try:
                        wavelength = (
                            lines[4]
                            .split(": ", 1)[1]
                            .split()[0]
                        )
                    except (IndexError, AttributeError):
                        pass

                # ----------------------------------------------------------
                # Extract Admin / Operational status
                # ----------------------------------------------------------

                status = "unknown"

                if len(lines) >= 3:

                    try:
                        admin_state = (
                            lines[1]
                            .split(": ", 1)[1]
                            .split()[0]
                        )

                        oper_state = (
                            lines[2]
                            .split(": ", 1)[1]
                            .split()[0]
                        )

                        if admin_state != oper_state:
                            status = "down"
                        else:
                            status = "up"

                    except (IndexError, AttributeError):
                        pass

                csv_file.write(
                    f"{host};{port};{status};{wavelength}\n"
                )

        print("\nResults saved to: check_host.csv")

    finally:

        device_connect.disconnect()

        print(f"Disconnected from {host}")


if __name__ == "__main__":
    main()
