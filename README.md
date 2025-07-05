# mission spacewalker — capillary-driven bioreactor system

welcome to the official code repository for **mission spacewalker**, University of Alberta's 2024-2025 CAN-RGX project. this system supports the automated cultivation of cyanobacteria under microgravity using a passive, capillary-driven nutrient and CO₂ injection system controlled by a Raspberry Pi.

---

## project overview

mission spacewalker explores autonomous life-support systems for long-duration spaceflight by using cyanobacteria to produce oxygen and biomass. this repository contains the software that interfaces with the sensors, actuators, and telemetry system deployed in the bioreactor during parabolic flight.

---

## software overview

the codebase is organized into the following modules:

### core application

- `main.py` - primary entry point and system control loop

### hardware interfaces

- `sensors/` - pressure, flow, and camera sensor drivers
- `actuators/` - stepper motor and solenoid valve control

---

## installation & setup

**prerequisites:**
- python 3.9+
- raspberry pi os (bookworm or later)
- enable ssh, i2c, and camera modules on pi

**to install and run the system:**

```bash
git clone https://github.com/MissionSpaceWalker/mission-spacewalker.git
cd mission-spacewalker
chmod +x run.sh
./run.sh
```

this script will:
- create a virtual environment
- install Python dependencies
- run the main control loop

## running the program

you can run the mission spacewalker system in two modes:

### real sensor mode (default)

this mode interfaces with the actual hardware connected to the raspberry pi.

```bash
./run.sh
```

this will:

- activate the virtual environment
- install all required dependencies (if not already installed)
- run the main control loop with real sensor input

note: root access may be required for gpio access. if needed, run with `sudo ./run.sh`

### dummy mode (for development without hardware)

if you're develioping on a non-raspberry pi system or testing without access to the hardware, use dummy mode:

```bash
./run.sh --dummy
```

this will:

- simulate flow sensor readings without requiring physical hardware
- use the same system logic and interfaces
- allow testing and development in a fully offline environment

dummy mode is ideal for debugging system logic, logging, or ui components before deploying to flight hardware.

# developers

## code quality

### formatting
this project uses black to enforce consistent formatting across all Python files.

the formatting check will run automatically on every pull request.
if it fails, run the following command to auto-format your code:

```bash
./format.sh
```

this script will:
- format all Python files with black
- sort imports using isort
- apply lint fixes with ruff

