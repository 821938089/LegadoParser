import resolve from '@rollup/plugin-node-resolve'
import commonjs from '@rollup/plugin-commonjs'
import { terser } from 'rollup-plugin-terser'

export default [
  // browser-friendly UMD build
  // https://github.com/rollup/rollup/issues/3714
  {
    input: 'src/main.js',
    output: {
      name: 'globalThis',
      file: 'dist/jsExtension.js',
      format: 'umd',
      strict: false,
      extend: true,
      esModule: false
    },
    // plugins: [resolve(), commonjs()]
    plugins: [resolve(), commonjs(), terser()]
  }
]
