---
name: The Design System
colors:
  surface: '#f9f9fb'
  surface-dim: '#d9dadc'
  surface-bright: '#f9f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f5'
  surface-container: '#eeeef0'
  surface-container-high: '#e8e8ea'
  surface-container-highest: '#e2e2e4'
  on-surface: '#1a1c1d'
  on-surface-variant: '#414753'
  inverse-surface: '#2f3132'
  inverse-on-surface: '#f0f0f2'
  outline: '#727784'
  outline-variant: '#c1c6d5'
  surface-tint: '#005cba'
  primary: '#004e9f'
  on-primary: '#ffffff'
  primary-container: '#0066cc'
  on-primary-container: '#dfe8ff'
  inverse-primary: '#aac7ff'
  secondary: '#006c49'
  on-secondary: '#ffffff'
  secondary-container: '#6cf8bb'
  on-secondary-container: '#00714d'
  tertiary: '#883700'
  on-tertiary: '#ffffff'
  tertiary-container: '#af4900'
  on-tertiary-container: '#ffe3d6'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d7e3ff'
  primary-fixed-dim: '#aac7ff'
  on-primary-fixed: '#001b3e'
  on-primary-fixed-variant: '#00458e'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffdbcb'
  tertiary-fixed-dim: '#ffb692'
  on-tertiary-fixed: '#341100'
  on-tertiary-fixed-variant: '#793000'
  background: '#f9f9fb'
  on-background: '#1a1c1d'
  surface-variant: '#e2e2e4'
typography:
  display-lg:
    fontFamily: Hanken Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 17px
    fontWeight: '400'
    lineHeight: '1.5'
    letterSpacing: 0em
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 15px
    fontWeight: '400'
    lineHeight: '1.5'
    letterSpacing: 0em
  label-md:
    fontFamily: Hanken Grotesk
    fontSize: 13px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.02em
  headline-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 28px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 64px
  container-max: 1200px
  gutter: 20px
---

## Brand & Style
The design system is rooted in the principles of high-end Swiss design and contemporary digital precision. It targets a professional audience that values clarity, efficiency, and aesthetic quietude. 

The visual direction is a blend of **Minimalism** and **Glassmorphism**. It leverages significant negative space to reduce cognitive load, paired with sophisticated translucent layers that provide a sense of physical context. The emotional response is one of calm confidence—where the interface recedes to allow the user's content and tasks to take center stage. Every interaction should feel intentional, precise, and effortless.

## Colors
The palette is monochromatic and functional. **Pure White (#FFFFFF)** serves as the primary base to maximize light and space. **Soft Gray (#F5F5F7)** is utilized for secondary surfaces, such as sidebars and grouped content areas, providing subtle differentiation without heavy borders.

**San Francisco Blue (#0066CC)** is the sole primary accent, reserved for interactive elements and primary calls to action. **Professional Emerald (#10B981)** is used exclusively for success states and positive data trends. High-contrast typography is maintained using **Deep Black (#000000)** for headings and a refined **Secondary Gray (#86868B)** for supportive metadata and body descriptions.

## Typography
The system utilizes **Hanken Grotesk** for its technical precision and humanist clarity. 

- **Headings:** Use bold weights (600-700) with slightly tight tracking (-0.01em to -0.02em) to create a premium, "editorial" feel. 
- **Body Text:** Use the 400 weight for maximum legibility. Line heights are generous (1.5) to ensure a comfortable reading rhythm amidst the negative space.
- **Hierarchy:** Contrast is achieved through weight and scale rather than color. Maintain a strict vertical rhythm by aligning all text to a 4px baseline grid.

## Layout & Spacing
This design system employs a **Fixed Grid** model for desktop environments, centering content within a 1200px container to maintain focus. On mobile and tablet, it shifts to a **Fluid Grid** with 20px side margins.

Spacing follows a strict 4pt / 8pt rhythmic scale. Negative space is used as a structural tool: sections should be separated by large `xxl` (64px) gaps to prevent visual clutter. Internal component padding should be generous, typically starting at `md` (16px) for small elements and scaling up to `xl` (32px) for card containers.

## Elevation & Depth
Depth is created through light and transparency rather than heavy shadows.

- **Glassmorphism:** Headers, navigation bars, and floating panels use a background blur (20px to 40px) with a 70-80% opacity white fill. This allows background colors to subtly bleed through, creating a sense of "layered glass."
- **Shadows:** Use a single, highly diffused "Ambient Shadow." Parameters: `0px 10px 40px rgba(0, 0, 0, 0.04)`. For active states or high-level modals, increase the blur to `60px` and the opacity slightly to `0.08`.
- **Z-Index Strategy:** Only three primary layers exist: the base (white), the structural containers (light gray panels), and the elevated glass (floating navigation/modals).

## Shapes
Shapes are defined by "Squircle"-style rounded corners, echoing premium hardware design. 

A standard radius of **10px to 12px** is applied to buttons, input fields, and cards. This provides a soft, approachable feel while maintaining professional structural integrity. Large containers or decorative background elements may use `rounded-xl` (24px) for a more pronounced, modern look.

## Components
- **Buttons:** Primary buttons feature a solid Deep Black or San Francisco Blue background with white text. Secondary buttons use a light gray fill (#F5F5F7) or a ghost style with a subtle 1px border.
- **Inputs:** Fields are minimal, using the soft gray (#F5F5F7) as a background fill with no border in its default state. On focus, a subtle 1px border of San Francisco Blue is applied.
- **Cards:** Cards should have no border. They are defined by their soft gray background or the ambient diffused shadow.
- **Glass Headers:** Global navigation must use a `backdrop-filter: blur()` to maintain context as the user scrolls.
- **Imagery:** Use 3D renders with soft studio lighting or vector technical diagrams with thin 1pt stroke weights to complement the precise nature of the typography.