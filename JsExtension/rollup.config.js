import resolve from '@rollup/plugin-node-resolve'
import commonjs from '@rollup/plugin-commonjs'
import { terser } from 'rollup-plugin-terser'

export default [
  // browser-friendly UMD build
  {
    input: 'src/main.js',
    output: {
      name: 'java',
      file: 'dist/jsExtension.js',
      format: 'umd',
      strict: false
    },
    plugins: [resolve(), commonjs(), terser()]
  }
]
