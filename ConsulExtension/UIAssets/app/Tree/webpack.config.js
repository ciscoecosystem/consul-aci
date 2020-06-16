module.exports = {
	'entry': {
		'tree': __dirname + "/src/client/app/index.js",
	},
	'module': {
		'rules': [{
			'test': /\.js$/,
			'exclude': /(node_modules|bower_compontents)/,
			'loader': 'babel-loader',
			'options': {
				"presets": [
					"es2015",
					"react",
					"env",
					"stage-3"
				],
				"plugins": [
					"transform-object-rest-spread"
				]
			}
		},
		{
			'test': /\.css$/,
			'loaders': ['style-loader', 'css-loader'],
		},
		{
			'test': /\.(png|jpg|gif|svg|eot|ttf|woff|woff2)$/,
			'loader': 'url-loader?limit=10000&name=[name].[ext]',
		}
		]
	},
	"stats": {
		"warnings": false
	},
	'output': {
		'filename': '[name].js',
		'path': __dirname + '/src/client/public',
		'chunkFilename': '[id].[chunkhash].js',
		'crossOriginLoading': "anonymous"
	},
};
