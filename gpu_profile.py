import sys
import subprocess
import time
import re
# python gpu_profile.py output.csv 0.2

# Define regular expressions to match the target attributes
temperature_pattern = r"(\d+)\s?°C"
utilization_pattern = r"(\d+)\s?%"
power_pattern = r"(\d+)\s?/\s?(\d+)\s?W"
memory_pattern = r"(\d+)\s?/\s?(\d+)\s?MB"

def run_gpustat(output_file, interval):
    # write header: temperature, utilization, power, memory
    with open(output_file, "w") as file:
        # file.write("temperature (°C)\tutilization (%)\tpower (W)\tmemory (MB)\n")
        file.write("TS,Utilization\n")

    while True:
        try:
            # Run the shell command and capture the output
            command_output = subprocess.check_output(["gpustat", "--no-header", "--show-power"], text=True)
            # Find matches for each attribute using regular expressions
            temperature_match = re.search(temperature_pattern, command_output)
            utilization_match = re.search(utilization_pattern, command_output)
            power_match = re.search(power_pattern,   command_output)
            memory_match = re.search(memory_pattern, command_output)

            temperature = temperature_match.group(1)
            utilization = utilization_match.group(1)
            power_current, power_max = power_match.groups()
            memory_used, memory_total = memory_match.groups()

            # output = f"{temperature}\t{utilization}\t{power_current}\t{memory_used}\n"
            output = f"{int(time.time())},{utilization}\n"

            # Write the captured output to the output file
            with open(output_file, "a") as file:
                file.write(output)

            print(f"Logged GPU stats to {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error running gpustat: {e}")

        # Wait for the specified interval before running the command again
        time.sleep(interval)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <output_file> <time_interval>")
        sys.exit(1)

    output_file = sys.argv[1]
    interval = float(sys.argv[2])

    run_gpustat(output_file, interval)
