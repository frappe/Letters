import frappeUIPreset from 'frappe-ui/tailwind'

// Icon class names used dynamically (template literals) — invisible to the
// JIT content scanner, so we safelist them explicitly.
const dynamicLucideIcons = [
  'lucide-align-justify',
  'lucide-award',
  'lucide-box',
  'lucide-chevron-right',
  'lucide-chevron-up',
  'lucide-columns',
  'lucide-layout',
  'lucide-message-square',
  'lucide-more-horizontal',
  'lucide-play-circle',
  'lucide-share-2',
  'lucide-shopping-bag',
  'lucide-sidebar',
  'lucide-tag',
  'lucide-user',
  'lucide-users',
]

export default {
  presets: [frappeUIPreset],
  content: [
    './index.html',
    './src/**/*.{vue,js,ts}',
    './node_modules/frappe-ui/src/**/*.{vue,js,ts}',
  ],
  safelist: dynamicLucideIcons,
  theme: {
    extend: {
      backgroundColor: {
        // surface.base was in a locally-modified frappe-ui that got wiped by
        // npm install. Define it here so bg-surface-base keeps working.
        surface: {
          base: 'var(--surface-base, #ffffff)',
        },
      },
    },
  },
}
