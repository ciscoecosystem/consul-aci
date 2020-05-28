module.exports = {
	'entry': {
		'mapping': __dirname + "/mapping.js",
		'details': __dirname + "/details.js",
		'login': __dirname + "/login.js",
		'app': __dirname + "/app.js",
	},
	'module': {
		'loaders': [{
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

	'output': {
		'filename': '[name].js',
		'path': __dirname + '/public',
		'chunkFilename': '[id].[chunkhash].js',
		'crossOriginLoading': "anonymous"
	},
};
