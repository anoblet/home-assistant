# Home Assistant Configuration

![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Core-blue?style=for-the-badge&logo=home-assistant)
![ESPHome](https://img.shields.io/badge/ESPHome-Firmware-black?style=for-the-badge&logo=esphome)
![TypeScript](https://img.shields.io/badge/TypeScript-Strict-3178C6?style=for-the-badge&logo=typescript)
![Lit](https://img.shields.io/badge/Lit-Components-324FFF?style=for-the-badge&logo=lit)
![Node.js](https://img.shields.io/badge/Node.js-Tooling-339933?style=for-the-badge&logo=nodedotjs)

This repository functions as a **Professional Grade Home Assistant Configuration & AI Development Framework**. It goes beyond a standard smart home setup by integrating a comprehensive AI agent ecosystem, custom hardware firmware, and a sophisticated TypeScript-based frontend architecture.

It powers a real-world apartment with over **45 automation packages** and **25+ ESPHome devices**, serving as both a production system and a testbed for advanced home automation patterns.

## Configuration Architecture

The system is architected for modularity, testability, and scale:

- **Split Configuration**: Logic is decentralized into `packages/`, where each directory (e.g., `packages/bedroom/`) contains all relevant entities, automations, and scripts for a specific domain or area. This is merged via `!include_dir_merge_named`.
- **Hardware-First**: Custom firmware for ESP32/ESP8266 devices lives in `esphome/`, ensuring sensor data (presence, air quality, environmental) is tightly coupled with Home Assistant entities.
- **Custom Frontend**: The UI is built with **Lit** and **TypeScript** in `www/custom-elements/`, adhering to modern web standards rather than just YAML dashboards.
- **AI-Driven DevOps**: The repository includes a custom "Copilot" framework for agentic development, automated refactoring, and semantic analysis.

## The Copilot Framework

A unique feature of this repository is the **Copilot Framework**, housed in the `copilot/` directory. This is a dedicated AI development environment that layers intelligent agents over the Home Assistant configuration.

- **Agentic Workflow**: Uses custom AI agents to analyze, refactor, and generate configuration code.
- **Context Awareness**: Integrates with Model Context Protocol (MCP) servers to understand the full repository state.
- **Automation**: Scripts for bootstrapping, testing, and verifying system integrity.

For a deep dive into the AI architecture, see the [Copilot Documentation](copilot/README.md).

## Repository Structure

```text
├── packages/           # Feature bundles (Areas, Domains, Integrations)
├── esphome/            # Firmware definitions for 25+ devices
├── copilot/            # AI Tooling, Agents, and Bootstrap scripts
├── www/
│   └── custom-elements # Lit-based Typescript UI components
├── custom_components/  # Custom integrations (Spook, VeSync, etc.)
└── reports/            # System audits and complexity analysis
```

## Complexity & Scale

This project is rated **5/5 (Professional Grade)** for complexity. It demonstrates exceptional technical depth but requires significant expertise to maintain.

- **Scale**: 45+ Packages, 25+ ESPHome Devices, 10+ Custom Components.
- **Stack**: Home Assistant YAML, ESPHome YAML/C++, TypeScript, Lit, Node.js, Python.
- **Analysis**: See the full [Complexity Report](reports/complexity.md) for architectural insights.

## Automation Pillars

- **Presence-driven logic**: Integrates device trackers, LD2410C radar sensors, and PIR motion across rooms.
- **Environmental management**: Monitors particulate matter, CO2, humidity, and temperature triggers.
- **Adaptive Lighting**: Coordinates color temperature and brightness with circadian rhythms.
- **Security & Safety**: Surfaces water leaks, door contacts, and unexpected occupancy.

## Dashboards and User Experience

- Primary dashboards are assembled in `includes/lovelace/`, referencing modular views.
- The UI leverages custom Lit components (`www/custom-elements/`) alongside standard cards for a tailored experience.

## Getting Started

To utilize the tooling and AI features of this repository, you must bootstrap the environment.

**Prerequisites**:

- Node.js 22.6+
- pnpm

**Bootstrap**:

1. Clone the repository.
2. Install dependencies and setup hooks:
   ```bash
   pnpm install
   pnpm bootstrap
   ```
3. Establish your `secrets.yaml` (not included in the repo) based on the package references.

**Tooling**:

- **Format**: `pnpm format` (Prettier)
- **Lint**: `lint-staged` runs automatically on commit.
- **Reload**: `pnpm reload` to apply configuration changes.
- **CLI**: Use `pnpm home-assistant` for state inspection and validation.

## Roadmap and Contributing

- **Refactoring**: Ongoing work to normalize package hierarchies and standardize naming.
- **Style Enforce**: Strict adherence to the guidelines in `.github/instructions/`.

For detailed contribution rules, refer to the [Home Assistant Instructions](.github/instructions/home-assistant.instructions.md).
