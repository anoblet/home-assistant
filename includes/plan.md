# Includes UI Plan

## Goals

- Provide a clear, minimal structure for Lovelace YAML under `includes/lovelace/` within the `includes/` folder.
- Keep existing `dashboards`/`views` layout, while adding a consistent place for reusable components and layout helpers.
- Standardize how `custom:flex-card` and `custom:grid-card` are used for responsive dashboards.
- Make it easy to compose dashboards from views, sub-views, and card fragments using `!include` semantics that match current patterns.

---

## Structure

### High-Level Layout

All Lovelace-related includes remain under `includes/lovelace/`:

- `includes/lovelace/dashboards/`  
  High-level dashboards (Overview, Devices, Rooms, Vacuum, specialized dashboards).

- `includes/lovelace/views/`  
  Area- and domain-specific views and sub-views.

- `includes/lovelace/components/` (new)  
  Reusable card fragments and layout wrappers (shared across views/dashboards).

- `includes/lovelace/layouts/` (new, lightweight)  
  Shared flex/grid layout patterns and style helpers.

- `includes/lovelace/apexcharts_card_templates/`  
  Existing chart templates (unchanged).

- `includes/lovelace/dashboards/decluttering_templates/`  
  Existing decluttering templates (unchanged; can coexist with new components).

The existing `packages/lovelace.yaml` continues to be the single source of truth wiring dashboards into Home Assistant:

- `packages/lovelace.yaml`
  - `lovelace.lovelace.dashboards.<id>.filename: includes/lovelace/dashboards/<dashboard>.yaml`

`includes/lovelace/dashboards.yaml` stays minimal and only acts as an informational placeholder.

---

## Dashboards

### Current Pattern

Examples:

- `includes/lovelace/dashboards/dashboard-room.yaml`
- `includes/lovelace/dashboards/dashboard-device.yaml`
- `includes/lovelace/dashboards/dashboard-vacuum.yaml`

These currently:

- Set `title` and optional top-level templates (`apexcharts_card_templates`, `decluttering_templates`).
- Define `views` by explicitly including view files, e.g.:

```yaml
title: Rooms
views:
  - !include ../views/bedroom/index.yaml
  - !include ../views/bathroom/index.yaml
  - !include ../views/living_room/index.yaml
  - !include ../views/storage_room/index.yaml
  - !include ../views/kitchen/index.yaml
```

### Dashboard Types

Recommended logical grouping (mostly already in place):

- **Area-oriented dashboards** (rooms / spaces)
  - e.g. `includes/lovelace/dashboards/dashboard-room.yaml` (Bedroom, Bathroom, Living Room, Storage Room, Kitchen).

- **Domain-oriented dashboards** (devices / capabilities)
  - e.g. `includes/lovelace/dashboards/dashboard-device.yaml` (Blinds, Presence, Fans, Lights, Locks, Media, Motion, Remotes, Climate, Battery, Vacuum).

- **Specialized dashboards**
  - e.g. `includes/lovelace/dashboards/dashboard-vacuum.yaml`, more can be added for Debug, Admin, etc.

### Dashboard Conventions

- **File naming**
  - `dashboard-<name>.yaml` for top-level dashboards.
  - Sub-dashboards stay under subfolders where needed (e.g. `dashboards/bedroom/display.yaml`, `dashboards/storage_room/printer.yaml`).

- **Registration**
  - Each dashboard must have a matching entry in `packages/lovelace.yaml`:
    ```yaml
    lovelace:
      lovelace:
        dashboards:
          dashboard-room:
            filename: includes/lovelace/dashboards/dashboard-room.yaml
            mode: yaml
            title: Rooms
            icon: mdi:floor-plan
    ```

- **View composition**
  - Dashboards should only include view entrypoints (`index.yaml` files under `includes/lovelace/views/`), not individual components.
  - Specialized dashboards may include dedicated views and sub-views (e.g. printer views under `includes/lovelace/views/storage_room/`).

---

## Views & Sub-Views

### Current Structure

Under `includes/lovelace/views/` there are:

- **Area views**: `bedroom/`, `bathroom/`, `living_room/`, `kitchen/`, `storage_room/`, etc.
  - Example: `bedroom/index.yaml`, `bathroom/index.yaml`, `living_room/index.yaml`, `storage_room/index.yaml`, `kitchen/index.yaml`.

- **Area sub-views & fragments**:
  - `includes/lovelace/views/bedroom/display/index.yaml`
  - `includes/lovelace/views/bedroom/temperature.yaml`, `includes/lovelace/views/bedroom/humidity.yaml`, `includes/lovelace/views/bedroom/pressure.yaml`, `includes/lovelace/views/bedroom/carbon_dioxide.yaml`
  - `includes/lovelace/views/storage_room/printer/index.yaml`
  - `includes/lovelace/views/storage_room/printer_two/index.yaml`

- **Domain views**: `battery/`, `blinds/`, `climate/`, `fans/`, `lights/`, `locks/`, `media/`, `motion/`, `presence/`, `vacuum/`, etc.
  - Example: `battery/index.yaml`, `blinds/index.yaml`, `vacuum/index.yaml`.

### View Conventions

1. **Entry point per view**
   - Each view has an `index.yaml` acting as the main file included by dashboards.
   - Path patterns:
     - Area view: `includes/lovelace/views/<area>/index.yaml`
     - Domain view: `includes/lovelace/views/<domain>/index.yaml`
     - Sub-view: `includes/lovelace/views/<area>/<sub_view>/index.yaml` (e.g. `includes/lovelace/views/bedroom/display/index.yaml`)

2. **Sub-view semantics**
   - Use sub-views when:
     - A view is logically secondary (e.g. detailed sensor display) but still exposed as its own Lovelace view.
     - It heavily reuses fragments from the main view (like Bedroom display using temperature/humidity/CO₂/pressure fragments).
   - Example (already in repo):

     ```yaml
     # includes/lovelace/views/bedroom/display/index.yaml
     cards:
       - cards:
           - type: custom:generic-card
             class:
               - padding
               - relative
             cards:
               - !include ../temperature.yaml
           - type: custom:grid-card
             cards:
               - !include ../humidity.yaml
               - !include ../carbon_dioxide.yaml
               - !include ../pressure.yaml
             style:
               gap: 1rem
               'grid-template-columns': repeat(auto-fit, minmax(256px, auto))
         type: custom:grid-card
     ```

3. **Fragments within a view folder**
  - Small, re-usable card groups (e.g. temperature/humidity graphs, printer info blocks) should live next to the view's `index.yaml` and be included via `!include`.
   - Naming convention:
     - `*_summary.yaml` (e.g. `air_quality_summary.yaml`)
     - `*_metrics.yaml` (e.g. `climate_metrics.yaml`)
     - `*_controls.yaml` (e.g. `room_controls.yaml`)

4. **When to factor into `components/` instead**
   - If a fragment is used in multiple areas or dashboards (e.g. room control block layout repeated across Bedroom/Living Room/Kitchen/Bathroom/Storage Room), move it into `includes/lovelace/components/` (see next section).

---

## Components

### Structure

Introduce a minimal components hierarchy:

- `includes/lovelace/components/`
  - `layouts/` – layout wrappers using flex/grid (shared).
  - `cards/` – reusable card blocks (room controls, metric tile grids, media blocks, etc.).
  - Optional deeper grouping:
    - `cards/areas/` – area-oriented card groups.
    - `cards/domains/` – domain-oriented card groups.
    - `cards/diagnostics/` – debug/diagnostic panels.

This complements existing:

- `includes/lovelace/apexcharts_card_templates/`
- `includes/lovelace/dashboards/decluttering_templates/`

### Recommended Components

Based on patterns in the repo:

1. **Room primary controls block**
  - Used in `includes/lovelace/views/bedroom/index.yaml`, `includes/lovelace/views/bathroom/index.yaml`, `includes/lovelace/views/living_room/index.yaml`, `includes/lovelace/views/storage_room/index.yaml`, `includes/lovelace/views/kitchen/index.yaml`.
   - Pattern: `grid-card` ➔ `flex-card` with min/max width and gap, containing mushroom cards for climate, lights, blinds, fans, humidifiers, media.

   Suggested component:

   - `includes/lovelace/components/cards/room_primary_controls.yaml`

   Example content pattern:

   ```yaml
   # room_primary_controls.yaml (example pattern)
   - type: custom:flex-card
     style:
       '--flex-card-min-width': '320px'
       '--flex-card-max-width': '100vw'
       'gap': '1rem'
     cards:
       # View-specific entities supplied via !include or custom variables
       # Example for Bedroom: mushroom climate, lights, blinds, fan, humidifier, media decluttering-cards
   ```

   In an area view:

   ```yaml
   # includes/lovelace/views/bedroom/index.yaml (conceptual)
   cards:
     - type: custom:generic-card
       style:
         'background-color': 'initial'
       cards:
         - type: custom:grid-card
           style:
             'gap': '1rem'
           cards:
             - !include ../../components/cards/room_primary_controls_bedroom.yaml
             - !include ../../components/cards/room_metrics_grid_bedroom.yaml
   ```

   (Alternatively, keep the entity lists per-room in separate files under `components/cards/areas/`.)

2. **Room metrics tile grid**
   - Existing pattern:

     ```yaml
     - type: custom:grid-card
       style:
         'gap': '1rem'
         'grid-template-columns': 'repeat(auto-fit, minmax(192px, auto))'
       cards:
         - type: tile
           entity: ...
         ...
     ```

   - Introduce a common pattern in `components/layouts/room_metrics_grid.yaml` to capture this grid behavior, while the actual tiles remain per-area.

3. **Printer layout block**
  - `includes/lovelace/views/storage_room/printer/index.yaml` and `includes/lovelace/views/storage_room/printer_two/index.yaml` share:
     - Outer `flex-card` with `background-color: initial`.
     - Inner `grid-card` with `grid-template-rows: 'auto max-content'`.
     - Nested `flex-card` centering a picture-entity and a responsive metrics grid.

   - Create:
     - `components/layouts/printer_layout.yaml` – the nested flex+grid structure.
     - `components/cards/printer_metrics_<name>.yaml` – per-printer tiles (X1 Carbon vs OctoPrint).

4. **Presence configuration grids**
  - `includes/lovelace/views/presence/index.yaml` and `includes/lovelace/views/presence/bedroom/index.yaml` share:
     - Outer `generic-card` ➔ `grid-card` container.
     - Inner `grid-card` with `repeat(auto-fit, minmax(192px, auto))` for presence and configuration tiles.

   - Extract a shared layout into `components/layouts/presence_grid.yaml`.

### Includes & Merge Strategies

- For **single components**:
  - Use `!include` from views and sub-views:
    ```yaml
    cards:
      - !include ../../components/cards/room_primary_controls_bedroom.yaml
    ```

- For **directories of fragments**:
  - When you have multiple YAML fragments representing a list of cards (e.g. multiple graphs or tiles), consider:
    ```yaml
    cards: !include_dir_merge_list ./cards
    ```
  - Keep this optional to avoid large reorganization; start using `!include_dir_merge_list` for new views where it makes sense.

---

## Responsive Layout with flex-card and grid-card

The repo already uses `custom:flex-card` and `custom:grid-card` in good patterns. This section standardizes those patterns.

### Pattern A: Room Overview (Controls + Metrics)

Used in:

- `includes/lovelace/views/bedroom/index.yaml`
- `includes/lovelace/views/bathroom/index.yaml`
- `includes/lovelace/views/kitchen/index.yaml`
- `includes/lovelace/views/living_room/index.yaml`
- `includes/lovelace/views/storage_room/index.yaml`

Structure:

1. **Outer container**: `custom:generic-card` with neutral background.

2. **Content layout**: `custom:grid-card` with `gap: '1rem'`.

3. **Primary controls**: `custom:flex-card` with min/max width.

4. **Metrics**: `custom:grid-card` with responsive columns.

Standard pattern:

```yaml
cards:
  - type: custom:generic-card
    style:
      'background-color': 'initial'
    cards:
      - type: custom:grid-card
        style:
          'gap': '1rem'
        cards:
          - type: custom:flex-card
            style:
              '--flex-card-min-width': '320px'
              '--flex-card-max-width': '100vw'
              'gap': '1rem'
            cards:
              # primary controls (climate, lights, blinds, media, etc.)
          - type: custom:grid-card
            style:
              'gap': '1rem'
              'grid-template-columns': 'repeat(auto-fit, minmax(192px, auto))'
            cards:
              # tiles for presence, temperature, humidity, pressure, vacuum, etc.
```

Responsive behavior:

- `flex-card`:
  - `--flex-card-min-width: 320px` → cards stack on narrow screens and wrap when space allows.
  - `--flex-card-max-width: 100vw` → avoids overflow on small devices.

- `grid-card` with `repeat(auto-fit, minmax(192px, auto))`:
  - Automatically adjusts column count based on viewport width.
  - Works well for small tiles (sensors, presence, media actions).

### Pattern B: Dense Metrics Grid (Bedroom Display)

Used in `includes/lovelace/views/bedroom/display/index.yaml`:

- Single `grid-card` acting as the root, with:
  - A full-width generic-card for a graph.
  - A responsive `grid-card` for multiple metric fragments (humidity, CO₂, pressure).

Key styles:

```yaml
type: custom:grid-card
style:
  '--gap': 1rem
  '--padding': 'var(--gap)'
  gap: 1rem
  'grid-template-rows': 'repeat(auto-fit, minmax(256px, auto))'
cards:
  - type: custom:generic-card
    style:
      'grid-column': 1 / -1
    cards:
      - !include ../temperature.yaml
  - type: custom:grid-card
    style:
      gap: 1rem
      'grid-template-columns': repeat(auto-fit, minmax(256px, auto))
    cards:
      - !include ../humidity.yaml
      - !include ../carbon_dioxide.yaml
      - !include ../pressure.yaml
```

Recommended usage:

- Use this pattern for rich diagnostic pages with multiple graphs and metrics.
- Keep graph content in separate fragments (`temperature.yaml`, etc.) and reference them via `!include`.

### Pattern C: Camera + Metrics (Printers)

Used in:

- `includes/lovelace/views/storage_room/printer/index.yaml`
- `includes/lovelace/views/storage_room/printer_two/index.yaml`

Structure:

1. Outer `flex-card` with `background-color: initial`.
2. Inner `grid-card` with two rows: camera on top, metrics grid at the bottom.
3. Inner `flex-card` centering the camera.
4. Metrics `grid-card` with `repeat(auto-fit, minmax(192px, auto))`.

Key pattern:

```yaml
cards:
  - type: custom:flex-card
    style:
      'background-color': 'initial'
    cards:
      - type: custom:grid-card
        style:
          'gap': '1rem'
          'grid-template-rows': 'auto max-content'
        cards:
          - type: custom:flex-card
            style:
              'align-items': 'center'
              'margin': '0 auto'
              'max-width': '50%'
            cards:
              - type: picture-entity
                camera_view: live
                entity: <camera_entity>
          - type: custom:grid-card
            style:
              'align-items': 'end'
              'gap': '1rem'
              'grid-template-columns': 'repeat(auto-fit, minmax(192px, auto))'
            cards:
              # printer tiles
```

Recommended usage:

- Reuse this layout via `includes/lovelace/components/layouts/printer_layout.yaml`.
- Supply printer-specific tiles via a separate included file.

### Pattern D: Configuration Grids (Presence Debug)

Used in:

- `includes/lovelace/views/presence/index.yaml`
- `includes/lovelace/views/presence/bedroom/index.yaml` (and similar per-area presence views).

Structure:

- Outer `generic-card` ➔ `grid-card`.
- Inner `grid-card` for configuration tiles, using `repeat(auto-fit, minmax(192px, auto))`.

Use this pattern whenever you need dense, configurable tiles that should wrap nicely on small screens.

---

## Implementation Steps

1. **Confirm existing wiring**
  - Keep `packages/lovelace.yaml` as the authoritative place to register dashboards pointing to `includes/lovelace/dashboards/*.yaml`.
  - Keep `includes/lovelace/dashboards.yaml` as is (informational).

2. **Introduce `components` and `layouts` directories**
   - Create:
     - `includes/lovelace/components/`
     - `includes/lovelace/components/cards/`
     - `includes/lovelace/components/layouts/`
   - Start by factoring out *new* shared blocks into components instead of moving everything at once.

3. **Factor out high-value shared patterns**
   - From , , , , :
     - Extract the `flex-card` primary controls into per-room or shared components under `components/cards/`.
     - Extract the metrics `grid-card` layout pattern into `components/layouts/room_metrics_grid.yaml`.

   - From :
     - Extract the camera+metrics layout into `components/layouts/printer_layout.yaml`.
     - Define printer-specific metrics files under `components/cards/`.

   - From  and :
     - Extract configuration grids into `components/layouts/presence_grid.yaml`.

4. **Standardize new views and dashboards**
   - When adding a new area or domain view:
  - Place it under `includes/lovelace/views/`.
     - Use one of the established layout patterns (A–D).
     - Use `!include` to pull in fragments and components rather than inlining large blocks.

   - When adding a new dashboard:
     - Create `includes/lovelace/dashboards/dashboard-<name>.yaml`.
     - Compose it from existing area/domain views via `!include`.
     - Register it in `packages/lovelace.yaml` under `lovelace.lovelace.dashboards`.

5. **Gradual refactor of existing views**
   - As you touch existing views:
     - Replace repeated inline patterns with references to `components/layouts/*` and `components/cards/*`.
     - Maintain existing visual behavior by preserving `flex-card` and `grid-card` style settings (min/max widths, gaps, `repeat(auto-fit, minmax(...))`).

6. **Keep responsiveness central**
   - Default to:
     - `custom:flex-card` with `--flex-card-min-width: 320px` and `gap: 1rem` for rows of primary controls.
     - `custom:grid-card` with `grid-template-columns: 'repeat(auto-fit, minmax(192px, auto))'` (or `256px` for larger content) for metric tiles.
   - Reserve more specialized layouts (camera+metrics, full-width graphs) for specific components under `layouts/`.

By following this structure and these patterns, the  folder remains close to the current organization while gaining a clear separation between dashboards, views, sub-views, and reusable flex/grid-based components.
By following this structure and these patterns, the `includes/` folder remains close to the current organization while gaining a clear separation between dashboards, views, sub-views, and reusable flex/grid-based components.
