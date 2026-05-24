# BetavanX Frontend Architecture

## Frontend Stack

- Next.js 16
- React
- TypeScript
- TailwindCSS

---

# Architecture Style

BetavanX frontend uses a modular reusable architecture.

The UI system is component-driven and separated into reusable layers.

---

# Main Structure

```plaintext
app/
components/
styles/
docs/
```

---

# Component Layers

## ui/

Reusable low-level UI components.

Examples:

- PageHeader
- SectionCard
- Badge
- LoadingState

---

## forms/

Reusable form system.

Examples:

- FormLayout
- FormGrid
- FormField
- TextInput
- TextareaInput
- SelectInput
- SubmitButton

---

## tables/

Reusable table architecture.

Examples:

- TableWrapper
- TableHead
- TableRow
- TableCell
- EmptyState
- TasksTable
- WorkersTable
- ReportsTable

---

## layout/

Layout components.

Examples:

- Sidebar
- DashboardLayout

---

# Design Philosophy

The frontend is designed for:

- scalability
- reusable systems
- enterprise dashboards
- BIM integrations
- real-time analytics
- construction intelligence systems

---

# Current State

Frontend foundation is stable.

Implemented systems:

- reusable tables
- reusable forms
- fixed sidebar
- collapsible navigation
- responsive layout foundation
- shared UI architecture

---

# Next Planned Systems

- API abstraction layer
- Authentication
- Charts system
- State management
- Realtime updates
- Notification system
- AI recommendation layer