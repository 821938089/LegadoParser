import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';

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
		plugins: [
			resolve(), // so Rollup can find `ms`
			commonjs() // so Rollup can convert `ms` to an ES module
		]
	}
];
