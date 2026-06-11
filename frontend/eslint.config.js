// Flat ESLint config (ESLint 10 + eslint-plugin-vue).
//
// Scope is deliberately narrow: this is NOT a full style linter. It exists to
// enforce one project rule — prefer frappe-ui components over the native HTML
// elements that have a direct frappe-ui equivalent. We start from vue's
// `flat/base` (SFC parsing + processor, no opinionated rules) so the only
// findings are the ones we opt into below; that keeps the signal high and the
// linter worth listening to.
//
// We restrict <select> and <textarea> only. These have clean frappe-ui
// replacements (Select, Textarea) and no legitimate native use in this app, so
// the rule has zero false positives. We intentionally do NOT restrict <button>
// or <input>: the canvas relies on native <button> affordances, the color
// picker needs <input type="color">, and ImageUploader needs a file <input> —
// blanket-flagging those would bury real violations in noise and train everyone
// to ignore the linter.

import vue from 'eslint-plugin-vue'

export default [
  { ignores: ['dist/**', 'node_modules/**'] },

  ...vue.configs['flat/base'],

  {
    files: ['**/*.vue'],
    rules: {
      'vue/no-restricted-html-elements': [
        'error',
        {
          element: 'select',
          message: 'Use the frappe-ui <Select> component instead of a native <select>.',
        },
        {
          element: 'textarea',
          message: 'Use the frappe-ui <Textarea> component instead of a native <textarea>.',
        },
      ],
    },
  },
]
