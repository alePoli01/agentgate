---
skill_name: "ui-designer"
description: "The UI/UX Designer Workflow. Platform-aware design system with consistency enforcement and optional GitHub design reference."
environment_target: "universal"
priority: 2
---
# The UI/UX Designer Workflow

**Trigger**: The user asks for UI design, styling, layout, component creation, or explicitly types `/ui`. Also triggered by the Interrogator Protocol when Aesthetics/UX is unaddressed.

> [!IMPORTANT]
> UI design is NOT one-size-fits-all. A web app and a native iOS app require fundamentally different design approaches. You MUST classify the platform BEFORE writing any UI code.

## Index
1. [Platform Classification](#1-platform-classification)
2. [Platform-Specific Design Rules](#2-platform-specific-design-rules)
3. [GitHub Reference Model](#3-github-reference-model-optional-enhancement)
4. [Consistency Enforcement](#4-consistency-enforcement)
5. [Template Selection & User Preferences](#5-template-selection--user-preferences)

---

## 1. Platform Classification

Before generating ANY UI code, classify the target platform. Use the project's detected tech stack (from `PROJECT_MANIFEST.md`, `ARCHITECTURE.md`, or file extensions):

| Platform Class | Technologies | Design Authority |
|---------------|-------------|-----------------|
| **Web** | HTML/CSS, React, Vue, Next.js, Svelte, Angular, Astro | WCAG AA, Responsive Web Design, CSS-specific |
| **iOS Native** | SwiftUI, UIKit | Apple Human Interface Guidelines (HIG) |
| **Android Native** | Jetpack Compose, XML Views | Material Design 3 (M3) |
| **Cross-Platform Native** | Flutter, React Native, .NET MAUI | Platform-adaptive (iOS → HIG, Android → M3) |
| **Hybrid/PWA** | Capacitor, Electron, Tauri | Lean native for the target platform |

**Action**: Output a classification statement before proceeding:
> *"Platform detected: [CLASS] ([TECHNOLOGY]). Applying [DESIGN AUTHORITY]."*

If the platform is ambiguous, ASK the user. Do not guess.

---

## 2. Platform-Specific Design Rules

### 🌐 Web Platform Rules
- **Responsive-first**: All layouts must work across mobile (320px), tablet (768px), desktop (1024px+).
- **Typography**: Use system font stacks or Google Fonts (Inter, Roboto, Outfit). Never use browser defaults.
- **Color**: Use curated HSL-based palettes. Never use raw CSS color names (`red`, `blue`).
- **Spacing**: Use a consistent spacing scale (4px/8px increments).
- **Interactions**: Hover effects, focus states, smooth transitions (200-300ms ease).
- **Accessibility**: WCAG AA minimum — proper contrast ratios, ARIA labels, keyboard navigation, focus rings.
- **Dark Mode**: If requested, implement via CSS custom properties (`--color-bg`, `--color-text`) with `prefers-color-scheme` media query.

### 🍎 iOS Native Rules (Apple HIG)
- **Navigation**: Use `NavigationStack` (not `NavigationView`), tab bars at the bottom, avoid hamburger menus.
- **Components**: Use SF Symbols for icons. Use native sheets, alerts, and action sheets — NOT custom modals.
- **Typography**: Use `Dynamic Type` system fonts (`.title`, `.body`, `.caption`). Never hardcode font sizes.
- **Color**: Use semantic colors (`Color.primary`, `Color.accentColor`). Support both light and dark mode.
- **Gestures**: Support swipe-to-go-back, pull-to-refresh where appropriate.
- **Safe Areas**: Respect safe area insets on all screens.
- **FORBIDDEN**: Material Design components (FABs, bottom app bars, standard Material cards), Android-style back buttons.

### 🤖 Android Native Rules (Material Design 3)
- **Navigation**: Use `NavigationBar` (bottom) or `NavigationRail` (tablet). Top app bars for context.
- **Components**: Use Material 3 components (`ElevatedCard`, `FilledButton`, `OutlinedTextField`).
- **Typography**: Use Material type scale (`displayLarge`, `bodyMedium`, `labelSmall`).
- **Color**: Use Material 3 dynamic color system. Support `MaterialTheme.colorScheme`.
- **Shape**: Use Material 3 shape tokens (rounded corners: small=4dp, medium=12dp, large=16dp).
- **FORBIDDEN**: iOS-style bottom sheets with grab handles, Apple HIG navigation patterns, flat iOS-style buttons.

### 🔄 Cross-Platform Rules (Flutter, React Native)
- **Adaptive**: Use platform checks (`Platform.isIOS`, `Platform.isAndroid`) to render platform-appropriate components.
- **Navigation**: `CupertinoNavigationBar` on iOS, `AppBar` on Android (Flutter). Platform-specific navigation in React Native.
- **Typography**: Use platform font families (`SF Pro` on iOS, `Roboto` on Android).
- **Components**: Use the `Cupertino` widget family on iOS, `Material` on Android (Flutter). Platform-aware libraries in React Native.

---

## 3. GitHub Reference Model (Optional Enhancement)

This skill works standalone with the built-in rules above. For advanced, comprehensive design systems, it can optionally pull in the `ui-ux-pro-max-skill`.

**Action**: If significant UI work is detected (creating a full page layout, building a design system, implementing multiple components), ask the user:

> *"This task involves significant UI work. Would you like me to download the enhanced design system from [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) for more comprehensive design tokens and style presets? (Yes/No)"*

If **Yes**:
1. Clone or fetch the relevant files into `.ai/design-system/`
2. Read `MASTER.md` for global design tokens
3. Apply tokens as constraints on all generated UI code

If **No**:
- Continue with the built-in platform-specific rules above.

---

## 4. Consistency Enforcement

> [!CAUTION]
> **Cross-contamination is FORBIDDEN.** You must NEVER mix design languages.

### Enforcement Rules
- If the platform is iOS: **zero** Material Design elements. No FABs, no Material cards, no top-aligned back arrows.
- If the platform is Android: **zero** Apple HIG elements. No iOS-style segmented controls, no Apple navigation patterns.
- If the platform is Web: **zero** native mobile patterns. No iOS pull-to-refresh on a desktop page.
- For cross-platform: each platform renders its own style. Components MUST be adaptive, not a single compromised design.

### The Consistency Check
Before marking any UI task as complete, verify:
1. **Are all components from the same design family?** (e.g., all Material 3, or all HIG)
2. **Is the color palette consistent?** (not mixing different color systems)
3. **Is the typography consistent?** (not mixing font scales)
4. **Is the navigation pattern consistent?** (not mixing navigation paradigms)

If any check fails, fix it before declaring the task complete.

---

## 5. Template Selection & User Preferences

If the user provides design preferences in their prompt, they MUST guide the output:

| User Keyword | Template / Approach |
|-------------|-------------------|
| "dark mode" | Dark-first color scheme, light backgrounds for contrast on text |
| "minimalist" | Maximum whitespace, 2-3 colors max, subtle borders |
| "glassmorphism" | Frosted glass effects, background blur, transparency layers |
| "brutalist" | Raw typography, high contrast, minimal decoration |
| "modern" / "premium" | Subtle gradients, micro-animations, refined shadows |
| "accessible" | WCAG AAA, high contrast, large touch targets |

If NO preferences are provided, default to: **clean, modern, accessible** with the platform's default design language.
