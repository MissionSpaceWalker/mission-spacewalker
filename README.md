# mission spacewalker — capillary-driven bioreactor system

Welcome to the official code repository for **mission spacewalker**, University of Alberta's 2024-2025 CAN-RGX project. This system supports the automated cultivation of cyanobacteria under microgravity using a passive, capillary-driven nutrient and CO₂ injection system controlled by a Raspberry Pi.

---

## project overview

mission spacewalker explores autonomous life-support systems for long-duration spaceflight by using cyanobacteria to produce oxygen and biomass. This repository contains the software that interfaces with the sensors, actuators, and telemetry system deployed in the bioreactor during parabolic flight.

---

## system architecture

The system includes:

- cyanobacteria bioreactor
- capillary-driven nutrient delivery
- CO₂ injection system
- dual raspberry pi camera monitoring
- raspberry pi control unit
- environmental sensors: pressure, flow rate
- actuators: solenoid valve, stepper motor, rotary encoder
- laptop gui (telemetry + ssh)

---

## hardware overview

| component               | function                          |
|------------------------|-----------------------------------|
| raspberry pi 4         | central controller (python-based) |
| stepper motor + driver | activates gas release             |
| solenoid valve         | controls nutrient delivery        |
| pressure sensor        | monitors internal chamber pressure|
| flow sensor            | measures bg-11 nutrient transfer  |
| dual cameras           | visual confirmation and backup    |

A complete electrical schematic is available in the `docs/` folder.

---

## software overview

This repo includes:

- `/main.py`: main system loop
- `/sensors/`: modular sensor drivers
- `/actuators/`: motor and solenoid interfaces
- `/utils/`: logging, data encoding, safety checks
- `/config/`: system constants and gpio maps
- `/gui/`: optional gui for real-time telemetry

---

## installation & setup

**prerequisites:**
- python 3.9+
- raspberry pi os (bookworm or later)
- enable ssh, i2c, and camera modules on pi

**to install and run the system:**

```bash
git clone https://github.com/mission-spacewalker/bioreactor.git
cd bioreactor
chmod +x run.sh
./run.sh
```

This script will:
- create a virtual environment
- install Python dependencies
- run the main control loop

