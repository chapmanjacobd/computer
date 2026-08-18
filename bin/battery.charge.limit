#!/usr/bin/python3
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Set charge limits or conservation mode on Linux.")
    parser.add_argument("--start", type=int, default=40, help="Set the start charge threshold")
    parser.add_argument("--end", type=int, default=80, help="Set the end charge threshold")
    parser.add_argument("--off", action="store_true", help="Disable all charge limiting and reset to 0-100.")
    args = parser.parse_args()

    power_supply_path = "/sys/class/power_supply"
    lenovo_conservation_path = "/sys/bus/platform/drivers/ideapad_acpi/VPC2004:00/conservation_mode"

    if args.off:
        for psu in os.listdir(power_supply_path):
            psu_path = os.path.join(power_supply_path, psu)
            start_path = os.path.join(psu_path, "charge_control_start_threshold")
            end_path = os.path.join(psu_path, "charge_control_end_threshold")
            charge_type_path = os.path.join(psu_path, "charge_type")

            if os.path.exists(start_path) and os.path.exists(end_path):
                try:
                    with open(start_path, "w") as f:
                        f.write("0")
                    with open(end_path, "w") as f:
                        f.write("100")
                    if os.path.exists(charge_type_path):
                        with open(charge_type_path, "w") as f:
                            f.write("Standard")
                    print(f"Standard thresholds reset for {psu}.")
                except IOError as e:
                    print(f"Failed to reset thresholds for {psu}: {e}")

        if os.path.exists(lenovo_conservation_path):
            try:
                with open(lenovo_conservation_path, "w") as f:
                    f.write("0")
                print("Lenovo conservation mode disabled.")
            except IOError as e:
                print(f"Failed to disable Lenovo conservation mode: {e}")

        return

    standard_support_found = False
    for psu in os.listdir(power_supply_path):
        psu_path = os.path.join(power_supply_path, psu)
        type_path = os.path.join(psu_path, "type")
        start_path = os.path.join(psu_path, "charge_control_start_threshold")
        end_path = os.path.join(psu_path, "charge_control_end_threshold")
        charge_type_path = os.path.join(psu_path, "charge_type")

        if os.path.exists(type_path) and os.path.exists(start_path) and os.path.exists(end_path):
            with open(type_path, "r") as f:
                if f.read().strip() == "Battery":
                    standard_support_found = True
                    try:
                        if os.path.exists(charge_type_path):
                            with open(charge_type_path, "w") as f:
                                f.write("Custom")
                        with open(start_path, "w") as f:
                            f.write(str(args.start))
                        with open(end_path, "w") as f:
                            f.write(str(args.end))
                        print(f"Standard thresholds set to {args.start}-{args.end} for {psu}.")
                    except IOError as e:
                        print(f"Failed to set thresholds for {psu}: {e}")

    if not standard_support_found and os.path.exists(lenovo_conservation_path):
        try:
            with open(lenovo_conservation_path, "w") as f:
                f.write("1")
            print("Lenovo conservation mode enabled.")
        except IOError as e:
            print(f"Failed to enable Lenovo conservation mode: {e}")

    if not standard_support_found and not os.path.exists(lenovo_conservation_path):
        print("No supported charge limiting mechanism found on this device.")

if __name__ == "__main__":
    main()
